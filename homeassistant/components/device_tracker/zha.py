"""
Device tracker on Zigbee Home Automation networks.

For more details on this platform, please refer to the documentation
at https://home-assistant.io/components/device_tracker.zha/
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.components.device_tracker import DOMAIN
from homeassistant.components import zha

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['zha']


@asyncio.coroutine
def async_setup_scanner(hass, config, async_see, discovery_info=None):
    """Set up Zigbee Home Automation sensors."""
    discovery_info = zha.get_discovery_info(hass, discovery_info)
    if discovery_info is None:
        return

    tracker = ZhaDeviceTracker(async_see, **discovery_info)
    yield from tracker.async_update()

    return True


class ZhaDeviceTracker(zha.Entity):
    """Zha device tracker."""
    _domain = DOMAIN

    def __init__(self, async_see, **kwargs):
        """Initialize the Tracker."""
        self._async_see = async_see
        super().__init__(**kwargs)

    @asyncio.coroutine
    def async_update(self) -> None:
        """Update the device info."""
        dev_id = self.entity_id.split(".", 1)[1]
        name = None
        if 'friendly_name' in self._device_state_attributes:
            name = self._device_state_attributes['friendly_name']

        _LOGGER.debug('Updating %s', dev_id)

        yield from self._async_see(
            dev_id=dev_id,
            host_name=name,
            consider_home=timedelta(seconds=60)
        )

    def cluster_command(self, tsn, command_id, args):
        """Handle a cluster command received on this cluster."""
        asyncio.ensure_future(self.async_update())
