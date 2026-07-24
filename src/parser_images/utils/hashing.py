#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File hashing utilities for Parser-Images.

Provides MD5 hashing with thread-safe caching for deduplication.
"""

import os
import hashlib
import threading

_existing_hashes_cache = {}
_cache_lock = threading.Lock()


def load_existing_hashes(folder_path):
    """Load MD5 hashes of all files in a folder (with caching).

    Args:
        folder_path: Path to folder to scan.

    Returns:
        Set of MD5 hex digest strings.
    """
    with _cache_lock:
        if folder_path in _existing_hashes_cache:
            return _existing_hashes_cache[folder_path].copy()

    hashes = set()
    if os.path.exists(folder_path):
        for root, _, files in os.walk(folder_path):
            if 'temp' in root.split(os.sep):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    h = hashlib.md5(usedforsecurity=False)
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(8192):
                            h.update(chunk)
                    hashes.add(h.hexdigest())
                except Exception:
                    pass

    with _cache_lock:
        _existing_hashes_cache[folder_path] = hashes
    return hashes


def clear_cache(folder_path=None):
    """Clear hash cache for a specific folder or all folders.

    Args:
        folder_path: Specific folder to clear, or None to clear all.
    """
    with _cache_lock:
        if folder_path is None:
            _existing_hashes_cache.clear()
        elif folder_path in _existing_hashes_cache:
            del _existing_hashes_cache[folder_path]