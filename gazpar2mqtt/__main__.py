import sys
import argparse
import logging
import traceback
from gazpar2mqtt import __version__
from gazpar2mqtt import config_utils
from gazpar2mqtt.bridge import Bridge


# ----------------------------------
def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version",
                        action="version",
                        version="Gazpar2MQTT version")
    parser.add_argument("-c", "--config",
                        required=False,
                        default="config/configuration.yaml",
                        help="Path to the configuration file")
    parser.add_argument("-s", "--secrets",
                        required=False,
                        default="config/secrets.yaml",
                        help="Path to the secret file")

    try:
        args = parser.parse_args()

        # Load configuration files
        config = config_utils.ConfigLoader(args.config, args.secrets)
        config.load_secrets()
        config.load_config()

        print(f"Gazpar2MQTT version: {__version__}")

        # Set up logging
        logging_file = config.get("logging.file")
        logging_level = config.get("logging.level")
        logging_format = config.get("logging.format")

        # Convert logging level to integer
        if logging_level == "DEBUG":
            level = logging.DEBUG
        elif logging_level == "INFO":
            level = logging.INFO
        elif logging_level == "WARNING":
            level = logging.WARNING
        elif logging_level == "ERROR":
            level = logging.ERROR
        elif logging_level == "CRITICAL":
            level = logging.CRITICAL
        else:
            level = logging.INFO

        logging.basicConfig(filename=logging_file, level=level, format=logging_format)

        logging.info(f"Starting Gazpar2MQTT version {__version__}")

        # Log configuration
        logging.info(f"Configuration:\n{config.dumps()}")

        # Start the bridge
        bridge = Bridge(config)
        bridge.run()

        logging.info("Gazpar2MQTT stopped.")

        return 0

    except BaseException:
        errorMessage = f"An error occured while running Gazpar2MQTT: {traceback.format_exc()}"
        logging.error(errorMessage)
        print(errorMessage)
        return 1


# ----------------------------------
if __name__ == '__main__':
    sys.exit(main())
