"""Coordinator for 17Track."""

from py17track import Client as SeventeenTrackClient

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class SeventeenTrackCoordinator(DataUpdateCoordinator[dict[str, int]]):
    """Class to manage fetching 17Track data."""

    def __init__(
        self, hass: HomeAssistant, client: SeventeenTrackClient, show_archived: bool
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._show_archived = show_archived
        self.api = client

    async def _async_update_data(self) -> dict[str, int]:
        """Fetch data from 17Track API."""

        summary = await self.hass.async_add_executor_job(
            self.api.profile.summary, self._show_archived
        )

        data = {}

        for status, quantity in summary.items():
            data[status.lower().replace(" ", "_")] = quantity

        return data
