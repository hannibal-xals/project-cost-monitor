import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass
class Config:
    update_interval_hours: int = int(os.getenv("UPDATE_INTERVAL_HOURS", "6"))
    threshold_eur: float = float(os.getenv("THRESHOLD_EUR", "5"))
    output_file: str = os.getenv("OUTPUT_FILE", "/data/cost-status.json")
    state_file: str = os.getenv("STATE_FILE", "/data/alert-state.json")
    port: int = int(os.getenv("PORT", "8080"))

    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")

    use_mock_data: bool = env_bool("USE_MOCK_DATA", True)
    mock_oracle_eur: float = float(os.getenv("MOCK_ORACLE_EUR", "1.25"))
    mock_cloudflare_eur: float = float(os.getenv("MOCK_CLOUDFLARE_EUR", "0.80"))

    oracle_tenant_id: str = os.getenv("ORACLE_TENANT_ID", "")
    oracle_user_ocid: str = os.getenv("ORACLE_USER_OCID", "")
    oracle_fingerprint: str = os.getenv("ORACLE_FINGERPRINT", "")
    oracle_private_key_path: str = os.getenv("ORACLE_PRIVATE_KEY_PATH", "")
    oracle_region: str = os.getenv("ORACLE_REGION", "")

    cloudflare_api_token: str = os.getenv("CLOUDFLARE_API_TOKEN", "")
    cloudflare_account_id: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
