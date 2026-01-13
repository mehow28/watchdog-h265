import os
import time
import json
import threading
import subprocess
import logging
import requests
import sys
import shutil
from flask import Flask, redirect, url_for
from watchdog_core import load_stats, save_stats, push_kuma, get_video_codec, kill_process_tree, get_last_logs

# --- DEFAULT CONFIGURATION ---
DEFAULT_CONFIG = {
    "SOURCE_DIRS": [],
    "TEMP_FOLDER": "watchdog_temp",
    "STATS_FILE": "stats.json",
    "LOG_FILE": "watchdog.log",
    "OUTPUT_SUFFIX": ".hevc.mkv",
    "PORT": 8085,
    "KUMA_URL": ""
}

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                user_config = json.load(f)
                return {**DEFAULT_CONFIG, **user_config}
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

state = {
    "status": "Inicjalizacja",
    "current_file": "Brak",
    "stats": load_stats(CONFIG["STATS_FILE"]),
    "paused": False,
    "skip": False
}

app = Flask(__name__)

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
            if os.path.exists(vid + CONFIG["OUTPUT_SUFFIX"]): continue
            codec = get_video_codec(vid)
            if codec and codec not in ['hevc', 'h265']:
                candidates.append((vid, codec))
        
        if candidates: logger.info(f"Queue: {len(candidates)} files.")

        for file_path, codec in candidates:
            while state['paused']:
                state['status'] = "PAUSED"
                state['current_file'] = "Waiting..."
                time.sleep(2)
            
            if state['skip']:
                state['skip'] = False
                continue

            file_name = os.path.basename(file_path)
            try:
                os.rename(file_path, file_path)
            except:
                logger.info(f"File in use: {file_name}")
                continue

            state['status'] = "Transcoding..."
            state['current_file'] = file_name
            logger.info(f"START: {file_name} ({codec})")
            
            output_file = os.path.join(CONFIG["TEMP_FOLDER"], file_name + CONFIG["OUTPUT_SUFFIX"])
            
            cmd = [
                "ffmpeg", "-i", file_path,
                "-c:v", "libx265", "-crf", "26", "-preset", "medium",
                "-c:a", "copy", "-c:s", "copy", "-map", "0",
                "-max_muxing_queue_size", "1024",
                "-y", output_file
            ]

            try:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    encoding='utf-8',
                    errors='replace',
                    creationflags=0x08000000
                )
                
                was_interrupted = False
                for line in process.stdout:
                    if state['skip'] or state['paused']:
                        logger.info(f"Forcing FFmpeg stop (PID: {process.pid})...")
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
                    if os.path.exists(output_file): os.remove(output_file)
                    if state['skip']:
                        state['skip'] = False
                        logger.info(f"Skipped file: {file_name}")
                        continue
                    else:
                        logger.info(f"Paused on file: {file_name}")
                        break 

                if process.returncode == 0 and os.path.exists(output_file):
                    orig_s = os.path.getsize(file_path) / (1024**3)
                    new_s = os.path.getsize(output_file) / (1024**3)
                    
                    if new_s < orig_s:
                        os.remove(file_path)
                        shutil.move(output_file, file_path)
                        state['stats']['processed'] += 1
                        state['stats']['gb_proc'] += orig_s
                        state['stats']['gb_saved'] += (orig_s - new_s)
                        save_stats(CONFIG["STATS_FILE"], state['stats'])
                        logger.info(f"SUCCESS: {file_name} (-{orig_s-new_s:.2f} GB)")
                    else:
                        os.remove(output_file)
                        logger.info(f"SKIPPED: {file_name} (No savings)")
                else:
                    if not was_interrupted:
                        logger.error(f"FFMPEG ERROR: {file_name}")
                    if os.path.exists(output_file): os.remove(output_file)
            except Exception as e:
                logger.error(f"Exception: {e}")

            state['current_file'] = "None"
            push_kuma(CONFIG["KUMA_URL"])

        state['status'] = "Idle"
        time.sleep(60)

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
    </body></html>"

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
    app.run(host='0.0.0.0', port=CONFIG["PORT"])"""