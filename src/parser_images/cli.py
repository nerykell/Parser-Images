#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Console UI and menu for Parser-Images.

Handles user interaction, file editing, settings management,
and orchestrates parser and cleaner modules.
"""

import os
import sys
import re
import time
import subprocess
import platform
import importlib
import importlib.util

from parser_images.i18n import set_language, t, get_language
from parser_images.config import Config

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

QUERIES_FILE = os.path.join(BASE_DIR, "queries.txt")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

config = Config(SETTINGS_FILE)


def animate_progress(filename, status, duration=0.1):
    """Show animated progress bar for file check."""
    bar_length = 12
    steps = 10
    for i in range(steps + 1):
        filled = int(bar_length * i / steps)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f'\r{filename} [{bar}]')
        sys.stdout.flush()
        time.sleep(duration / (steps + 1))
    sys.stdout.write(f'\r{filename} [{bar}] [{status}]\n')
    sys.stdout.flush()


def create_default_files(missing_optional):
    """Create default queries.txt and settings.json if missing."""
    if "queries.txt" in missing_optional:
        try:
            with open(QUERIES_FILE, 'w', encoding='utf-8') as f:
                f.write("""# Single queries / Одиночные запросы
cute cats 100

# Query groups / Группы запросов
# Format: [folder name] total count
#         &extra query count

[drones] 1000
&drones fpv 250
&drones racing 250
&drones with camera 250

# Single query after group
cars 50
""")
        except Exception:
            pass

    if "settings.json" in missing_optional:
        config.save_defaults()


def select_language():
    """Prompt user to select language."""
    while True:
        clear_screen()
        print(t('select_language'))
        print(f"  {t('lang_ru')}")
        print(f"  {t('lang_en')}")
        choice = input("\n> ").strip()
        if choice == '1':
            config.set('language', 'ru')
            set_language('ru')
            return 'ru'
        elif choice == '2':
            config.set('language', 'en')
            set_language('en')
            return 'en'
        else:
            input(f"\n{t('invalid_input')}")
            flush_input()


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def flush_input():
    """Flush stdin buffer."""
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        pass

    try:
        import termios
        fd = sys.stdin.fileno()
        attr = termios.tcgetattr(fd)
        attr[3] |= termios.ICANON | termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, attr)
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except Exception:
        pass


def open_in_editor(filepath):
    """Open file in system default text editor."""
    if not os.path.exists(filepath):
        print(t('file_not_found').format(os.path.basename(filepath)))
        return

    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.run(['notepad', filepath], check=True)
        elif system == 'Darwin':
            subprocess.run(['open', '-t', filepath], check=True)
        else:
            # Try common Linux editors
            for editor in ['xdg-open', 'gedit', 'kate', 'mousepad', 'leafpad']:
                try:
                    subprocess.run([editor, filepath], check=True)
                    return
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            # Fallback: nano
            subprocess.run(['nano', filepath], check=True)
    except Exception as e:
        print(f"{t('error').format(e)}")
        print("Please edit the file manually.")


def get_download_folder():
    """Return path to downloads folder."""
    return os.path.join(BASE_DIR, "downloads")


def load_module_from_file(filepath, module_name):
    """Dynamically load a Python module from file path."""
    if not os.path.exists(filepath):
        print(t('file_not_found').format(os.path.basename(filepath)))
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_image_counts():
    """Count images per folder in downloads directory."""
    download_folder = get_download_folder()
    counts = {}
    if not os.path.exists(download_folder):
        return counts

    for entry in os.listdir(download_folder):
        folder_path = os.path.join(download_folder, entry)
        if not os.path.isdir(folder_path):
            continue
        if entry in ('duplicates', 'temp'):
            continue

        count = 0
        for root, _, files in os.walk(folder_path):
            if 'temp' in root.split(os.sep):
                continue
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif',
                                           '.bmp', '.tiff', '.webp', '.svg')):
                    count += 1
        counts[entry] = count
    return counts


def show_statistics():
    """Display current download statistics."""
    counts = get_image_counts()
    if not counts:
        print(f"\n{t('no_folders')}")
        return
    print(f"\n{t('stored_images')}")
    for query, count in sorted(counts.items()):
        print(f"  {query} — {count} {t('pcs')}")


def show_image_quality_menu():
    """Submenu for image quality settings."""
    while True:
        flush_input()
        clear_screen()
        print(t('image_quality_title'))
        print(f"  {t('quality_low_option')}")
        print(f"  {t('quality_high_option')}")
        print(f"  {t('quality_back')}")
        choice = input(f"\n{t('quality_choice')}").strip()

        if choice == '1':
            config.set('search_engine', 'google')
            config.set('image_quality', 'low')
            print(f"\n{t('quality_set_low')}")
            input(f"\n{t('press_enter_back')}")
            flush_input()

        elif choice == '2':
            config.set('search_engine', 'duckduckgo')
            config.set('image_quality', 'high')
            print(f"\n{t('quality_set_high')}")
            input(f"\n{t('press_enter_back')}")
            flush_input()

        elif choice == '3':
            break
        else:
            input(f"\n{t('invalid_input')}")
            flush_input()


def show_settings_menu():
    """Settings submenu."""
    while True:
        flush_input()
        clear_screen()
        print(t('settings_title'))
        print(f"  {t('settings_characteristics')}")
        print(f"  {t('settings_image_quality')}")
        print(f"  {t('settings_language')}")
        print(f"  {t('settings_back')}")
        choice = input(f"\n{t('settings_choice')}").strip()

        if choice == '1':
            clear_screen()
            if not os.path.exists(SETTINGS_FILE):
                print(t('file_not_found').format('settings.json'))
                input(f"\n{t('press_enter_menu')}")
                flush_input()
                continue
            print(t('opening_editor').format(SETTINGS_FILE))
            open_in_editor(SETTINGS_FILE)
            # Reload config after editing
            config.reload()
            set_language(config.get('language', 'en'))
            input(f"\n{t('press_enter_menu')}")
            flush_input()

        elif choice == '2':
            show_image_quality_menu()

        elif choice == '3':
            clear_screen()
            old_lang = get_language()
            new_lang = select_language()
            if new_lang != old_lang:
                print(f"\n{t('language_changed').format(t('lang_ru' if new_lang == 'ru' else 'lang_en').split('. ')[1])}")
                input(f"\n{t('press_enter_menu')}")
                flush_input()

        elif choice == '4':
            break
        else:
            input(f"\n{t('invalid_input')}")
            flush_input()


def show_menu():
    """Main application menu loop."""
    while True:
        flush_input()
        clear_screen()
        print(t('menu_title'))
        print(t('menu_author'))
        print(f"  {t('menu_queries')}")
        print(f"  {t('menu_start')}")
        print(f"  {t('menu_duplicates')}")
        print(f"  {t('menu_settings')}")
        print(f"  {t('menu_exit')}")
        choice = input(f"\n{t('menu_choice')}").strip()

        if choice == '1':
            clear_screen()
            if not os.path.exists(QUERIES_FILE):
                print(t('file_not_found').format('queries.txt'))
                input(f"\n{t('press_enter_menu')}")
                flush_input()
                continue
            print(t('opening_editor').format(QUERIES_FILE))
            open_in_editor(QUERIES_FILE)

            # Show current settings info
            quality_str = (t('quality_high') if config.get('image_quality') == 'high'
                           else t('quality_low'))
            engine_str = (t('engine_ddg') if config.get('search_engine') == 'duckduckgo'
                          else t('engine_google'))
            print(f"\n{t('image_quality_info').format(quality_str, engine_str)}")

            show_statistics()
            input(f"\n{t('press_enter_menu')}")
            flush_input()

        elif choice == '2':
            clear_screen()
            print(t('launching_parser'))
            try:
                if 'parser_images.parser' in sys.modules:
                    importlib.reload(sys.modules['parser_images.parser'])
                from parser_images.parser import main as parser_main

                parser_main(
                    queries_file=QUERIES_FILE,
                    search_engine=config.get('search_engine', 'google'),
                    image_quality=config.get('image_quality', 'low'),
                    headless=config.get('headless', True),
                    download_folder=get_download_folder(),
                    config_obj=config,
                )
            except Exception as e:
                print(f"\n{t('error').format(e)}")
            input(f"\n{t('press_enter_menu')}")
            flush_input()

        elif choice == '3':
            clear_screen()
            print(t('launching_cleaner'))
            try:
                if 'parser_images.cleaner' in sys.modules:
                    importlib.reload(sys.modules['parser_images.cleaner'])
                from parser_images.cleaner import find_duplicates

                duplicates_folder = os.path.join(get_download_folder(), "duplicates")
                find_duplicates(root_dir=get_download_folder(), move_to=duplicates_folder)
            except Exception as e:
                print(f"\n{t('error').format(e)}")
            input(f"\n{t('press_enter_menu')}")
            flush_input()

        elif choice == '4':
            show_settings_menu()

        elif choice == '5':
            sys.exit(0)

        elif choice == '67':
            print(f"\n{t('sixty_seven')}")
            input()
            flush_input()

        else:
            input(f"\n{t('invalid_input')}")
            flush_input()


def main():
    """Application entry point."""
    # Language setup
    lang = config.get('language')
    if lang is None:
        lang = select_language()
    else:
        set_language(lang)

    # Create default files if missing
    missing_optional = []
    if not os.path.exists(QUERIES_FILE):
        missing_optional.append("queries.txt")
    if not os.path.exists(SETTINGS_FILE):
        missing_optional.append("settings.json")

    if missing_optional:
        create_default_files(missing_optional)

    clear_screen()
    show_menu()


if __name__ == "__main__":
    main()