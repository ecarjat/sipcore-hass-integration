

import logging
from hashlib import sha256
from pathlib import Path
from homeassistant.components.lovelace.resources import (
    ResourceStorageCollection,
    ResourceYAMLCollection,
)
from homeassistant.const import CONF_ID, CONF_URL
from homeassistant.components.lovelace.const import (
    CONF_RESOURCE_TYPE_WS,
    DOMAIN as LL_DOMAIN,
)
from .const import JS_URL_PATH
from homeassistant.core import HomeAssistant


logger = logging.getLogger(__name__)


def resource_url() -> str:
    """Return a cache-busting URL for the compiled frontend module."""
    asset = Path(__file__).parent / "www" / "sip_core.js"
    digest = sha256(asset.read_bytes()).hexdigest()[:12]
    return f"{JS_URL_PATH}?v={digest}"


async def add_resources(hass: HomeAssistant):
    """Add SIP Core resources to Lovelace."""

    resources: ResourceStorageCollection | ResourceYAMLCollection | None = None
    if lovelace_data := hass.data.get(LL_DOMAIN):
        resources = lovelace_data.resources
    if resources:
        if not resources.loaded:
            await resources.async_load()
            logger.debug("Manually loaded resources")
            resources.loaded = True

        resource = next(
            (data for data in resources.async_items() if data[CONF_URL].split("?", 1)[0] == JS_URL_PATH),
            None,
        )
        res_id = resource[CONF_ID] if resource else None
        versioned_url = resource_url()

        if res_id is None:
            logger.info("Registering SIP Core module in Lovelace resources")
            if isinstance(resources, ResourceYAMLCollection):
                logger.warning("SIP Core module not registered because resources are managed via YAML")
                return False # TODO: Return error for user?
            else:
                data = await resources.async_create_item(
                    {CONF_RESOURCE_TYPE_WS: "module", CONF_URL: versioned_url}
                )
                logger.debug(f"Registered SIP Core module with resource ID {data[CONF_ID]}")
        elif resource[CONF_URL] != versioned_url and isinstance(resources, ResourceStorageCollection):
            logger.info("Updating SIP Core module URL to refresh the frontend cache")
            await resources.async_delete_item(res_id)
            data = await resources.async_create_item(
                {CONF_RESOURCE_TYPE_WS: "module", CONF_URL: versioned_url}
            )
            logger.debug(f"Updated SIP Core module resource ID {data[CONF_ID]}")
        else:
            logger.debug(f"module already registered with resource ID {res_id}")


async def remove_resources(hass: HomeAssistant):
    """Remove SIP Core resources from Lovelace."""

    resources: ResourceStorageCollection | ResourceYAMLCollection | None = None
    if lovelace_data := hass.data.get(LL_DOMAIN):
        resources = lovelace_data.resources
    if resources:
        if not resources.loaded:
            await resources.async_load()
            logger.debug("Manually loaded resources for unload")
            resources.loaded = True

        res_id = next(
            (
                data[CONF_ID]
                for data in resources.async_items()
                if data[CONF_URL].split("?", 1)[0] == JS_URL_PATH
            ),
            None,
        )

        if res_id is not None and isinstance(resources, ResourceStorageCollection):
            logger.info("Removing SIP Core module from Lovelace resources")
            await resources.async_delete_item(res_id)
        else:
            logger.debug("SIP Core module resource not found during unload")
