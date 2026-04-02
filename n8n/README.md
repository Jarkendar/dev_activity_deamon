# n8n Flows

This directory contains exported n8n workflow definitions for the Dev-Tracker project.

## Related Repository

All n8n infrastructure (Docker setup, Raspberry Pi configuration, other automation flows) lives in a separate repository:

**[Jarkendar/pi-automate](https://github.com/Jarkendar/pi-automate)**

## Flows

All three flows are exported as a single file: `dev_activity_reporter.json`

Import it into your n8n instance via **Settings → Import Workflow**.

---

### Flow 1 — Data Collector

Receives session data from the Python daemon running on the developer's PC and stores it in n8n Data Tables.
```
Webhook (POST)
    → Split Out (sessions array)
    → Code JS: fix datetime format
    → Data Tables: Insert Row (dev_activity_daemon)
```

---

### Flow 2 — Weekly Report

Triggered every **Sunday at 22:00**. Fetches last 7 days of sessions and sends an HTML email report.
```
Schedule (Sunday 22:00)
    → Data Tables: Get Rows (last 7 days)
    → Python: aggregate data
    → Python: generate charts (Quickchart.io)
    → Python: build HTML email
    → SMTP: send report
```

Charts included: time per category, daily activity, category per day (stacked), top 10 apps, active vs idle, productivity heatmap.

---

### Flow 3 — Monthly Report

Triggered on the **1st of every month at midnight**. Fetches all sessions from the previous month.
```
Schedule (1st of month, midnight)
    → Data Tables: Get Rows (previous month)
    → Python: aggregate data
    → Python: generate charts (Quickchart.io)
    → Python: build HTML email
    → SMTP: send report
```

Charts included: time per category, weekly breakdown, best day of week, peak hours, top 10 apps, active vs idle, daily activity calendar.

---

## Setup

1. Import `dev_activity_reporter.json` into your n8n instance
2. Configure SMTP credentials in n8n
3. Set environment variables in n8n:
   - `N8N_AGENT_EMAIL_FROM` — sender email address
   - `DEV_ACTIVITY_DAEMON_EMAIL_TO` — recipient email address
4. Set your webhook URL in `config/config.yaml` on your PC:
```yaml
n8n_webhook_url: "https://your-n8n-instance/webhook/your-webhook-id"
```
5. Activate the workflow in n8n

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