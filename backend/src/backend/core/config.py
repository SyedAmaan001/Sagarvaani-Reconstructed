"""
Sagarvani Reconstructed — Application Configuration
Environment settings, CORS rules, and feature flags.
"""

import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Sagarvani Reconstructed API"
    app_version: str = "0.1.0"
    environment: str = Field(default_factory=lambda: os.getenv("ENV", "development"))
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if o.strip()
        ]
    )
    enable_external_dispatch: bool = False
    enable_laya_selector: bool = Field(
        default_factory=lambda: os.getenv("ENABLE_LAYA_SELECTOR", "false").lower() in ("true", "1", "yes")
    )
    laya_model_checkpoint: str = Field(
        default_factory=lambda: os.getenv("LAYA_MODEL_CHECKPOINT", "convaiinnovations/laya")
    )
    laya_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("LAYA_TIMEOUT_SECONDS", "3.0"))
    )
    open_meteo_marine_base_url: str = Field(
        default_factory=lambda: os.getenv("OPEN_METEO_MARINE_BASE_URL", "https://marine-api.open-meteo.com/v1/marine")
    )
    open_meteo_weather_base_url: str = Field(
        default_factory=lambda: os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
    )
    gateway_timeout_seconds: float = 10.0
    gateway_max_retries: int = 2
    run_deadline_seconds: float = 30.0    # Overall wall-clock deadline for a query run
    max_task_concurrency: int = 4         # Maximum concurrent tasks in the harness
    artifacts_dir: str = Field(
        default_factory=lambda: os.getenv("ARTIFACTS_DIR", str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "artifacts"))))
    )
    sqlite_db_path: str = Field(
        default_factory=lambda: os.getenv("SQLITE_DB_PATH", str(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "sagarvani.db"))))
    )
    max_artifact_bytes: int = 5 * 1024 * 1024  # 5 MB maximum payload cap


settings = Settings()
