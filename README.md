Tabii ki, işte README dosyanın emojilerden arındırılmış, sade ve temiz hali:

# System Health Monitor & Alerter

A system monitoring tool with Discord Webhook integration, colorized console output, and full logging support.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

---

## Features

| Feature | Description |
|---|---|
| Real-time Monitoring | CPU, RAM, Disk, and CPU Temperature |
| Discord Notifications | Instant alerts in formatted Embed style |
| Anti-Spam | Configurable alert cooldown for repeated errors |
| Logging | History tracking in `system_logs.txt` with timestamps |
| Colorized Terminal | Green/Yellow/Red status indicators |
| .env Support | Secure configuration management |

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/system-health-monitor.git
cd system-health-monitor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Configuration File

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
CHECK_INTERVAL=30
ALERT_COOLDOWN=300
THRESHOLD_CPU=80
THRESHOLD_RAM=80
THRESHOLD_DISK=90
THRESHOLD_TEMP=85
```

> **How to create a Discord Webhook?**
> Discord Channel -> Channel Settings -> Integrations -> Webhooks -> New Webhook

### 4. Run the Application

```bash
python monitor.py
```

---

## Preview

```
══════════════════════════════════════════════════════
  System Health Monitor  |  14:32:07
══════════════════════════════════════════════════════
  Hostname : DESKTOP-ABC123
  CPU      : 23.4%         <- Green
  RAM      : 67.2%  (10.8 / 16.0 GB)
  Disk     : 91.5%         <- RED (Threshold exceeded!)
  Temp     : 58.0°C
```

---

## Autostart Setup

### Windows — Task Scheduler

1. Open **Task Scheduler** (Win + R -> `taskschd.msc`)
2. Select **"Create Task"** in the right panel.
3. **General** tab:
   - Name: `System Health Monitor`
   - Check "Run with highest privileges".
4. **Triggers** tab -> **New**:
   - Begin the task: `At log on` (or `At startup`).
5. **Actions** tab -> **New**:
   - Program/script: `C:\Python311\python.exe`
   - Add arguments: `C:\path\to\your\monitor.py`
6. Click **OK** to save.

### Linux — systemd Service

Create `/etc/systemd/system/system-monitor.service`:

```ini
[Unit]
Description=System Health Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/system-health-monitor
ExecStart=/usr/bin/python3 /home/your_username/system-health-monitor/monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable system-monitor
sudo systemctl start system-monitor

# Check status:
sudo systemctl status system-monitor
```

---

## Project Structure

```
system-health-monitor/
├── monitor.py          # Main application
├── .env                # Configuration (DO NOT UPLOAD TO GIT)
├── .env.example        # Configuration template
├── requirements.txt    # Python dependencies
├── system_logs.txt     # Auto-generated log file
├── .gitignore
└── README.md
```

---

## Security Note

Ensure your `.gitignore` includes the following to prevent leaking your webhook URL:

```
.env
system_logs.txt
__pycache__/
*.pyc
```

---

## License

This project is licensed under the MIT License - feel free to use it as you wish.
