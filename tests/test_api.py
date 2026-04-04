"""Tests for AskoheatApiClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.askoheat.api import AskoheatApiClient, AskoheatConnectionError
from custom_components.askoheat.const import ENDPOINT_EMA, ENDPOINT_PAR


def _make_mock_response(data=None, status=200):
    """Create a mock aiohttp response as an async context manager."""
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=data)
    mock_resp.raise_for_status = MagicMock()
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=False)
    return mock_resp


@pytest.mark.asyncio
async def test_get_ema(mock_ema_response):
    """Test that get_ema returns the EMA data from the device."""
    mock_resp = _make_mock_response(mock_ema_response)

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.get = MagicMock(return_value=mock_resp)

    client = AskoheatApiClient("192.168.1.100", session=mock_session)
    result = await client.get_ema()

    assert result == mock_ema_response
    mock_session.get.assert_called_once_with("http://192.168.1.100/GETEMA.JSON")


@pytest.mark.asyncio
async def test_get_par(mock_par_response):
    """Test that get_par returns the PAR data from the device."""
    mock_resp = _make_mock_response(mock_par_response)

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.get = MagicMock(return_value=mock_resp)

    client = AskoheatApiClient("192.168.1.100", session=mock_session)
    result = await client.get_par()

    assert result == mock_par_response
    mock_session.get.assert_called_once_with("http://192.168.1.100/GETPAR.JSON")


@pytest.mark.asyncio
async def test_patch_ema():
    """Test that patch_ema sends a PATCH request with the correct URL and data."""
    mock_resp = _make_mock_response()

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.patch = MagicMock(return_value=mock_resp)

    client = AskoheatApiClient("192.168.1.100", session=mock_session)
    data = {"MODBUS_EMA_SET_HEATER_STEP": "3"}
    await client.patch_ema(data)

    mock_session.patch.assert_called_once_with(
        "http://192.168.1.100/GETEMA.JSON", json=data
    )


@pytest.mark.asyncio
async def test_connection_error():
    """Test that a network error is wrapped in AskoheatConnectionError."""
    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.get = MagicMock(side_effect=Exception("Connection refused"))

    client = AskoheatApiClient("192.168.1.100", session=mock_session)

    with pytest.raises(AskoheatConnectionError, match="Error communicating"):
        await client.get_ema()


@pytest.mark.asyncio
async def test_detect_connected_sensors(mock_ema_response):
    """Test that only sensors with real temperatures are detected as connected.

    In the mock EMA response, sensors 0 and 1 have real values (45.5, 38.2),
    while sensors 2-5 report 9999.90 (disconnected).
    """
    mock_resp = _make_mock_response(mock_ema_response)

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.get = MagicMock(return_value=mock_resp)

    client = AskoheatApiClient("192.168.1.100", session=mock_session)
    connected = await client.detect_connected_sensors()

    assert connected == [0, 1]
