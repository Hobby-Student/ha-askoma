"""Water heater platform for the Askoheat integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    CON_TEMPERATURE_LOAD_SETPOINT,
    EMA_LOAD_FEEDIN_VALUE,
    EMA_LOAD_SETPOINT_VALUE,
    EMA_SET_HEATER_STEP,
    EMA_STATUS,
    EMA_TEMP_SENSORS,
    PAR_MAX_POWER,
    SENSOR_DISCONNECTED_TOLERANCE,
    SENSOR_DISCONNECTED_VALUE,
)
from .entity import AskoheatEntity

_LOGGER = logging.getLogger(__name__)

# Operation mode constants
STATE_OFF = "off"
STATE_PERFORMANCE = "performance"
STATE_HEAT_PUMP = "heat_pump"
STATE_ELECTRIC = "electric"

OPERATION_LIST = [STATE_OFF, STATE_PERFORMANCE, STATE_HEAT_PUMP, STATE_ELECTRIC]


class AskoheatWaterHeater(AskoheatEntity, WaterHeaterEntity):
    """Water heater entity for Askoheat."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )
    _attr_operation_list = OPERATION_LIST
    _attr_min_temp = 0
    _attr_max_temp = 95
    _attr_name = "Water heater"

    def __init__(self, data: AskoheatData, host: str) -> None:
        """Initialize the water heater."""
        super().__init__(
            coordinator=data.ema_coordinator,
            par_data=data.par_data,
            host=host,
            key="water_heater",
        )
        self._data = data

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature from the first EMA sensor."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(EMA_TEMP_SENSORS[0])
        if raw is None:
            return None
        try:
            val = float(raw)
        except (ValueError, TypeError):
            return None
        if abs(val - SENSOR_DISCONNECTED_VALUE) <= SENSOR_DISCONNECTED_TOLERANCE:
            return None
        return val

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature from the slow coordinator."""
        slow_data = self._data.slow_coordinator.data
        if slow_data is None:
            return None
        raw = slow_data.get(CON_TEMPERATURE_LOAD_SETPOINT)
        if raw is None:
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None

    @property
    def current_operation(self) -> str:
        """Derive the current operation mode from EMA data."""
        if self.coordinator.data is None:
            return STATE_OFF

        # Check status register
        raw_status = self.coordinator.data.get(EMA_STATUS)
        if raw_status is not None:
            try:
                if int(raw_status) & 0x07 == 0:
                    return STATE_OFF
            except (ValueError, TypeError):
                pass

        # Check setpoint value
        raw_setpoint = self.coordinator.data.get(EMA_LOAD_SETPOINT_VALUE)
        if raw_setpoint is not None:
            try:
                if int(float(raw_setpoint)) > 0:
                    return STATE_PERFORMANCE
            except (ValueError, TypeError):
                pass

        # Check heater step
        raw_step = self.coordinator.data.get(EMA_SET_HEATER_STEP)
        if raw_step is not None:
            try:
                if int(raw_step) > 0:
                    return STATE_HEAT_PUMP
            except (ValueError, TypeError):
                pass

        return STATE_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature via CON register."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        await self._data.client.patch_con(
            {CON_TEMPERATURE_LOAD_SETPOINT: str(int(temperature))}
        )
        await self._data.slow_coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the operation mode."""
        if operation_mode == STATE_OFF:
            await self._data.client.patch_ema(
                {
                    EMA_LOAD_SETPOINT_VALUE: "0",
                    EMA_SET_HEATER_STEP: "0",
                }
            )
            self._data.last_setpoint = 0

        elif operation_mode == STATE_PERFORMANCE:
            # Use max power from par_data as default setpoint
            max_power = self._par_data.get(PAR_MAX_POWER, 3000)
            try:
                setpoint = int(max_power)
            except (ValueError, TypeError):
                setpoint = 3000
            await self._data.client.patch_ema(
                {
                    EMA_LOAD_SETPOINT_VALUE: str(setpoint),
                    EMA_SET_HEATER_STEP: "0",
                }
            )
            self._data.last_setpoint = setpoint

        elif operation_mode == STATE_HEAT_PUMP:
            # Manual step mode: full power (step 7)
            await self._data.client.patch_ema(
                {
                    EMA_SET_HEATER_STEP: "7",
                    EMA_LOAD_SETPOINT_VALUE: "0",
                }
            )
            self._data.last_setpoint = 0

        elif operation_mode == STATE_ELECTRIC:
            # Feed-in mode: set a feed-in value
            max_power = self._par_data.get(PAR_MAX_POWER, 3000)
            try:
                feedin = int(max_power)
            except (ValueError, TypeError):
                feedin = 3000
            await self._data.client.patch_ema(
                {
                    EMA_LOAD_FEEDIN_VALUE: str(feedin),
                    EMA_SET_HEATER_STEP: "0",
                    EMA_LOAD_SETPOINT_VALUE: "0",
                }
            )
            self._data.last_setpoint = 0

        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self) -> None:
        """Subscribe to both coordinators."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._data.slow_coordinator.async_add_listener(
                self._handle_slow_coordinator_update
            )
        )

    @callback
    def _handle_slow_coordinator_update(self) -> None:
        """Handle updated data from the slow coordinator."""
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Askoheat water heater entity."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]
    async_add_entities([AskoheatWaterHeater(data, host)])
