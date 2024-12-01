from gazpar2mqtt import config_utils, gazpar2mqtt


def test_publish():
    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    gazpar2mqtt.publish(config)

    assert True
