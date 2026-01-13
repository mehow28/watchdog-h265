import os
import json
import requests
import subprocess
import logging

def load_stats(stats_file):
    stats = {"processed": 0, "gb_proc": 0.0, "gb_saved": 0.0}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        except:
            pass
    return stats

def save_stats(stats_file, stats):
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f)
    except:
        pass

def push_kuma(kuma_url):
    if kuma_url:
        try:
            requests.get(kuma_url, timeout=10)
        except:
            pass

def get_video_codec(filepath):
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15, creationflags=0x08000000)
        return result.stdout.strip()
    except:
        return None

def kill_process_tree(pid):
    try:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True, creationflags=0x08000000)
    except:
        pass

def get_last_logs(log_file, n=120):
    if not os.path.exists(log_file):
        return ""
    try:
        with open(log_file, "r", encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-n:])
    except:
        return "Błąd odczytu logów..."