"""Binary sensor platform for the Askoheat integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AskoheatConfigEntry, AskoheatData
from .const import (
    EMA_EMERGENCY_MODE,
    EMA_HEAT_PUMP_REQUEST,
    EMA_STATUS,
    STATUS_RELAY1,
    STATUS_RELAY2,
    STATUS_RELAY3,
    VAL_ERROR_STATUS,
    VAL_LEGIO_STATUS,
)
from .entity import AskoheatEntity


@dataclass(frozen=True, kw_only=True)
class AskoheatBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Extended binary sensor description."""

    value_key: str
    is_on_fn: Callable[[str], bool]
    coordinator_type: str = "ema"  # "ema" or "slow"


def _is_255(val: str) -> bool:
    return val == "255"


def _bit_check(bit: int) -> Callable[[str], bool]:
    def check(val: str) -> bool:
        try:
            return bool(int(val) & bit)
        except (ValueError, TypeError):
            return False
    return check


def _is_nonzero(val: str) -> bool:
    return val != "0"


BINARY_SENSOR_DESCRIPTIONS: tuple[AskoheatBinarySensorEntityDescription, ...] = (
    AskoheatBinarySensorEntityDescription(
        key="emergency_mode",
        translation_key="emergency_mode",
        name="Emergency mode",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_key=EMA_EMERGENCY_MODE,
        is_on_fn=_is_255,
        coordinator_type="ema",
    ),
    AskoheatBinarySensorEntityDescription(
        key="heat_pump_request",
        translation_key="heat_pump_request",
        name="Heat pump request",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_key=EMA_HEAT_PUMP_REQUEST,
        is_on_fn=_is_255,
        coordinator_type="ema",
    ),
    AskoheatBinarySensorEntityDescription(
        key="heater_relay_1",
        translation_key="heater_relay_1",
        name="Heater relay 1",
        device_class=BinarySensorDeviceClass.POWER,
        value_key=EMA_STATUS,
        is_on_fn=_bit_check(STATUS_RELAY1),
        coordinator_type="ema",
    ),
    AskoheatBinarySensorEntityDescription(
        key="heater_relay_2",
        translation_key="heater_relay_2",
        name="Heater relay 2",
        device_class=BinarySensorDeviceClass.POWER,
        value_key=EMA_STATUS,
        is_on_fn=_bit_check(STATUS_RELAY2),
        coordinator_type="ema",
    ),
    AskoheatBinarySensorEntityDescription(
        key="heater_relay_3",
        translation_key="heater_relay_3",
        name="Heater relay 3",
        device_class=BinarySensorDeviceClass.POWER,
        value_key=EMA_STATUS,
        is_on_fn=_bit_check(STATUS_RELAY3),
        coordinator_type="ema",
    ),
    AskoheatBinarySensorEntityDescription(
        key="legionella_active",
        translation_key="legionella_active",
        name="Legionella protection active",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_key=VAL_LEGIO_STATUS,
        is_on_fn=_is_nonzero,
        coordinator_type="slow",
    ),
    AskoheatBinarySensorEntityDescription(
        key="error_status",
        translation_key="error_status",
        name="Error status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_key=VAL_ERROR_STATUS,
        is_on_fn=_is_nonzero,
        coordinator_type="slow",
    ),
)


class AskoheatBinarySensor(AskoheatEntity, BinarySensorEntity):
    """Binary sensor for the Askoheat integration."""

    entity_description: AskoheatBinarySensorEntityDescription

    def __init__(
        self,
        data: AskoheatData,
        host: str,
        description: AskoheatBinarySensorEntityDescription,
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
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self.entity_description.value_key)
        if raw is None:
            return None
        return self.entity_description.is_on_fn(str(raw))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Askoheat binary sensor entities."""
    data: AskoheatData = entry.runtime_data
    host: str = entry.data["host"]

    async_add_entities(
        AskoheatBinarySensor(data, host, desc)
        for desc in BINARY_SENSOR_DESCRIPTIONS
    )
