"""Diagnostics support for Askoheat integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import AskoheatConfigEntry

TO_REDACT = {"MODBUS_PAR_ID", "MODBUS_EMA_ID", "DEVICEID", "host"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AskoheatConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data

    try:
        all_data = await data.client.get_all()
    except Exception:
        all_data = {"error": "Failed to fetch GETALL.JSON"}

    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "entry_options": dict(entry.options),
        "device_parameters": async_redact_data(data.par_data, TO_REDACT),
        "connected_sensors": data.connected_sensors,
        "ema_data": async_redact_data(
            data.ema_coordinator.data or {}, TO_REDACT
        ),
        "slow_data": async_redact_data(
            data.slow_coordinator.data or {}, TO_REDACT
        ),
        "heartbeat": {
            "active": data.last_setpoint > 0,
            "last_setpoint": data.last_setpoint,
        },
        "full_dump": async_redact_data(all_data, TO_REDACT),
    }
