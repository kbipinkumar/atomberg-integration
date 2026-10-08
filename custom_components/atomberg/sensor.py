"""Support for sensor entities of Atomberg integration."""

from logging import getLogger

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AtombergDataUpdateCoordinator
from .device import (
    ATTR_CHOKING_FAULTS,
    ATTR_INPUT_TDS,
    ATTR_SYSTEM_FAULTS,
    ATTR_TANK_TDS,
    ATTR_TIMER_HOURS,
    ATTR_TIMER_TIME_ELAPSED_MINS,
    AtombergDevice,
)
from .entity import AtombergEntity, platform_async_setup_entry

_LOGGER = getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Automatically setup the sensor entities from the devices list."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        TimerElapsedTimeSensor,
        filter_func=lambda d: d.series != "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierInputTdsSensor,
        filter_func=lambda d: d.series == "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierTankTdsSensor,
        filter_func=lambda d: d.series == "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierChokingFaultSensor,
        filter_func=lambda d: d.series == "W2"
    )

    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        AtombergPurifierSystemFaultSensor,
        filter_func=lambda d: d.series == "W2"
    )


class TimerElapsedTimeSensor(AtombergEntity, SensorEntity):
    """Timer elapsed time sensor entity."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)

        self._attr_unique_id = self._get_unique_id(
            Platform.SENSOR, suffix="timer_elapsed_time"
        )
        self._attr_name = self._device.name + " timer elapsed time"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_native_unit_of_measurement = "min"

    @property
    def icon(self) -> str:
        """Get icon dynamically."""
        icons = [
            "mdi:clock-time-twelve-outline",
            "mdi:clock-time-one-outline",
            "mdi:clock-time-two-outline",
            "mdi:clock-time-three-outline",
            "mdi:clock-time-four-outline",
            "mdi:clock-time-five-outline",
            "mdi:clock-time-six-outline",
            "mdi:clock-time-seven-outline",
            "mdi:clock-time-eight-outline",
            "mdi:clock-time-nine-outline",
            "mdi:clock-time-ten-outline",
            "mdi:clock-time-eleven-outline",
        ]
        timer_mins = self.device_state.get(ATTR_TIMER_HOURS, 0) * 60
        if not timer_mins:
            return icons[0]

        value = self.native_value or 0
        return icons[round(value / timer_mins * (len(icons) - 1))]

    @property
    def native_value(self) -> int:
        """Get value in minutes."""
        return self.device_state.get(ATTR_TIMER_TIME_ELAPSED_MINS, 0)


class AtombergPurifierInputTdsSensor(AtombergEntity, SensorEntity):
    """Input TDS sensor entity for Atomberg Water Purifier."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)

        self._attr_unique_id = self._get_unique_id(
            Platform.SENSOR, suffix="input_tds"
        )
        self._attr_name = self._device.name + " input TDS"
        self._attr_icon = "mdi:water-opacity"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Get value in ppm."""
        return self.device_state.get(ATTR_INPUT_TDS)


class AtombergPurifierTankTdsSensor(AtombergEntity, SensorEntity):
    """Tank TDS sensor entity for Atomberg Water Purifier."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)

        self._attr_unique_id = self._get_unique_id(
            Platform.SENSOR, suffix="tank_tds"
        )
        self._attr_name = self._device.name + " tank TDS"
        self._attr_icon = "mdi:water-opacity"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Get value in ppm."""
        return self.device_state.get(ATTR_TANK_TDS)


class AtombergPurifierChokingFaultSensor(AtombergEntity, SensorEntity):
    """Choking faults sensor entity for Atomberg Water Purifier."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)
        self._attr_unique_id = self._get_unique_id(Platform.SENSOR, suffix="choking_faults")
        self._attr_name = self._device.name + " choking faults"
        self._attr_icon = "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str | None:
        """Get value."""
        val = self.device_state.get(ATTR_CHOKING_FAULTS)
        if not val:
            return None
        if val.get("healthy"):
            return "Healthy"
        return ", ".join(val.get("codes", [])) or "Unknown Fault"


class AtombergPurifierSystemFaultSensor(AtombergEntity, SensorEntity):
    """System faults sensor entity for Atomberg Water Purifier."""

    def __init__(
        self, coordinator: AtombergDataUpdateCoordinator, device: AtombergDevice
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, device, _LOGGER)
        self._attr_unique_id = self._get_unique_id(Platform.SENSOR, suffix="system_faults")
        self._attr_name = self._device.name + " system faults"
        self._attr_icon = "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str | None:
        """Get value."""
        val = self.device_state.get(ATTR_SYSTEM_FAULTS)
        if not val:
            return None
        if val.get("healthy"):
            return "Healthy"
        return ", ".join(val.get("codes", [])) or "Unknown Fault"
