"""Base entities for the Askoheat integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_info import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    PAR_ARTICLE_NAME,
    PAR_ARTICLE_NUMBER,
    PAR_HARDWARE_VERSION,
    PAR_ID,
    PAR_SOFTWARE_VERSION,
)


class AskoheatEntity(CoordinatorEntity):
    """Base class for Askoheat entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        par_data: dict[str, Any],
        host: str,
        key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._par_data = par_data
        self._host = host
        serial = par_data.get(PAR_ID, host)
        self._attr_unique_id = f"{serial}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        serial = self._par_data.get(PAR_ID, self._host)
        return DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=self._par_data.get(PAR_ARTICLE_NAME, "Askoheat"),
            manufacturer="Askoma AG",
            model=self._par_data.get(PAR_ARTICLE_NUMBER),
            sw_version=self._par_data.get(PAR_SOFTWARE_VERSION),
            hw_version=self._par_data.get(PAR_HARDWARE_VERSION),
            serial_number=serial,
            configuration_url=f"http://{self._host}/",
        )
