import os
import time
import json
import threading
import subprocess
import logging
import requests
import sys
import shutil
import platform
from queue import Queue, Empty
from flask import Flask, redirect, url_for
from watchdog_core import (load_stats, save_stats, push_kuma, get_video_codec, 
                           kill_process_tree, get_last_logs, load_processed_files, 
                           save_processed_files, estimate_hevc_size)

# --- STRINGS / TRANSLATIONS ---
STRINGS = {
    "EN": {
        "init": "Initialization",
        "scanning": "Scanning...",
        "paused": "PAUSED",
        "waiting": "Waiting...",
        "transcoding": "Transcoding...",
        "idle": "Idle",
        "files": "Files",
        "gb_proc": "GB Proc",
        "savings": "Savings",
        "skip_q": "Skip file?",
        "skip_desc": "Current transcoding will be terminated.",
        "yes": "YES",
        "no": "NIE"
    },
    "PL": {
        "init": "Inicjalizacja",
        "scanning": "Skanowanie...",
        "paused": "PAUZA",
        "waiting": "Oczekiwanie...",
        "transcoding": "Konwersja...",
        "idle": "Czuwanie",
        "files": "Pliki",
        "gb_proc": "GB Proc",
        "savings": "Oszczędność",
        "skip_q": "Pominąć plik?",
        "skip_desc": "Obecna konwersja zostanie przerwana.",
        "yes": "TAK",
        "no": "NIE"
    }
}

# --- DEFAULT CONFIGURATION ---
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
    "PARALLEL_PROCESSING": False
}

def normalize_source_dirs(source_dirs, default_interval):
    """
    Normalize SOURCE_DIRS to unified format with per-folder config.
    Supports:
    - Old: ["path1", "path2"]
    - New: [{"path": "path1", "scan_interval_minutes": 60, "name": "Movies"}]
    """
    normalized = []
    
    for item in source_dirs:
        if isinstance(item, str):
            # Old format: just path string
            normalized.append({
                "path": item,
                "scan_interval_minutes": default_interval,
                "name": os.path.basename(item) or item
            })
        elif isinstance(item, dict):
            # New format: dict with config
            if "path" not in item:
                logger.warning(f"Skipping invalid SOURCE_DIR entry (no path): {item}")
                continue
            normalized.append({
                "path": item["path"],
                "scan_interval_minutes": item.get("scan_interval_minutes", default_interval),
                "name": item.get("name", os.path.basename(item["path"]) or item["path"])
            })
        else:
            logger.warning(f"Skipping invalid SOURCE_DIR entry: {item}")
    
    return normalized

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                user_config = json.load(f)
                config = {**DEFAULT_CONFIG, **user_config}
                
                # Normalize SOURCE_DIRS to new format
                if "SOURCE_DIRS" in config:
                    default_interval = config.get("SCAN_INTERVAL_MINUTES", 60)
                    config["SOURCE_DIRS"] = normalize_source_dirs(
                        config["SOURCE_DIRS"], 
                        default_interval
                    )
                
                return config
        except Exception as e:
            print(f"Error loading config.json: {e}")
    return DEFAULT_CONFIG

CONFIG = load_config()

# Ensure folders exist
if not os.path.exists(CONFIG["TEMP_FOLDER"]):
    try: os.makedirs(CONFIG["TEMP_FOLDER"])
    except: pass

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

try:
    fh = logging.FileHandler(CONFIG["LOG_FILE"], encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except: pass

logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Per-folder scan schedule
scan_schedule = {}
for folder_config in CONFIG["SOURCE_DIRS"]:
    scan_schedule[folder_config["path"]] = {
        "last_scan": 0,
        "interval": folder_config["scan_interval_minutes"] * 60,
        "name": folder_config["name"],
        "next_scan": 0,
        "status": "Idle"
    }

state = {
    "status": "Inicjalizacja",
    "current_file": "Brak",
    "current_folder": "",
    "stats": load_stats(CONFIG["STATS_FILE"]),
    "processed_files": load_processed_files(CONFIG["PROCESSED_FILES"]),
    "paused": False,
    "skip": False,
    "processing_active": False,
    "transcode_start_time": 0,
    "transcode_file_size": 0,
    "folder_statuses": {}  # For parallel mode: track each folder status
}

app = Flask(__name__)

def format_time_remaining():
    """Calculate and format estimated time remaining for current transcode"""
    if not state['processing_active'] or state['transcode_start_time'] == 0:
        return ""
    
    elapsed = time.time() - state['transcode_start_time']
    if elapsed < 10:  # Too early to estimate
        return "Calculating..."
    
    # Rough estimate: assume ~0.5 GB per minute (very approximate)
    # Better would be to parse FFmpeg progress, but this is MVP
    minutes_elapsed = elapsed / 60
    gb_per_minute = state['transcode_file_size'] / minutes_elapsed if minutes_elapsed > 0 else 0
    
    if gb_per_minute > 0:
        # Estimate based on rough 50% compression
        estimated_output_size = state['transcode_file_size'] * 0.5
        # Rough time estimate
        estimated_total_minutes = state['transcode_file_size'] / gb_per_minute if gb_per_minute > 0 else 0
        remaining_minutes = max(0, estimated_total_minutes - minutes_elapsed)
        
        if remaining_minutes > 60:
            hours = int(remaining_minutes // 60)
            mins = int(remaining_minutes % 60)
            return f"~{hours}h {mins}m"
        else:
            return f"~{int(remaining_minutes)}m"
    
    return "Calculating..."

def worker_loop():
    logger.info("=== HEVC WATCHDOG V1.0 START ===")
    
    while True:
        if state['paused']:
            state['status'] = "PAUSED"
            time.sleep(2)
            continue

        state['status'] = "Scanning..."
        push_kuma(CONFIG["KUMA_URL"])
        
        all_videos = []
        for root_dir in CONFIG["SOURCE_DIRS"]:
            if not os.path.exists(root_dir):
                logger.error(f"Directory unreachable: {root_dir}")
                continue
            for dirpath, _, filenames in os.walk(root_dir):
                for f in filenames:
                    if f.lower().endswith(('.mkv', '.mp4', '.avi')) and not f.endswith(CONFIG["OUTPUT_SUFFIX"]):
                        all_videos.append(os.path.join(dirpath, f))
        
        all_videos.sort()
        
        candidates = []
        for vid in all_videos:
            # Skip if output file already exists
            if os.path.exists(vid + CONFIG["OUTPUT_SUFFIX"]): 
                continue
            
            # Skip if already processed (file path in history)
            if vid in state['processed_files']:
                continue
            
            codec = get_video_codec(vid)
            if codec and codec not in ['hevc', 'h265']:
                # Estimate if conversion is worth it
                estimated_size, worth_it = estimate_hevc_size(vid, codec)
                if worth_it:
                    candidates.append((vid, codec, estimated_size))
                else:
                    logger.info(f"SKIP (too small savings): {os.path.basename(vid)} - estimated savings < {CONFIG['MIN_SAVINGS_GB']} GB")
                    # Mark as processed so we don't check again
                    state['processed_files'].add(vid)
                    save_processed_files(CONFIG["PROCESSED_FILES"], state['processed_files'])
        
        if candidates: logger.info(f"Queue: {len(candidates)} files (pre-checked for worthwhile savings)")

        for file_path, codec, estimated_size in candidates:
            # Check for skip before processing
            if state['skip']:
                state['skip'] = False
                logger.info(f"Skipped file (queued): {os.path.basename(file_path)}")
                continue
            
            while state['paused']:
                state['status'] = "PAUSED"
                state['current_file'] = "Waiting..."
                time.sleep(2)
                # Allow skip during pause
                if state['skip']:
                    state['skip'] = False
                    logger.info(f"Skipped file (paused): {os.path.basename(file_path)}")
                    break
            
            # If skipped during pause, continue to next file  
            if not state['paused'] and state.get('skip'):
                continue

            file_name = os.path.basename(file_path)
            try:
                os.rename(file_path, file_path)
            except:
                logger.info(f"File in use: {file_name}")
                continue

            state['status'] = "Transcoding..."
            state['current_file'] = file_name
            state['processing_active'] = True
            state['transcode_start_time'] = time.time()
            orig_size_gb = os.path.getsize(file_path) / (1024**3)
            state['transcode_file_size'] = orig_size_gb
            logger.info(f"START: {file_name} ({codec}) - {orig_size_gb:.2f} GB → est. {estimated_size:.2f} GB")
            
            output_file = os.path.join(CONFIG["TEMP_FOLDER"], file_name + CONFIG["OUTPUT_SUFFIX"])
            
            cmd = [
                "ffmpeg", "-i", file_path,
                "-c:v", "libx265", "-crf", "26", "-preset", "medium",
                "-c:a", "copy", "-c:s", "copy", "-map", "0",
                "-max_muxing_queue_size", "1024",
                "-y", output_file
            ]

            try:
                # Ensure temp file doesn't exist from previous failed run
                if os.path.exists(output_file):
                    logger.warning(f"Removing stale temp file: {output_file}")
                    os.remove(output_file)
                
                # Cross-platform subprocess
                popen_kwargs = {
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.STDOUT,
                    'text': True,
                    'encoding': 'utf-8',
                    'errors': 'replace'
                }
                if platform.system() == 'Windows':
                    popen_kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW
                else:
                    # Linux: create new process group for easier cleanup
                    if hasattr(os, 'setpgrp'):
                        popen_kwargs['preexec_fn'] = os.setpgrp
                
                process = subprocess.Popen(cmd, **popen_kwargs)
                
                was_interrupted = False
                was_skipped = False
                
                for line in process.stdout:
                    # Check for skip/pause during transcoding
                    if state['skip']:
                        logger.info(f"Skip requested - stopping FFmpeg (PID: {process.pid})...")
                        kill_process_tree(process.pid)
                        was_interrupted = True
                        was_skipped = True
                        state['skip'] = False
                        break
                    
                    if state['paused']:
                        logger.info(f"Pause requested - stopping FFmpeg (PID: {process.pid})...")
                        kill_process_tree(process.pid)
                        was_interrupted = True
                        break

                    clean_line = line.strip()
                    if clean_line and ("frame=" in clean_line or "time=" in clean_line):
                        if "frame=" in clean_line and "fps=" in clean_line:
                             if time.time() % 10 < 0.5:
                                 print(f"\rProgress: {clean_line}", end="", flush=True)
                    elif clean_line:
                        logger.info(f"FFmpeg: {clean_line}")

                process.wait() # Wait for the process to complete
                
                if was_interrupted:
                    # Clean up temp file
                    if os.path.exists(output_file): 
                        os.remove(output_file)
                    
                    if was_skipped:
                        logger.info(f"Skipped file: {file_name}")
                        continue  # Move to next file
                    else:
                        logger.info(f"Paused - will resume on: {file_name}")
                        break  # Break from candidates loop, will retry this file later

                if process.returncode == 0 and os.path.exists(output_file):
                    orig_s = os.path.getsize(file_path) / (1024**3)
                    new_s = os.path.getsize(output_file) / (1024**3)
                    
                    if new_s < orig_s:
                        os.remove(file_path)
                        shutil.move(output_file, file_path)
                        
                        # Add to processed files list
                        state['processed_files'].add(file_path)
                        save_processed_files(CONFIG["PROCESSED_FILES"], state['processed_files'])
                        
                        state['stats']['processed'] += 1
                        state['stats']['gb_proc'] += orig_s
                        state['stats']['gb_saved'] += (orig_s - new_s)
                        save_stats(CONFIG["STATS_FILE"], state['stats'])
                        logger.info(f"SUCCESS: {file_name} (-{orig_s-new_s:.2f} GB) | Est: {estimated_size:.2f} GB, Actual: {new_s:.2f} GB")
                    else:
                        os.remove(output_file)
                        # Mark as processed even if no savings (don't retry)
                        state['processed_files'].add(file_path)
                        save_processed_files(CONFIG["PROCESSED_FILES"], state['processed_files'])
                        logger.info(f"SKIPPED: {file_name} (No actual savings, will not retry)")
                else:
                    if not was_interrupted:
                        logger.error(f"FFMPEG ERROR: {file_name}")
                    if os.path.exists(output_file): os.remove(output_file)
            except Exception as e:
                logger.error(f"Exception: {e}")

            state['current_file'] = "None"
            state['processing_active'] = False
            push_kuma(CONFIG["KUMA_URL"])

        state['status'] = "Idle"
        scan_interval = CONFIG.get("SCAN_INTERVAL_MINUTES", 60) * 60
        logger.info(f"Scan complete. Next scan in {CONFIG.get('SCAN_INTERVAL_MINUTES', 60)} minutes.")
        time.sleep(scan_interval)

@app.route('/')
def dashboard():
    s = state['stats']
    logs = get_last_logs(CONFIG["LOG_FILE"])
    pause_icon = "fa-play" if state['paused'] else "fa-pause"
    pause_color = "#fcc419" if state['paused'] else "#fa5252"
    
    return f"""
    <!DOCTYPE html><html><head>
    <meta charset="UTF-8"><meta http-equiv="refresh" content="5">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    body{{background:#1a1b1e;color:#fff;font-family:sans-serif;margin:0;padding:10px;height:100vh;display:flex;flex-direction:column;box-sizing:border-box}}
    .card{{background:#25262b;border:1px solid #373a40;border-radius:8px;padding:15px;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;position:relative}}
    .info-section{{display:flex;align-items:center;gap:20px}}
    .status-group{{display:flex;flex-direction:column}}
    .status{{color:#4dabf7;font-weight:bold;text-transform:uppercase;font-size:1.1em;line-height:1}}
    .file{{color:#909296;font-size:0.75em;max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:4px}}
    .val{{color:#69db7c;font-weight:bold;font-size:1.2em}}
    .lbl{{color:#868e96;font-size:0.7em;text-transform:uppercase}}
    .controls{{display:flex;gap:8px}}
    .btn{{
        background:#2c2e33;color:#ced4da;border:1px solid #373a40;
        width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;
        cursor:pointer;text-decoration:none;transition:all 0.2s;font-size:0.9em;
    }}
    .btn:hover{{background:#383a40;color:#fff;border-color:#4dabf7}}
    .btn-pause{{color:{pause_color};border-color:{pause_color}44}}
    .btn-pause:hover{{background:{pause_color}22;border-color:{pause_color}}}
    .log-container{{
        background:#000;color:#0f0;font-family:'Consolas',monospace;font-size:0.75em;
        margin-top:10px;padding:10px;border-radius:4px;border:1px solid #333;
        flex-grow:1;overflow-y:auto;white-space:pre-wrap;word-break:break-all;
    }}
    #confirmModal{{
        display:none;position:fixed;top:0;left:0;width:100%;height:100%;
        background:rgba(0,0,0,0.8);z-index:1000;justify-content:center;align-items:center;
    }}
    .modal-content{{ 
        background:#25262b;padding:20px;border-radius:8px;border:1px solid #373a40;
        text-align:center;max-width:280px;box-shadow:0 10px 25px rgba(0,0,0,0.5);
    }}
    .modal-btns{{display:flex;gap:10px;justify-content:center;margin-top:20px}}
    .m-btn{{
        padding:8px 20px;border-radius:4px;cursor:pointer;font-weight:bold;font-size:0.8em;border:none;
    }}
    .m-btn-yes{{background:#fa5252;color:#fff}}
    .m-btn-no{{background:#373a40;color:#ced4da}}
    </style></head><body>

    <div id="confirmModal">
        <div class="modal-content">
            <div style="font-weight:bold;margin-bottom:10px">Skip file?</div>
            <div style="font-size:0.8em;color:#909296">Current transcoding will be terminated.</div>
            <div class="modal-btns">
                <button class="m-btn m-btn-yes" onclick="window.location.href='/skip'">YES</button>
                <button class="m-btn m-btn-no" onclick="document.getElementById('confirmModal').style.display='none'">NO</button>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="info-section">
            <div class="status-group">
                <div class="status">{state['status']}</div>
                <div class="file">{state['current_file']}</div>
                {'<div class="file" style="color:#fcc419;margin-top:2px"><i class="fa-solid fa-clock"></i> ETA: ' + format_time_remaining() + '</div>' if state['processing_active'] else ''}
            </div>
            <div class="controls">
                <a href="/toggle_pause" class="btn btn-pause" title="Pause/Start"><i class="fa-solid {pause_icon}"></i></a>
                <a href="javascript:void(0)" class="btn" title="Skip current file" onclick="document.getElementById('confirmModal').style.display='flex'"><i class="fa-solid fa-forward-step"></i></a>
            </div>
        </div>
        <div style="display:flex;gap:20px">
            <div style="text-align:center"><span class="val">{s['processed']}</span><br><span class="lbl">Files</span></div>
            <div style="text-align:center"><span class="val">{s['gb_proc']:.1f}</span><br><span class="lbl">GB Proc</span></div>
            <div style="text-align:center"><span class="val">{s['gb_saved']:.1f}</span><br><span class="lbl">Savings</span></div>
        </div>
    </div>
    <div class="log-container">{logs}</div>
    <script>
        var objDiv = document.querySelector(".log-container");
        if(objDiv) objDiv.scrollTop = objDiv.scrollHeight;
    </script>
    </body></html>"""

@app.route('/toggle_pause')
def toggle_pause():
    state['paused'] = not state['paused']
    return redirect(url_for('dashboard'))

@app.route('/skip')
def skip():
    state['skip'] = True
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=CONFIG["PORT"])