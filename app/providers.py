from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any
import requests

from .config import Config


@dataclass
class ProviderResult:
    cost_eur: float
    health: Dict[str, Any]


def _now_iso() -> str:
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')


def get_oracle_monthly_cost_eur(config: Config) -> ProviderResult:
    if config.use_mock_data:
        return ProviderResult(
            cost_eur=config.mock_oracle_eur,
            health={"status": "mock", "message": "Using mock Oracle cost", "checked_at": _now_iso()},
        )

    required = [
        config.oracle_tenant_id,
        config.oracle_user_ocid,
        config.oracle_fingerprint,
        config.oracle_private_key_path,
        config.oracle_region,
    ]
    if not all(required):
        return ProviderResult(
            cost_eur=0.0,
            health={
                "status": "error",
                "message": "Oracle credentials missing (tenant/user/fingerprint/key/region)",
                "checked_at": _now_iso(),
            },
        )

    try:
        import oci

        oci_cfg = {
            "user": config.oracle_user_ocid,
            "fingerprint": config.oracle_fingerprint,
            "tenancy": config.oracle_tenant_id,
            "region": config.oracle_region,
            "key_file": config.oracle_private_key_path,
        }

        usage_client = oci.usage_api.UsageapiClient(oci_cfg)

        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        details = oci.usage_api.models.RequestSummarizedUsagesDetails(
            tenant_id=config.oracle_tenant_id,
            time_usage_started=month_start,
            time_usage_ended=month_end,
            granularity="MONTHLY",
            query_type="COST",
        )

        resp = usage_client.request_summarized_usages(details)
        items = getattr(resp.data, "items", []) or []

        total = 0.0
        for item in items:
            cost = getattr(item, "computed_amount", None)
            unit = str(getattr(item, "computed_amount_unit", "")).upper()
            if cost is None:
                continue
            # We only add native EUR amounts in MVP.
            if "EUR" in unit or unit == "":
                total += float(cost)

        return ProviderResult(
            cost_eur=round(total, 2),
            health={"status": "ok", "message": "Oracle live API", "checked_at": _now_iso()},
        )
    except Exception as exc:
        return ProviderResult(
            cost_eur=0.0,
            health={
                "status": "error",
                "message": f"Oracle request failed: {exc}",
                "checked_at": _now_iso(),
            },
        )


def get_cloudflare_monthly_cost_eur(config: Config) -> ProviderResult:
    if config.use_mock_data:
        return ProviderResult(
            cost_eur=config.mock_cloudflare_eur,
            health={"status": "mock", "message": "Using mock Cloudflare cost", "checked_at": _now_iso()},
        )

    if not config.cloudflare_api_token:
        return ProviderResult(
            cost_eur=0.0,
            health={"status": "error", "message": "Cloudflare API token missing", "checked_at": _now_iso()},
        )

    url = "https://api.cloudflare.com/client/v4/user/billing/history"
    headers = {
        "Authorization": f"Bearer {config.cloudflare_api_token}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code != 200:
            return ProviderResult(
                cost_eur=0.0,
                health={
                    "status": "error",
                    "message": f"Cloudflare API HTTP {resp.status_code}",
                    "checked_at": _now_iso(),
                },
            )

        payload = resp.json()
        if not payload.get("success"):
            return ProviderResult(
                cost_eur=0.0,
                health={
                    "status": "error",
                    "message": "Cloudflare API response success=false",
                    "checked_at": _now_iso(),
                },
            )

        total = 0.0
        for entry in payload.get("result", []):
            amount = float(entry.get("amount", 0) or 0)
            currency = str(entry.get("currency", "USD")).upper()
            if currency == "EUR":
                total += amount
            else:
                # MVP assumption: non-EUR ignored unless a conversion service is added.
                pass

        return ProviderResult(
            cost_eur=round(total, 2),
            health={"status": "ok", "message": "Cloudflare live API", "checked_at": _now_iso()},
        )
    except Exception as exc:
        return ProviderResult(
            cost_eur=0.0,
            health={"status": "error", "message": f"Cloudflare request failed: {exc}", "checked_at": _now_iso()},
        )
