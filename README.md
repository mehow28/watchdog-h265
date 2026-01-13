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

### Quick Start
1.  **Install Requirements:** `pip install flask requests`
2.  **Configure:** Edit `config.json` with your paths.
3.  **Run:** `python watchdog_h265.py`

---

<a name="polski"></a>
## PL

**Automatyczna optymalizacja biblioteki wideo do standardu H.265 (HEVC).**

HEVC Watchdog to inteligentna usługa działająca w tle, stworzona dla serwerów domowych i użytkowników NAS. Monitoruje foldery z mediami i automatycznie konwertuje pliki do formatu H.265, oszczędzając od 50% do 70% miejsca na dysku.

### Funkcje
*   **Automatyczna konwersja:** Wykrywa pliki wymagające optymalizacji i przetwarza je w kolejce.
*   **Dashboard WWW:** Interfejs w czasie rzeczywistym z logami i statystykami oszczędności - w sam raz na widget IFrame do Homarr .
*   **Kontrolki:** Przyciski **Pauza/Play** oraz **Pomiń (Skip)** obecny plik.
*   **Monitoring:** Wsparcie dla powiadomień Uptime Kuma.

### 🚀 Szybki Start
1.  **Instalacja:** `pip install flask requests`
2.  **Konfiguracja:** Edytuj `config.json` wpisując swoje ścieżki.
3.  **Uruchomienie:** `python watchdog_h265.py`
