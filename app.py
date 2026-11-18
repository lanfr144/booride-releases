# app.py
import json
import os
import re
import sys
from datetime import datetime, timezone

from config_loader import load_config

SERVICE = "booride"
APP_VERSION = "1.1.0"   # 1.0.0 + this logging feature (a compatible addition)


def mask_url(url):
    # postgresql://user:pass@host/db -> postgresql://user:****@host/db
    return re.sub(r"(://[^:]+:)[^@]+@", r"\1****@", url)


def log_event(level, message, **fields):
    """Write ONE log line in JSON on standard output.

    One JSON object per line (NDJSON) is the format Elasticsearch reads with
    its _bulk API. The field names are the ones of the logs-demo index of
    Unit 02: @timestamp, service, level, message. Never put a secret here.
    """
    record = {
        "@timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "service": SERVICE,
        "level": level,
        "message": message,
        "version": APP_VERSION,
        **fields,
    }
    print(json.dumps(record), flush=True)


def main():
    app_env = os.getenv("APP_ENV", "dev")
    try:
        cfg = load_config()
    except ValueError:
        # load_config() raises ValueError when APP_ENV is not one of the
        # environments of config.yaml. Any other error is a different problem
        # (missing file, broken YAML) and is not hidden here.
        log_event("ERROR", "app_start_failed", app_env=app_env, reason="unknown APP_ENV")
        print(f"APP_ENV={app_env} : value not known")
        sys.exit(1)

    # The single start-up log line: which environment, which mode, which
    # database (password masked).
    log_event("INFO", "app_started", app_env=app_env.lower(), debug=cfg["DEBUG"],
              db_url=mask_url(cfg["DB_URL"]))

    if cfg["DEBUG"]:
        print("[DEBUG MODE] Verbose logs enabled")
    else:
        print("[PRODUCTION MODE] Logging minimal")

    print(f"Connecting to DB: {mask_url(cfg['DB_URL'])}")
    # print(f"Using API key: {cfg['API_KEY'][:4]}... (masked)")


if __name__ == "__main__":
    main()
