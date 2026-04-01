# Dev-Tracker

Lekki daemon do śledzenia aktywności deweloperskiej z naciskiem na prywatność.

## Architektura koncepcyjna

```
[Python Daemon]
    │
    ├── Window title poller (co 5s)
    ├── Active process tracker
    └── Idle detector (XScreenSaver API)
         │
         ▼
[SQLite local database]
         │
         ▼ (tygodniowy eksport JSON przez HTTP POST)
[n8n flow]
    ├── Agregacja + podsumowanie
    └── Wysyłka HTML email → Gmail
```

## Faza 1 - Podstawowa funkcjonalność ✅

### Funkcje
- ✅ Śledzenie aktywnego okna (tytuł + nazwa procesu)
- ✅ Wykrywanie bezczynności (2 minuty bez aktywności)
- ✅ Automatyczna kategoryzacja na podstawie reguł regex
- ✅ Zapis sesji do SQLite
- ✅ Polling co 5 sekund
- ✅ Privacy-first: tylko tytuł okna i nazwa procesu, bez zawartości

### Wymagania
- Python 3.11+
- Linux z X11
- `xdotool` (do pobierania informacji o oknach)
- XScreenSaver (do wykrywania bezczynności)

### Instalacja

```bash
# Zainstaluj zależności systemowe
sudo apt-get install xdotool libxss-dev

# Zainstaluj zależności Python
pip install -r requirements.txt
```

### Użycie

#### Uruchomienie ręczne

```bash
# Uruchom trackera
python -m daemon.main

# Zatrzymaj: Ctrl+C
```

#### Uruchomienie jako usługa systemd (zalecane)

```bash
# Skopiuj plik usługi do katalogu użytkownika
mkdir -p ~/.config/systemd/user
cp systemd/dev-tracker.service ~/.config/systemd/user/

# Włącz automatyczne uruchamianie przy logowaniu
systemctl --user enable dev-tracker

# Uruchom usługę teraz
systemctl --user start dev-tracker

# Sprawdź status
systemctl --user status dev-tracker

# Zobacz logi
journalctl --user -u dev-tracker -f

# Zatrzymaj usługę
systemctl --user stop dev-tracker

# Wyłącz automatyczne uruchamianie
systemctl --user disable dev-tracker
```

**Uwaga:** Upewnij się, że ścieżka w pliku `systemd/dev-tracker.service` wskazuje na właściwą lokalizację projektu (domyślnie `~/dev-tracker`). Jeśli projekt znajduje się w innym miejscu, edytuj `WorkingDirectory` i `ExecStart` w pliku usługi.

### Konfiguracja

Edytuj `config/categories.yaml` aby dostosować reguły kategoryzacji.

### Struktura bazy danych

Tabela `sessions`:
- `id` - ID sesji
- `window_title` - Tytuł okna
- `process_name` - Nazwa procesu
- `category` - Kategoria (z reguł regex)
- `start_time` - Czas rozpoczęcia
- `end_time` - Czas zakończenia
- `duration_seconds` - Czas trwania w sekundach
- `is_idle` - Czy zakończono z powodu bezczynności

### Prywatność

Dev-tracker **NIE** zapisuje:
- Zawartości okien
- Naciśnięć klawiszy
- Zrzutów ekranu
- Danych osobowych

Zapisuje **TYLKO**:
- Tytuł okna
- Nazwę procesu
- Czasy rozpoczęcia/zakończenia sesji

## Roadmap

### Faza 2 (planowana)
- Eksport danych do JSON
- Integracja z n8n (HTTP POST)
- Agregacja tygodniowa

### Faza 3 (planowana)
- Generowanie raportów HTML
- Wysyłka emaili przez n8n
