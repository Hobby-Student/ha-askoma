"""Data update coordinators for Askoheat integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AskoheatApiClient, AskoheatConnectionError
from .const import SLOW_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AskoheatEmaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fast-polling EMA data (temperatures, power, status)."""

    def __init__(self, hass: HomeAssistant, client: AskoheatApiClient, update_interval: timedelta) -> None:
        super().__init__(hass, _LOGGER, name="askoheat_ema", update_interval=update_interval)
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_ema()
        except AskoheatConnectionError as err:
            raise UpdateFailed(f"EMA update failed: {err}") from err


class AskoheatSlowCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for slow-polling CON/VAL/EXT data."""

    def __init__(self, hass: HomeAssistant, client: AskoheatApiClient) -> None:
        super().__init__(hass, _LOGGER, name="askoheat_slow", update_interval=SLOW_SCAN_INTERVAL)
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            con, val, ext = await asyncio.gather(
                self.client.get_con(),
                self.client.get_val(),
                self.client.get_ext(),
            )
            merged: dict[str, Any] = {}
            merged.update(con)
            merged.update(val)
            merged.update(ext)
            return merged
        except AskoheatConnectionError as err:
            raise UpdateFailed(f"Slow update failed: {err}") from err
