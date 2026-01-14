# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2025-01-14

### Added
- **Audit Tools:** PowerShell and Bash scripts to detect corrupted MKV files (`audit_corrupted.ps1`, `audit_corrupted.sh`)
- **Skip Statistics:** Dashboard now displays skipped files with detailed reasons (codec already efficient, file too small, etc.)
- **GPU Encoding Support:** NVIDIA NVENC, Intel QSV, and AMD AMF hardware acceleration (10x faster encoding)
- **GPU Auto-detection:** Automatic detection of available GPU encoders with fallback to CPU
- **Collapsible Folder Schedules:** Dashboard UI improvement with localStorage persistence for folder schedule visibility
- Version badges in README.md

### Changed
- **CRITICAL: Atomic File Replacement** - Replaced unsafe `os.remove()` + `shutil.move()` with atomic `os.replace()` to prevent data corruption during power loss or crashes
- Enhanced `ENCODE_SETTINGS` configuration with GPU codec support (`hevc_nvenc`, `hevc_qsv`, `hevc_amf`)
- Improved stats structure with backward compatibility (`files_skipped`, `gb_skipped`, `skip_reasons`)
- Dashboard UI improvements: consistent font sizes, better responsive text overflow handling
- Extended CONFIG.md with comprehensive GPU encoding documentation

### Fixed
- Font size consistency across dashboard elements
- Text overflow handling for long file paths in dashboard
- Backup restoration mechanism in file replacement error scenarios

### Security
- Atomic file operations eliminate risk of file corruption or loss during transcoding failures

## [2.0.0] - 2025-01-13

### Added
- **Per-Folder Scan Intervals:** Configure different scan frequencies for each source directory
- **Advanced SOURCE_DIRS Format:** Support for folder objects with `path`, `scan_interval_minutes`, and `name` properties
- **Dashboard Schedule Display:** Shows next scan time for each folder with collapsible UI
- **MIN_SAVINGS_GB Configuration:** Skip files that won't save enough space (pre-check feature)
- **Smart Codec Detection:** Automatically skip AV1, VP9, and already-encoded HEVC files
- **Processed Files Tracking:** Fast skip mechanism using `processed_files.json` cache
- **Bilingual Support:** Polish (PL) and English (EN) UI translations
- **CONFIG.md:** Comprehensive configuration documentation with examples
- Uptime Kuma monitoring integration

### Changed
- Major refactor for production readiness
- Improved pause/skip logic - works reliably at any point in process
- Better error handling and logging throughout
- Platform-agnostic process management (Windows/Linux/macOS)
- Config validation with fallback to defaults
- Stale temp file cleanup to prevent disk bloat

### Fixed
- Syntax errors in watchdog_h265.py
- Windows-specific process flags compatibility
- Linux process group handling for clean FFmpeg termination
- Docker configuration now uses config.json (no hardcoded paths)

### Security
- Sensitive config files added to .gitignore

## [1.0.0] - 2025-01-12

### Added
- Initial release
- Automatic H.265/HEVC transcoding for video libraries
- Web dashboard on port 8085
- Real-time encoding progress and logs
- Storage savings statistics
- Pause/Play and Skip controls
- FFmpeg integration with configurable quality settings (CRF, preset)
- Docker support with docker-compose
- Cross-platform compatibility (Windows, Linux, macOS)
- MIT License

[Unreleased]: https://github.com/mehow28/watchdog-h265/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/mehow28/watchdog-h265/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/mehow28/watchdog-h265/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/mehow28/watchdog-h265/releases/tag/v1.0.0
