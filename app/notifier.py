from __future__ import annotations

import json
import os
from datetime import datetime, timezone
import requests


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"last_threshold_exceeded": False, "updated_at": _now_iso()}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_threshold_exceeded": False, "updated_at": _now_iso()}


def _write_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def notify_threshold_transition(slack_webhook_url: str, state_file: str, threshold_exceeded: bool, total_eur: float, threshold_eur: float) -> dict:
    state = _read_state(state_file)
    prev = bool(state.get("last_threshold_exceeded", False))

    event = "none"
    if threshold_exceeded and not prev:
        event = "exceeded"
    elif (not threshold_exceeded) and prev:
        event = "recovered"

    state["last_threshold_exceeded"] = threshold_exceeded
    state["updated_at"] = _now_iso()
    _write_state(state_file, state)

    if event == "none":
        return {"sent": False, "event": "none"}

    if not slack_webhook_url:
        return {"sent": False, "event": event, "error": "SLACK_WEBHOOK_URL missing"}

    if event == "exceeded":
        text = f":rotating_light: Cost alert: monthly total is {total_eur:.2f} EUR (threshold {threshold_eur:.2f} EUR)."
    else:
        text = f":white_check_mark: Cost recovered: monthly total is {total_eur:.2f} EUR (below threshold {threshold_eur:.2f} EUR)."

    try:
        resp = requests.post(slack_webhook_url, json={"text": text}, timeout=15)
        return {"sent": resp.status_code < 300, "event": event, "status_code": resp.status_code}
    except Exception as exc:
        return {"sent": False, "event": event, "error": str(exc)}
