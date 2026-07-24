#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entry point for Parser-Images."""

import sys
import os

# Добавляем src/ в путь для PyInstaller
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src_dir = os.path.join(_base_dir, "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from parser_images.cli import main

if __name__ == "__main__":
    main()