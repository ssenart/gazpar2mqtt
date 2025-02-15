import hashlib
import json
import logging

import paho.mqtt.client as mqtt
from jinja2 import Template

from gazpar2mqtt import __version__, config_utils

# ----------------------------------
availability_payload = [
    {
        "topic": "gazpar2mqtt/bridge/availability",
        "value_template": "{{ value_json.state }}",
    },
    {
        "topic": "gazpar2mqtt/unknown/availability",
        "value_template": "{{ value_json.state }}",
    },
]

# ----------------------------------
device_payload = {
    "identifiers": ["gazpar2mqtt_unknown"],
    "manufacturer": "gazpar2mqtt",
    "model": "gazpar2mqtt",
    "name": "unknown",
    "sw_version": __version__,
    "via_device": "gazpar2mqtt",
}

# ----------------------------------
origin_payload = {
    "name": "Gazpar2MQTT",
    "sw_version": __version__,
    "support_url": "https://github.com/ssenart/gazpar2mqtt",
}

# ----------------------------------
attribution = "Data provided by GrDF"


# ----------------------------------
class HomeAssistant:  # pylint: disable=too-few-public-methods

    # ----------------------------------
    def __init__(
        self,
        config: config_utils.ConfigLoader,
        mqqtt_client: mqtt.Client,
        mqtt_base_topic: str,
    ):
        self._config = config
        self._mqtt_client = mqqtt_client
        self._mqtt_base_topic = mqtt_base_topic

    # ----------------------------------
    # Publish HomeAssistant data to MQTT
    def publish(self, device_names: list[str]) -> None:

        # Home Assistant configuration
        ha_discovery = bool(self._config.get("homeassistant.discovery"))

        if not ha_discovery:
            return

        ha_discovery_topic = self._config.get("homeassistant.discovery_topic")

        # Publish Home Assistant device messages
        for ha_device_name in device_names:
            ha_device_unique_id = HomeAssistant._generate_unique_objectid(ha_device_name)

            logging.info(f"Publishing Home Assistant device '{ha_device_name}' with unique ID '{ha_device_unique_id}'")

            availability_payload[0]["topic"] = f"{self._mqtt_base_topic}/bridge/availability"
            availability_payload[1]["topic"] = f"{self._mqtt_base_topic}/{ha_device_name}/availability"

            device_payload["identifiers"] = [f"{self._mqtt_base_topic}_{ha_device_unique_id}"]
            device_payload["name"] = ha_device_name

            # Publish Home Assistant entity messages
            ha_payloads = self._config.get("homeassistant.entities")

            for ha_entity, ha_payload in ha_payloads.items():

                payload = ha_payload.copy()

                logging.info(f"Publishing Home Assistant entity '{ha_entity}' of device '{ha_device_name}'")
                payload["object_id"] = f"{ha_device_name}_{ha_entity}"
                if payload.get("state_topic") is not None:
                    template = Template(payload["state_topic"])
                    payload["state_topic"] = template.render(
                        mqtt_base_topic=self._mqtt_base_topic,
                        device_name=ha_device_name,
                    )
                if payload.get("json_attributes_topic") is not None:
                    template = Template(payload["json_attributes_topic"])
                    payload["json_attributes_topic"] = template.render(
                        mqtt_base_topic=self._mqtt_base_topic,
                        device_name=ha_device_name,
                    )
                payload["state_topic"] = f"{self._mqtt_base_topic}/{ha_device_name}"
                payload["availability"] = availability_payload
                payload["availability_mode"] = "all"
                payload["unique_id"] = f"{ha_device_unique_id}_{ha_entity}_{self._mqtt_base_topic}"
                payload["attribution"] = attribution
                payload["device"] = device_payload
                payload["origin"] = origin_payload
                self._mqtt_client.publish(
                    f"{ha_discovery_topic}/sensor/{ha_device_unique_id}/{ha_entity}/config",
                    json.dumps(payload),
                    retain=True,
                )

    # ----------------------------------
    # Generate an unique objectid of the device
    @staticmethod
    def _generate_unique_objectid(device_name: str) -> str:

        # Compute SHA-256 hash and take the first 8 bytes for a short result
        hash_bytes = hashlib.sha256(device_name.encode()).digest()[:8]

        # Convert bytes to an integer, then format it as hex with "0x" prefix
        res = f"0x{int.from_bytes(hash_bytes, 'big'):x}"

        return res
