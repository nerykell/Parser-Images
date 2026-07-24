#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core parsing logic for Parser-Images.

Handles URL collection from Google Images and DuckDuckGo,
parallel downloading, deduplication, and reverse image search.
"""

import os
import sys
import re
import time
import random
import hashlib
import shutil
import tempfile
import threading
import requests
from urllib.parse import urlparse, unquote, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

from .i18n import set_language, t, get_language
from .utils.hashing import load_existing_hashes
from .utils.download import download_image_to_temp
from .utils.file_ops import create_folder, make_unique_filename

session = requests.Session()

# =============================================================================
# STOP EVENT
# =============================================================================
stop_event = threading.Event()


def _esc_listener():
    """Listen for ESC key to stop parsing."""
    if os.name == 'nt':
        import msvcrt
        while not stop_event.is_set():
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':
                    stop_event.set()
                    print("\n[ESC] " + t('stop_user').strip())
                    break
                while msvcrt.kbhit():
                    msvcrt.getch()
            time.sleep(0.1)
    else:
        import select
        import termios
        import tty
        old_settings = None
        try:
            old_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        except Exception:
            while not stop_event.is_set():
                time.sleep(0.5)
            return

        try:
            while not stop_event.is_set():
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key == '\x1b':
                        while select.select([sys.stdin], [], [], 0.01)[0]:
                            sys.stdin.read(1)
                        stop_event.set()
                        print("\n[ESC] " + t('stop_user').strip())
                        break
                time.sleep(0.05)
        finally:
            if old_settings is not None:
                try:
                    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
                except Exception:
                    pass


def parse_query(line):
    """Parse a query line into text and limit."""
    line = line.strip()
    if not line:
        return None, None
    match = re.search(r'(\d+)$', line)
    if match:
        number = int(match.group(1))
        text = re.sub(r'\s*\d+$', '', line).strip()
        return text, number
    return line, None


# =============================================================================
# PARSING queries.txt
# =============================================================================
def parse_queries_file(filepath, default_count=10):
    """Parse queries.txt into list of single queries and groups."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    queries = []
    current_group = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Group: [name] count
        if stripped.startswith('['):
            if current_group is not None:
                queries.append(current_group)

            match = re.match(r'\[(.*?)\]\s*(\d+)', stripped)
            if match:
                name = match.group(1).strip()
                total = int(match.group(2))
            else:
                name = stripped[1:].strip()
                if name.endswith(']'):
                    name = name[:-1].strip()
                total = default_count

            current_group = {
                'type': 'group',
                'folder': name,
                'total_limit': total,
                'variations': []
            }
            continue

        # Extra in group: &query count
        if stripped.startswith('&'):
            if current_group is None:
                print(t('warn_outside_group').format(stripped))
                continue
            rest = stripped[1:].strip()
            query_text, limit = parse_query(rest)
            if query_text:
                current_group['variations'].append({
                    'query': query_text,
                    'limit': limit if limit is not None else default_count
                })
            continue

        # Single query
        if current_group is not None:
            queries.append(current_group)
            current_group = None

        query_text, limit = parse_query(stripped)
        if query_text:
            queries.append({
                'type': 'single',
                'query': query_text,
                'limit': limit if limit is not None else default_count,
                'folder': re.sub(r'[\\/*?:"<>|]', "_", query_text)
            })

    if current_group is not None:
        queries.append(current_group)

    return queries


# =============================================================================
# GOOGLE: HELPER FUNCTIONS
# =============================================================================
def handle_age_verification(driver, search_engine):
    """Click age verification button if present."""
    if search_engine == 'google':
        xpath = "//button[contains(text(), \"I'm over 18\") or contains(text(), 'Continue')]"
    else:
        xpath = "//button[contains(text(), 'Подтвердить') or contains(text(), 'Continue')]"
    try:
        age_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", age_button)
        time.sleep(0.5)
        return True
    except Exception:
        return False


def set_image_size(driver, search_engine, quality):
    """Set image size filter to Large if quality is high."""
    if quality == 'low':
        return
    if search_engine != 'google':
        return
    try:
        tools_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(., 'Tools')]"))
        )
        tools_button.click()
        time.sleep(0.5)
        size_menu = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Size']/parent::div"))
        )
        size_menu.click()
        time.sleep(0.5)
        large_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Large')]"))
        )
        large_option.click()
        time.sleep(0.5)
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.5)
    except Exception:
        try:
            current_url = driver.current_url
            if '&tbs=isz:' not in current_url:
                driver.get(current_url + "&tbs=isz:l")
                time.sleep(1)
        except Exception:
            pass


# =============================================================================
# GOOGLE: URL COLLECTION
# =============================================================================
def collect_google_urls(driver, seen_srcs, processed_urls, needed, config):
    """Collect image URLs from Google Images via scrolling."""
    new_urls = []
    empty_scrolls = 0
    max_empty = 20
    start_time = time.time()
    timeout = config.get('timeout_collect', 60)
    last_height = driver.execute_script("return document.body.scrollHeight")
    img_selector = "img[data-src], img.rg_i, img[src]"
    min_size = config.get('min_image_size', 200)

    pbar = tqdm(total=needed, desc="   Collect URLs",
                bar_format='{l_bar}{bar}{r_bar}', leave=True)

    while (time.time() - start_time < timeout) and len(new_urls) < needed:
        if stop_event.is_set():
            break

        handle_age_verification(driver, 'google')

        try:
            imgs = driver.find_elements(By.CSS_SELECTOR, img_selector)
        except StaleElementReferenceException:
            time.sleep(0.5)
            continue

        found_new = False
        for img in imgs:
            if stop_event.is_set():
                break

            try:
                w = img.size.get('width', 0)
                h = img.size.get('height', 0)
                if w < min_size or h < min_size:
                    continue
            except StaleElementReferenceException:
                continue

            try:
                src = img.get_attribute('data-src') or img.get_attribute('src') or ''
            except StaleElementReferenceException:
                continue

            if not src or not src.startswith('http'):
                continue
            if src in seen_srcs or 'logo' in src.lower() or 'button' in src.lower():
                continue

            # Extract original from parent <a> href
            if 'encrypted-tbn' in src or 'gstatic' in src:
                try:
                    parent = img.find_element(By.XPATH, "./ancestor::a[1]")
                    href = parent.get_attribute('href')
                    if href and 'imgurl=' in href:
                        match = re.search(r'imgurl=([^&]+)', href)
                        if match:
                            real_url = unquote(match.group(1))
                            if real_url and real_url.startswith('http'):
                                src = real_url
                except Exception:
                    pass

            seen_srcs.add(src)

            if src not in processed_urls:
                processed_urls.add(src)
                new_urls.append(src)
                pbar.update(1)
                found_new = True
                if len(new_urls) >= needed:
                    break

        if len(new_urls) >= needed:
            break

        if not found_new:
            empty_scrolls += 1
        else:
            empty_scrolls = 0

        # Click "Show more" if available
        try:
            show_more = driver.find_element(By.CSS_SELECTOR, "#smb, input[value='Показать ещё']")
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(0.5)
        except Exception:
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(
            config.get('scroll_pause_min', 1.0),
            config.get('scroll_pause_max', 2.5)
        ))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(0.5)
            if not found_new:
                empty_scrolls += 1
            if empty_scrolls >= max_empty:
                break
        else:
            last_height = new_height

    pbar.close()
    return new_urls


# =============================================================================
# DUCKDUCKGO: URL COLLECTION
# =============================================================================
def collect_duckduckgo_urls(query, needed, processed_urls, config):
    """Collect image URLs from DuckDuckGo via API."""
    if processed_urls is None:
        processed_urls = set()
    try:
        search_url = f"https://duckduckgo.com/?q={quote(query)}&iax=images&ia=images"
        r = session.get(search_url, timeout=15)
        vqd_match = re.search(r'vqd="([^"]+)"', r.text)
        if not vqd_match:
            print(t('ddg_vqd_error'))
            return []
        vqd = vqd_match.group(1)

        urls = []
        s = 0
        target = min(needed, config.get('max_images_per_query', 5000))
        pbar = tqdm(total=target, desc="   Collect URLs",
                    bar_format='{l_bar}{bar}{r_bar}', leave=True)

        while len(urls) < target:
            if stop_event.is_set():
                break

            api_url = (f"https://duckduckgo.com/i.js?q={quote(query)}"
                       f"&o=json&s={s}&u=bing&vqd={vqd}&p=1")
            resp = session.get(
                api_url,
                headers={'Referer': 'https://duckduckgo.com/'},
                timeout=15
            )
            try:
                data = resp.json()
            except Exception:
                break

            results = data.get('results', [])
            if not results:
                break

            for item in results:
                img_url = item.get('image')
                if (img_url and img_url.startswith('http')
                        and img_url not in processed_urls):
                    urls.append(img_url)
                    processed_urls.add(img_url)
                    pbar.update(1)
                if len(urls) >= target:
                    break

            if not data.get('next'):
                break
            s += len(results)
            time.sleep(0.5)

        pbar.close()
        return urls

    except Exception as e:
        print(t('ddg_error').format(e))
        return []


# =============================================================================
# SINGLE QUERY URL COLLECTION
# =============================================================================
def _collect_urls_single(driver, query_text, needed, search_engine,
                         image_quality, processed_urls, config):
    """Collect URLs for a single query text."""
    if search_engine == 'duckduckgo':
        return collect_duckduckgo_urls(query_text, needed, processed_urls, config)

    search_url = f"https://www.google.com/search?q={quote(query_text)}&tbm=isch"
    driver.get(search_url)
    try:
        WebDriverWait(driver, config.get('timeout_load_page', 10)).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "img[data-src], img.rg_i, img[src]")
            )
        )
    except Exception:
        pass
    set_image_size(driver, search_engine, image_quality)

    seen_srcs = set()
    return collect_google_urls(driver, seen_srcs, processed_urls, needed, config)


# =============================================================================
# REVERSE SEARCH
# =============================================================================
def reverse_search_by_file(driver, file_path, needed, search_engine,
                           image_quality, processed_urls, config):
    """Perform reverse image search using a local file."""
    if search_engine == 'duckduckgo':
        print(t('reverse_not_supported'))
        return []

    try:
        print(t('reverse_open'))
        driver.get("https://images.google.com")
        time.sleep(1.5)

        try:
            camera_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "div[aria-label='Search by image'], div[jsname='Q4iAWc'], "
                    "a[aria-label='Search by image']"
                ))
            )
            camera_btn.click()
            time.sleep(1)
        except Exception:
            pass

        upload_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        abs_path = os.path.abspath(file_path)
        upload_input.send_keys(abs_path)

        print(t('reverse_wait'))
        time.sleep(3)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "img[src], img[data-src], img.rg_i")
            )
        )
        time.sleep(2)

        seen_srcs = set()
        return collect_google_urls(driver, seen_srcs, processed_urls, needed, config)

    except Exception as e:
        print(t('reverse_error').format(e))
        return []


def try_reverse_search(driver, folder_path, needed_remaining, search_engine,
                       image_quality, processed_urls, config):
    """Offer reverse search if not enough images collected."""
    if needed_remaining <= 0:
        return []

    image_files = []
    for root, _, files in os.walk(folder_path):
        if 'temp' in root.split(os.sep) or 'duplicates' in root.split(os.sep):
            continue
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif',
                                    '.bmp', '.tiff', '.webp', '.svg')):
                image_files.append(os.path.join(root, f))

    if not image_files:
        print(t('reverse_no_files'))
        return []

    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    last_file = image_files[0]

    print(t('reverse_last_file').format(os.path.basename(last_file)))
    print(t('reverse_missing').format(needed_remaining))

    try:
        choice = input(t('reverse_prompt')).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return []

    if choice not in ('y', 'yes', 'д', 'да'):
        print(t('reverse_skip'))
        return []

    print(t('reverse_launch'))
    return reverse_search_by_file(driver, last_file, needed_remaining,
                                  search_engine, image_quality, processed_urls, config)


# =============================================================================
# DOWNLOAD URL LIST
# =============================================================================
def download_urls(executor, urls, folder_path, temp_dir, existing_hashes,
                  existing_count, limit, search_engine, config):
    """Download a list of URLs with deduplication."""
    if not urls:
        return existing_count

    create_folder(folder_path)
    create_folder(temp_dir)

    downloaded_hashes = existing_hashes.copy()
    hash_lock = threading.Lock()
    unique_count = existing_count
    user_agent = config.get('user_agent', '')
    session.headers.update({"User-Agent": user_agent})

    print(t('downloading_urls').format(len(urls)))
    pbar = tqdm(total=limit, initial=existing_count, desc="   Downloading",
                bar_format='{l_bar}{bar}{r_bar} [{elapsed}]', leave=True)

    try:
        tasks = [(url, temp_dir, search_engine) for url in urls]
        futures = {executor.submit(download_image_to_temp, task, session): task
                   for task in tasks}
        for future in as_completed(futures):
            if stop_event.is_set():
                break
            if unique_count >= limit:
                break

            try:
                success, temp_path, file_hash, url = future.result()
            except Exception:
                continue

            if success and temp_path and file_hash:
                with hash_lock:
                    if file_hash not in downloaded_hashes:
                        downloaded_hashes.add(file_hash)
                        try:
                            final_name = make_unique_filename(url, folder_path)
                            final_path = os.path.join(folder_path, final_name)
                            shutil.move(temp_path, final_path)
                            unique_count += 1
                            pbar.update(1)
                        except Exception:
                            if temp_path and os.path.exists(temp_path):
                                os.remove(temp_path)
                    else:
                        if temp_path and os.path.exists(temp_path):
                            os.remove(temp_path)
            else:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    except KeyboardInterrupt:
        raise
    finally:
        pbar.close()

        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass

    return unique_count


# =============================================================================
# UNIFIED COLLECT + DOWNLOAD WITH MODIFIERS
# =============================================================================
def _collect_and_download(driver, executor, query_text, collect_limit,
                          folder_path, temp_dir, search_engine, image_quality,
                          processed_urls, existing_hashes, unique_count,
                          total_limit, config):
    """Collect and download URLs with modifier fallback."""
    modifiers = config.get('query_modifiers', [])
    modifier_idx = 0

    while unique_count < total_limit and not stop_event.is_set():
        if modifier_idx == 0:
            current_query = query_text
            label = "база" if get_language() == 'ru' else "base"
        elif modifier_idx <= len(modifiers):
            mod = modifiers[modifier_idx - 1]
            current_query = f"{query_text} {mod}"
            label = f"mod:{mod}"
        else:
            break

        print(t('collecting').format(label, current_query, collect_limit))
        urls = _collect_urls_single(driver, current_query, collect_limit,
                                    search_engine, image_quality,
                                    processed_urls, config)

        if urls:
            if config.get('check_existing_hashes', True):
                current_hashes = load_existing_hashes(folder_path)
            else:
                current_hashes = existing_hashes

            prev_count = unique_count
            unique_count = download_urls(executor, urls, folder_path, temp_dir,
                                         current_hashes, unique_count,
                                         total_limit, search_engine, config)
            added = unique_count - prev_count
            print(t('new_added').format(label, added, unique_count, total_limit))

            if unique_count >= total_limit:
                break
        else:
            print(t('no_url').format(label))

        modifier_idx += 1
        if search_engine != 'duckduckgo':
            time.sleep(config.get('delay_between_requests', 1))

    return unique_count


# =============================================================================
# SINGLE QUERY PROCESSING
# =============================================================================
def process_query(driver, executor, query_text, limit, search_engine,
                  image_quality, download_folder, config):
    """Process a single query."""
    start_time = time.time()
    print(t('single_header').format(query_text, limit))

    safe_name = re.sub(r'[\\/*?:"<>|]', "_", query_text)
    folder_path = os.path.join(download_folder, safe_name)
    temp_dir = os.path.join(folder_path, 'temp')

    if config.get('check_existing_hashes', True):
        existing_hashes = load_existing_hashes(folder_path)
        existing_count = len(existing_hashes)
    else:
        existing_hashes = set()
        existing_count = 0
    unique_count = existing_count

    print(t('found_photos').format(unique_count))
    if unique_count >= limit:
        print(t('skip').format(unique_count, limit))
        return

    processed_urls = set()
    remaining = limit - unique_count
    collect_limit = max(remaining, 100)

    unique_count = _collect_and_download(
        driver, executor, query_text, collect_limit, folder_path, temp_dir,
        search_engine, image_quality, processed_urls, existing_hashes,
        unique_count, limit, config
    )

    # Reverse search
    if unique_count < limit and search_engine != 'duckduckgo':
        extra_urls = try_reverse_search(
            driver, folder_path, limit - unique_count,
            search_engine, image_quality, processed_urls, config
        )
        if extra_urls:
            if config.get('check_existing_hashes', True):
                current_hashes = load_existing_hashes(folder_path)
            else:
                current_hashes = existing_hashes
            prev_count = unique_count
            unique_count = download_urls(executor, extra_urls, folder_path, temp_dir,
                                         current_hashes, unique_count, limit,
                                         search_engine, config)
            print(t('new_added').format('reverse', unique_count - prev_count,
                                        unique_count, limit))

    # Summary
    print(t('total_saved').format(unique_count, folder_path))
    if unique_count == existing_count:
        print(t('no_new'))
    elif unique_count < limit:
        print(t('warn_not_enough').format(limit))

    elapsed = time.time() - start_time
    if elapsed < 60:
        time_str = f"[0:{int(elapsed):02d}]"
    elif elapsed < 3600:
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"[{minutes}:{seconds:02d}]"
    else:
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        time_str = f"[{hours}:{minutes}:{seconds:02d}]"
    print(t('query_time').format(time_str))

    if driver:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")


# =============================================================================
# GROUP QUERY PROCESSING
# =============================================================================
def process_group(driver, executor, group, search_engine, image_quality,
                  download_folder, config):
    """Process a group of queries."""
    folder_name = group['folder']
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", folder_name)
    folder_path = os.path.join(download_folder, safe_name)
    temp_dir = os.path.join(folder_path, 'temp')
    total_limit = group['total_limit']

    print(t('group_header').format(folder_name, total_limit))

    if config.get('check_existing_hashes', True):
        existing_hashes = load_existing_hashes(folder_path)
        existing_count = len(existing_hashes)
    else:
        existing_hashes = set()
        existing_count = 0
    unique_count = existing_count

    print(t('found_photos').format(unique_count))
    if unique_count >= total_limit:
        print(t('skip').format(unique_count, total_limit))
        return

    processed_urls = set()

    # Phase 1: Base query
    remaining = total_limit - unique_count
    collect_limit = max(remaining, 100)

    print(t('base_query').format(folder_name, remaining))
    unique_count = _collect_and_download(
        driver, executor, folder_name, collect_limit, folder_path, temp_dir,
        search_engine, image_quality, processed_urls, existing_hashes,
        unique_count, total_limit, config
    )

    # Phase 2: Extra queries
    for var in group['variations']:
        if unique_count >= total_limit or stop_event.is_set():
            break

        remaining = total_limit - unique_count
        var_limit = var['limit']
        collect_limit = max(min(remaining, var_limit), 100)

        print(t('extra_query').format(var['query'], var_limit, remaining))

        prev_count = unique_count
        unique_count = _collect_and_download(
            driver, executor, var['query'], collect_limit, folder_path, temp_dir,
            search_engine, image_quality, processed_urls, existing_hashes,
            unique_count, total_limit, config
        )

        if unique_count == prev_count:
            print(t('no_new_extra'))

    # Reverse search
    if unique_count < total_limit and search_engine != 'duckduckgo':
        extra_urls = try_reverse_search(
            driver, folder_path, total_limit - unique_count,
            search_engine, image_quality, processed_urls, config
        )
        if extra_urls:
            if config.get('check_existing_hashes', True):
                current_hashes = load_existing_hashes(folder_path)
            else:
                current_hashes = existing_hashes
            prev_count = unique_count
            unique_count = download_urls(executor, extra_urls, folder_path, temp_dir,
                                         current_hashes, unique_count, total_limit,
                                         search_engine, config)
            print(t('new_added').format('reverse', unique_count - prev_count,
                                        unique_count, total_limit))

    # Summary
    print(t('total_saved').format(unique_count, folder_path))
    if unique_count == existing_count:
        print(t('no_new'))
    elif unique_count < total_limit:
        print(t('warn_not_enough').format(total_limit))


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main(queries_file=None, search_engine=None, image_quality=None,
         headless=None, download_folder=None, config_obj=None):
    """Main parser entry point."""
    config = config_obj

    if search_engine is None:
        search_engine = config.get('search_engine', 'google')
    if image_quality is None:
        image_quality = config.get('image_quality', 'low')
    if headless is None:
        headless = config.get('headless', True)
    if download_folder is None:
        download_folder = os.path.join(os.path.dirname(__file__), "downloads")

    if queries_file is None:
        queries_file = os.path.join(os.path.dirname(__file__), "queries.txt")

    if not os.path.exists(queries_file):
        print(t('queries_not_found').format(queries_file))
        return

    queries = parse_queries_file(queries_file, config.get('default_image_count', 10))
    if not queries:
        print(t('queries_empty'))
        return

    # Sync language from config
    try:
        lang = config.get('language')
        if lang:
            set_language(lang)
    except Exception:
        pass

    # Save terminal settings
    old_term_settings = None
    if os.name != 'nt':
        try:
            import termios
            old_term_settings = termios.tcgetattr(sys.stdin.fileno())
        except Exception:
            pass

    threading.Thread(target=_esc_listener, daemon=True).start()
    print(t('stop_esc'))

    driver = None
    executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 20))

    if search_engine != 'duckduckgo':
        print(t('chrome_start').format(image_quality))
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument(f"--user-agent={config.get('user_agent', '')}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    else:
        print(t('ddg_start').format(image_quality))

    try:
        for item in queries:
            if stop_event.is_set():
                print(t('stop_user'))
                break

            if item['type'] == 'group':
                process_group(driver, executor, item, search_engine,
                              image_quality, download_folder, config)
            else:
                limit = item.get('limit')
                if limit is None:
                    limit = config.get('default_image_count', 10)
                limit = min(limit, config.get('max_images_per_query', 5000))
                process_query(driver, executor, item['query'], limit,
                              search_engine, image_quality, download_folder, config)

            if search_engine != 'duckduckgo':
                time.sleep(config.get('delay_between_requests', 1))
    except KeyboardInterrupt:
        print(t('stop_ctrlc'))
    finally:
        stop_event.set()
        time.sleep(0.3)

        if os.name != 'nt' and old_term_settings is not None:
            try:
                import termios
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term_settings)
                termios.tcflush(sys.stdin.fileno(), termios.TCIOFLUSH)
            except Exception:
                pass

        executor.shutdown(wait=False)
        if driver:
            driver.quit()
        print(t('parsing_done'))


if __name__ == "__main__":
    from .config import Config
    cfg = Config("settings.json")
    main(config_obj=cfg)