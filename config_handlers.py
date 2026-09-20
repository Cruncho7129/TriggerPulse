import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path("config.json")

def load_config() -> Dict[str, Any]:
    """
    Load the JSON config file if it exists.
    Ensures each rule has defaults for missing fields.
    """
    if not CONFIG_FILE.exists():
        return {
            "serial_port": "",
            "monitor_index": 1,
            "rules": []
        }

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[config_handlers] Failed to read config: {e}")
        data = {
            "serial_port": "",
            "monitor_index": 1,
            "rules": []
        }

    # Ensure top-level keys
    data.setdefault("serial_port", "")
    data.setdefault("monitor_index", 1)
    data.setdefault("rules", [])

    # Ensure each rule has defaults
    for rule in data["rules"]:
        rule.setdefault("threshold", 0.9)
        rule.setdefault("detect_time", 0)
        rule.setdefault("cooldown", 0)
        rule.setdefault("actions", [])

        # Add missing 'failure' defaults
        if "failure" not in rule:
            rule["failure"] = {
                "max_retries": 0,
                "retry_delay_ms": 0,
                "skip_actions": []
            }
        else:
            rule["failure"].setdefault("max_retries", 0)
            rule["failure"].setdefault("retry_delay_ms", 0)
            rule["failure"].setdefault("skip_actions", [])

    return data


def save_config(config: Dict[str, Any]):
    """
    Write the config dict to config.json.
    Keeps missing rules so user can re-add screenshots later.
    """
    # Ensure types
    config["monitor_index"] = int(config.get("monitor_index", 1))
    config["serial_port"] = str(config.get("serial_port", ""))

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[config_handlers] Failed to save config: {e}")
