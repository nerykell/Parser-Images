# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-alpha] - 2026-07-24

### Added
- Support for Google Images and DuckDuckGo search engines
- Grouped queries with fallback variations
- Automatic search modifiers when results are insufficient
- Reverse image search via Google Images
- Parallel downloading with configurable thread count
- MD5-based deduplication
- Duplicate finder with move-to-folder functionality
- Bilingual interface (Russian / English)
- JSON-based configuration (`settings.json`)
- PyInstaller build script for standalone executables
- GitHub Actions CI/CD for automated releases

### Features
- Console menu with 5 options: Edit queries, Download, Find duplicates, Settings, Exit
- Automatic creation of default `queries.txt` and `settings.json` on first launch
- Language selection prompt on first run
- Real-time download progress with tqdm
- ESC / Ctrl+C graceful shutdown
- Cross-platform support (Windows, Linux, macOS)

[1.0.0-alpha]: https://github.com/nerykell/Parser-Images/releases/tag/v1.0.0
