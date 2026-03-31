# dev_activity_deamon
A Python daemon that runs in the background on Linux, tracks your work activity, stores data locally, and sends it to n8n which builds a weekly HTML email report to Gmail.

Concept Architecture
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
    ├── Aggregate + summarize
    └── Send HTML email → Gmail
