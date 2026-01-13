import os
import time
import json
import threading
import subprocess
import logging
import requests
import sys
from flask import Flask
from watchdog_core import load_stats, save_stats, push_kuma, get_video_codec

# --- DEFAULT CONFIGURATION ---
DEFAULT_CONFIG = {
    "SOURCE_DIRS": ["/films", "/tv"],
    "STATS_FILE": "/config/stats.json",
    "LOG_FILE": "/config/watchdog.log",
    "TEMP_EXT": ".temp.mkv",
    "PORT": 8085,
    "KUMA_URL": ""
}

def load_config():
    """Load config from /config/config.json or use defaults"""
    config_path = "/config/config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding='utf-8') as f:
                user_config = json.load(f)
                return {**DEFAULT_CONFIG, **user_config}
        except Exception as e:
            print(f"Error loading {config_path}: {e}")
    return DEFAULT_CONFIG

CONFIG = load_config()

# Setup Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

try:
    log_dir = os.path.dirname(CONFIG["LOG_FILE"])
    if log_dir and not os.path.exists(log_dir): 
        os.makedirs(log_dir)
    fh = logging.FileHandler(CONFIG["LOG_FILE"])
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except: pass

logging.getLogger('werkzeug').setLevel(logging.ERROR)

state = {
    "status": "Inicjalizacja",
    "current_file": "Brak",
    "stats": load_stats(CONFIG["STATS_FILE"])
}

app = Flask(__name__)

def worker_loop():
    logger.info("=== HEVC WATCHDOG DOCKER V1.0 START ===")
    
    while True:
        state['status'] = "Skanowanie..."
        push_kuma(CONFIG["KUMA_URL"])
        
        found_files = []
        for root_dir in CONFIG["SOURCE_DIRS"]:
            if not os.path.exists(root_dir):
                logger.error(f"DEBUG: Folder {root_dir} nie istnieje w kontenerze!")
                continue
            
            try:
                items = os.listdir(root_dir)
                logger.info(f"DEBUG: Skanowanie {root_dir}. Znaleziono elementow: {len(items)}")
                
                for dirpath, _, filenames in os.walk(root_dir):
                    for f in filenames:
                        if f.lower().endswith(('.mkv', '.mp4', '.avi')) and not f.endswith(CONFIG["TEMP_EXT"]):
                            found_files.append(os.path.join(dirpath, f))
            except Exception as e:
                logger.error(f"Blad skanowania {root_dir}: {e}")
        
        found_files.sort(key=lambda x: os.path.getmtime(x))
        if found_files:
            logger.info(f"Lacznie znaleziono {len(found_files)} plikow do konwersji.")

        for file_path in found_files:
            file_name = os.path.basename(file_path)
            try:
                cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
                codec = subprocess.check_output(cmd, text=True, timeout=30).strip()
            except: continue

            if codec in ['hevc', 'h265']: continue

            state['status'] = "Konwersja..."
            state['current_file'] = file_name
            logger.info(f"START: {file_name} ({codec})")
            
            output_file = file_path + CONFIG["TEMP_EXT"]
            cmd = ["ffmpeg", "-i", file_path, "-c:v", "libx265", "-crf", "26", "-preset", "medium", "-c:a", "copy", "-c:s", "copy", "-map", "0", "-y", output_file]

            try:
                p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                _, stderr = p.communicate()
                
                if p.returncode == 0 and os.path.exists(output_file):
                    orig_s = os.path.getsize(file_path) / (1024**3)
                    new_s = os.path.getsize(output_file) / (1024**3)
                    if new_s < orig_s:
                        os.remove(file_path)
                        os.rename(output_file, file_path)
                        state['stats']['processed'] += 1
                        state['stats']['gb_proc'] += orig_s
                        state['stats']['gb_saved'] += (orig_s - new_s)
                        save_stats(CONFIG["STATS_FILE"], state['stats'])
                        logger.info(f"SUKCES: {file_name} (-{orig_s-new_s:.2f} GB)")
                    else:
                        os.remove(output_file)
                else: logger.error(f"FFMPEG FAIL: {file_name}")
            except Exception as e: logger.error(f"Wyjatek: {e}")

            state['current_file'] = "Brak"
            push_kuma(CONFIG["KUMA_URL"])

        state['status'] = "Czuwanie"
        time.sleep(60)

@app.route('/')
def dashboard():
    s = state['stats']
    return f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="3">
    <style>
    body{{background:#1a1b1e;color:#fff;font-family:sans-serif;margin:0;padding:10px}}
    .card{{background:#25262b;border:1px solid #373a40;border-radius:8px;padding:15px;display:flex;justify-content:space-between;align-items:center}}
    .status{{color:#4dabf7;font-weight:bold;text-transform:uppercase}}
    .file{{color:#909296;font-size:0.8em;max-width:300px;overflow:hidden;text-overflow:ellipsis}}
    .val{{color:#69db7c;font-weight:bold;font-size:1.2em}}
    .lbl{{color:#868e96;font-size:0.7em}}
    </style></head><body>
    <div class="card">
        <div><div class="status">{state['status']}</div><div class="file">{state['current_file']}</div></div>
        <div style="display:flex;gap:20px">
            <div style="text-align:center"><span class="val">{s['processed']}</span><br><span class="lbl">Pliki</span></div>
            <div style="text-align:center"><span class="val">{s['gb_proc']:.1f}</span><br><span class="lbl">GB Proc</span></div>
            <div style="text-align:center"><span class="val">{s['gb_saved']:.1f}</span><br><span class="lbl">GB Oszcz</span></div>
        </div>
    </div></body></html>"""

if __name__ == "__main__":
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=CONFIG["PORT"])
