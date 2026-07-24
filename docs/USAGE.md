# Usage Guide

Detailed instructions for using Parser-Images.

## Table of Contents

- [First Launch](#first-launch)
- [Query File Format](#query-file-format)
- [Settings](#settings)
- [Download Process](#download-process)
- [Duplicate Finder](#duplicate-finder)
- [Tips](#tips)

## First Launch

On first launch, the program prompts you to select a language:

```
Select language / Выберите язык:
  1. Русский
  2. English
>
```

This choice is saved to `settings.json` and can be changed later by editing the file.

## Query File Format

The `queries.txt` file defines what images to download.

### Single Query

```
cute cats 100
```

Downloads 100 images of "cute cats" into folder `downloads/cute_cats/`.

### Query Group

```
[drones] 1000
&drones fpv 250
&drones racing 250
&drones with camera 250
```

- `[drones] 1000` — folder name `downloads/drones/`, total target 1000 images
- `&drones fpv 250` — first extra query, tries to get up to 250 images
- `&drones racing 250` — second extra query, if first didn't reach the limit
- `&drones with camera 250` — third extra query

The parser tries the base query first. If it doesn't collect enough images, it proceeds through extra queries one by one until the total limit is reached.

### Comments

Lines starting with `#` are ignored:

```
# This is a comment
cats 50
```

### Rules

- Minimum 100 URLs are always collected, even if you request fewer (for deduplication reserve)
- If an extra query yields zero new images, the parser moves to the next one
- Folder names are sanitized: invalid characters become underscores

## Settings

Edit `settings.json` to customize behavior:

| Setting | Default | Description |
|---------|---------|-------------|
| `language` | `null` | Interface language: `"ru"` or `"en"` |
| `search_engine` | `"google"` | `"google"` or `"duckduckgo"` |
| `image_quality` | `"low"` | `"low"` (Google, fast) or `"high"` (DuckDuckGo, better quality) |
| `headless` | `true` | Run browser without visible window |
| `max_workers` | `20` | Parallel download threads |
| `delay_between_requests` | `1` | Seconds between queries |
| `timeout_collect` | `60` | Max seconds to spend collecting URLs per query |
| `scroll_pause_min` / `scroll_pause_max` | `1.0` / `2.5` | Random pause between page scrolls |
| `min_image_size` | `200` | Minimum thumbnail size in pixels |
| `check_existing_hashes` | `true` | Skip already downloaded images |
| `query_modifiers` | `[...]` | Auto-applied search modifiers when results are low |
| `max_images_per_query` | `5000` | Hard limit per query/group |

### Changing Image Quality

Via menu (Option 4 → 2):
- **Low (Google)** — fast, smaller images, more results
- **High (DuckDuckGo)** — slower, larger images, fewer but better quality results

## Download Process

1. Select **2. Start downloading** from the menu
2. The parser reads `queries.txt`
3. For each query/group:
   - Collects URLs by scrolling (Google) or API (DuckDuckGo)
   - Downloads images in parallel
   - Checks for duplicates by MD5 hash
   - Applies search modifiers if results are insufficient
   - Offers reverse image search as last resort
4. Progress is shown in the terminal
5. Press **ESC** or **Ctrl+C** to stop at any time

Downloaded images are saved to `downloads/<query_folder>/`.

## Duplicate Finder

Select **3. Find duplicates** from the menu to:

1. Scan all images in `downloads/`
2. Compare by MD5 hash
3. Move duplicates to `downloads/duplicates/`

Original files are kept, duplicates are moved (not deleted).

## Tips

- **Start small**: Test with 10-50 images per query before large batches
- **Use groups**: Group related queries to avoid redundant downloads
- **Check modifiers**: If a query returns few results, the modifiers in `settings.json` will help
- **Reverse search**: Useful when standard queries are exhausted
- **DuckDuckGo for quality**: Switch to high quality for wallpapers, art, or professional images
- **Headless mode**: Set `headless: false` in settings to watch the browser work (slower but useful for debugging)
