import json
import logging

import paho.mqtt.client as mqtt

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
    def publish(self):

        # Home Assistant configuration
        ha_discovery = bool(self._config.get("homeassistant.discovery"))

        if not ha_discovery:
            return

        ha_discovery_topic = self._config.get("homeassistant.discovery_topic")

        # Publish Home Assistant device messages
        for ha_device_config in self._config.get("homeassistant.devices"):
            ha_device_name = ha_device_config.get("device_name")
            ha_device_unique_id = ha_device_config.get("device_unique_id")

            logging.info(
                f"Publishing Home Assistant device '{ha_device_name}' with unique ID '{ha_device_unique_id}'"
            )

            availability_payload[0][
                "topic"
            ] = f"{self._mqtt_base_topic}/bridge/availability"
            availability_payload[1][
                "topic"
            ] = f"{self._mqtt_base_topic}/{ha_device_name}/availability"

            device_payload["identifiers"] = [
                f"{self._mqtt_base_topic}_{ha_device_unique_id}"
            ]
            device_payload["name"] = ha_device_name

            # Publish Home Assistant entity messages
            ha_payloads = ha_device_config.get("payloads")
            for ha_entity, ha_payload in ha_payloads.items():

                logging.info(
                    f"Publishing Home Assistant entity '{ha_entity}' of device '{ha_device_name}'"
                )

                ha_payload["availability"] = availability_payload
                ha_payload["availability_mode"] = "all"
                ha_payload["unique_id"] = (
                    f"{ha_device_unique_id}_{ha_entity}_{self._mqtt_base_topic}"
                )
                ha_payload["attribution"] = attribution
                ha_payload["device"] = device_payload
                ha_payload["origin"] = origin_payload
                self._mqtt_client.publish(
                    f"{ha_discovery_topic}/sensor/{ha_device_unique_id}/{ha_entity}/config",
                    json.dumps(ha_payload),
                    retain=True,
                )
