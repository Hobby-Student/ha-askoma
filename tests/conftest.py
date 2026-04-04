"""Fixtures for Askoheat tests."""

import pytest
from unittest.mock import AsyncMock, patch

from custom_components.askoheat.const import DOMAIN


@pytest.fixture
def mock_ema_response():
    """Return a mock EMA JSON response (all values are strings like the real device)."""
    return {
        "ASKOHEAT_PLUS_INFO": {
            "ARTICLE_NAME": "ASKOHEAT+ 3kW",
            "SOFTWARE_VERSION": "1.2.3",
            "DEVICEID": "AA:BB:CC:DD:EE:FF",
        },
        "MODBUS_EMA_STATUS": "7",
        "MODBUS_EMA_HEATER_LOAD": "3000",
        "MODBUS_EMA_SET_HEATER_STEP": "7",
        "MODBUS_EMA_LOAD_SETPOINT_VALUE": "3000",
        "MODBUS_EMA_LOAD_FEEDIN_VALUE": "0",
        "MODBUS_EMA_EMERGENCY_MODE": "0",
        "MODBUS_EMA_HEAT_PUMP_REQUEST": "0",
        "MODBUS_EMA_ANALOG_INPUT_FLOAT": "0.0",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR0": "45.5",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR1": "38.2",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR2": "9999.90",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR3": "9999.90",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR4": "9999.90",
        "MODBUS_EMA_TEMPERATURE_FLOAT_SENSOR5": "9999.90",
        "MODBUS_EMA_STATUS_EXTENDED": "0",
    }


@pytest.fixture
def mock_par_response():
    """Return a mock PAR JSON response."""
    return {
        "MODBUS_PAR_ID": "SN-12345678",
        "MODBUS_PAR_TYPE": "1",
        "MODBUS_PAR_HEATER1_POWER": "1000",
        "MODBUS_PAR_HEATER2_POWER": "1000",
        "MODBUS_PAR_HEATER3_POWER": "1000",
        "MODBUS_PAR_ARTICLE_NUMBER": "AH-3000",
        "MODBUS_PAR_ARTICLE_NAME": "ASKOHEAT+ 3kW",
        "MODBUS_PAR_SOFTWARE_VERSION": "1.2.3",
        "MODBUS_PAR_HARDWARE_VERSION": "2.0",
        "MODBUS_PAR_NUMBER_OF_HEATER": "3",
        "MODBUS_PAR_NUMBER_OF_STEPS": "7",
        "MODBUS_PAR_MAX_POWER": "3000",
    }


@pytest.fixture
def mock_con_response():
    """Return a mock CON JSON response."""
    return {
        "MODBUS_CON_INPUT_SETTING": "24",
        "MODBUS_CON_RELAY_SEC_COUNT": "2",
        "MODBUS_CON_PUMP_SEC_COUNT": "120",
        "MODBUS_CON_AUTO_HEATER_OFF_MINUTES": "1440",
        "MODBUS_CON_AUTO_HEATER_OFF_SETTING": "0",
        "MODBUS_CON_TEMPERATURE_LOAD_SETPOINT": "60",
        "MODBUS_CON_TEMPERATURE_HYSTERESIS": "5",
        "MODBUS_CON_TEMPERATURE_MINIMUM": "10",
        "MODBUS_CON_HEATBUFFER_TYPE": "0",
        "MODBUS_CON_HEATBUFFER_VOLUME": "300",
        "MODBUS_CON_HEATER_POSITION": "0",
        "MODBUS_CON_LEGIO_SETTING": "0",
        "MODBUS_CON_LEGIO_TEMPERATURE": "60",
        "MODBUS_CON_LEGIO_HEATUP_MINUTES": "120",
        "MODBUS_CON_HOUSETYPE": "0",
        "MODBUS_CON_HOUSEHOLD_MEMBERS": "4",
        "MODBUS_CON_LOAD_FEEDIN_DELAY": "10",
        "MODBUS_CON_LOAD_FEEDIN_BIAS": "0",
        "MODBUS_CON_TIMEZONE_BIAS": "1",
        "MODBUS_CON_SUMMERTIME_BIAS": "1",
        "MODBUS_CON_CASCADE_PRIO": "0",
        "MODBUS_CON_TEMPERATURE_SETTING": "0",
        "MODBUS_CON_TEMPERATURE_SET_HEATER_STEP": "85",
        "MODBUS_CON_TEMPERATURE_LOW_TARIFF": "55",
        "MODBUS_CON_TEMPERATURE_HEAT_PUMP_REQUEST": "65",
        "MODBUS_CON_HEAT_PUMP_REQUEST_OFF_STEP": "0",
        "MODBUS_CON_HEAT_PUMP_REQUEST_ON_STEP": "7",
        "MODBUS_CON_EMERGENCY_MODE_ON_STEP": "7",
        "MODBUS_CON_RTU_ENERGY_METER_TYPE": "0",
        "MODBUS_CON_ANALOG_IN_HYSTERESIS": "0.5",
    }
