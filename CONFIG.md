# Configuration Guide

## Quick Start

1. Copy the example config:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your settings

3. **You only need to specify options you want to change** - missing fields will use defaults from code

---

## Configuration Options

### Required Fields

#### `SOURCE_DIRS`
**Type:** Array of strings or objects  
**Default:** `[]`  
**Description:** List of folders to monitor for video files

**Simple format:**
```json
"SOURCE_DIRS": [
    "/path/to/movies",
    "/path/to/tv-shows"
]
```

**Advanced format (per-folder intervals):**
```json
"SOURCE_DIRS": [
    {
        "path": "/path/to/movies",
        "scan_interval_minutes": 180,
        "name": "Movies"
    },
    {
        "path": "/path/to/tv-shows",
        "scan_interval_minutes": 30,
        "name": "TV Shows"
    }
]
```

**Per-folder options:**
- `path` (required) - Folder path to scan
- `scan_interval_minutes` (optional) - How often to scan this specific folder (overrides global `SCAN_INTERVAL_MINUTES`)
- `name` (optional) - Display name for dashboard (defaults to folder name)

This is useful when different folders have different update frequencies. For example, scan TV shows every 30 minutes (new episodes often), but movies only every 3 hours (updated less frequently).

---

### Optional Fields

#### `SCAN_INTERVAL_MINUTES`
**Type:** Integer  
**Default:** `60`  
**Description:** Global default for how often to scan folders (in minutes)

This can be overridden per-folder using the advanced `SOURCE_DIRS` format.

**Example:**
```json
"SCAN_INTERVAL_MINUTES": 120
```
Scans every 2 hours instead of every hour (applies to all folders unless overridden).

---

#### `MIN_SAVINGS_GB`
**Type:** Float  
**Default:** `0.5`  
**Description:** Minimum GB savings required to proceed with conversion (pre-check feature)

Files that won't save at least this much space will be skipped.

**Example:**
```json
"MIN_SAVINGS_GB": 1.0
```
Only convert files that will save at least 1 GB.

---

#### `LANGUAGE`
**Type:** String (`"EN"` or `"PL"`)  
**Default:** `"PL"`  
**Description:** UI language for dashboard

**Example:**
```json
"LANGUAGE": "EN"
```

---

#### `PORT`
**Type:** Integer  
**Default:** `8085`  
**Description:** Web dashboard port

**Example:**
```json
"PORT": 9000
```
Dashboard will be at http://localhost:9000

---

#### `KUMA_URL`
**Type:** String  
**Default:** `""`  
**Description:** Optional Uptime Kuma push URL for monitoring

**Example:**
```json
"KUMA_URL": "https://uptime.example.com/api/push/xxxxx?status=up&msg=OK&ping="
```

---

#### `TEMP_FOLDER`
**Type:** String  
**Default:** `"watchdog_temp"`  
**Description:** Temporary folder for transcoding files (relative to script location)

---

#### `OUTPUT_SUFFIX`
**Type:** String  
**Default:** `".hevc.mkv"`  
**Description:** Suffix for already-processed files

Files with this suffix will be skipped to prevent re-processing.

---

#### `STATS_FILE`
**Type:** String  
**Default:** `"stats.json"`  
**Description:** File to store conversion statistics

---

#### `LOG_FILE`
**Type:** String  
**Default:** `"watchdog.log"`  
**Description:** Log file location

---

#### `PROCESSED_FILES`
**Type:** String  
**Default:** `"processed_files.json"`  
**Description:** File to track already processed files (for fast skip on rescan)

---

## Example Configurations

### Minimal Config
Only specify what you need - rest uses defaults:

```json
{
    "SOURCE_DIRS": [
        "/mnt/media/movies",
        "/mnt/media/tv"
    ]
}
```

### Power User Config
```json
{
    "SOURCE_DIRS": [
        "\\\\nas\\movies",
        "\\\\nas\\tv"
    ],
    "SCAN_INTERVAL_MINUTES": 120,
    "MIN_SAVINGS_GB": 1.0,
    "LANGUAGE": "PL",
    "PORT": 8085,
    "KUMA_URL": "https://uptime.example.com/api/push/xxxxx?status=up&msg=OK&ping="
}
```

### Per-Folder Intervals Config
Different scan frequencies for different folders:
```json
{
    "SOURCE_DIRS": [
        {
            "path": "\\\\nas\\movies",
            "scan_interval_minutes": 240,
            "name": "Movies (4h)"
        },
        {
            "path": "\\\\nas\\tv",
            "scan_interval_minutes": 30,
            "name": "TV Shows (30m)"
        },
        {
            "path": "\\\\nas\\archive",
            "scan_interval_minutes": 1440,
            "name": "Archive (daily)"
        }
    ],
    "LANGUAGE": "PL",
    "MIN_SAVINGS_GB": 1.0
}
```
The dashboard will show each folder's schedule and next scan time.

### Docker Config
```json
{
    "SOURCE_DIRS": [
        "/films",
        "/tv"
    ],
    "TEMP_FOLDER": "/temp",
    "STATS_FILE": "/config/stats.json",
    "LOG_FILE": "/config/watchdog.log",
    "PROCESSED_FILES": "/config/processed_files.json"
}
```

---

## How Defaults Work

The code has built-in defaults:

```python
DEFAULT_CONFIG = {
    "SOURCE_DIRS": [],
    "TEMP_FOLDER": "watchdog_temp",
    "STATS_FILE": "stats.json",
    "LOG_FILE": "watchdog.log",
    "PROCESSED_FILES": "processed_files.json",
    "OUTPUT_SUFFIX": ".hevc.mkv",
    "PORT": 8085,
    "KUMA_URL": "",
    "MIN_SAVINGS_GB": 0.5,
    "LANGUAGE": "PL",
    "SCAN_INTERVAL_MINUTES": 60,
    "PARALLEL_PROCESSING": false
}
```

**Your `config.json` overrides these defaults.**  
Missing fields automatically use default values.

---

## Troubleshooting

### Config not loading?
- Check JSON syntax (use https://jsonlint.com)
- Ensure proper escaping of backslashes in Windows paths: `"\\\\server\\share"`
- Check file encoding (should be UTF-8)

### Values not applying?
- Restart the script after changing config
- Check logs for config loading errors
- Verify field names match exactly (case-sensitive)
