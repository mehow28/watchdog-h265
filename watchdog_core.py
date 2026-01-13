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

def load_processed_files(processed_file):
    """Load list of already processed files"""
    if os.path.exists(processed_file):
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_processed_files(processed_file, processed_set):
    """Save list of processed files"""
    try:
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(list(processed_set), f, indent=2)
    except:
        pass

def estimate_hevc_size(filepath, codec):
    """
    Estimate potential file size after HEVC conversion.
    Returns (estimated_size_gb, worth_converting: bool)
    
    Rough estimates based on codec:
    - h264/avc: ~50% compression
    - mpeg4/xvid: ~60% compression  
    - mpeg2: ~70% compression
    - others: ~50% compression
    """
    try:
        original_size = os.path.getsize(filepath) / (1024**3)  # GB
        
        # Compression ratios (how much smaller HEVC will be)
        compression_ratios = {
            'h264': 0.50,
            'avc': 0.50,
            'mpeg4': 0.60,
            'xvid': 0.60,
            'mpeg2': 0.70,
            'vc1': 0.55,
            'vp8': 0.55,
            'vp9': 0.45
        }
        
        ratio = compression_ratios.get(codec.lower(), 0.50)
        estimated_size = original_size * ratio
        
        # Only worth converting if we save at least 500 MB
        min_savings = 0.5  # GB
        potential_savings = original_size - estimated_size
        
        return estimated_size, potential_savings >= min_savings
        
    except:
        return 0, True  # If estimation fails, proceed with conversion