#!/bin/bash
# === AUDIT SCRIPT dla corrupted files ===
# Uruchom to na maszynie Linux z Miami Vice

echo "=== FULL MEDIA AUDIT ==="
echo "Starting: $(date)"
echo ""

# 1. Find ALL corrupted MKV files
echo "1. Scanning ALL media folders for corrupted files..."
find /media/boni/2TB/data/media -name "*.mkv" -type f -exec file {} \; 2>/dev/null | grep -v "Matroska" > /tmp/all_corrupted.txt

TOTAL_CORRUPTED=$(cat /tmp/all_corrupted.txt | wc -l)
echo "   Found: $TOTAL_CORRUPTED corrupted files"
echo ""

# 2. Group by show/folder
echo "2. Breakdown by show:"
cat /tmp/all_corrupted.txt | sed 's|/media/boni/2TB/data/media/||' | cut -d'/' -f1-2 | sort | uniq -c | sort -rn
echo ""

# 3. Miami Vice specific - extract episodes
echo "3. Miami Vice corrupted episodes (sXXeXX):"
grep -i "miami" /tmp/all_corrupted.txt | while read line; do
    filepath=$(echo "$line" | cut -d: -f1)
    filename=$(basename "$filepath")
    # Extract sXXeXX pattern
    episode=$(echo "$filename" | grep -oP '[sS]\d{2}[eE]\d{2}' | head -1 | tr '[:upper:]' '[:lower:]')
    if [ -n "$episode" ]; then
        echo "   $episode - $filename"
    else
        echo "   [no pattern] - $filename"
    fi
done | sort
echo ""

# 4. Check if corrupted = processed by watchdog
echo "4. Checking if corrupted files are .hevc.mkv (watchdog processed):"
HEVC_CORRUPTED=$(cat /tmp/all_corrupted.txt | grep -c "\.hevc\.mkv")
echo "   Corrupted with .hevc.mkv suffix: $HEVC_CORRUPTED / $TOTAL_CORRUPTED"
echo ""

# 5. Check if watchdog processed ANY files
echo "5. Checking watchdog activity:"
if [ -f ~/.watchdog/processed_files.json ] || [ -f ./processed_files.json ]; then
    PROC_FILE=$(find ~ . -name "processed_files.json" 2>/dev/null | head -1)
    if [ -n "$PROC_FILE" ]; then
        TOTAL_PROC=$(cat "$PROC_FILE" | grep -o '"' | wc -l)
        echo "   Watchdog processed files: $((TOTAL_PROC / 2))"
        echo "   Processed files location: $PROC_FILE"
    fi
else
    echo "   No processed_files.json found - watchdog may not have run here"
fi
echo ""

# 6. Stats
echo "6. Total statistics:"
TOTAL_MKV=$(find /media/boni/2TB/data/media -name "*.mkv" -type f 2>/dev/null | wc -l)
echo "   Total MKV files: $TOTAL_MKV"
echo "   Corrupted: $TOTAL_CORRUPTED"
if [ $TOTAL_MKV -gt 0 ]; then
    echo "   Corruption rate: $(awk "BEGIN {printf \"%.2f\", ($TOTAL_CORRUPTED/$TOTAL_MKV)*100}")%"
fi
echo ""

# 7. List ALL corrupted (full paths)
echo "7. Full list of corrupted files (saved to /tmp/corrupted_list.txt):"
cat /tmp/all_corrupted.txt | cut -d: -f1 | tee /tmp/corrupted_list.txt
echo ""

# 8. Generate re-download list with episodes
echo "8. Generating re-download list with episode numbers:"
grep -i "miami" /tmp/all_corrupted.txt | while read line; do
    filepath=$(echo "$line" | cut -d: -f1)
    filename=$(basename "$filepath")
    episode=$(echo "$filename" | grep -oP '[sS]\d{2}[eE]\d{2}' | head -1 | tr '[:upper:]' '[:lower:]')
    if [ -n "$episode" ]; then
        echo "$episode"
    fi
done | sort -u > /tmp/miami_episodes_to_redownload.txt

echo "   Miami Vice episodes to re-download:"
cat /tmp/miami_episodes_to_redownload.txt
echo ""

echo "=== AUDIT COMPLETE ==="
echo "Reports saved:"
echo "  - /tmp/all_corrupted.txt (full file output)"
echo "  - /tmp/corrupted_list.txt (file paths only)"
echo "  - /tmp/miami_episodes_to_redownload.txt (episode list)"
