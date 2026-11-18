# app.py
import os
import re
import sys

from config_loader import load_config


def mask_url(url):
    # postgresql://user:pass@host/db -> postgresql://user:****@host/db
    return re.sub(r"(://[^:]+:)[^@]+@", r"\1****@", url)


def main():
    try:
        cfg = load_config()
    except ValueError:
        # load_config() raises ValueError when APP_ENV is not one of the
        # environments of config.yaml. Any other error is a different problem
        # (missing file, broken YAML) and is not hidden here.
        app_env = os.getenv("APP_ENV", "dev")
        print(f"APP_ENV={app_env} : value not known", file=sys.stderr)
        sys.exit(1)

    if cfg["DEBUG"]:
        print("[DEBUG MODE] Verbose logs enabled")
    else:
        print("[PRODUCTION MODE] Logging minimal")

    print(f"Connecting to DB: {mask_url(cfg['DB_URL'])}")
    # print(f"Using API key: {cfg['API_KEY'][:4]}... (masked)")


if __name__ == "__main__":
    main()
