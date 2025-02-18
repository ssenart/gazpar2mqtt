from gazpar2mqtt import config_utils
from gazpar2mqtt.bridge import Bridge


def test_run():

    # Load configuration
    config = config_utils.ConfigLoader("tests/config/configuration.yaml", "tests/config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    bridge = Bridge(config)
    bridge.run()
