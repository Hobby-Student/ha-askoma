"""Button platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import CMD_CLEAR_TEMP_SENSOR_ERROR, CMD_IDENTIFY, CMD_RESET
from .entity import AskoheatEntity

@dataclass(frozen=True, kw_only=True)
class AskoheatButtonDescription(ButtonEntityDescription):
    """Button description with command key."""

    cmd_key: str
    cmd_value: str = "1"


BUTTON_DESCRIPTIONS: tuple[AskoheatButtonDescription, ...] = (
    AskoheatButtonDescription(
        key="identify",
        translation_key="identify",
        name="Identify",
        device_class=ButtonDeviceClass.IDENTIFY,
        cmd_key=CMD_IDENTIFY,
    ),
    AskoheatButtonDescription(
        key="clear_sensor_errors",
        translation_key="clear_sensor_errors",
        name="Clear sensor errors",
        cmd_key=CMD_CLEAR_TEMP_SENSOR_ERROR,
    ),
    AskoheatButtonDescription(
        key="reboot",
        translation_key="reboot",
        name="Reboot",
        device_class=ButtonDeviceClass.RESTART,
        cmd_key=CMD_RESET,
    ),
)


class AskoheatButton(AskoheatEntity, ButtonEntity):
    """Button entity for Askoheat commands."""

    entity_description: AskoheatButtonDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatButtonDescription,
    ) -> None:
        """Initialize."""
        super().__init__(
            coordinator=data.ema_coordinator,
            par_data=data.par_data,
            host=host,
            key=description.key,
        )
        self.entity_description = description
        self._client = data.client

    async def async_press(self) -> None:
        """Handle the button press."""
        desc = self.entity_description
        await self._client.patch_ema({desc.cmd_key: desc.cmd_value})


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat button entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]

    async_add_entities(
        AskoheatButton(data, host, desc) for desc in BUTTON_DESCRIPTIONS
    )
