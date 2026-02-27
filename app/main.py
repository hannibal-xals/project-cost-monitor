from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from flask import Flask, jsonify

from .config import Config
from .providers import get_oracle_monthly_cost_eur, get_cloudflare_monthly_cost_eur
from .notifier import notify_threshold_transition


config = Config()
app = Flask(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def collect_and_store() -> dict:
    oracle = get_oracle_monthly_cost_eur(config)
    cloudflare = get_cloudflare_monthly_cost_eur(config)

    total = round(oracle.cost_eur + cloudflare.cost_eur, 2)
    exceeded = total > config.threshold_eur

    output = {
        "provider_costs": {
            "oracle_eur": round(oracle.cost_eur, 2),
            "cloudflare_eur": round(cloudflare.cost_eur, 2),
        },
        "total_eur": total,
        "threshold_eur": config.threshold_eur,
        "threshold_exceeded": exceeded,
        "last_updated_at": _now_iso(),
        "source_health": {
            "oracle": oracle.health,
            "cloudflare": cloudflare.health,
        },
    }

    os.makedirs(os.path.dirname(config.output_file), exist_ok=True)
    with open(config.output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    notify_threshold_transition(
        slack_webhook_url=config.slack_webhook_url,
        state_file=config.state_file,
        threshold_exceeded=exceeded,
        total_eur=total,
        threshold_eur=config.threshold_eur,
    )

    return output


def scheduler_loop() -> None:
    interval_seconds = max(config.update_interval_hours, 1) * 3600
    while True:
        collect_and_store()
        time.sleep(interval_seconds)


@app.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok", "time": _now_iso()}), 200


@app.route("/cost-status", methods=["GET"])
def cost_status() -> tuple:
    if not os.path.exists(config.output_file):
        data = collect_and_store()
        return jsonify(data), 200

    with open(config.output_file, "r", encoding="utf-8") as f:
        return app.response_class(response=f.read(), mimetype="application/json")


if __name__ == "__main__":
    collect_and_store()  # startup refresh
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=config.port)
