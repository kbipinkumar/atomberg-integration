"""Support for select entities of Atomberg integration."""

from logging import getLogger

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AtombergDataUpdateCoordinator
from .device import (
    ATTR_FALLBACK_MODE,
    ATTR_MODE,
    ATTR_TIMER_HOURS,
    TIMER_MAPPING,
    AtombergDevice,
)
from .entity import AtombergEntity, platform_async_setup_entry

_LOGGER = getLogger(__name__)

PURIFIER_MODE_MAPPING = {
    0: "RO_ONLY",
    1: "ADAPTIVE",
    2: "TasteTune 50-100",
    3: "TasteTune 75-125",
    4: "TasteTune 100-150",
    10: "Vacay"
}

PURIFIER_FALLBACK_MODE_MAPPING = {
    0: "RO_ONLY",
    2: "TasteTune 50-100",
    3: "TasteTune 75-125",
    4: "TasteTune 100-150"
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Automatically setup the select entities from the devices list."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        SetTimerSelect,
        filter_func=lambda d: d.series != "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierModeSelect,
        filter_func=lambda d: d.series == "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierFallbackModeSelect,
        filter_func=lambda d: d.series == "W2"
    )


class SetTimerSelect(AtombergEntity, SelectEntity):
    """Set timer select entity."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)

        self._attr_unique_id = self._get_unique_id(Platform.SELECT, suffix="set_timer")
        self._attr_name = self._device.name + " set timer"
        self._attr_icon = "mdi:av-timer"
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def options(self) -> list[str]:
        """Get the available options."""
        return [_t[1] for _t in TIMER_MAPPING]

    @property
    def current_option(self) -> str:
        """Get the current option."""
        val = self.device_state.get(ATTR_TIMER_HOURS, 0)
        return next(filter(lambda _t: _t[0] == val, TIMER_MAPPING))[1]

    async def async_select_option(self, option: str) -> None:
        """When selected an option."""
        await self._device.async_set_timer(self.options.index(option))
        self.update_ha_state_if_required()


class AtombergPurifierModeSelect(AtombergEntity, SelectEntity):
    """Select entity for purifier mode."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)
        self._attr_unique_id = self._get_unique_id(Platform.SELECT, suffix="mode")
        self._attr_name = self._device.name + " mode"
        self._attr_icon = "mdi:water"
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def options(self) -> list[str]:
        """Get the available options."""
        return list(PURIFIER_MODE_MAPPING.values())

    @property
    def current_option(self) -> str:
        """Get the current option."""
        val = self.device_state.get(ATTR_MODE)
        return PURIFIER_MODE_MAPPING.get(val)

    async def async_select_option(self, option: str) -> None:
        """When selected an option."""
        for k, v in PURIFIER_MODE_MAPPING.items():
            if v == option:
                await self._device.async_set_purifier_mode(k)
                self.update_ha_state_if_required()
                return


class AtombergPurifierFallbackModeSelect(AtombergEntity, SelectEntity):
    """Select entity for purifier fallback mode."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)
        self._attr_unique_id = self._get_unique_id(Platform.SELECT, suffix="fallback_mode")
        self._attr_name = self._device.name + " fallback mode"
        self._attr_icon = "mdi:water-outline"
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def options(self) -> list[str]:
        """Get the available options."""
        return list(PURIFIER_FALLBACK_MODE_MAPPING.values())

    @property
    def current_option(self) -> str:
        """Get the current option."""
        val = self.device_state.get(ATTR_FALLBACK_MODE)
        return PURIFIER_FALLBACK_MODE_MAPPING.get(val)

    async def async_select_option(self, option: str) -> None:
        """When selected an option."""
        for k, v in PURIFIER_FALLBACK_MODE_MAPPING.items():
            if v == option:
                await self._device.async_set_purifier_fallback_mode(k)
                self.update_ha_state_if_required()
                return
