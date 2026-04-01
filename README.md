# Dev-Tracker

A lightweight daemon for tracking developer activity with a focus on privacy.

## Conceptual Architecture
```
[Python Daemon]
    │
    ├── Window title poller (every 5s)
    ├── Active process tracker
    └── Idle detector (XScreenSaver API)
         │
         ▼
[SQLite local database]
         │
         ▼ (weekly JSON export via HTTP POST)
[n8n flow]
    ├── Aggregation + summary
    └── HTML email → Gmail
```

## Phase 1 - Core Functionality ✅

### Features
- ✅ Active window tracking (title + process name)
- ✅ Idle detection (2 minutes of inactivity)
- ✅ Automatic categorization based on regex rules
- ✅ Session storage in SQLite
- ✅ Polling every 5 seconds
- ✅ Privacy-first: only window title and process name, never content

### Requirements
- Python 3.11+
- Linux with X11
- `xdotool` (for reading window information)
- XScreenSaver (for idle detection)

### Installation
```bash
# Install system dependencies
sudo apt-get install xdotool libxss-dev

# Install Python dependencies
pip install -r requirements.txt
```

### Usage

#### Manual start
```bash
# Start the tracker
python -m daemon.main

# Stop: Ctrl+C
```

#### Run as systemd service (recommended)
```bash
# Copy the service file to the user directory
mkdir -p ~/.config/systemd/user
cp systemd/dev-tracker.service ~/.config/systemd/user/

# Enable autostart on login
systemctl --user enable dev-tracker

# Start the service now
systemctl --user start dev-tracker

# Check status
systemctl --user status dev-tracker

# View logs
journalctl --user -u dev-tracker -f

# Stop the service
systemctl --user stop dev-tracker

# Disable autostart
systemctl --user disable dev-tracker
```

**Note:** Make sure the path in `systemd/dev-tracker.service` points to the correct project location (default `~/dev-tracker`). If the project is located elsewhere, edit `WorkingDirectory` and `ExecStart` in the service file.

### Configuration

Edit `config/categories.yaml` to customize categorization rules.

### Database Structure

Table `sessions`:
- `id` - Session ID
- `window_title` - Window title
- `process_name` - Process name
- `category` - Category (from regex rules)
- `start_time` - Session start time
- `end_time` - Session end time
- `duration_seconds` - Duration in seconds
- `is_idle` - Whether session ended due to idle

### Privacy

Dev-tracker does **NOT** store:
- Window contents
- Keystrokes
- Screenshots
- Personal data

It stores **ONLY**:
- Window title
- Process name
- Session start/end times

## Roadmap

### Phase 2 (planned)
- Data export to JSON
- Integration with n8n (HTTP POST)
- Weekly aggregation

### Phase 3 (planned)
- HTML report generation
- Email sending via n8n