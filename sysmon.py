import psutil
import time
import docker
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = "XXXXX"  # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = "YYYYY"  # Replace with your Telegram chat ID
CHECK_INTERVAL = 60  # Check system status every 60 seconds

# Thresholds
CPU_THRESHOLD = 80  # CPU usage in %
TEMP_THRESHOLD = 70  # CPU temperature in °C
DISK_THRESHOLD = 95  # Disk usage in %
RAM_THRESHOLD = 90  # RAM usage in %

# Mount points to monitor
MOUNT_POINTS = ["/mnt/mount1", "/mnt/mount2", "/mnt/mount3", "/mnt/mount4"]

# Initialize Docker client
docker_client = docker.from_env()

# Keep track of the latest alert
latest_alert = None

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_cpu_temp():
    temps = psutil.sensors_temperatures()
    if "coretemp" in temps:
        return temps["coretemp"][0].current
    elif "cpu_thermal" in temps:
        return temps["cpu_thermal"][0].current
    else:
        return None

def get_disk_usage():
    disk_usages = {}
    for mount_point in MOUNT_POINTS:
        try:
            usage = psutil.disk_usage(mount_point)
            disk_usages[mount_point] = f"{usage.percent}% ({usage.used // (1024**3)}GB/{usage.total // (1024**3)}GB)"
        except Exception as e:
            disk_usages[mount_point] = f"Error: {e}"
    return disk_usages

def get_ram_usage():
    ram_usage = psutil.virtual_memory()
    return ram_usage.percent

def get_docker_status():
    try:
        containers = docker_client.containers.list(all=True)
        running = [c for c in containers if c.status == "running"]
        total = len(containers)
        running_count = len(running)
        container_status = f"🛠️ **Docker Containers:** {running_count}/{total} running\n"
        container_status += "\n".join([f"• {c.name}: {c.status}" for c in containers])
        return container_status
    except Exception as e:
        return f"⚠️ Error fetching Docker status: {e}"

async def send_telegram_alert(message):
    global latest_alert
    latest_alert = message  # Save the latest alert
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def monitor_system():
    global latest_alert
    while True:
        cpu_usage = get_cpu_usage()
        cpu_temp = get_cpu_temp()
        disk_usages = get_disk_usage()
        ram_usage = get_ram_usage()
        
        alerts = []
        if cpu_usage > CPU_THRESHOLD:
            alerts.append(f"🚨 **High CPU Usage**: {cpu_usage}%")
        if cpu_temp and cpu_temp > TEMP_THRESHOLD:
            alerts.append(f"🔥 **High CPU Temperature**: {cpu_temp}°C")
        for mount, usage in disk_usages.items():
            percent = int(usage.split("% ")[0])
            if percent > DISK_THRESHOLD:
                alerts.append(f"💾 **Disk almost full on {mount}**: {usage}")
        if ram_usage > RAM_THRESHOLD:
            alerts.append(f"🧠 **High RAM Usage**: {ram_usage}%")

        if alerts:
            message = "\n".join(alerts)
            if message != latest_alert:  # Only send if it's not the same alert
                asyncio.run(send_telegram_alert(message))

        time.sleep(CHECK_INTERVAL)

async def ack_command(update: Update, context: CallbackContext):
    global latest_alert
    if latest_alert:
        await update.message.reply_text(f"✅ The following alert has been acknowledged and will not be sent again: \n{latest_alert}")
        latest_alert = None
    else:
        await update.message.reply_text("🔹 No active alerts to acknowledge.")

async def status_command(update: Update, context: CallbackContext):
    status_message = get_system_status()
    await update.message.reply_text(status_message)

def get_system_status():
    cpu_usage = get_cpu_usage()
    cpu_temp = get_cpu_temp()
    disk_usages = get_disk_usage()
    ram_usage = get_ram_usage()
    docker_status = get_docker_status()
    
    disk_status = "\n".join([f"• {mount}: {usage}" for mount, usage in disk_usages.items()])
    
    status_message = (
        f"📊 **System Status**\n"
        f"• CPU Usage: {cpu_usage}%\n"
        f"• CPU Temperature: {cpu_temp if cpu_temp else 'N/A'}°C\n"
        f"• RAM Usage: {ram_usage}%\n"
        f"💾 **Disk Space**\n"
        f"{disk_status}\n\n"
        f"{docker_status}"
    )
    return status_message

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("ack", ack_command))
    
    threading.Thread(target=monitor_system, daemon=True).start()
    application.run_polling()

if __name__ == "__main__":
    main()
