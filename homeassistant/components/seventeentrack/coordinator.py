"""Coordinator for 17Track."""

from py17track import Client as SeventeenTrackClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_SHOW_ARCHIVED, DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class SeventeenTrackCoordinator(DataUpdateCoordinator[dict[str, int]]):
    """Class to manage fetching 17Track data."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, client: SeventeenTrackClient, entry: ConfigEntry
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._show_archived = entry.options[CONF_SHOW_ARCHIVED]
        self.client = client
        self.entry = entry

    async def _async_update_data(self) -> dict[str, int]:
        """Fetch data from 17Track API."""

        summary = await self.client.profile.summary(self._show_archived)

        data = {}

        for status, quantity in summary.items():
            data[status.lower().replace(" ", "_")] = quantity

        return data
