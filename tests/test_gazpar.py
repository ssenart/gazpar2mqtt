import paho.mqtt.client as mqtt

import gazpar2mqtt
from gazpar2mqtt import config_utils
from gazpar2mqtt.gazpar import Gazpar


def test_version():
    assert gazpar2mqtt.__version__ is not None


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

    grdf_device_config = config.get("grdf.devices")[0]

    gazpar = Gazpar(grdf_device_config, mqtt_client, mqtt_base_topic)

    gazpar.publish()

    mqtt_client.loop_stop()
    mqtt_client.disconnect()

    assert True
