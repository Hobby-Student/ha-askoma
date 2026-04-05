"""Sensor platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    EMA_ANALOG_INPUT_FLOAT,
    EMA_HEATER_LOAD,
    EMA_LOAD_SETPOINT_VALUE,
    EMA_TEMP_SENSORS,
    EXT_LOAD_FEEDIN_VALUE,
    SENSOR_DISCONNECTED_TOLERANCE,
    SENSOR_DISCONNECTED_VALUE,
    VAL_ACTUAL_TEMPERATURE_LIMIT,
    VAL_ANALOG_IN_COUNT,
    VAL_BOOT_COUNT,
    VAL_EMERGENCY_MODE_COUNT,
    VAL_HEAT_PUMP_REQUEST_COUNT,
    VAL_LEGIO_COUNT,
    VAL_LOAD_FEEDIN_COUNT,
    VAL_LOAD_SETPOINT_COUNT,
    VAL_LOW_TARIFF_COUNT,
    VAL_MAX_TEMPERATURE,
    VAL_MINIMAL_TEMP_COUNT,
    VAL_OPERATING_HEATER1,
    VAL_OPERATING_HEATER2,
    VAL_OPERATING_HEATER3,
    VAL_OPERATING_HEATER_STEPS,
    VAL_OPERATING_LOAD_SETPOINT,
    VAL_OPERATING_PUMP,
    VAL_OPERATING_SET_HEATER_STEP,
    VAL_OPERATING_TIME,
    VAL_OPERATION_ANALOG_IN,
    VAL_OPERATION_EMERGENCY_MODE,
    VAL_OPERATION_HEAT_PUMP_REQUEST,
    VAL_OPERATION_LEGIO,
    VAL_OPERATION_LOAD_FEEDIN,
    VAL_OPERATION_LOW_TARIFF,
    VAL_OPERATION_MINIMAL_TEMP,
    VAL_RELAY1_COUNT,
    VAL_RELAY2_COUNT,
    VAL_RELAY3_COUNT,
    VAL_RELAY4_COUNT,
    VAL_SET_HEATER_STEP_COUNT,
)
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatSensorEntityDescription(SensorEntityDescription):
    """Extended sensor description with value key and type."""

    value_key: str
    value_type: type = float
    coordinator_type: str = "ema"  # "ema" or "slow"


# --- EMA (fast) sensors ---
EMA_SENSOR_DESCRIPTIONS: tuple[AskoheatSensorEntityDescription, ...] = (
    AskoheatSensorEntityDescription(
        key="heater_load",
        translation_key="heater_load",
        name="Heater load",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=EMA_HEATER_LOAD,
        coordinator_type="ema",
    ),
    AskoheatSensorEntityDescription(
        key="load_setpoint",
        translation_key="load_setpoint",
        name="Load setpoint",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=EMA_LOAD_SETPOINT_VALUE,
        coordinator_type="ema",
    ),
    AskoheatSensorEntityDescription(
        key="analog_input",
        translation_key="analog_input",
        name="Analog input",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=EMA_ANALOG_INPUT_FLOAT,
        coordinator_type="ema",
    ),
)

# --- Slow sensors ---
SLOW_SENSOR_DESCRIPTIONS: tuple[AskoheatSensorEntityDescription, ...] = (
    # Operating hours
    AskoheatSensorEntityDescription(
        key="operating_time",
        translation_key="operating_time",
        name="Operating time",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_TIME,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_heater1",
        translation_key="operating_heater1",
        name="Heater 1 operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_HEATER1,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_heater2",
        translation_key="operating_heater2",
        name="Heater 2 operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_HEATER2,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_heater3",
        translation_key="operating_heater3",
        name="Heater 3 operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_HEATER3,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_pump",
        translation_key="operating_pump",
        name="Pump operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_PUMP,
        value_type=float,
        coordinator_type="slow",
    ),
    # Relay / boot counts
    AskoheatSensorEntityDescription(
        key="relay1_count",
        translation_key="relay1_count",
        name="Relay 1 switch count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_RELAY1_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="relay2_count",
        translation_key="relay2_count",
        name="Relay 2 switch count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_RELAY2_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="relay3_count",
        translation_key="relay3_count",
        name="Relay 3 switch count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_RELAY3_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="relay4_count",
        translation_key="relay4_count",
        name="Relay 4 switch count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_RELAY4_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="boot_count",
        translation_key="boot_count",
        name="Boot count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_BOOT_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    # Temperatures
    AskoheatSensorEntityDescription(
        key="max_temperature",
        translation_key="max_temperature",
        name="Maximum temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=VAL_MAX_TEMPERATURE,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="actual_temperature_limit",
        translation_key="actual_temperature_limit",
        name="Actual temperature limit",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=VAL_ACTUAL_TEMPERATURE_LIMIT,
        value_type=float,
        coordinator_type="slow",
    ),
    # Feed-in power
    AskoheatSensorEntityDescription(
        key="feedin_value",
        translation_key="feedin_value",
        name="Feed-in value",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key=EXT_LOAD_FEEDIN_VALUE,
        value_type=float,
        coordinator_type="slow",
    ),
    # Mode operating hours
    AskoheatSensorEntityDescription(
        key="operating_set_heater_step",
        translation_key="operating_set_heater_step",
        name="Set heater step operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_SET_HEATER_STEP,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_load_setpoint",
        translation_key="operating_load_setpoint",
        name="Load setpoint operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATING_LOAD_SETPOINT,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_load_feedin",
        translation_key="operating_load_feedin",
        name="Load feed-in operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_LOAD_FEEDIN,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_heat_pump_request",
        translation_key="operating_heat_pump_request",
        name="Heat pump request operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_HEAT_PUMP_REQUEST,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_analog_in",
        translation_key="operating_analog_in",
        name="Analog input operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_ANALOG_IN,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_emergency_mode",
        translation_key="operating_emergency_mode",
        name="Emergency mode operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_EMERGENCY_MODE,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_legio",
        translation_key="operating_legio",
        name="Legionella operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_LEGIO,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_low_tariff",
        translation_key="operating_low_tariff",
        name="Low tariff operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_LOW_TARIFF,
        value_type=float,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="operating_minimal_temp",
        translation_key="operating_minimal_temp",
        name="Minimal temp operating hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_OPERATION_MINIMAL_TEMP,
        value_type=float,
        coordinator_type="slow",
    ),
    # Mode usage counts
    AskoheatSensorEntityDescription(
        key="set_heater_step_count",
        translation_key="set_heater_step_count",
        name="Set heater step usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_SET_HEATER_STEP_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="load_setpoint_count",
        translation_key="load_setpoint_count",
        name="Load setpoint usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_LOAD_SETPOINT_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="load_feedin_count",
        translation_key="load_feedin_count",
        name="Load feed-in usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_LOAD_FEEDIN_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="heat_pump_request_count",
        translation_key="heat_pump_request_count",
        name="Heat pump request usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_HEAT_PUMP_REQUEST_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="analog_in_count",
        translation_key="analog_in_count",
        name="Analog input usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_ANALOG_IN_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="emergency_mode_count",
        translation_key="emergency_mode_count",
        name="Emergency mode usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_EMERGENCY_MODE_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="legio_count",
        translation_key="legio_count",
        name="Legionella usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_LEGIO_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="low_tariff_count",
        translation_key="low_tariff_count",
        name="Low tariff usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_LOW_TARIFF_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
    AskoheatSensorEntityDescription(
        key="minimal_temp_count",
        translation_key="minimal_temp_count",
        name="Minimal temp usage count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key=VAL_MINIMAL_TEMP_COUNT,
        value_type=int,
        coordinator_type="slow",
    ),
)


def _build_step_operating_hours() -> tuple[AskoheatSensorEntityDescription, ...]:
    """Build sensor descriptions for per-step operating hours."""
    descs = []
    for i, key in enumerate(VAL_OPERATING_HEATER_STEPS, start=1):
        descs.append(
            AskoheatSensorEntityDescription(
                key=f"operating_heater_step_{i}",
                translation_key=f"operating_heater_step_{i}",
                name=f"Step {i} operating hours",
                native_unit_of_measurement=UnitOfTime.HOURS,
                device_class=SensorDeviceClass.DURATION,
                state_class=SensorStateClass.TOTAL_INCREASING,
                value_key=key,
                value_type=float,
                coordinator_type="slow",
            )
        )
    return tuple(descs)


STEP_SENSOR_DESCRIPTIONS = _build_step_operating_hours()


class AskoheatTemperatureSensor(AskoheatEntity, SensorEntity):
    """Sensor for an Askoheat temperature probe."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        sensor_index: int,
    ) -> None:
        """Initialize."""
        super().__init__(
            coordinator=data.ema_coordinator,
            par_data=data.par_data,
            host=host,
            key=f"temp_sensor_{sensor_index}",
        )
        self._sensor_index = sensor_index
        self._attr_translation_key = f"temperature_sensor_{sensor_index}"

    @property
    def native_value(self) -> float | None:
        """Return current temperature or None if disconnected."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(EMA_TEMP_SENSORS[self._sensor_index])
        if raw is None:
            return None
        try:
            val = float(raw)
        except (ValueError, TypeError):
            return None
        if abs(val - SENSOR_DISCONNECTED_VALUE) <= SENSOR_DISCONNECTED_TOLERANCE:
            return None
        return val


class AskoheatDescriptorSensor(AskoheatEntity, SensorEntity):
    """Generic descriptor-driven sensor."""

    entity_description: AskoheatSensorEntityDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatSensorEntityDescription,
    ) -> None:
        """Initialize."""
        coordinator = (
            data.ema_coordinator
            if description.coordinator_type == "ema"
            else data.slow_coordinator
        )
        super().__init__(
            coordinator=coordinator,
            par_data=data.par_data,
            host=host,
            key=description.key,
        )
        self.entity_description = description

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.value_key)
        if raw is None:
            return None
        try:
            return self.entity_description.value_type(raw)
        except (ValueError, TypeError):
            return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat sensor entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]
    entities: list[SensorEntity] = []

    # Temperature sensors (only connected ones)
    for idx in data.connected_sensors:
        entities.append(AskoheatTemperatureSensor(data, host, idx))

    # EMA descriptor sensors
    for desc in EMA_SENSOR_DESCRIPTIONS:
        entities.append(AskoheatDescriptorSensor(data, host, desc))

    # Slow descriptor sensors
    for desc in SLOW_SENSOR_DESCRIPTIONS:
        entities.append(AskoheatDescriptorSensor(data, host, desc))

    # Step operating hours
    for desc in STEP_SENSOR_DESCRIPTIONS:
        entities.append(AskoheatDescriptorSensor(data, host, desc))

    async_add_entities(entities)
