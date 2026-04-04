"""Number platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    CON_AUTO_HEATER_OFF_MINUTES,
    CON_CASCADE_PRIO,
    CON_HEATBUFFER_VOLUME,
    CON_HOUSEHOLD_MEMBERS,
    CON_LEGIO_HEATUP_MINUTES,
    CON_LEGIO_TEMPERATURE,
    CON_LOAD_FEEDIN_BIAS,
    CON_LOAD_FEEDIN_DELAY,
    CON_PUMP_SEC_COUNT,
    CON_RELAY_SEC_COUNT,
    CON_TEMPERATURE_HEAT_PUMP_REQUEST,
    CON_TEMPERATURE_HYSTERESIS,
    CON_TEMPERATURE_LOAD_SETPOINT,
    CON_TEMPERATURE_LOW_TARIFF,
    CON_TEMPERATURE_MINIMUM,
    CON_TEMPERATURE_SET_HEATER_STEP,
    CON_TIMEZONE_BIAS,
    EMA_LOAD_FEEDIN_VALUE,
    EMA_LOAD_SETPOINT_VALUE,
    con_analog_threshold,
    con_analog_threshold_temp,
)
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatNumberEntityDescription(NumberEntityDescription):
    """Extended number description with register key and patch target."""

    json_key: str
    patch_target: str  # "ema" or "con"
    coordinator_type: str  # "ema" or "slow"


# --- EMA numbers (fast coordinator, PATCH to EMA) ---
EMA_NUMBER_DESCRIPTIONS: tuple[AskoheatNumberEntityDescription, ...] = (
    AskoheatNumberEntityDescription(
        key="power_setpoint",
        translation_key="power_setpoint",
        name="Power setpoint",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=30000,
        native_step=1,
        mode=NumberMode.BOX,
        json_key=EMA_LOAD_SETPOINT_VALUE,
        patch_target="ema",
        coordinator_type="ema",
    ),
    AskoheatNumberEntityDescription(
        key="feedin_value",
        translation_key="feedin_value_number",
        name="Feed-in value",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=-30000,
        native_max_value=30000,
        native_step=1,
        mode=NumberMode.BOX,
        json_key=EMA_LOAD_FEEDIN_VALUE,
        patch_target="ema",
        coordinator_type="ema",
    ),
)

# --- CON numbers (slow coordinator, PATCH to CON) ---
CON_NUMBER_DESCRIPTIONS: tuple[AskoheatNumberEntityDescription, ...] = (
    # Temperature limits
    AskoheatNumberEntityDescription(
        key="temperature_load_setpoint",
        translation_key="temperature_load_setpoint",
        name="Temperature load setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_LOAD_SETPOINT,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="temperature_hysteresis",
        translation_key="temperature_hysteresis",
        name="Temperature hysteresis",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_HYSTERESIS,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="temperature_minimum",
        translation_key="temperature_minimum",
        name="Temperature minimum",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_MINIMUM,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="temperature_low_tariff",
        translation_key="temperature_low_tariff",
        name="Temperature low tariff",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_LOW_TARIFF,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="temperature_heat_pump_request",
        translation_key="temperature_heat_pump_request",
        name="Temperature heat pump request",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_HEAT_PUMP_REQUEST,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="temperature_set_heater_step",
        translation_key="temperature_set_heater_step",
        name="Temperature set heater step",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=95,
        native_step=1,
        json_key=CON_TEMPERATURE_SET_HEATER_STEP,
        patch_target="con",
        coordinator_type="slow",
    ),
    # Legio
    AskoheatNumberEntityDescription(
        key="legio_temperature",
        translation_key="legio_temperature",
        name="Legionella temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=50,
        native_max_value=65,
        native_step=1,
        json_key=CON_LEGIO_TEMPERATURE,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="legio_heatup_minutes",
        translation_key="legio_heatup_minutes",
        name="Legionella heat-up duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=0,
        native_max_value=1440,
        native_step=1,
        mode=NumberMode.BOX,
        json_key=CON_LEGIO_HEATUP_MINUTES,
        patch_target="con",
        coordinator_type="slow",
    ),
    # Timing
    AskoheatNumberEntityDescription(
        key="relay_sec_count",
        translation_key="relay_sec_count",
        name="Relay seconds count",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=16,
        native_step=1,
        json_key=CON_RELAY_SEC_COUNT,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="pump_sec_count",
        translation_key="pump_sec_count",
        name="Pump seconds count",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=240,
        native_step=1,
        json_key=CON_PUMP_SEC_COUNT,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="auto_heater_off_minutes",
        translation_key="auto_heater_off_minutes",
        name="Auto heater off delay",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=2,
        native_max_value=10080,
        native_step=1,
        mode=NumberMode.BOX,
        json_key=CON_AUTO_HEATER_OFF_MINUTES,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="load_feedin_delay",
        translation_key="load_feedin_delay",
        name="Feed-in delay",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=120,
        native_step=1,
        json_key=CON_LOAD_FEEDIN_DELAY,
        patch_target="con",
        coordinator_type="slow",
    ),
    # Other
    AskoheatNumberEntityDescription(
        key="load_feedin_bias",
        translation_key="load_feedin_bias",
        name="Feed-in bias",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=0,
        native_max_value=10000,
        native_step=1,
        mode=NumberMode.BOX,
        json_key=CON_LOAD_FEEDIN_BIAS,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="timezone_bias",
        translation_key="timezone_bias",
        name="Timezone bias",
        native_unit_of_measurement=UnitOfTime.HOURS,
        native_min_value=-12,
        native_max_value=12,
        native_step=1,
        json_key=CON_TIMEZONE_BIAS,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="heatbuffer_volume",
        translation_key="heatbuffer_volume",
        name="Heat buffer volume",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        native_min_value=0,
        native_max_value=1000,
        native_step=1,
        json_key=CON_HEATBUFFER_VOLUME,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="household_members",
        translation_key="household_members",
        name="Household members",
        native_min_value=1,
        native_max_value=255,
        native_step=1,
        json_key=CON_HOUSEHOLD_MEMBERS,
        patch_target="con",
        coordinator_type="slow",
    ),
    AskoheatNumberEntityDescription(
        key="cascade_prio",
        translation_key="cascade_prio",
        name="Cascade priority",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        json_key=CON_CASCADE_PRIO,
        patch_target="con",
        coordinator_type="slow",
    ),
)


def _build_analog_threshold_numbers() -> tuple[AskoheatNumberEntityDescription, ...]:
    """Build number descriptions for analog threshold registers (0-7)."""
    descs: list[AskoheatNumberEntityDescription] = []
    for i in range(8):
        descs.append(
            AskoheatNumberEntityDescription(
                key=f"analog_threshold_{i}",
                translation_key=f"analog_threshold_{i}",
                name=f"Analog threshold {i} voltage",
                native_min_value=0,
                native_max_value=10,
                native_step=0.01,
                mode=NumberMode.BOX,
                json_key=con_analog_threshold(i),
                patch_target="con",
                coordinator_type="slow",
            )
        )
        descs.append(
            AskoheatNumberEntityDescription(
                key=f"analog_threshold_temp_{i}",
                translation_key=f"analog_threshold_temp_{i}",
                name=f"Analog threshold {i} temperature",
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                device_class=NumberDeviceClass.TEMPERATURE,
                native_min_value=0,
                native_max_value=95,
                native_step=1,
                json_key=con_analog_threshold_temp(i),
                patch_target="con",
                coordinator_type="slow",
            )
        )
    return tuple(descs)


ANALOG_THRESHOLD_DESCRIPTIONS = _build_analog_threshold_numbers()


class AskoheatNumber(AskoheatEntity, NumberEntity):
    """Number entity for a writable Askoheat register."""

    entity_description: AskoheatNumberEntityDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatNumberEntityDescription,
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
        self._data = data

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.json_key)
        if raw is None:
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the register value."""
        desc = self.entity_description
        payload = {desc.json_key: str(int(value)) if value == int(value) else str(value)}

        if desc.patch_target == "ema":
            await self._data.client.patch_ema(payload)
        else:
            await self._data.client.patch_con(payload)

        # Update heartbeat tracking for setpoint
        if desc.json_key == EMA_LOAD_SETPOINT_VALUE:
            self._data.last_setpoint = int(value)

        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat number entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]
    entities: list[NumberEntity] = []

    for desc in EMA_NUMBER_DESCRIPTIONS:
        entities.append(AskoheatNumber(data, host, desc))

    for desc in CON_NUMBER_DESCRIPTIONS:
        entities.append(AskoheatNumber(data, host, desc))

    for desc in ANALOG_THRESHOLD_DESCRIPTIONS:
        entities.append(AskoheatNumber(data, host, desc))

    async_add_entities(entities)
