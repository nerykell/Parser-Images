#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image download utilities for Parser-Images.

Handles HTTP downloading with session management, size validation,
and temporary file handling.
"""

import os
import hashlib
import tempfile


def download_image_to_temp(args, session):
    """Download an image URL to a temporary file.

    Args:
        args: Tuple of (url, temp_dir, search_engine).
        session: requests.Session instance with configured headers.

    Returns:
        Tuple of (success, temp_path, file_hash, url).
    """
    url, temp_dir, search_engine = args
    temp_path = None
    try:
        req_headers = {}
        if search_engine == 'google' or 'gstatic' in url:
            req_headers['Referer'] = 'https://www.google.com/'
        elif search_engine == 'duckduckgo':
            req_headers['Referer'] = 'https://duckduckgo.com/'

        response = session.get(url, timeout=30, stream=True,
                               headers=req_headers, allow_redirects=True)
        if response.status_code != 200:
            return False, None, None, url

        content_type = response.headers.get("Content-Type", "").lower()
        if content_type:
            if any(ct in content_type for ct in ['text/html', 'application/json',
                                                   'application/xml']):
                return False, None, None, url

        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp',
                                         dir=temp_dir) as tmp_f:
            temp_path = tmp_f.name
            h = hashlib.md5(usedforsecurity=False)
            total_size = 0
            for chunk in response.iter_content(8192):
                if chunk:
                    tmp_f.write(chunk)
                    h.update(chunk)
                    total_size += len(chunk)
            file_hash = h.hexdigest()

            min_size = 30720 if search_engine == 'duckduckgo' else 100
            if total_size < min_size:
                return False, None, None, url

        return True, temp_path, file_hash, url
    except Exception:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return False, None, None, url