# HEVC Watchdog

[EN](#english) | [PL](#polski)

---

<a name="english"></a>
## EN

**Automated video library optimization to H.265 (HEVC) standard.**

HEVC Watchdog is a "set-and-forget" background service designed for home servers and NAS enthusiasts. It monitors your media folders and automatically transcodes files to H.265 to save up to 50-70% of disk space.

### Features
*   **Automatic Transcoding:** Detects files requiring optimization and processes them in a sorted queue.
*   **Web Dashboard:** Real-time UI (default port 8085) with logs and storage savings stats - great to make into a Homarr IFrame widget.
*   **Controls:** Controls to **Pause/Play** or **Skip** the current file.
*   **Monitoring:** Built-in support for Uptime Kuma.
*   **Cross-Platform:** Works on Windows, Linux, and macOS.
*   **Docker Support:** Containerized version available for easy deployment.

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

### License
MIT License - see [LICENSE](LICENSE) file for details

---

<a name="polski"></a>
## PL

**Automatyczna optymalizacja biblioteki wideo do standardu H.265 (HEVC).**

HEVC Watchdog to inteligentna usługa działająca w tle, stworzona dla serwerów domowych i użytkowników NAS. Monitoruje foldery z mediami i automatycznie konwertuje pliki do formatu H.265, oszczędzając od 50% do 70% miejsca na dysku.

### Funkcje
*   **Automatyczna konwersja:** Wykrywa pliki wymagające optymalizacji i przetwarza je w kolejce.
*   **Dashboard WWW:** Interfejs w czasie rzeczywistym z logami i statystykami oszczędności - w sam raz na widget IFrame do Homarr.
*   **Kontrolki:** Przyciski **Pauza/Play** oraz **Pomiń (Skip)** obecny plik.
*   **Monitoring:** Wsparcie dla powiadomień Uptime Kuma.
*   **Wieloplatformowość:** Działa na Windows, Linux i macOS.
*   **Wsparcie Docker:** Dostępna wersja kontenerowa dla łatwego wdrożenia.

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

### Licencja
Licencja MIT - szczegóły w pliku [LICENSE](LICENSE)
