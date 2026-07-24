#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File and folder operations for Parser-Images.

Provides utilities for folder creation and unique filename generation.
"""

import os
import re
import hashlib
import threading

_filename_lock = threading.Lock()


def create_folder(path):
    """Create folder if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def make_unique_filename(url, folder_path):
    """Generate a unique filename for a URL in a folder.

    Args:
        url: Image URL.
        folder_path: Destination folder path.

    Returns:
        Unique filename string.
    """
    from urllib.parse import urlparse, unquote

    parsed = urlparse(url)
    path = unquote(parsed.path)
    filename = os.path.basename(path)
    if '?' in filename:
        filename = filename.split('?')[0]
    if not filename or '.' not in filename:
        ext = os.path.splitext(path)[1]
        if not ext or len(ext) > 5:
            ext = '.jpg'
        hash_name = hashlib.md5(url.encode(), usedforsecurity=False).hexdigest()[:10]
        filename = f"{hash_name}{ext}"
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    base, ext = os.path.splitext(filename)

    with _filename_lock:
        counter = 1
        new_filename = filename
        dest = os.path.join(folder_path, new_filename)
        while os.path.exists(dest):
            new_filename = f"{base}_{counter}{ext}"
            dest = os.path.join(folder_path, new_filename)
            counter += 1
        open(dest, 'wb').close()
    return new_filename