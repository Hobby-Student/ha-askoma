"""The Askoheat integration."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import AskoheatApiClient, AskoheatConnectionError
from .const import (
    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN,
    HEARTBEAT_INTERVAL, EMA_LOAD_SETPOINT_VALUE,
)
from .coordinator import AskoheatEmaCoordinator, AskoheatSlowCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]


@dataclass
class AskoheatData:
    """Runtime data for the Askoheat integration."""
    client: AskoheatApiClient
    ema_coordinator: AskoheatEmaCoordinator
    slow_coordinator: AskoheatSlowCoordinator
    par_data: dict[str, Any]
    connected_sensors: list[int]
    heartbeat_task: asyncio.Task | None = None
    last_setpoint: int = 0


type AskoheatConfigEntry = ConfigEntry[AskoheatData]


async def async_setup_entry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> bool:
    """Set up Askoheat from a config entry."""
    host = entry.data[CONF_HOST]
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    # Create dedicated session with keep-alive disabled (device quirk: stale connections cause EOF)
    connector = aiohttp.TCPConnector(force_close=True)
    session = aiohttp.ClientSession(
        connector=connector, timeout=aiohttp.ClientTimeout(total=5)
    )
    client = AskoheatApiClient(host=host, session=session)

    try:
        par_data = await client.get_par()
        connected_sensors = await client.detect_connected_sensors()
    except AskoheatConnectionError as err:
        await session.close()
        raise ConfigEntryNotReady(f"Cannot connect to Askoheat at {host}") from err

    # Warn if load setpoint is not enabled in device settings
    if entry.data.get("setpoint_warning"):
        _LOGGER.warning(
            "Askoheat at %s: Load Setpoint input is not enabled in the device's "
            "web interface Input Settings. External control may not work until enabled",
            host,
        )

    ema_coordinator = AskoheatEmaCoordinator(
        hass=hass, client=client, update_interval=timedelta(seconds=scan_interval),
    )
    slow_coordinator = AskoheatSlowCoordinator(hass=hass, client=client)

    await ema_coordinator.async_config_entry_first_refresh()
    await slow_coordinator.async_config_entry_first_refresh()

    runtime_data = AskoheatData(
        client=client,
        ema_coordinator=ema_coordinator,
        slow_coordinator=slow_coordinator,
        par_data=par_data,
        connected_sensors=connected_sensors,
    )

    runtime_data.heartbeat_task = entry.async_create_background_task(
        hass, _heartbeat_loop(runtime_data), name="askoheat_heartbeat",
    )

    entry.runtime_data = runtime_data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    return True


async def _heartbeat_loop(data: AskoheatData) -> None:
    """Re-send setpoint every 30s to prevent device timeout."""
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        if data.last_setpoint > 0:
            try:
                await data.client.patch_ema(
                    {EMA_LOAD_SETPOINT_VALUE: str(data.last_setpoint)}
                )
            except Exception:
                _LOGGER.warning("Heartbeat failed for Askoheat")


async def _async_update_options(hass: HomeAssistant, entry: AskoheatConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> bool:
    if entry.runtime_data.heartbeat_task:
        entry.runtime_data.heartbeat_task.cancel()
    await entry.runtime_data.client.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
