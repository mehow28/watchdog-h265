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
    
    Compression ratios based on real-world testing:
    - Modern codecs (AV1, VP9, HEVC) = DON'T convert (already efficient or better)
    - Old codecs (MPEG2, VC1) = Large savings
    - H.264 = Moderate savings (depends on source quality)
    
    Note: Ratios assume CRF 26 output. High-CRF sources (28+) may not save space.
    """
    try:
        original_size = os.path.getsize(filepath) / (1024**3)  # GB
        
        # Compression ratios (estimated output size as % of input)
        # Values >1.0 = conversion would increase size (skip these!)
        compression_ratios = {
            # Already efficient - DON'T convert
            'hevc': 1.00,       # Already HEVC
            'h265': 1.00,       # Already HEVC
            'av1': 1.15,        # AV1 better than HEVC - conversion = worse quality + bigger
            'vp9': 0.95,        # VP9 comparable to HEVC - minimal benefit
            
            # Old/inefficient - GOOD candidates
            'mpeg2': 0.25,      # DVD/old broadcasts - huge savings
            'mpeg4': 0.50,      # DivX/XviD era
            'xvid': 0.50,
            'vc1': 0.50,        # WMV/VC-1 (Blu-ray, old Xbox)
            'vp8': 0.60,        # Old YouTube
            
            # H.264 - depends on source quality (conservative estimate)
            'h264': 0.55,       # Assumes decent quality source (CRF 18-23)
            'avc': 0.55,        # High-CRF H.264 (28+) may not save space!
        }
        
        ratio = compression_ratios.get(codec.lower(), 0.60)  # Conservative default
        estimated_size = original_size * ratio
        
        # Only worth converting if we save at least MIN_SAVINGS_GB
        min_savings = 0.5  # GB (configurable via CONFIG)
        potential_savings = original_size - estimated_size
        
        # Don't convert if ratio >= 0.95 (less than 5% savings)
        if ratio >= 0.95:
            return estimated_size, False
        
        return estimated_size, potential_savings >= min_savings
        
    except:
        return 0, True  # If estimation fails, proceed with conversion