"""Support for number entities of Atomberg integration."""

from logging import getLogger

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AtombergDataUpdateCoordinator
from .device import ATTR_TDS_THRESHOLD, AtombergDevice
from .entity import AtombergEntity, platform_async_setup_entry

_LOGGER = getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Automatically setup the number entities from the devices list."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierTdsThresholdNumber,
        filter_func=lambda d: d.series == "W2",
    )


class AtombergPurifierTdsThresholdNumber(AtombergEntity, NumberEntity):
    """TDS Threshold number entity for Atomberg Water Purifier."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)

        self._attr_unique_id = self._get_unique_id(
            Platform.NUMBER, suffix="tds_threshold"
        )
        self._attr_name = self._device.name + " TDS threshold"
        self._attr_icon = "mdi:water-percent"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_native_min_value = 100
        self._attr_native_max_value = 300
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "ppm"

    @property
    def native_value(self) -> float | None:
        """Return the current TDS threshold."""
        return self.device_state.get(ATTR_TDS_THRESHOLD)

    async def async_set_native_value(self, value: float) -> None:
        """Update the TDS threshold."""
        await self._device.async_set_purifier_tds_threshold(int(value))
        self.update_ha_state_if_required()
