import paho.mqtt.client as mqtt

from gazpar2mqtt import config_utils
from gazpar2mqtt.homeassistant import HomeAssistant


# ----------------------------------
def test_publish():

    # Load configuration
    config = config_utils.ConfigLoader(
        "tests/config/configuration.yaml", "tests/config/secrets.yaml"
    )
    config.load_secrets()
    config.load_config()

    # MQTT configuration
    mqtt_broker = config.get("mqtt.broker")
    mqtt_port = int(config.get("mqtt.port"))
    mqtt_username = config.get("mqtt.username")
    mqtt_password = config.get("mqtt.password")
    mqtt_keepalive = int(config.get("mqtt.keepalive"))
    mqtt_base_topic = config.get("mqtt.base_topic")

    # Initialize MQTT client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)

    mqtt_client.connect(mqtt_broker, mqtt_port, mqtt_keepalive)
    mqtt_client.loop_start()

    bridge = HomeAssistant(config, mqtt_client, mqtt_base_topic)
    bridge.publish(["maison", "appartement"])


# ----------------------------------
def test_generate_objectid():

    unique_id = HomeAssistant._generate_unique_objectid(
        "test"
    )  # pylint: disable=protected-access

    assert unique_id == "0x9f86d081884c7d65"
