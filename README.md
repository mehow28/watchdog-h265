# HEVC Watchdog

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<img width="734" height="542" alt="image" src="https://github.com/user-attachments/assets/ec144e20-8e70-4049-ab71-93fa65beabc3" />

(localhost:8085) -> Homar iFrame widget)

[EN](#english) | [PL](#polski)

---

<a name="english"></a>
## EN

**Automated video library optimization to H.265 (HEVC) standard.**

HEVC Watchdog is a "set-and-forget" background service designed for home servers and NAS enthusiasts. It monitors your media folders and automatically transcodes files to H.265 to save up to 50-70% of disk space.

### 🆕 Recent Updates (v2.1.0)
- **🛡️ Data Safety:** Atomic file replacement prevents corruption during power loss or crashes
- **🎮 GPU Encoding:** NVIDIA NVENC, Intel QSV, AMD AMF support (10x faster!)
- **📊 Skip Statistics:** Dashboard now shows skipped files and reasons
- **🔧 Audit Tools:** Scripts to detect corrupted MKV files (`audit_corrupted.sh`, `audit_corrupted.ps1`)

See [CHANGELOG.md](CHANGELOG.md) for full version history.

### ⚠️ Important Quality Notice

**This tool prioritizes automation and space savings over maximum quality.** Default settings:
- **CRF 26** - Good balance, but not cinema-grade
- **Preset "slow"** - Better quality than "medium", still reasonable encoding time
- **constrained-intra** - Minimizes re-encoding artifacts
- **Smart codec detection** - Skips AV1, VP9, and existing HEVC files

**Who should NOT use this:**
- Archivists wanting lossless/near-lossless quality
- Sources already in efficient codecs (AV1, VP9, high-CRF H.264)
- Users wanting frame-perfect encode analysis

**Better alternatives for quality-focused workflows:** [Tdarr](https://tdarr.io/), [FileFlows](https://fileflows.com/)

See [CONFIG.md](CONFIG.md) for customizing quality settings.

### Features
*   **Automatic Transcoding:** Detects files requiring optimization and processes them in a sorted queue.
*   **Atomic File Operations:** Safe file replacement prevents data corruption during failures.
*   **Web Dashboard:** Real-time UI (default port 8085) with logs, storage savings, and skip statistics - great to make into a Homarr IFrame widget.
*   **Controls:** Controls to **Pause/Play** or **Skip** the current file.
*   **GPU Acceleration:** NVIDIA NVENC, Intel QSV, AMD AMF support for 10x faster encoding.
*   **Monitoring:** Built-in support for Uptime Kuma.
*   **Cross-Platform:** Works on Windows, Linux, and macOS.
*   **Docker Support:** Containerized version available for easy deployment.
*   **Audit Tools:** Detect corrupted video files with included scripts.

### Requirements
*   **Python:** 3.7 or higher
*   **FFmpeg:** Must be installed and available in PATH
    *   Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
    *   Linux: `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo yum install ffmpeg` (RHEL/CentOS)
    *   macOS: `brew install ffmpeg`
*   **Python packages:** `pip install -r requirements.txt`

### Quick Start

#### Standalone Version
1.  **Install Requirements:** 
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure:** 
    ```bash
    cp config.example.json config.json
    # Edit config.json with your paths
    ```
3.  **Run:** 
    ```bash
    python watchdog_h265.py
    ```
4.  **Access Dashboard:** Open `http://localhost:8085` in your browser

#### Docker Version
1.  **Navigate to docker folder:**
    ```bash
    cd docker-watchdog
    ```
2.  **Edit docker-compose.yml:** Update volume paths to your media folders
3.  **Optional - Configure:** 
    ```bash
    cp config.example.json data/config.json
    # Edit data/config.json if needed
    ```
4.  **Start container:**
    ```bash
    docker-compose up -d
    ```
5.  **Access Dashboard:** Open `http://localhost:8085` in your browser

### Configuration

Edit `config.json` (or `docker-watchdog/data/config.json` for Docker):

```json
{
    "SOURCE_DIRS": ["/path/to/movies", "/path/to/tv-shows"],
    "TEMP_FOLDER": "watchdog_temp",
    "STATS_FILE": "stats.json",
    "LOG_FILE": "watchdog.log",
    "OUTPUT_SUFFIX": ".hevc.mkv",
    "PORT": 8085,
    "KUMA_URL": ""
}
```

**Configuration Options:**
*   `SOURCE_DIRS`: List of folders to monitor (absolute paths)
*   `TEMP_FOLDER`: Temporary folder for transcoding (relative to script location)
*   `STATS_FILE`: File to store statistics
*   `LOG_FILE`: Log file location
*   `OUTPUT_SUFFIX`: Suffix for already-processed files (prevents re-processing)
*   `PORT`: Web dashboard port
*   `KUMA_URL`: (Optional) Uptime Kuma push URL for monitoring

### How It Works
1.  Scans all `SOURCE_DIRS` for video files (.mkv, .mp4, .avi)
2.  Checks codec using FFprobe - skips files already in H.265/HEVC
3.  Transcodes files using FFmpeg with libx265 (CRF 26, medium preset)
4.  Compares file sizes - only replaces original if new file is smaller
5.  Updates statistics and repeats every 60 seconds

### Troubleshooting

**FFmpeg not found:**
*   Ensure FFmpeg is installed and in your system PATH
*   Test with: `ffmpeg -version`

**Permission denied:**
*   Check folder permissions - script needs read/write access
*   On Linux: ensure user has access to media folders

**Docker container can't access network shares:**
*   Use correct volume syntax: `//host/share:/mount` (Windows) or `/mnt/share:/mount` (Linux)
*   Check SMB/NFS mount permissions

**Files not being processed:**
*   Check logs in dashboard or `watchdog.log`
*   Verify `SOURCE_DIRS` paths are correct
*   Ensure files don't already have `OUTPUT_SUFFIX` in filename

**Corrupted video files detected:**
*   Use included audit tools to scan your library:
    *   **Linux/macOS:** `bash audit_corrupted.sh`
    *   **Windows:** `powershell -ExecutionPolicy Bypass -File audit_corrupted.ps1`
*   These scripts use FFprobe to detect invalid Matroska headers and incomplete files
*   Results are exported to `corrupted_files_report.txt` with episode numbers for re-download

### License
MIT License - see [LICENSE](LICENSE) file for details

---

<a name="polski"></a>
## PL

**Automatyczna optymalizacja biblioteki wideo do standardu H.265 (HEVC).**

HEVC Watchdog to inteligentna usługa działająca w tle, stworzona dla serwerów domowych i użytkowników NAS. Monitoruje foldery z mediami i automatycznie konwertuje pliki do formatu H.265, oszczędzając od 50% do 70% miejsca na dysku.

### 🆕 Ostatnie Aktualizacje (v2.1.0)
- **🛡️ Bezpieczeństwo Danych:** Atomowa zamiana plików zapobiega uszkodzeniom przy awarii prądu lub crashu
- **🎮 Enkodowanie GPU:** Wsparcie NVIDIA NVENC, Intel QSV, AMD AMF (10x szybsze!)
- **📊 Statystyki Pominiętych:** Dashboard pokazuje pominięte pliki i powody
- **🔧 Narzędzia Audytu:** Skrypty do wykrywania uszkodzonych plików MKV (`audit_corrupted.sh`, `audit_corrupted.ps1`)

Zobacz [CHANGELOG.md](CHANGELOG.md) dla pełnej historii wersji.

### ⚠️ Ważna Uwaga o Jakości

**To narzędzie priorytetyzuje automatyzację i oszczędność miejsca nad maksymalną jakość.** Domyślne ustawienia:
- **CRF 26** - Dobry balans, ale nie jakość kinowa
- **Preset "slow"** - Lepsza jakość niż "medium", rozsądny czas encodowania
- **constrained-intra** - Minimalizuje artefakty przy re-encodingu
- **Inteligentna detekcja** - Pomija pliki AV1, VP9 i już istniejące HEVC

**Kto NIE powinien używać:**
- Archiwiści chcący jakości lossless/near-lossless
- Źródła już w efektywnych kodekach (AV1, VP9, wysokie CRF H.264)
- Użytkownicy wymagający klatka-po-klatce analizy

**Lepsze alternatywy dla jakości:** [Tdarr](https://tdarr.io/), [FileFlows](https://fileflows.com/)

Zobacz [CONFIG.md](CONFIG.md) aby dostosować ustawienia jakości.

### Funkcje
*   **Automatyczna konwersja:** Wykrywa pliki wymagające optymalizacji i przetwarza je w kolejce.
*   **Atomowe Operacje:** Bezpieczna zamiana plików zapobiega utracie danych przy awariach.
*   **Dashboard WWW:** Interfejs w czasie rzeczywistym z logami, statystykami oszczędności i pominięć - w sam raz na widget IFrame do Homarr.
*   **Kontrolki:** Przyciski **Pauza/Play** oraz **Pomiń (Skip)** obecny plik.
*   **Akceleracja GPU:** Wsparcie NVIDIA NVENC, Intel QSV, AMD AMF dla 10x szybszego enkodowania.
*   **Monitoring:** Wsparcie dla powiadomień Uptime Kuma.
*   **Wieloplatformowość:** Działa na Windows, Linux i macOS.
*   **Wsparcie Docker:** Dostępna wersja kontenerowa dla łatwego wdrożenia.
*   **Narzędzia Audytu:** Wykrywanie uszkodzonych plików wideo za pomocą dołączonych skryptów.

### Wymagania
*   **Python:** 3.7 lub wyższy
*   **FFmpeg:** Musi być zainstalowany i dostępny w PATH
    *   Windows: Pobierz z [ffmpeg.org](https://ffmpeg.org/download.html)
    *   Linux: `sudo apt install ffmpeg` (Debian/Ubuntu) lub `sudo yum install ffmpeg` (RHEL/CentOS)
    *   macOS: `brew install ffmpeg`
*   **Pakiety Python:** `pip install -r requirements.txt`

### Szybki Start

#### Wersja Standalone
1.  **Instalacja wymagań:** 
    ```bash
    pip install -r requirements.txt
    ```
2.  **Konfiguracja:** 
    ```bash
    cp config.example.json config.json
    # Edytuj config.json podając swoje ścieżki
    ```
3.  **Uruchomienie:** 
    ```bash
    python watchdog_h265.py
    ```
4.  **Dashboard:** Otwórz `http://localhost:8085` w przeglądarce

#### Wersja Docker
1.  **Przejdź do folderu docker:**
    ```bash
    cd docker-watchdog
    ```
2.  **Edytuj docker-compose.yml:** Zaktualizuj ścieżki volume do swoich folderów
3.  **Opcjonalnie - Konfiguracja:** 
    ```bash
    cp config.example.json data/config.json
    # Edytuj data/config.json jeśli potrzeba
    ```
4.  **Uruchom kontener:**
    ```bash
    docker-compose up -d
    ```
5.  **Dashboard:** Otwórz `http://localhost:8085` w przeglądarce

### Konfiguracja

Edytuj `config.json` (lub `docker-watchdog/data/config.json` dla Dockera):

```json
{
    "SOURCE_DIRS": ["/ścieżka/do/filmów", "/ścieżka/do/seriali"],
    "TEMP_FOLDER": "watchdog_temp",
    "STATS_FILE": "stats.json",
    "LOG_FILE": "watchdog.log",
    "OUTPUT_SUFFIX": ".hevc.mkv",
    "PORT": 8085,
    "KUMA_URL": ""
}
```

**Opcje konfiguracji:**
*   `SOURCE_DIRS`: Lista folderów do monitorowania (ścieżki bezwzględne)
*   `TEMP_FOLDER`: Folder tymczasowy dla konwersji (względem lokalizacji skryptu)
*   `STATS_FILE`: Plik z statystykami
*   `LOG_FILE`: Lokalizacja pliku logów
*   `OUTPUT_SUFFIX`: Sufiks dla przetworzonych plików (zapobiega powtórnej konwersji)
*   `PORT`: Port dashboardu webowego
*   `KUMA_URL`: (Opcjonalnie) URL push Uptime Kuma dla monitoringu

### Jak to działa
1.  Skanuje wszystkie `SOURCE_DIRS` w poszukiwaniu plików wideo (.mkv, .mp4, .avi)
2.  Sprawdza kodek używając FFprobe - pomija pliki już w H.265/HEVC
3.  Konwertuje pliki używając FFmpeg z libx265 (CRF 26, preset medium)
4.  Porównuje rozmiary plików - zamienia oryginał tylko jeśli nowy plik jest mniejszy
5.  Aktualizuje statystyki i powtarza co 60 sekund

### Rozwiązywanie problemów

**FFmpeg nie znaleziony:**
*   Upewnij się, że FFmpeg jest zainstalowany i znajduje się w PATH systemowym
*   Testuj komendą: `ffmpeg -version`

**Brak dostępu:**
*   Sprawdź uprawnienia do folderów - skrypt potrzebuje dostępu odczytu/zapisu
*   Na Linux: upewnij się, że użytkownik ma dostęp do folderów medialnych

**Kontener Docker nie ma dostępu do udziałów sieciowych:**
*   Użyj poprawnej składni volume: `//host/udział:/mount` (Windows) lub `/mnt/udział:/mount` (Linux)
*   Sprawdź uprawnienia montowania SMB/NFS

**Pliki nie są przetwarzane:**
*   Sprawdź logi w dashboardzie lub `watchdog.log`
*   Zweryfikuj czy ścieżki `SOURCE_DIRS` są poprawne
*   Upewnij się, że pliki nie mają już `OUTPUT_SUFFIX` w nazwie

**Wykryto uszkodzone pliki wideo:**
*   Użyj dołączonych narzędzi audytu do przeskanowania biblioteki:
    *   **Linux/macOS:** `bash audit_corrupted.sh`
    *   **Windows:** `powershell -ExecutionPolicy Bypass -File audit_corrupted.ps1`
*   Skrypty używają FFprobe do wykrywania nieprawidłowych nagłówków Matroska i niekompletnych plików
*   Wyniki są eksportowane do `corrupted_files_report.txt` z numerami odcinków do ponownego pobrania

### Licencja
Licencja MIT - szczegóły w pliku [LICENSE](LICENSE)
