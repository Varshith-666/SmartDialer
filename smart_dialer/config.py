"""SmartDialer Configuration Module."""

import os
from dataclasses import dataclass
from pathlib import Path


def _get_default_db_path() -> str:
    env_path = os.getenv("DB_PATH")
    if env_path:
        return env_path
    candidate = Path(__file__).resolve().parent.parent / "smart_dialer.db"
    if candidate.is_file():
        return str(candidate)
    return "smart_dialer.db"


@dataclass
class Settings:
    # Environment & Database
    ENV: str = os.getenv("SMART_DIALER_ENV", "development")
    DB_PATH: str = _get_default_db_path()
    DATASET_DIR: str = os.getenv(
        "DATASET_DIR", r"C:\Users\HP\Downloads\collections_30k_dataset (1)"
    )

    # Dialer Defaults
    DEFAULT_DIALER_MODE: str = os.getenv("DEFAULT_DIALER_MODE", "PROGRESSIVE")  # PROGRESSIVE or PREDICTIVE
    RESERVATION_TTL_SECONDS: int = int(os.getenv("RESERVATION_TTL_SECONDS", "30"))

    # Safety Controller Hard Thresholds
    MAX_OVERDIAL_RATIO: float = float(os.getenv("MAX_OVERDIAL_RATIO", "2.5"))
    MAX_ABANDON_RATE: float = float(os.getenv("MAX_ABANDON_RATE", "0.03"))  # 3% standard FCC compliance ceiling
    CIRCUIT_BREAKER_PROVIDER_ERROR_THRESHOLD: float = float(
        os.getenv("CIRCUIT_BREAKER_PROVIDER_ERROR_THRESHOLD", "0.15")  # 15% error rate trips circuit breaker
    )
    MIN_AVAILABLE_AGENTS_FOR_PREDICTIVE: int = int(
        os.getenv("MIN_AVAILABLE_AGENTS_FOR_PREDICTIVE", "2")
    )
    ANSWER_RATE_VOLATILITY_DROP_LIMIT: float = float(
        os.getenv("ANSWER_RATE_VOLATILITY_DROP_LIMIT", "0.25")  # >25% drop triggers safety downgrade
    )

    # Telephony Calibration
    CALL_SETUP_LATENCY_SECONDS: float = float(os.getenv("CALL_SETUP_LATENCY_SECONDS", "5.0"))
    DEFAULT_TALK_TIME_SECONDS: float = float(os.getenv("DEFAULT_TALK_TIME_SECONDS", "120.0"))
    DEFAULT_ANSWER_RATE: float = float(os.getenv("DEFAULT_ANSWER_RATE", "0.20"))  # Real dataset shows ~19.86%

    # Active Provider
    PROVIDER_TYPE: str = os.getenv("PROVIDER_TYPE", "reliable")  # "reliable" or "chaotic"
    PROVIDER_FAILURE_RATE: float = float(os.getenv("PROVIDER_FAILURE_RATE", "0.05"))
    PROVIDER_LATENCY_MIN_MS: int = int(os.getenv("PROVIDER_LATENCY_MIN_MS", "50"))
    PROVIDER_LATENCY_MAX_MS: int = int(os.getenv("PROVIDER_LATENCY_MAX_MS", "200"))


settings = Settings()
