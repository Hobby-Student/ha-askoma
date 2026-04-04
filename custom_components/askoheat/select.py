"""Select platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass, field

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    CON_EMERGENCY_MODE_ON_STEP,
    CON_HEATBUFFER_TYPE,
    CON_HEATER_POSITION,
    CON_HEAT_PUMP_REQUEST_OFF_STEP,
    CON_HEAT_PUMP_REQUEST_ON_STEP,
    CON_HOUSETYPE,
    CON_LEGIO_SETTING,
    CON_RTU_ENERGY_METER_TYPE,
    CON_TEMPERATURE_SETTING,
    EMA_SET_HEATER_STEP,
    con_analog_threshold_step,
)
from .entity import AskoheatEntity

STEP_OPTIONS_MAP: dict[str, str] = {
    "Off": "0",
    "Step 1": "1",
    "Step 2": "2",
    "Step 3": "3",
    "Step 4": "4",
    "Step 5": "5",
    "Step 6": "6",
    "Step 7": "7",
}


@dataclass(frozen=True, kw_only=True)
class AskoheatSelectEntityDescription(SelectEntityDescription):
    """Extended select description with register key and options map."""

    json_key: str
    patch_target: str  # "ema" or "con"
    coordinator_type: str  # "ema" or "slow"
    options_map: dict[str, str] = field(default_factory=dict)


# --- EMA selects ---
EMA_SELECT_DESCRIPTIONS: tuple[AskoheatSelectEntityDescription, ...] = (
    AskoheatSelectEntityDescription(
        key="heater_step",
        translation_key="heater_step",
        name="Heater step",
        options=list(STEP_OPTIONS_MAP.keys()),
        json_key=EMA_SET_HEATER_STEP,
        patch_target="ema",
        coordinator_type="ema",
        options_map=STEP_OPTIONS_MAP,
    ),
)

# --- CON selects ---
CON_SELECT_DESCRIPTIONS: tuple[AskoheatSelectEntityDescription, ...] = (
    AskoheatSelectEntityDescription(
        key="heatbuffer_type",
        translation_key="heatbuffer_type",
        name="Heat buffer type",
        options=["None", "Heat pump", "Burner", "CHP"],
        json_key=CON_HEATBUFFER_TYPE,
        patch_target="con",
        coordinator_type="slow",
        options_map={"None": "0", "Heat pump": "1", "Burner": "2", "CHP": "3"},
    ),
    AskoheatSelectEntityDescription(
        key="heater_position",
        translation_key="heater_position",
        name="Heater position",
        options=["ASKOWALL", "Middle", "Bottom"],
        json_key=CON_HEATER_POSITION,
        patch_target="con",
        coordinator_type="slow",
        options_map={"ASKOWALL": "0", "Middle": "1", "Bottom": "2"},
    ),
    AskoheatSelectEntityDescription(
        key="house_type",
        translation_key="house_type",
        name="House type",
        options=["Single family", "Two family", "Apartment", "Commercial"],
        json_key=CON_HOUSETYPE,
        patch_target="con",
        coordinator_type="slow",
        options_map={
            "Single family": "0",
            "Two family": "1",
            "Apartment": "2",
            "Commercial": "3",
        },
    ),
    AskoheatSelectEntityDescription(
        key="heat_pump_off_step",
        translation_key="heat_pump_off_step",
        name="Heat pump request off step",
        options=list(STEP_OPTIONS_MAP.keys()),
        json_key=CON_HEAT_PUMP_REQUEST_OFF_STEP,
        patch_target="con",
        coordinator_type="slow",
        options_map=STEP_OPTIONS_MAP,
    ),
    AskoheatSelectEntityDescription(
        key="heat_pump_on_step",
        translation_key="heat_pump_on_step",
        name="Heat pump request on step",
        options=list(STEP_OPTIONS_MAP.keys()),
        json_key=CON_HEAT_PUMP_REQUEST_ON_STEP,
        patch_target="con",
        coordinator_type="slow",
        options_map=STEP_OPTIONS_MAP,
    ),
    AskoheatSelectEntityDescription(
        key="emergency_mode_on_step",
        translation_key="emergency_mode_on_step",
        name="Emergency mode on step",
        options=list(STEP_OPTIONS_MAP.keys()),
        json_key=CON_EMERGENCY_MODE_ON_STEP,
        patch_target="con",
        coordinator_type="slow",
        options_map=STEP_OPTIONS_MAP,
    ),
    AskoheatSelectEntityDescription(
        key="legio_setting",
        translation_key="legio_setting",
        name="Legionella protection setting",
        options=["Off", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Daily"],
        json_key=CON_LEGIO_SETTING,
        patch_target="con",
        coordinator_type="slow",
        options_map={
            "Off": "0", "Monday": "1", "Tuesday": "2", "Wednesday": "3",
            "Thursday": "4", "Friday": "5", "Saturday": "6", "Sunday": "7", "Daily": "8",
        },
    ),
    AskoheatSelectEntityDescription(
        key="temperature_setting",
        translation_key="temperature_setting",
        name="Temperature sensor selection",
        options=["Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"],
        json_key=CON_TEMPERATURE_SETTING,
        patch_target="con",
        coordinator_type="slow",
        options_map={
            "Sensor 0": "0", "Sensor 1": "1", "Sensor 2": "2",
            "Sensor 3": "3", "Sensor 4": "4",
        },
    ),
    AskoheatSelectEntityDescription(
        key="energy_meter_type",
        translation_key="energy_meter_type",
        name="Energy meter type",
        options=["None", "ABB B23", "Eastron SDM630", "Eastron SDM72D"],
        json_key=CON_RTU_ENERGY_METER_TYPE,
        patch_target="con",
        coordinator_type="slow",
        options_map={
            "None": "0", "ABB B23": "1", "Eastron SDM630": "2", "Eastron SDM72D": "3",
        },
    ),
)


def _build_analog_threshold_step_selects() -> (
    tuple[AskoheatSelectEntityDescription, ...]
):
    """Build select descriptions for analog threshold step registers (0-7)."""
    descs: list[AskoheatSelectEntityDescription] = []
    for i in range(8):
        descs.append(
            AskoheatSelectEntityDescription(
                key=f"analog_threshold_step_{i}",
                translation_key=f"analog_threshold_step_{i}",
                name=f"Analog threshold {i} step",
                options=list(STEP_OPTIONS_MAP.keys()),
                json_key=con_analog_threshold_step(i),
                patch_target="con",
                coordinator_type="slow",
                options_map=STEP_OPTIONS_MAP,
            )
        )
    return tuple(descs)


ANALOG_THRESHOLD_STEP_DESCRIPTIONS = _build_analog_threshold_step_selects()


class AskoheatSelect(AskoheatEntity, SelectEntity):
    """Select entity for an Askoheat enum register."""

    entity_description: AskoheatSelectEntityDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatSelectEntityDescription,
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
        # Build reverse map: register value -> display label
        self._reverse_map: dict[str, str] = {
            v: k for k, v in description.options_map.items()
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.json_key)
        if raw is None:
            return None
        return self._reverse_map.get(str(raw))

    async def async_select_option(self, option: str) -> None:
        """Set the register to the value mapped from the selected option."""
        desc = self.entity_description
        reg_value = desc.options_map.get(option)
        if reg_value is None:
            return

        payload = {desc.json_key: reg_value}
        if desc.patch_target == "ema":
            await self._data.client.patch_ema(payload)
        else:
            await self._data.client.patch_con(payload)

        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat select entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]
    entities: list[SelectEntity] = []

    for desc in EMA_SELECT_DESCRIPTIONS:
        entities.append(AskoheatSelect(data, host, desc))

    for desc in CON_SELECT_DESCRIPTIONS:
        entities.append(AskoheatSelect(data, host, desc))

    for desc in ANALOG_THRESHOLD_STEP_DESCRIPTIONS:
        entities.append(AskoheatSelect(data, host, desc))

    async_add_entities(entities)
