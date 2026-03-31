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

```bash
# Uruchom trackera
python -m daemon.main

# Zatrzymaj: Ctrl+C
```

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
