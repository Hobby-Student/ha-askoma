"""Switch platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    CON_INPUT_SETTING,
    CON_SUMMERTIME_BIAS,
    INPUT_SETTING_ANALOG,
    INPUT_SETTING_EMERGENCY,
    INPUT_SETTING_FEEDIN,
    INPUT_SETTING_HEAT_PUMP,
    INPUT_SETTING_SETPOINT,
)
from .entity import AskoheatEntity

@dataclass(frozen=True, kw_only=True)
class AskoheatBitSwitchDescription(SwitchEntityDescription):
    """Description for a bit-flag switch in CON_INPUT_SETTING."""

    bit_mask: int


BIT_SWITCH_DESCRIPTIONS: tuple[AskoheatBitSwitchDescription, ...] = (
    AskoheatBitSwitchDescription(
        key="input_analog_enabled",
        translation_key="input_analog_enabled",
        name="Analog input enabled",
        bit_mask=INPUT_SETTING_ANALOG,
    ),
    AskoheatBitSwitchDescription(
        key="input_heat_pump_enabled",
        translation_key="input_heat_pump_enabled",
        name="Heat pump input enabled",
        bit_mask=INPUT_SETTING_HEAT_PUMP,
    ),
    AskoheatBitSwitchDescription(
        key="input_emergency_enabled",
        translation_key="input_emergency_enabled",
        name="Emergency input enabled",
        bit_mask=INPUT_SETTING_EMERGENCY,
    ),
    AskoheatBitSwitchDescription(
        key="input_setpoint_enabled",
        translation_key="input_setpoint_enabled",
        name="Setpoint input enabled",
        bit_mask=INPUT_SETTING_SETPOINT,
    ),
    AskoheatBitSwitchDescription(
        key="input_feedin_enabled",
        translation_key="input_feedin_enabled",
        name="Feed-in input enabled",
        bit_mask=INPUT_SETTING_FEEDIN,
    ),
)


class AskoheatBitSwitch(AskoheatEntity, SwitchEntity):
    """Switch that controls a single bit in CON_INPUT_SETTING."""

    entity_description: AskoheatBitSwitchDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatBitSwitchDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            coordinator=data.slow_coordinator,
            par_data=data.par_data,
            host=host,
            key=description.key,
        )
        self.entity_description = description
        self._data = data

    @property
    def is_on(self) -> bool | None:
        """Return true if the bit is set."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(CON_INPUT_SETTING)
        if raw is None:
            return None
        try:
            return bool(int(raw) & self.entity_description.bit_mask)
        except (ValueError, TypeError):
            return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set the bit."""
        await self._set_bit(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Clear the bit."""
        await self._set_bit(False)

    async def _set_bit(self, on: bool) -> None:
        """Read current value, flip the bit, and write back."""
        raw = (self.coordinator.data or {}).get(CON_INPUT_SETTING, "0")
        try:
            current = int(raw)
        except (ValueError, TypeError):
            current = 0

        if on:
            new_val = current | self.entity_description.bit_mask
        else:
            new_val = current & ~self.entity_description.bit_mask

        await self._data.client.patch_con({CON_INPUT_SETTING: str(new_val)})
        await self.coordinator.async_request_refresh()


class AskoheatDstSwitch(AskoheatEntity, SwitchEntity):
    """Switch for daylight saving time (summertime bias)."""

    _attr_name = "Daylight saving time"

    def __init__(self, data: AskoheatData, host: str) -> None:
        """Initialize."""
        super().__init__(
            coordinator=data.slow_coordinator,
            par_data=data.par_data,
            host=host,
            key="dst_switch",
        )
        self._data = data

    @property
    def is_on(self) -> bool | None:
        """Return true if DST is enabled."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(CON_SUMMERTIME_BIAS)
        if raw is None:
            return None
        return str(raw) != "0"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable DST."""
        await self._data.client.patch_con({CON_SUMMERTIME_BIAS: "1"})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable DST."""
        await self._data.client.patch_con({CON_SUMMERTIME_BIAS: "0"})
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat switch entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]
    entities: list[SwitchEntity] = []

    for desc in BIT_SWITCH_DESCRIPTIONS:
        entities.append(AskoheatBitSwitch(data, host, desc))

    entities.append(AskoheatDstSwitch(data, host))

    async_add_entities(entities)
