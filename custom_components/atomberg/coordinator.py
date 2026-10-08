"""Data update coordinator for the Atomberg integration."""

from datetime import timedelta
from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import utcnow

from .api import AtombergCloudAPI
from .const import MANUFACTURER
from .device import AtombergDevice
from .udp_listener import UDPListener

_LOGGER = getLogger(__name__)


class AtombergDataUpdateCoordinator(DataUpdateCoordinator):
    """Atomberg data update coordinator."""

    def __init__(
        self, hass: HomeAssistant, api: AtombergCloudAPI, udp_listener: UDPListener
    ) -> None:
        """Init data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{MANUFACTURER} Coordinator",
        )

        self.api = api
        self.udp_listener = udp_listener
        self.devices = [
            AtombergDevice(data=data, api=self.api, config_entry=self.config_entry)
            for data in self.api.device_list.values()
        ]

        # Add callback on udp listener
        self.udp_listener.add_callback(self.config_entry, self.async_set_updated_data)

        # Setup independent cloud polling
        self.hass.async_create_task(self.async_refresh())
        self._unsub_cloud_poll = async_track_time_interval(
            self.hass,
            self._async_poll_cloud,
            timedelta(minutes=60),
        )
        if self.config_entry:
            self.config_entry.async_on_unload(self._unsub_cloud_poll)

    async def _async_poll_cloud(self, now=None):
        """Timer callback to fetch data from API endpoint."""
        await self.async_refresh()

    async def _async_update_data(self):
        """Fetch data from API endpoint for devices that don't broadcast UDP."""
        try:
            polled_devices = [dev for dev in self.devices if dev.series == "W2"]
            if not polled_devices:
                return {"polled": True}

            states = await self.api.async_get_device_state(
                [dev.id for dev in polled_devices]
            )
            if states:
                for state in states:
                    device = next(
                        (d for d in polled_devices if d.id == state["device_id"]), None
                    )
                    if device:
                        if device.ip_address:
                            state["ip_address"] = device.ip_address
                        device.update_state({**state, "is_online": True})
                        device.update_last_seen(utcnow().timestamp())
        except Exception as err:
            _LOGGER.error("Failed to poll cloud data: %s", err)

        return {"polled": True}
