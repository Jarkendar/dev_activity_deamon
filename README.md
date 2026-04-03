# Dev-Tracker

A lightweight daemon for tracking developer activity with a focus on privacy.

## Architecture
```
[Python Daemon]
    │
    ├── Window title poller (every 5s)
    ├── Active process tracker
    └── Idle detector (XScreenSaver / Windows API)
         │
         ▼
[SQLite local database]
         │
         ▼ (on daemon start — unsynced sessions via HTTP POST)
[n8n flow — Raspberry Pi]
    ├── Split sessions array
    ├── Insert into Data Tables (dev_activity_daemon)
    ├── Weekly HTML report → Gmail (every Sunday 22:00)
    └── Monthly HTML report → Gmail (1st of every month)
```

## Features

- Active window tracking (title + process name)
- Idle detection (2 minutes of inactivity)
- Automatic categorization based on regex rules
- Session storage in SQLite
- Polling every 5 seconds
- Privacy-first: only window title and process name, never content
- Auto-sync to n8n on every daemon start
- Autostart on login via systemd
- Cross-platform: Linux (X11) and Windows support

## Platform Support

| Feature | Linux | Windows |
|---|---|---|
| Window tracking | `xdotool` | `pywin32` |
| Idle detection | XScreenSaver API | `ctypes.windll` |
| Everything else | ✅ | ✅ |

The correct platform module is selected automatically via `platform.system()`.

> **Note:** Windows support has not been tested. The implementation is based on the `pywin32` API and should work in theory, but may require adjustments.

## Requirements

**Linux:**
- Python 3.11+
- X11
- `xdotool` and `libxss-dev`

**Windows:**
- Python 3.11+
- `pywin32>=306` (install manually)

## Installation

### Linux
```bash
# Install system dependencies
sudo apt-get install xdotool libxss-dev

# Install Python dependencies
pip install -r daemon/requirements.txt
```

### Windows
```bash
pip install -r daemon/requirements.txt
pip install pywin32
```

## Usage

### Manual start
```bash
./run_time_tracker.sh

# Stop: Ctrl+C
```

### Autostart on login — systemd service (Linux, recommended)
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

**Note:** Make sure the path in `systemd/dev-tracker.service` points to the correct project location. Edit `WorkingDirectory` and `ExecStart` in the service file if needed.

## Configuration

Edit `config/categories.yaml` to customize categorization rules.

Edit `config/config.yaml` to set your n8n webhook URL:
```yaml
n8n_webhook_url: "https://your-n8n-instance/webhook/..."
```

> `config/config.yaml` is excluded from git — never commit your webhook URL.

## Data Sync

On every daemon start, `daemon/exporter.py` automatically:
- Queries all unsynced sessions from SQLite
- Sends them as a JSON payload via HTTP POST to the configured n8n webhook
- Marks sessions as `synced = 1` on successful response
- Deletes records older than 3 days that have already been synced

If the network is unavailable at startup, the sync is skipped silently and retried on the next start.

## n8n Reports

All n8n flows, Docker setup and Raspberry Pi configuration live in a separate repository:

**[Jarkendar/pi-automate](https://github.com/Jarkendar/pi-automate)**

Exported flow definitions are available in the [`n8n/`](./n8n/) directory.

### Weekly report — every Sunday at 22:00
Aggregates last 7 days of sessions and sends an HTML email with:
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

## Database Structure

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

## Privacy

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

## Development History

The project was built incrementally in 7 phases:

| Phase | Description |
|---|---|
| 1 | Core daemon — window tracking, idle detection, SQLite |
| 2 | Bash startup script with venv activation |
| 3 | Sync / Exporter — HTTP POST to n8n on every start |
| 4 | n8n Data Tables storage |
| 5 | Autostart on login via systemd user service |
| 6 | Weekly and monthly HTML reports via n8n + Gmail |
| 7 | Windows support — platform-specific modules in `linux/` and `windows/` subdirectories |
