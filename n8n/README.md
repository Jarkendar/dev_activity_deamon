# n8n Flows

This directory contains exported n8n workflow definitions for the Dev-Tracker project.

## Related Repository

All n8n infrastructure (Docker setup, Raspberry Pi configuration, other automation flows) lives in a separate repository:

**[Jarkendar/pi-automate](https://github.com/Jarkendar/pi-automate)**

That repository contains:
- Docker Compose setup for n8n on Raspberry Pi
- Startup scripts and service configuration
- Other n8n automation projects

## Flows in this directory

### `weekly_report.json`
Triggered every **Sunday at 20:00**. Fetches last 7 days of sessions from n8n Data Tables, aggregates activity data, generates charts via Quickchart.io and sends an HTML email report via Gmail.

Flow structure:
```
Schedule (Sunday 20:00)
    → n8n Data Tables - Get Rows (last 7 days)
    → Python: aggregate data
    → Python: generate chart URLs
    → Python: build HTML email
    → Gmail: send report
```

### `monthly_report.json`
Triggered on the **1st of every month at midnight**. Fetches all sessions from the previous month, generates extended analysis with weekly breakdown, peak hours, best day of week and daily calendar.

Flow structure:
```
Schedule (1st of month, midnight)
    → n8n Data Tables - Get Rows (previous month)
    → Python: aggregate data
    → Python: generate chart URLs
    → Python: build HTML email
    → Gmail: send report
```

### `dev_tracker_webhook.json`
Receives session data from the Python daemon running on the developer's PC. Splits the session array and inserts each row into the `dev_activity_daemon` Data Table.

Flow structure:
```
Webhook (POST)
    → Split Out (sessions array)
    → n8n Data Tables - Insert Row
```

## Setup

1. Import the JSON files into your n8n instance via **Settings → Import Workflow**
2. Configure Gmail credentials in n8n
3. Set your webhook URL in `config/config.yaml` on your PC:
```yaml
n8n_webhook_url: "https://your-n8n-instance/webhook/your-webhook-id"
```
4. Activate all workflows in n8n

## Data Tables

The flows use a built-in n8n Data Table called `dev_activity_daemon` with the following columns:

| Column | Type |
|---|---|
| `session_id` | Number |
| `window_title` | Text |
| `process_name` | Text |
| `category` | Text |
| `start_time` | Date |
| `end_time` | Date |
| `duration_seconds` | Number |
| `is_idle` | Boolean |