# Parser-Images

> CLI tool for bulk image downloading from Google Images and DuckDuckGo. Supports grouped queries, automatic search modifiers, reverse image search, and deduplication.

## Features

- **Two search engines** — Google Images (fast, thumbnails) or DuckDuckGo (high quality)
- **Grouped queries** — collect images from multiple query variations into one folder
- **Auto-modifiers** — automatically adds `site:pinterest.com`, `before:2023`, `filetype:png`, etc. when results are insufficient
- **Reverse search** — find similar images via Google Images
- **Deduplication** — remove duplicates by MD5 hash
- **Bilingual UI** — Russian and English (switchable in settings)

## Installation

### From source

```bash
git clone https://github.com/nerykell/Parser-Images.git
cd Parser-Images
pip install -e .
parser-images
```

### Pre-built binaries

Download the latest release for your OS from the [Releases](https://github.com/nerykell/Parser-Images/releases) page.

## Usage

```bash
./Parser-Images        # Linux / macOS
Parser-Images.exe      # Windows
```

### Interface

```
Parser-Images
Made by Nerykell

  1. Edit queries
  2. Start downloading
  3. Find duplicates
  4. Settings
  5. Exit
```

| Option | Description |
|--------|-------------|
| **1. Edit queries** | Opens `queries.txt` in system text editor. Also shows current download statistics. |
| **2. Start downloading** | Runs the parser with current queries from `queries.txt`. |
| **3. Find duplicates** | Scans `downloads/` and moves duplicates to `downloads/duplicates/`. |
| **4. Settings** | Edit `settings.json` in system text editor — search engine, image quality, language, etc. |
| **5. Exit** | Close the program. |

### Query format (queries.txt)

**Single query:**
```
cute cats 100
```

**Query group** (all variations → one folder):
```
[drones] 1000
&drones fpv 250
&drones racing 250
&drones with camera 250
```

**Rules:**
- `[name] 1000` — folder name and total limit
- `&query 250` — extra query. If base query doesn't yield enough images, parser tries extras sequentially
- Lines starting with `#` are comments
- Minimum 100 URLs are always collected, even if less needed (deduplication reserve)

### Settings format (settings.json)

```json
{
  "language": "en",
  "search_engine": "google",
  "image_quality": "low",
  "headless": true,
  "max_workers": 20,
  "delay_between_requests": 1,
  "timeout_load_page": 10,
  "timeout_get_image": 3,
  "timeout_collect": 60,
  "scroll_pause_min": 1.0,
  "scroll_pause_max": 2.5,
  "min_image_size": 200,
  "check_existing_hashes": true,
  "max_images_per_query": 5000,
  "query_modifiers": [
    "site:pinterest.com",
    "before:2023",
    "after:2024",
    "filetype:png",
    "wallpaper",
    "hd"
  ],
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
```

| Setting | Description |
|---------|-------------|
| `language` | Interface language: `"ru"` or `"en"` |
| `search_engine` | `"google"` or `"duckduckgo"` |
| `image_quality` | `"low"` (Google) or `"high"` (DuckDuckGo) |
| `headless` | Run browser without window (`true`/`false`) |
| `max_workers` | Download threads |
| `delay_between_requests` | Pause between queries (seconds) |
| `query_modifiers` | Auto-applied search modifiers when results are insufficient |

## Project Structure

```
Parser-Images/
├── src/parser_images/        # Source code
│   ├── __init__.py
│   ├── __main__.py           # Entry point: python -m parser_images
│   ├── cli.py                # Console menu and UI
│   ├── parser.py             # Core parsing logic
│   ├── cleaner.py            # Duplicate finder
│   ├── config.py             # Configuration loader/saver
│   ├── i18n.py               # Translations (RU/EN)
│   └── utils/
│       ├── hashing.py        # MD5 hashing
│       ├── download.py       # Parallel downloading
│       ├── browser.py        # Chrome/Selenium setup
│       └── file_ops.py       # File and folder operations
├── scripts/
│   └── build.py              # Build script for .exe
├── docs/
│   ├── USAGE.md              # Detailed usage guide
│   └── CHANGELOG.md          # Version history
├── .github/workflows/
│   └── release.yml           # CI/CD: auto-build releases
├── pyproject.toml            # Dependencies and metadata
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## Building from source

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
python scripts/build.py
```

The executable will appear in `build/Parser-Images_<timestamp>/`.

## Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for version history.

## License

MIT © [Nerykell](https://github.com/nerykell)

---

**Note:** When running the pre-built executable, ensure `queries.txt` and `settings.json` are in the same directory as the binary. The program will create default versions if they are missing.
