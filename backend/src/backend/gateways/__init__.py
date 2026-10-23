"""
Sagarvani Reconstructed — Gateways Package
Exports Open-Meteo gateways and exceptions.
"""

from backend.gateways.exceptions import (
    GatewayError,
    GatewayHTTPStatusError,
    GatewayNetworkError,
    GatewaySchemaValidationError,
    GatewayTimeoutError,
)
from backend.gateways.open_meteo_marine import OpenMeteoMarineGateway
from backend.gateways.open_meteo_weather import OpenMeteoWeatherGateway

__all__ = [
    "GatewayError",
    "GatewayHTTPStatusError",
    "GatewayNetworkError",
    "GatewaySchemaValidationError",
    "GatewayTimeoutError",
    "OpenMeteoMarineGateway",
    "OpenMeteoWeatherGateway",
]
