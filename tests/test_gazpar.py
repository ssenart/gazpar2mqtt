from gazpar2mqtt import config_utils, gazpar


def test_version():
    assert gazpar.__version__ is not None


def test_publish():
    # Load configuration
    config = config_utils.ConfigLoader("config/configuration.yaml", "config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    gazpar.publish(config)

    assert True
