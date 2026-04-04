"""HTTP API client for Askoheat+ devices."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientSession, ClientTimeout, TCPConnector

from .const import (
    ENDPOINT_CON, ENDPOINT_EMA, ENDPOINT_EXT, ENDPOINT_INT,
    ENDPOINT_PAR, ENDPOINT_VAL, ENDPOINT_ALL,
    EMA_TEMP_SENSORS, NUM_TEMP_SENSORS,
    SENSOR_DISCONNECTED_TOLERANCE, SENSOR_DISCONNECTED_VALUE,
)

_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = ClientTimeout(total=5)


class AskoheatConnectionError(Exception):
    """Error communicating with the Askoheat device."""


class AskoheatApiClient:
    """HTTP client for Askoheat+ JSON API.

    Known quirks from evcc reference implementation:
    - Keep-alive must be disabled (device drops stale connections with EOF)
    - All JSON values are returned as strings
    - Disconnected temperature sensors return 9999.90
    """

    def __init__(self, host: str, session: ClientSession | None = None) -> None:
        self._host = host
        self._base_url = f"http://{host}"
        self._session = session
        self._owned_session = session is None

    async def _ensure_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            connector = TCPConnector(force_close=True)
            self._session = ClientSession(connector=connector, timeout=REQUEST_TIMEOUT)
            self._owned_session = True
        return self._session

    async def close(self) -> None:
        if self._owned_session and self._session and not self._session.closed:
            await self._session.close()

    async def _get(self, endpoint: str) -> dict[str, Any]:
        session = await self._ensure_session()
        url = f"{self._base_url}{endpoint}"
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except Exception as err:
            raise AskoheatConnectionError(
                f"Error communicating with Askoheat at {self._host}: {err}"
            ) from err

    async def _patch(self, endpoint: str, data: dict[str, str]) -> None:
        session = await self._ensure_session()
        url = f"{self._base_url}{endpoint}"
        try:
            async with session.patch(url, json=data) as resp:
                resp.raise_for_status()
        except Exception as err:
            raise AskoheatConnectionError(
                f"Error writing to Askoheat at {self._host}: {err}"
            ) from err

    async def get_ema(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_EMA)

    async def get_par(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_PAR)

    async def get_con(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_CON)

    async def get_val(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_VAL)

    async def get_ext(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_EXT)

    async def get_int(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_INT)

    async def get_all(self) -> dict[str, Any]:
        return await self._get(ENDPOINT_ALL)

    async def patch_ema(self, data: dict[str, str]) -> None:
        await self._patch(ENDPOINT_EMA, data)

    async def patch_con(self, data: dict[str, str]) -> None:
        await self._patch(ENDPOINT_CON, data)

    async def detect_connected_sensors(self) -> list[int]:
        ema = await self.get_ema()
        connected = []
        for i in range(NUM_TEMP_SENSORS):
            key = EMA_TEMP_SENSORS[i]
            try:
                val = float(ema.get(key, "9999.90"))
                if abs(val - SENSOR_DISCONNECTED_VALUE) > SENSOR_DISCONNECTED_TOLERANCE:
                    connected.append(i)
            except (ValueError, TypeError):
                pass
        return connected
