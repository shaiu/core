"""Support for package tracking sensors from 17track.net."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_SHOW_ARCHIVED, CONF_SHOW_DELIVERED, DOMAIN
from .coordinator import SeventeenTrackCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SHOW_ARCHIVED, default=False): cv.boolean,
        vol.Optional(CONF_SHOW_DELIVERED, default=False): cv.boolean,
    }
)

ISSUE_PLACEHOLDER = {"url": "/config/integrations/dashboard/add?domain=seventeentrack"}

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="delivered",
        translation_key="delivered",
    ),
    SensorEntityDescription(
        key="expired",
        translation_key="expired",
    ),
    SensorEntityDescription(
        key="in_transit",
        translation_key="in_transit",
    ),
    SensorEntityDescription(
        key="not_found",
        translation_key="not_found",
    ),
    SensorEntityDescription(
        key="ready_to_be_picked_up",
        translation_key="ready_to_be_picked_up",
    ),
    SensorEntityDescription(
        key="returned",
        translation_key="returned",
    ),
    SensorEntityDescription(
        key="undelivered",
        translation_key="undelivered",
    ),
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Initialize 17Track import from config."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_IMPORT}, data=config
    )
    if (
        result["type"] == FlowResultType.CREATE_ENTRY
        or result["reason"] == "already_configured"
    ):
        async_create_issue(
            hass,
            HOMEASSISTANT_DOMAIN,
            f"deprecated_yaml_{DOMAIN}",
            is_fixable=False,
            breaks_in_ha_version="2024.10.0",
            severity=IssueSeverity.WARNING,
            translation_key="deprecated_yaml",
            translation_placeholders={
                "domain": DOMAIN,
                "integration_title": "17Track",
            },
        )
    else:
        async_create_issue(
            hass,
            DOMAIN,
            f"deprecated_yaml_import_issue_{result['reason']}",
            breaks_in_ha_version="2024.10.0",
            is_fixable=False,
            issue_domain=DOMAIN,
            severity=IssueSeverity.WARNING,
            translation_key=f"deprecated_yaml_import_issue_{result['reason']}",
            translation_placeholders=ISSUE_PLACEHOLDER,
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a 17Track sensor entry."""

    coordinator: SeventeenTrackCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    assert config_entry.unique_id
    unique_id = config_entry.unique_id

    async_add_entities(
        SeventeenTrackSummarySensor(unique_id, description, coordinator)
        for description in SENSOR_TYPES
    )


class SeventeenTrackSummarySensor(
    CoordinatorEntity[SeventeenTrackCoordinator], SensorEntity
):
    """Define a summary sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:package"
    _attr_native_unit_of_measurement = "packages"

    def __init__(
        self,
        unique_id: str,
        description: SensorEntityDescription,
        coordinator: SeventeenTrackCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
