# 📺 HEVC Watchdog

[English](#english) | [Polski](#polski)

---

<a name="english"></a>
## English Version

**Automated video library optimization to H.265 (HEVC) standard.**

HEVC Watchdog is a "set-and-forget" background service designed for home servers and NAS enthusiasts. It monitors your media folders and automatically transcodes files to H.265 to save up to 50-70% of disk space.

### ✨ Features
*   🚀 **Automatic Transcoding:** Detects files requiring optimization and processes them in a sorted queue.
*   📊 **Modern Web Dashboard:** Real-time UI (default port 8085) with logs and storage savings stats.
*   🕹️ **Interactive Controls:** Professional-grade controls to **Pause/Play** or **Skip** the current file.
*   🛡️ **Smart Replacement:** Uses a temporary folder during transcoding to prevent duplicate detection by Radarr/Sonarr.
*   📡 **Monitoring:** Built-in support for Uptime Kuma.

### 🚀 Quick Start
1.  **Install Requirements:** `pip install flask requests`
2.  **Configure:** Edit `config.json` with your paths.
3.  **Run:** `python watchdog_h265.py`

---

<a name="polski"></a>
## Polska Wersja

**Automatyczna optymalizacja biblioteki wideo do standardu H.265 (HEVC).**

HEVC Watchdog to inteligentna usługa działająca w tle, stworzona dla serwerów domowych i użytkowników NAS. Monitoruje foldery z mediami i automatycznie konwertuje pliki do formatu H.265, oszczędzając od 50% do 70% miejsca na dysku.

### ✨ Funkcje
*   🚀 **Automatyczna konwersja:** Wykrywa pliki wymagające optymalizacji i przetwarza je w kolejce.
*   📊 **Nowoczesny Dashboard WWW:** Interfejs w czasie rzeczywistym z logami i statystykami oszczędności.
*   🕹️ **Pełna kontrola:** Przyciski **Pauza/Play** oraz **Pomiń (Skip)** obecny plik.
*   🛡️ **Bezpieczna podmiana:** Używa folderu tymczasowego, dzięki czemu Radarr/Sonarr nie wykrywają dubli podczas pracy.
*   📡 **Monitoring:** Wsparcie dla powiadomień Uptime Kuma.

### 🚀 Szybki Start
1.  **Instalacja:** `pip install flask requests`
2.  **Konfiguracja:** Edytuj `config.json` wpisując swoje ścieżki.
3.  **Uruchomienie:** `python watchdog_h265.py`
