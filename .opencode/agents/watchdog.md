# HEVC Watchdog - Development Agent

## Project Overview

**Name:** HEVC Watchdog  
**Purpose:** Automated video transcoding service (H.264/other → HEVC) for home servers/NAS  
**Language:** Python 3.7+  
**Key Dependencies:** Flask, FFmpeg, requests  
**Repository:** https://github.com/mehow28/watchdog-h265  
**YouTrack:** https://ofield.youtrack.cloud/issues/HEVC  

---

## 🏗️ Architecture

### Core Files
- `watchdog_h265.py` - Main application (Flask web server + worker loop)
- `watchdog_core.py` - Helper functions (codec detection, stats, process management)
- `config.json` - User configuration (not in repo)
- `config.example.json` - Example config (simple format)
- `config.example.advanced.json` - Example with advanced features
- `CONFIG.md` - Complete configuration documentation

### Key Components
1. **Worker Loop** (watchdog_h265.py:~290) - Main scanning/transcoding logic
2. **Scan Scheduling** (watchdog_h265.py:~210) - Per-folder scan intervals
3. **Dashboard** (watchdog_h265.py:~520) - Flask web UI (port 8085)
4. **Codec Detection** (watchdog_core.py:~33) - FFprobe-based detection
5. **Size Estimation** (watchdog_core.py:~96) - Pre-check before transcoding

### State Management
```python
state = {
    "status": str,              # Current status
    "current_file": str,        # File being processed
    "current_folder": str,      # Folder being scanned
    "stats": dict,              # Processed count, GB saved
    "processed_files": set,     # Skip list
    "paused": bool,             # Pause flag
    "skip": bool,               # Skip current file flag
    "processing_active": bool,  # Currently transcoding
    "transcode_start_time": float,
    "transcode_file_size": float
}
```

---

## 📝 Coding Standards

### Python Style
- **PEP 8** compliant (except line length can be 100-120)
- Use **descriptive variable names** (`folder_config` not `fc`)
- **Type hints** optional but appreciated for new functions
- **Docstrings** for all public functions:
  ```python
  def function_name(param):
      """
      Brief description.
      Returns (type, type): description
      """
  ```

### Naming Conventions
- **Functions:** `snake_case` (e.g., `scan_folder`, `get_next_scan_time`)
- **Constants:** `UPPER_CASE` (e.g., `DEFAULT_CONFIG`, `STRINGS`)
- **Variables:** `snake_case` (e.g., `folder_path`, `estimated_size`)
- **Config keys:** `UPPER_CASE` (e.g., `SOURCE_DIRS`, `ENCODE_SETTINGS`)

### Error Handling
- Use **try/except** with broad catch for non-critical functions
- **Log errors** instead of crashing: `logger.error(f"...")`
- Return **safe defaults** when possible
- Example:
  ```python
  try:
      result = risky_operation()
  except Exception as e:
      logger.error(f"Operation failed: {e}")
      return default_value
  ```

---

## 🔧 Configuration Philosophy

### Backward Compatibility is CRITICAL
- **Always support old config formats**
- Use `normalize_source_dirs()` pattern for migrations
- New features = **opt-in**, never break existing configs

### Config Structure
```python
DEFAULT_CONFIG = {
    # Simple settings
    "SETTING_NAME": default_value,
    
    # Nested settings (use deep merge in load_config)
    "ENCODE_SETTINGS": {
        "subsetting": value
    }
}
```

### Docker Support
- **ENV variables** should override config.json
- Pattern: `HEVC_<SETTING_NAME>` (e.g., `HEVC_CRF`, `HEVC_PRESET`)
- Check in `load_config()` after loading JSON

---

## 🎬 Encoding Settings

### Current Defaults (DO NOT CHANGE without discussion)
```python
"ENCODE_SETTINGS": {
    "codec": "libx265",              # Always HEVC for now
    "crf": 26,                       # Good balance
    "preset": "slow",                # Quality over speed (automated tool)
    "x265_params": "constrained-intra=1"  # Re-encoding safety
}
```

### Compression Ratios (watchdog_core.py)
**Based on real-world testing - DO NOT guess:**
```python
compression_ratios = {
    # Don't convert (already efficient)
    'hevc': 1.00,
    'h265': 1.00,
    'av1': 1.15,    # Better than HEVC!
    'vp9': 0.95,    # Nearly as good
    
    # Old codecs (good candidates)
    'mpeg2': 0.25,  # Huge savings
    'h264': 0.55,   # Conservative
    'avc': 0.55,
}
```

### When Adding New Codecs
1. Research real-world benchmarks (NOT AI guesses)
2. Test with actual files if possible
3. Be conservative (overestimate ratio)
4. Document source of ratio in comments

---

## 🧪 Testing Workflow

### Before ANY Code Changes
1. **Read the code first** - understand current implementation
2. **Check backward compatibility** - will old configs work?
3. **Plan the change** - discuss architecture if major

### Manual Testing Checklist
```bash
# 1. Syntax check
python -m py_compile watchdog_h265.py watchdog_core.py

# 2. Import test
python -c "import watchdog_h265; print('OK')"

# 3. Config loading test
cd C:\Users\PC\.ofield_new
python -c "import watchdog_h265; print(watchdog_h265.CONFIG['ENCODE_SETTINGS'])"

# 4. Function tests (create simple test script)
```

### Test Environments
- **Development:** `D:\Repos\watchdog-h265`
- **Staging:** `C:\Users\PC\.ofield_new` (test before production)
- **Production:** `C:\Users\PC\.ofield` (user's actual setup)

**ALWAYS test in `.ofield_new` before deploying to `.ofield`!**

---

## 📦 Git Workflow

### Branch Strategy
- `main` - stable, working code
- `feature/<name>` - new features (merge when done)
- Fast-forward merges preferred

### Commit Messages
**Format:**
```
Type: Brief description (50 chars max)

Detailed explanation of changes:
- What changed
- Why it changed
- Impact on users

Commit: <hash>
Status: Tested/Deployed/WIP
```

**Types:**
- `Feature:` - New functionality
- `Fix:` - Bug fix
- `Docs:` - Documentation only
- `Refactor:` - Code restructure, no behavior change
- `Quality:` - Performance/quality improvements

**Example:**
```
Feature: Per-folder scan intervals with dashboard UI

Implemented independent scan schedules for each monitored folder:
- Each folder can have its own scan_interval_minutes
- Dashboard shows per-folder schedules and next scan times
- Backward compatible with simple path strings

Commit: 8bcd5b8
Status: Tested and deployed
```

### Pre-Commit Checklist
- [ ] Code compiles (`python -m py_compile`)
- [ ] Imports work (test in clean environment)
- [ ] Backward compatible (old configs work)
- [ ] Documentation updated (README.md, CONFIG.md)
- [ ] Tested in `.ofield_new`
- [ ] YouTrack updated (if major feature)

### After Commit
1. **Test in `.ofield_new`** - validate works with real config
2. **Update YouTrack** - create/update issue with details
3. **Copy files** - deploy to staging
4. **Create UPDATE_NOTES.txt** - if major changes

---

## 🐛 Common Pitfalls

### 1. Encoding Characters (Windows)
**Problem:** Unicode errors with Polish characters
```python
# BAD
print("✓ Success")  # Fails on Windows console

# GOOD
print("Success")  # ASCII only
```

### 2. Path Handling
**Problem:** Windows uses backslashes
```python
# BAD
path = "C:\folder\file"  # Escape issues

# GOOD
path = os.path.join("C:", "folder", "file")
path = "C:\\folder\\file"  # Double backslash in strings
```

### 3. Config Merging
**Problem:** Nested dicts don't merge properly
```python
# BAD
config = {**DEFAULT_CONFIG, **user_config}  # Overwrites nested dicts

# GOOD (for nested settings)
if "ENCODE_SETTINGS" in user_config:
    config["ENCODE_SETTINGS"] = {
        **DEFAULT_CONFIG["ENCODE_SETTINGS"], 
        **user_config["ENCODE_SETTINGS"]
    }
```

### 4. FFmpeg Process Handling
**Problem:** Zombie processes
```python
# ALWAYS use kill_process_tree() for FFmpeg
# NEVER just process.terminate()
```

### 5. State File Corruption
**Problem:** JSON write interrupted
```python
# GOOD - atomic write pattern
with open(file + ".tmp", 'w') as f:
    json.dump(data, f)
os.replace(file + ".tmp", file)
```

---

## 📚 Documentation Standards

### README.md
- Keep bilingual (EN + PL)
- **Quality disclaimer** at top (transparency!)
- Quick start must be copy-paste ready

### CONFIG.md
- Document **every config option**
- Include **examples** for each
- Explain **when to use** different settings
- Docker ENV variables noted

### Code Comments
```python
# GOOD - Explain WHY, not WHAT
# Use slow preset because this is automated - quality over speed

# BAD - Obvious what
# Set preset to slow
```

---

## 🎯 Feature Development Process

### 1. **Planning Phase**
- [ ] Discuss with user (if major)
- [ ] Check existing issues in YouTrack
- [ ] Review similar features in code
- [ ] Plan backward compatibility

### 2. **Implementation Phase**
- [ ] Create feature branch (if complex)
- [ ] Write helper functions first
- [ ] Update DEFAULT_CONFIG if needed
- [ ] Maintain state structure compatibility
- [ ] Add logging for new operations

### 3. **Testing Phase**
- [ ] Syntax check
- [ ] Import test
- [ ] Config test (old format works)
- [ ] Function tests (if possible)
- [ ] Deploy to `.ofield_new`
- [ ] Monitor first scan cycle

### 4. **Documentation Phase**
- [ ] Update CONFIG.md
- [ ] Update README.md (if user-facing)
- [ ] Create/update examples
- [ ] Write commit message

### 5. **Release Phase**
- [ ] Commit to repo
- [ ] Push to GitHub
- [ ] Create YouTrack issue (mark as Done)
- [ ] Update `.ofield_new`
- [ ] Create UPDATE_NOTES.txt (if major)

---

## 🚨 Critical Rules

### NEVER:
- ❌ Change encoding defaults without discussion
- ❌ Break backward compatibility
- ❌ Commit directly to main (if major feature)
- ❌ Push untested code to production
- ❌ Modify user's actual `.ofield` without backup
- ❌ Use AI-guessed compression ratios (research!)
- ❌ Remove safety checks (pause/skip logic)

### ALWAYS:
- ✅ Test in `.ofield_new` first
- ✅ Support old config formats
- ✅ Log important operations
- ✅ Use try/except for risky operations
- ✅ Update documentation
- ✅ Think about Docker users
- ✅ Be transparent about quality tradeoffs

---

## 🔗 External Resources

### FFmpeg/x265 Reference
- **x265 params:** https://x265.readthedocs.io/
- **CRF guide:** https://trac.ffmpeg.org/wiki/Encode/H.265
- **Preset comparison:** https://x265.readthedocs.io/en/master/presets.html

### Community Feedback
- Monitor GitHub issues for quality concerns
- Be receptive to criticism (recent feedback improved project significantly!)
- Document tradeoffs when criticized

### Similar Tools (for reference)
- **Tdarr:** https://tdarr.io/ (more complex, quality-focused)
- **FileFlows:** https://fileflows.com/ (node-based)
- Our niche: **Simplicity + automation**

---

## 💡 Current Priorities (as of 2025-01-14)

### Completed ✅
- Per-folder scan intervals
- Configurable encoding settings
- Better codec detection (AV1/VP9/HEVC skip)
- Quality improvements (slow preset, constrained-intra)
- Comprehensive documentation

### Future Ideas (NOT committed)
- GPU encoding support (`hevc_nvenc`)
- Source CRF detection (complex, low priority)
- Web API for manual triggers
- Parallel folder processing (careful with state!)
- Advanced x265 params customization

### Won't Do
- AV1 output (too slow for automation)
- Lossless encoding (not the purpose)
- Real-time transcoding
- Multi-node distributed processing

---

## 📞 Communication

### When to Ask User
- Major architectural changes
- Default setting changes
- Breaking changes (even with migration)
- Unclear requirements
- Quality vs performance tradeoffs

### Project Tone
- **Helpful, not preachy**
- **Transparent about limitations**
- **Professional objectivity** (facts over validation)
- **Polish language OK** (user is Polish)

---

## 🎓 Remember

This is a **hobby project** for a home server, not enterprise software:
- **Simplicity > Features**
- **Reliability > Performance**
- **Backward compatibility > Clean code**
- **User's use case > Generic solution**

The user values:
1. **It works** without babysitting
2. **Saves disk space** effectively  
3. **Reasonable quality** (not cinema-grade)
4. **Easy to configure**

---

**Last Updated:** 2025-01-14  
**Agent Version:** 1.0  
**Current Commit:** 8131b59
