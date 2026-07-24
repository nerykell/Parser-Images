#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Duplicate image finder for Parser-Images.

Scans directories for duplicate images by MD5 hash and moves
or deletes them.
"""

import os
import hashlib
import shutil
from pathlib import Path
from tqdm import tqdm

from .i18n import set_language, t

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}


def get_file_hash(filepath, chunk_size=8192):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError):
        return None


def find_duplicates(root_dir=None, move_to=None, language=None):
    """Find and handle duplicate images in a directory tree.

    Args:
        root_dir: Root directory to scan. Defaults to "downloads".
        move_to: Directory to move duplicates to. If None, deletes them.
        language: Optional language code ('ru' or 'en') to override current.
    """
    if language:
        set_language(language)

    if root_dir is None:
        root_dir = "downloads"

    root_path = Path(root_dir)
    if not root_path.exists():
        print(t('cleaner_error_folder').format(root_dir))
        return

    print(t('cleaner_scan').format(root_path))
    all_files = []
    for ext in IMAGE_EXTENSIONS:
        all_files.extend(root_path.rglob(f"*{ext}"))
        all_files.extend(root_path.rglob(f"*{ext.upper()}"))
    all_files = list(set(all_files))
    print(t('cleaner_found_files').format(len(all_files)))

    if not all_files:
        return

    hash_map = {}
    for file_path in tqdm(all_files, desc="Processing", unit="file"):
        file_hash = get_file_hash(file_path)
        if file_hash:
            hash_map.setdefault(file_hash, []).append(file_path)

    duplicate_groups = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    total_duplicates = sum(len(paths) - 1 for paths in duplicate_groups.values())

    if not duplicate_groups:
        print(t('cleaner_no_duplicates'))
        return

    print(t('cleaner_found_groups').format(len(duplicate_groups), total_duplicates))

    kept_count = len(all_files) - total_duplicates
    processed = 0

    for _, paths in duplicate_groups.items():
        duplicates = paths[1:]
        for dup_path in duplicates:
            if move_to:
                dest_dir = Path(move_to)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / dup_path.name
                counter = 1
                while dest_path.exists():
                    stem = dup_path.stem
                    suffix = dup_path.suffix
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                shutil.move(str(dup_path), str(dest_path))
            else:
                try:
                    dup_path.unlink()
                except OSError as e:
                    print(t('cleaner_error_delete').format(dup_path, e))
            processed += 1

    print(t('cleaner_done'))
    print(t('cleaner_unique').format(kept_count))
    print(t('cleaner_moved').format(processed, move_to))
