"""
Sagarvani Reconstructed — Open-Meteo Weather Gateway
Fetches wind speed at 10m, wind direction at 10m, and wind gusts at 10m.
Normalizes data into canonical EvidenceRecord schemas.
"""

from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Dict, List, Optional
import httpx

from backend.core.config import settings
from backend.gateways.exceptions import (
    GatewayHTTPStatusError,
    GatewayNetworkError,
    GatewaySchemaValidationError,
    GatewayTimeoutError,
)
from backend.models.enums import DataMode
from backend.models.evidence import EvidenceRecord, GeoLocation


class OpenMeteoWeatherGateway:
    """Gateway for Open-Meteo Atmospheric Weather API."""

    PROVIDER_NAME = "Open-Meteo Weather API"
    SOURCE_ID = "open_meteo_weather"
    PRODUCT_ID = "weather_wind_forecast"
    DOCS_URL = "https://open-meteo.com/en/docs"
    ATTRIBUTION = "Atmospheric weather data by Open-Meteo.com under CC BY 4.0. Free non-commercial use."

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        http_client: Optional[httpx.Client] = None,
    ):
        self.base_url = base_url or settings.open_meteo_weather_base_url
        self.timeout = timeout or settings.gateway_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.gateway_max_retries
        self._external_client = http_client

    def fetch_weather_forecast(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 2,
    ) -> Dict[str, Any]:
        """
        Query Open-Meteo Weather API with bounded retries for transient failures.
        Returns raw validated JSON response dictionary.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m",
            "timezone": "UTC",
            "forecast_days": forecast_days,
        }

        retries = 0
        last_error: Optional[Exception] = None

        while retries <= self.max_retries:
            try:
                if self._external_client:
                    resp = self._external_client.get(self.base_url, params=params, timeout=self.timeout)
                else:
                    with httpx.Client(timeout=self.timeout) as client:
                        resp = client.get(self.base_url, params=params)

                if resp.status_code >= 400:
                    raise GatewayHTTPStatusError(
                        resp.text[:200], self.PROVIDER_NAME, resp.status_code
                    )

                try:
                    data = resp.json()
                except Exception as e:
                    raise GatewaySchemaValidationError(
                        f"Response is not valid JSON: {str(e)}", self.PROVIDER_NAME
                    )

                return data

            except httpx.TimeoutException as e:
                last_error = GatewayTimeoutError(f"Request timed out: {str(e)}", self.PROVIDER_NAME)
            except httpx.NetworkError as e:
                last_error = GatewayNetworkError(f"Network error: {str(e)}", self.PROVIDER_NAME)
            except GatewayHTTPStatusError as e:
                if 400 <= e.status_code < 500:
                    raise e
                last_error = e

            retries += 1
            if retries <= self.max_retries:
                time.sleep(0.2 * (2 ** (retries - 1)))

        if last_error:
            raise last_error
        raise GatewayNetworkError("Unknown failure during weather forecast fetch", self.PROVIDER_NAME)

    def parse_and_normalize(
        self,
        raw_payload: Dict[str, Any],
        requested_lat: float,
        requested_lon: float,
        retrieved_at: Optional[datetime] = None,
        data_mode: DataMode = DataMode.LIVE_FORECAST,
        target_timestamp: Optional[datetime] = None,
    ) -> List[EvidenceRecord]:
        """
        Validates raw response and normalizes into typed EvidenceRecords.
        Picks the forecast slot matching target_timestamp, or the earliest/current slot.
        """
        retrieved_at = retrieved_at or datetime.now(timezone.utc)

        if not isinstance(raw_payload, dict):
            raise GatewaySchemaValidationError("Payload must be a dictionary", self.PROVIDER_NAME)

        hourly = raw_payload.get("hourly")
        hourly_units = raw_payload.get("hourly_units", {})
        if not hourly or not isinstance(hourly, dict):
            raise GatewaySchemaValidationError("Missing 'hourly' data section", self.PROVIDER_NAME)

        times = hourly.get("time")
        wind_speeds = hourly.get("wind_speed_10m")
        wind_directions = hourly.get("wind_direction_10m")
        wind_gusts = hourly.get("wind_gusts_10m")

        if not isinstance(times, list) or len(times) == 0:
            raise GatewaySchemaValidationError("Missing or empty 'time' array", self.PROVIDER_NAME)

        n = len(times)
        for var_name, var_arr in [
            ("wind_speed_10m", wind_speeds),
            ("wind_direction_10m", wind_directions),
            ("wind_gusts_10m", wind_gusts),
        ]:
            if not isinstance(var_arr, list) or len(var_arr) != n:
                raise GatewaySchemaValidationError(
                    f"Array length mismatch for '{var_name}': expected {n}, got {len(var_arr) if isinstance(var_arr, list) else 'non-list'}",
                    self.PROVIDER_NAME,
                )

        # Provider resolved coordinates
        grid_lat = raw_payload.get("latitude", requested_lat)
        grid_lon = raw_payload.get("longitude", requested_lon)

        quality_flags: List[str] = []
        if round(grid_lat, 2) != round(requested_lat, 2) or round(grid_lon, 2) != round(requested_lon, 2):
            quality_flags.append(f"GRID_OFFSET: requested ({requested_lat:.2f}, {requested_lon:.2f}) -> model grid ({grid_lat:.2f}, {grid_lon:.2f})")

        # Determine target index
        selected_index = 0
        if target_timestamp:
            target_iso = target_timestamp.strftime("%Y-%m-%dT%H:00")
            for idx, t_str in enumerate(times):
                if t_str.startswith(target_iso):
                    selected_index = idx
                    break

        selected_time_str = times[selected_index]
        try:
            valid_time = datetime.fromisoformat(selected_time_str).replace(tzinfo=timezone.utc)
        except Exception as e:
            raise GatewaySchemaValidationError(f"Invalid timestamp format '{selected_time_str}': {str(e)}", self.PROVIDER_NAME)

        records: List[EvidenceRecord] = []
        location = GeoLocation(lat=grid_lat, lon=grid_lon)

        variables = [
            ("wind_speed_10m", wind_speeds[selected_index], hourly_units.get("wind_speed_10m", "km/h")),
            ("wind_direction_10m", wind_directions[selected_index], hourly_units.get("wind_direction_10m", "°")),
            ("wind_gusts_10m", wind_gusts[selected_index], hourly_units.get("wind_gusts_10m", "km/h")),
        ]

        for param_name, param_val, param_unit in variables:
            ev_hash = hashlib.sha256(
                f"{self.SOURCE_ID}:{param_name}:{grid_lat}:{grid_lon}:{selected_time_str}".encode("utf-8")
            ).hexdigest()[:12]

            var_flags = list(quality_flags)
            if param_val is None:
                var_flags.append("NULL_VALUE")

            records.append(
                EvidenceRecord(
                    evidence_id=f"ev_ow_{ev_hash}",
                    source_id=self.SOURCE_ID,
                    source_name=self.PROVIDER_NAME,
                    product_id=self.PRODUCT_ID,
                    parameter=param_name,
                    value=param_val if param_val is not None else "UNAVAILABLE",
                    unit=param_unit,
                    location=location,
                    observed_at=None,
                    issued_at=None,
                    model_run_at=None,
                    valid_from=valid_time,
                    valid_to=None,
                    retrieved_at=retrieved_at,
                    data_mode=data_mode,
                    quality_flags=var_flags,
                    lineage_parent_ids=[],
                    source_url=self.DOCS_URL,
                    attribution=self.ATTRIBUTION,
                    schema_version="v1.0",
                )
            )

        return records
