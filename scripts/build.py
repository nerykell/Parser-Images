#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script for Parser-Images.

Compiles the project into a single executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
import platform
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src", "parser_images")

MAIN_SCRIPT = os.path.join(SRC_DIR, "__main__.py")
OUTPUT_DIR = "build_output"
FINAL_DIR_NAME = "build"

FINAL_NAME = "Parser-Images"


def find_file(filename):
    """Find file in src/parser_images directory."""
    local_path = os.path.join(SRC_DIR, filename)
    if os.path.exists(local_path):
        return local_path
    return None


def clean_temp():
    """Remove temporary build folders."""
    for folder in ["pyinstaller_build", "dist", "__pycache__"]:
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"[OK] Deleted: {folder_path}")
    for f in glob.glob(os.path.join(BASE_DIR, "*.spec")):
        os.remove(f)
        print(f"[OK] Deleted: {f}")


def clean_build_output():
    """Remove previous build output."""
    output_path = os.path.join(BASE_DIR, OUTPUT_DIR)
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
        print(f"[OK] Deleted: {output_path}")


def copy_file_with_check(src, dst):
    """Copy file with verification."""
    if not src or not os.path.exists(src):
        print(f"[WARNING] Source file not found: {src}")
        return False
    try:
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f"[OK] Copied: {os.path.basename(src)} -> {dst} ({size} bytes)")
        return True
    except Exception as e:
        print(f"[ERROR] Copy error {src} -> {dst}: {e}")
        return False


def build_exe():
    """Build executable using PyInstaller."""
    system = platform.system()
    exe_name = "Parser-Images.exe" if system == "Windows" else "Parser-Images"

    clean_temp()
    clean_build_output()

    if not os.path.exists(MAIN_SCRIPT):
        print(f"[ERROR] Main script not found: {MAIN_SCRIPT}")
        sys.exit(1)

    hidden_imports = [
        "requests",
        "urllib3",
        "chardet",
        "certifi",
        "idna",
        "selenium",
        "selenium.webdriver",
        "selenium.webdriver.common",
        "selenium.webdriver.chrome",
        "selenium.webdriver.chrome.options",
        "selenium.webdriver.chrome.service",
        "selenium.webdriver.chrome.webdriver",
        "selenium.webdriver.remote",
        "selenium.webdriver.remote.webelement",
        "selenium.webdriver.support",
        "selenium.webdriver.support.ui",
        "selenium.webdriver.support.expected_conditions",
        "webdriver_manager",
        "webdriver_manager.chrome",
        "webdriver_manager.core",
        "webdriver_manager.core.driver_cache",
        "webdriver_manager.core.download_manager",
        "webdriver_manager.core.manager",
        "webdriver_manager.core.utils",
        "tqdm",
        "tqdm.contrib.concurrent",
        "tqdm.auto",
        "tqdm.std",
        "packaging",
        "packaging.version",
        "packaging.specifiers",
        "packaging.requirements",
        "colorama",
    ]

    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name", "Parser-Images",
        "--distpath", os.path.join(BASE_DIR, "dist"),
        "--workpath", os.path.join(BASE_DIR, "pyinstaller_build"),
        "--specpath", BASE_DIR,
        "--paths", os.path.join(BASE_DIR, "src"),
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    cmd.append(MAIN_SCRIPT)

    print("[INFO] Starting build...")
    subprocess.run(cmd, check=True)

    # Create final output folder
    temp_final_dir = os.path.join(BASE_DIR, OUTPUT_DIR, FINAL_NAME)
    os.makedirs(temp_final_dir, exist_ok=True)

    # Copy executable
    dist_exe = os.path.join(BASE_DIR, "dist", exe_name)
    if os.path.exists(dist_exe):
        shutil.copy2(dist_exe, temp_final_dir)
        print(f"[OK] Executable copied to {temp_final_dir}")
    else:
        print(f"[ERROR] Executable not found: {dist_exe}")
        sys.exit(1)

    # Create default queries.txt
    queries_path = os.path.join(temp_final_dir, "queries.txt")
    with open(queries_path, 'w', encoding='utf-8') as f:
        f.write("""# Single queries
cute cats 100

# Query groups
# Format: [folder name] total count
#         &extra query count

[drones] 1000
&drones fpv 250
&drones racing 250
&drones with camera 250

# Single query after group
cars 50
""")
    print(f"[OK] Created: queries.txt")

    # Create default settings.json
    settings_path = os.path.join(temp_final_dir, "settings.json")
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write("""{
  "language": null,
  "default_image_count": 10,
  "delay_between_requests": 1,
  "headless": true,
  "max_workers": 20,
  "batch_size": 15,
  "timeout_load_page": 10,
  "timeout_get_image": 3,
  "timeout_collect": 60,
  "scroll_pause_min": 1.0,
  "scroll_pause_max": 2.5,
  "min_image_size": 200,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
  "check_existing_hashes": true,
  "image_quality": "low",
  "search_engine": "google",
  "query_modifiers": [
    "site:pinterest.com",
    "before:2023",
    "after:2024",
    "filetype:png",
    "wallpaper",
    "hd"
  ],
  "max_images_per_query": 5000
}
""")
    print(f"[OK] Created: settings.json")

    # Create downloads folder
    downloads_dir = os.path.join(temp_final_dir, "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    print(f"[OK] Created: downloads/")

    clean_temp()

    # Move to final build directory
    build_path = os.path.join(BASE_DIR, FINAL_DIR_NAME)
    os.makedirs(build_path, exist_ok=True)

    final_dest = os.path.join(build_path, FINAL_NAME)
    if os.path.exists(final_dest):
        shutil.rmtree(final_dest)
        print("[WARNING] Old version removed")
    shutil.move(temp_final_dir, final_dest)
    print(f"[OK] Build moved to {final_dest}")

    try:
        os.rmdir(os.path.join(BASE_DIR, OUTPUT_DIR))
        print(f"[OK] Temp folder {OUTPUT_DIR} removed")
    except OSError:
        pass

    print(f"\n[OK] Done! Final folder: {final_dest}")
    print("   Structure:")
    print(f"   {FINAL_DIR_NAME}/")
    print(f"   +-- {FINAL_NAME}/")
    print(f"   |   +-- {exe_name}")
    print("   |   +-- queries.txt")
    print("   |   +-- settings.json")
    print("   |   +-- downloads/")


def main():
    build_exe()


if __name__ == "__main__":
    main()