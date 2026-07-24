#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration manager for Parser-Images.

Handles loading, saving, and accessing settings from settings.json.
"""

import os
import sys
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_SETTINGS = {
    "language": None,
    "default_image_count": 10,
    "delay_between_requests": 1,
    "headless": True,
    "max_workers": 20,
    "batch_size": 15,
    "timeout_load_page": 10,
    "timeout_get_image": 3,
    "timeout_collect": 60,
    "scroll_pause_min": 1.0,
    "scroll_pause_max": 2.5,
    "min_image_size": 200,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "check_existing_hashes": True,
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


class Config:
    """Configuration manager with dict-like access."""

    def __init__(self, filepath=None):
        """Initialize config with optional custom filepath."""
        if filepath is None:
            filepath = os.path.join(BASE_DIR, "settings.json")
        self._filepath = filepath
        self._data = {}
        self.reload()

    def reload(self):
        """Reload configuration from file."""
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = DEFAULT_SETTINGS.copy()
                self.save()
        else:
            self._data = DEFAULT_SETTINGS.copy()
            self.save()

    def save(self):
        """Save current configuration to file."""
        try:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def save_defaults(self):
        """Reset and save default configuration."""
        self._data = DEFAULT_SETTINGS.copy()
        self.save()

    def get(self, key, default=None):
        """Get configuration value by key."""
        return self._data.get(key, default)

    def set(self, key, value):
        """Set configuration value and save to file."""
        self._data[key] = value
        self.save()

    def __getitem__(self, key):
        """Allow dict-style access: config['key']."""
        return self._data[key]

    def __setitem__(self, key, value):
        """Allow dict-style assignment: config['key'] = value."""
        self._data[key] = value
        self.save()

    def __contains__(self, key):
        """Allow 'in' operator: 'key' in config."""
        return key in self._data

    def all(self):
        """Return copy of all configuration data."""
        return self._data.copy()