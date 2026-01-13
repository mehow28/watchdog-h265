import os
import json
import requests
import subprocess
import logging
import platform
import signal

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
    """Get video codec using ffprobe (cross-platform)"""
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", 
               "-show_entries", "stream=codec_name", 
               "-of", "default=noprint_wrappers=1:nokey=1", filepath]
        
        # Windows-specific flag to prevent console window
        kwargs = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE, 
                  'text': True, 'timeout': 15}
        if platform.system() == 'Windows':
            kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW
        
        result = subprocess.run(cmd, **kwargs)
        return result.stdout.strip()
    except:
        return None

def kill_process_tree(pid):
    """Kill process tree (cross-platform)"""
    try:
        system = platform.system()
        if system == 'Windows':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                          capture_output=True, creationflags=0x08000000)
        else:
            # Linux/Unix: use process group kill
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except:
                # Fallback to single process kill
                os.kill(pid, signal.SIGTERM)
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