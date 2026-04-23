"""
System Health Monitor & Alerter v1.0
Discord Webhook + File Logging + Colorama Console Output
"""

import os
import time
import socket
import logging
import psutil
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

load_dotenv()

CONFIG = {
    "WEBHOOK_URL":             os.getenv("DISCORD_WEBHOOK_URL"),
    "CHECK_INTERVAL_SECONDS":  int(os.getenv("CHECK_INTERVAL", 30)),
    "ALERT_COOLDOWN_SECONDS":  int(os.getenv("ALERT_COOLDOWN", 300)),
    "DISK_PATH":               os.getenv("DISK_PATH", "/"),
    "THRESHOLDS": {
        "cpu":  float(os.getenv("THRESHOLD_CPU",  80)),
        "ram":  float(os.getenv("THRESHOLD_RAM",  80)),
        "disk": float(os.getenv("THRESHOLD_DISK", 90)),
        "temp": float(os.getenv("THRESHOLD_TEMP", 85)),
    },
    "LOG_FILE":        os.getenv("LOG_FILE",   "system_logs.txt"),
    "LOG_LEVEL":       os.getenv("LOG_LEVEL",  "INFO"),
    "ALERT_COLOR":     int(os.getenv("ALERT_COLOR", "0xFF4444"), 16),
    "EMBED_FOOTER":    os.getenv("EMBED_FOOTER", ""),
    "DISCORD_USERNAME": os.getenv("DISCORD_USERNAME", "System Monitor"),
}

logging.basicConfig(
    level=getattr(logging, CONFIG["LOG_LEVEL"], logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(CONFIG["LOG_FILE"], encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def color_value(value: float, threshold: float) -> str:
    if not COLORAMA_AVAILABLE:
        return f"{value:.1f}%"
    if value >= threshold:
        return f"{Fore.RED}{Style.BRIGHT}{value:.1f}%{Style.RESET_ALL}"
    elif value >= threshold * 0.85:
        return f"{Fore.YELLOW}{value:.1f}%{Style.RESET_ALL}"
    else:
        return f"{Fore.GREEN}{value:.1f}%{Style.RESET_ALL}"


def print_banner():
    separator = "=" * 54
    label = f"  System Health Monitor  |  {datetime.now().strftime('%H:%M:%S')}"
    if COLORAMA_AVAILABLE:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{separator}")
        print(label)
        print(f"{separator}{Style.RESET_ALL}")
    else:
        print(f"\n{separator}")
        print(label)
        print(separator)


def get_metrics() -> dict:
    metrics = {}

    try:
        metrics["cpu"] = psutil.cpu_percent(interval=1)
    except Exception as e:
        logger.warning(f"Could not read CPU usage: {e}")
        metrics["cpu"] = None

    try:
        ram = psutil.virtual_memory()
        metrics["ram"]          = ram.percent
        metrics["ram_used_gb"]  = ram.used  / (1024 ** 3)
        metrics["ram_total_gb"] = ram.total / (1024 ** 3)
    except Exception as e:
        logger.warning(f"Could not read RAM usage: {e}")
        metrics["ram"] = None

    try:
        disk = psutil.disk_usage(CONFIG["DISK_PATH"])
        metrics["disk"]          = disk.percent
        metrics["disk_free_gb"]  = disk.free  / (1024 ** 3)
        metrics["disk_total_gb"] = disk.total / (1024 ** 3)
    except Exception as e:
        logger.warning(f"Could not read disk usage: {e}")
        metrics["disk"] = None

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            first_sensor = next(iter(temps.values()))
            metrics["temp"] = first_sensor[0].current
        else:
            metrics["temp"] = None
    except (AttributeError, Exception):
        metrics["temp"] = None

    metrics["hostname"] = socket.gethostname()
    return metrics


def build_embed(alerts: list[dict], metrics: dict) -> dict:
    hostname  = metrics.get("hostname", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    footer    = CONFIG["EMBED_FOOTER"] or f"System Health Monitor | {hostname}"

    fields = []
    for alert in alerts:
        fields.append({
            "name": alert["label"],
            "value": (
                f"**Current:** `{alert['current']:.1f}%`\n"
                f"**Threshold:** `{alert['threshold']:.0f}%`\n"
                f"**Status:** {alert['status']}"
            ),
            "inline": True,
        })

    return {
        "title": "System Alert",
        "description": (
            f"Critical values detected on **`{hostname}`**.\n"
            f"Please review the system immediately."
        ),
        "color":  CONFIG["ALERT_COLOR"],
        "fields": fields,
        "footer": {"text": footer},
        "timestamp": timestamp,
    }


def send_discord_alert(alerts: list[dict], metrics: dict) -> bool:
    webhook_url = CONFIG["WEBHOOK_URL"]

    if not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL is not set in .env — skipping alert.")
        return False

    payload = {
        "username": CONFIG["DISCORD_USERNAME"],
        "embeds":   [build_embed(alerts, metrics)],
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Discord alert sent successfully ({len(alerts)} alert(s)).")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord alert: {e}")
        return False


_last_alert_times: dict[str, float] = {}


def should_alert(key: str) -> bool:
    return (time.time() - _last_alert_times.get(key, 0)) >= CONFIG["ALERT_COOLDOWN_SECONDS"]


def mark_alerted(key: str):
    _last_alert_times[key] = time.time()


def print_metrics(metrics: dict):
    thresholds = CONFIG["THRESHOLDS"]
    hostname   = metrics.get("hostname", "unknown")

    print_banner()
    print(f"  Hostname : {hostname}")

    if metrics["cpu"] is not None:
        print(f"  CPU      : {color_value(metrics['cpu'], thresholds['cpu'])}")
    else:
        print("  CPU      : N/A")

    if metrics["ram"] is not None:
        print(
            f"  RAM      : {color_value(metrics['ram'], thresholds['ram'])}"
            f"  ({metrics.get('ram_used_gb', 0):.1f} / {metrics.get('ram_total_gb', 0):.1f} GB)"
        )
    else:
        print("  RAM      : N/A")

    if metrics["disk"] is not None:
        print(
            f"  Disk     : {color_value(metrics['disk'], thresholds['disk'])}"
            f"  ({metrics.get('disk_free_gb', 0):.1f} GB free)"
        )
    else:
        print("  Disk     : N/A")

    if metrics.get("temp") is not None:
        print(f"  Temp     : {color_value(metrics['temp'], thresholds['temp'])}")
    else:
        print("  Temp     : Not supported on this platform")

    print()


def check_and_alert(metrics: dict):
    thresholds     = CONFIG["THRESHOLDS"]
    pending_alerts = []

    checks = [
        ("cpu",  "CPU Usage",       metrics.get("cpu")),
        ("ram",  "RAM Usage",       metrics.get("ram")),
        ("disk", "Disk Usage",      metrics.get("disk")),
        ("temp", "CPU Temperature", metrics.get("temp")),
    ]

    for key, label, value in checks:
        if value is None:
            continue
        threshold = thresholds[key]
        if value >= threshold and should_alert(key):
            pending_alerts.append({
                "key":       key,
                "label":     label,
                "current":   value,
                "threshold": threshold,
                "status":    "CRITICAL",
            })
            mark_alerted(key)
            logger.warning(
                f"ALERT | {label}: {value:.1f}% "
                f"(threshold: {threshold:.0f}%) | "
                f"host: {metrics['hostname']}"
            )

    if pending_alerts:
        send_discord_alert(pending_alerts, metrics)
    else:
        logger.info(
            f"OK | "
            f"CPU: {metrics.get('cpu', 'N/A'):.1f}%  "
            f"RAM: {metrics.get('ram', 'N/A'):.1f}%  "
            f"Disk: {metrics.get('disk', 'N/A'):.1f}%"
        )


def run():
    logger.info("System Health Monitor started.")
    logger.info(
        f"Interval: {CONFIG['CHECK_INTERVAL_SECONDS']}s | "
        f"Cooldown: {CONFIG['ALERT_COOLDOWN_SECONDS']}s | "
        f"Disk path: {CONFIG['DISK_PATH']}"
    )

    while True:
        try:
            metrics = get_metrics()
            print_metrics(metrics)
            check_and_alert(metrics)
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)

        time.sleep(CONFIG["CHECK_INTERVAL_SECONDS"])


if __name__ == "__main__":
    run()