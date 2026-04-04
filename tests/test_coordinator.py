"""Tests for the Askoheat coordinators."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import timedelta

from custom_components.askoheat.coordinator import (
    AskoheatEmaCoordinator,
    AskoheatSlowCoordinator,
)
from custom_components.askoheat.api import AskoheatApiClient


@pytest.mark.asyncio
async def test_ema_coordinator_update(mock_ema_response):
    mock_client = AsyncMock(spec=AskoheatApiClient)
    mock_client.get_ema = AsyncMock(return_value=mock_ema_response)

    hass = MagicMock()
    coordinator = AskoheatEmaCoordinator(
        hass=hass, client=mock_client, update_interval=timedelta(seconds=5),
    )
    data = await coordinator._async_update_data()
    assert data["MODBUS_EMA_HEATER_LOAD"] == "3000"
    mock_client.get_ema.assert_called_once()


@pytest.mark.asyncio
async def test_slow_coordinator_merges_blocks(mock_con_response):
    mock_client = AsyncMock(spec=AskoheatApiClient)
    mock_client.get_con = AsyncMock(return_value=mock_con_response)
    mock_client.get_val = AsyncMock(return_value={"MODBUS_VAL_BOOT_COUNT": "42"})
    mock_client.get_ext = AsyncMock(return_value={"MODBUS_EXT_HEATER_LOAD": "3000"})

    hass = MagicMock()
    coordinator = AskoheatSlowCoordinator(hass=hass, client=mock_client)
    data = await coordinator._async_update_data()

    assert data["MODBUS_CON_TEMPERATURE_LOAD_SETPOINT"] == "60"
    assert data["MODBUS_VAL_BOOT_COUNT"] == "42"
    assert data["MODBUS_EXT_HEATER_LOAD"] == "3000"
