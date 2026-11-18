# Exercise 2: load_config() selects the configuration of one environment.
#
# Fix 2026-10-26: config.yaml groups the environments under a top-level key
#     environments:
#       dev: ...
#       staging: ...
#       prod: ...
# The first version looked for "dev" at the top level, found only
# "environments", and raised ValueError for EVERY environment
# ("Invalid APP_ENV: dev. Choose from ['environments']").
# The loader now reads the "environments" section (and still accepts a file
# where dev/staging/prod are at the top level).
import os
from pathlib import Path

import yaml

# Resolve config.yaml next to this file, so the app works from any directory.
DEFAULT_CONFIG = Path(__file__).with_name("config.yaml")


def load_config(path=DEFAULT_CONFIG):
    env = os.getenv("APP_ENV", "dev").lower()  # default to dev

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Environments live under "environments:" (fallback: top level).
    configs = data.get("environments", data)

    if env not in configs:
        raise ValueError(
            f"Invalid APP_ENV: {env}. Choose from {list(configs.keys())}"
        )

    config = configs[env]

    # Normalize types (DEBUG must be a boolean). YAML already turns true/false
    # into booleans; a quoted value ("true") or an env variable is a string.
    if isinstance(config.get("DEBUG"), str):
        config["DEBUG"] = config["DEBUG"].lower() == "true"

    return config


if __name__ == "__main__":
    cfg = load_config()
    print("Loaded environment:", os.getenv("APP_ENV", "dev"))
    print("DB_URL =", cfg["DB_URL"])
    print("API_KEY =", cfg["API_KEY"])
    print("DEBUG =", cfg["DEBUG"])
