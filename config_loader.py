# load_config() selects the configuration of one environment.
#
# config.yaml holds the structure (which environments, DEBUG on or off) and
# refers to the secrets by name: DB_URL: "${DEV_DB_URL}".
# The values come from the .env file next to this script, or from real
# environment variables, which win over .env (that is how a server or a
# pipeline injects its own secrets). Nothing secret is stored in config.yaml.
import os
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
DEFAULT_CONFIG = HERE / "config.yaml"
DEFAULT_ENV_FILE = HERE / ".env"

_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def load_env_file(path=DEFAULT_ENV_FILE):
    """Read KEY=value lines of .env into os.environ.

    A variable that already exists in the environment is kept as it is.
    Empty lines and lines starting with # are ignored; quotes around a value
    are removed. A missing .env is not an error: the variables may all come
    from the real environment.
    """
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _expand(value, env_name):
    """Replace every ${NAME} of a string by the value of the variable NAME."""
    if not isinstance(value, str):
        return value

    def replace(match):
        name = match.group(1)
        if name not in os.environ:
            raise KeyError(
                f"{name} is not defined (needed by environment '{env_name}'): "
                f"add it to .env, see .env.example"
            )
        return os.environ[name]

    return _PLACEHOLDER.sub(replace, value)


def load_config(path=DEFAULT_CONFIG, env_file=DEFAULT_ENV_FILE):
    load_env_file(env_file)
    env = os.getenv("APP_ENV", "dev").lower()  # default to dev

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Environments live under "environments:" (fallback: top level).
    configs = data.get("environments", data)

    if env not in configs:
        raise ValueError(
            f"Invalid APP_ENV: {env}. Choose from {list(configs.keys())}"
        )

    # Only the selected environment is expanded: running in dev does not
    # require the production secrets to be present.
    config = {key: _expand(value, env) for key, value in configs[env].items()}

    # Normalize types (DEBUG must be a boolean).
    if isinstance(config.get("DEBUG"), str):
        config["DEBUG"] = config["DEBUG"].lower() == "true"

    return config


if __name__ == "__main__":
    cfg = load_config()
    print("Loaded environment:", os.getenv("APP_ENV", "dev"))
    print("DEBUG =", cfg["DEBUG"])
    print("DB_URL and API_KEY loaded:", bool(cfg["DB_URL"]) and bool(cfg["API_KEY"]))
