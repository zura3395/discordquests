import os
import re
import sys
import time
from datetime import datetime
from typing import Optional

import requests
from getpass import getpass


DISCORD_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9210 "
    "Chrome/134.0.6998.205 Electron/35.3.0 Safari/537.36"
)


def extract_quest_id(value: str) -> str:
    """Return quest ID from a plain ID or a Discord quest URL/path.

    Accepts either:
      - a numeric/alphanumeric ID, e.g. "123456..."
      - a full URL like https://discord.com/quests/<id>/...
      - a path-like value containing slashes and ending with the ID
    """
    value = value.strip()
    if "/" in value:
        # Try to find .../quests/<id>(/|\b)
        m = re.search(r"/quests/([^/?#]+)", value)
        if m:
            return m.group(1)
        # Fallback: take the last non-empty segment
        parts = [p for p in value.split('/') if p]
        if parts:
            return parts[-1]
    return value


def build_headers(authorization: str, x_super_properties: str) -> dict:
    return {
        "authorization": authorization,
        "content-type": "application/json",
        "x-super-properties": x_super_properties,
        "user-agent": DISCORD_UA,
        # These additional headers commonly appear in browser requests
        "origin": "https://discord.com",
        "referer": "https://discord.com",
    }


def send_heartbeat_once(session: requests.Session, url: str, body: dict) -> tuple[int, Optional[dict], Optional[str]]:
    """Send a single heartbeat. Returns (status, json_or_none, text_or_none)."""
    try:
        resp = session.post(url, json=body, timeout=20)
    except requests.RequestException as e:
        return 0, None, f"Request error: {e}"

    status = resp.status_code
    # Some endpoints may respond 204 No Content; handle gracefully
    content_type = resp.headers.get("content-type", "")
    if status == 204 or not resp.content:
        return status, None, None

    if "application/json" in content_type.lower():
        try:
            return status, resp.json(), None
        except ValueError:
            # Not valid JSON though claimed; fall back to text
            return status, None, resp.text
    else:
        return status, None, resp.text


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def prompt_value(label: str, env_key: str, *, required: bool = True, secret: bool = False) -> str:
    env_default = os.getenv(env_key)
    if env_default:
        return env_default.strip()

    while True:
        if secret and env_default:
            prompt = f"{label} (press Enter to use value from {env_key}): "
        elif env_default:
            prompt = f"{label} [{env_default}]: "
        else:
            prompt = f"{label}: "

        raw = getpass(prompt) if secret else input(prompt)
        value = raw.strip()

        if value:
            return value
        if env_default:
            return env_default.strip()
        if not required:
            return ""
        print("This value is required. Please enter a value.")


def prompt_interval(env_key: str, default: float = 30.0) -> float:
    env_val = os.getenv(env_key)
    if env_val:
        try:
            value = float(env_val)
            if value <= 0:
                raise ValueError
            return max(0.5, value)
        except ValueError:
            print(f"Warning: environment variable {env_key}='{env_val}' is not a positive number. Using {default}.")
            return max(0.5, default)

    while True:
        raw = input(f"Seconds between heartbeats [{default}]: ").strip()
        if not raw:
            return max(0.5, default)
        try:
            value = float(raw)
            if value <= 0:
                raise ValueError
            return max(0.5, value)
        except ValueError:
            print("Please enter a positive number.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        raw = input(question + suffix).strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please answer with 'y' or 'n'.")


def gather_inputs() -> tuple[str, str, str, str, str, float, bool]:
    print("Enter the details for your Discord quest heartbeat. Environment variables (DQ_*) will be used as defaults when available.\n")

    quest = prompt_value("Quest ID or URL", "DQ_QUEST_ID")
    voice_channel_id = prompt_value("Voice Channel ID", "DQ_VOICE_CHANNEL_ID")
    user_id = prompt_value("User ID", "DQ_USER_ID")
    authorization = prompt_value("Authorization header", "DQ_AUTHORIZATION", secret=True)
    x_super_properties = prompt_value("x-super-properties header", "DQ_X_SUPER_PROPERTIES", secret=True)
    interval = prompt_interval("DQ_INTERVAL", default=30.0)
    send_once = prompt_yes_no("Send only one heartbeat and exit?", default=False)

    return quest, voice_channel_id, user_id, authorization, x_super_properties, interval, send_once


DEFAULT_ENV_FILE = ".env"


def load_env_file(path: str = DEFAULT_ENV_FILE) -> None:
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        return
    with open(abs_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            val = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


def main() -> int:
    load_env_file()
    quest, voice_channel_id, user_id, authorization, x_super_properties, interval, send_once = gather_inputs()

    quest_id = extract_quest_id(quest)
    url = f"https://discord.com/api/v9/quests/{quest_id}/heartbeat"

    headers = build_headers(authorization.strip(), x_super_properties.strip())
    body = {
        "stream_key": f"call:{voice_channel_id.strip()}:{user_id.strip()}",
        "terminal": False,
    }

    session = requests.Session()
    session.headers.update(headers)

    def do_send():
        status, j, t = send_heartbeat_once(session, url, body)
        if status == 0:
            print(f"[{now()}] Heartbeat error: {t}")
            return False
        if 200 <= status < 300:
            print(f"[{now()}] Heartbeat OK (status {status}).")
        else:
            print(f"[{now()}] Heartbeat failed (status {status}).")
        # Print a compact response preview
        if j is not None:
            try:
                import json as _json

                snippet = _json.dumps(j)[:500]
            except Exception:
                snippet = str(j)[:500]
            print(f"[{now()}] Response JSON: {snippet}")
        elif t:
            snippet = t.replace("\n", " ")[:500]
            print(f"[{now()}] Response text: {snippet}")
        return 200 <= status < 300

    if send_once:
        ok = do_send()
        return 0 if ok else 1

    print(
        f"Starting heartbeat loop for quest {quest_id} every {interval} seconds. Press Ctrl+C to stop."
    )
    try:
        while True:
            do_send()
            time.sleep(max(0.5, interval))
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
