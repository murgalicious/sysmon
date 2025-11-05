# SysMon2 - System & Docker Monitoring Bot

**SysMon2** is a Python-based monitoring bot that keeps track of system resources, disk usage, and Docker container statuses. It sends alerts to a Telegram chat when thresholds are exceeded, allowing you to monitor your server remotely.

---

## Features

- **CPU Monitoring:** Alerts when CPU usage is above a configurable threshold.
- **RAM Monitoring:** Alerts when RAM usage exceeds the set limit.
- **Disk Monitoring:** Monitors specified mount points and alerts when disk usage is high.
- **CPU Temperature:** Alerts if CPU temperature goes above a defined threshold.
- **Docker Monitoring:** Checks the status of all Docker containers and reports running vs total containers.
- **Telegram Alerts:** Sends real-time alerts to your Telegram bot for easy remote monitoring.
- **Acknowledgment Command:** Allows acknowledging alerts via Telegram to avoid repeated notifications.
- **Status Command:** Get a full system status report via Telegram on demand.

---

## Installation

1. Clone this repository:
```bash
git clone https://github.com/murgalicious/sysmon2.git
cd sysmon2
