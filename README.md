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
         ▼ (on daemon start — unsynced sessions via HTTP POST)
[n8n flow — Raspberry Pi]
    ├── Split sessions array
    ├── Insert into Data Tables (dev_activity_daemon)
    ├── Weekly HTML report → Gmail (every Sunday 20:00)
    └── Monthly HTML report → Gmail (1st of every month)
```

## n8n Infrastructure

All n8n flows, Docker setup and Raspberry Pi configuration live in a separate repository:

**[Jarkendar/pi-automate](https://github.com/Jarkendar/pi-automate)**

Exported flow definitions are available in the [`n8n/`](./n8n/) directory of this repository.

---

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
pip install -r daemon/requirements.txt
```

### Usage

#### Manual start
```bash
./run_time_tracker.sh

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

Edit `config/config.yaml` to set your n8n webhook URL:
```yaml
n8n_webhook_url: "https://your-n8n-instance/webhook/..."
```

> `config/config.yaml` is excluded from git — never commit your webhook URL.

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
- `synced` - Whether session was exported to n8n (0/1)

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

---

## Phase 2 - Bash Script ✅

`run_time_tracker.sh` activates the `.venv` virtual environment and starts the daemon. Use this for manual runs.

## Phase 3 - Sync / Exporter ✅

On every daemon start, `daemon/exporter.py`:
- Queries all unsynced sessions from SQLite
- Sends them as a JSON payload via HTTP POST to the configured n8n webhook
- Marks sessions as `synced = 1` on successful response
- Deletes records older than 3 days that have already been synced

## Phase 4 - n8n Storage ✅

n8n flow receives the session payload and stores each session as a row in the built-in **Data Tables** (`dev_activity_daemon`). Flow structure:
```
Webhook → Split Out (sessions array) → Insert Row (Data Tables)
```

## Phase 5 - Autostart on Login ✅

The daemon runs automatically on user login via a systemd user service. See installation instructions above.

## Phase 6 - Weekly & Monthly HTML Reports ✅

### Weekly report — every Sunday at 20:00
Python Code nodes in n8n aggregate last 7 days of sessions and send an HTML email via Gmail with:
- Time per category
- Daily activity bar chart
- Category time per day (stacked bar)
- Top 10 apps (pie chart)
- Active vs Idle ratio (doughnut)
- Productivity heatmap (hour vs day)

### Monthly report — 1st of every month at midnight
Covers the full previous month with extended analysis:
- Time per category
- Weekly breakdown (week by week comparison)
- Best day of week
- Peak hours distribution
- Top 10 apps (pie chart)
- Active vs Idle ratio
- Daily activity calendar

Charts are generated via **[Quickchart.io](https://quickchart.io)**.

---

## Roadmap

### Phase 7 - Windows Support (planned)
- Replace `daemon/window.py` and `daemon/idle.py` with `pywin32` equivalents
- All other modules (DB, categorizer, exporter) remain unchanged