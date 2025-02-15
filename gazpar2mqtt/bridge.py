import json
import logging
import signal
import time

import paho.mqtt.client as mqtt

from gazpar2mqtt import config_utils
from gazpar2mqtt.gazpar import Gazpar
from gazpar2mqtt.homeassistant import HomeAssistant


# ----------------------------------
class Bridge:

    # ----------------------------------
    def __init__(self, config: config_utils.ConfigLoader):

        # GrDF scan interval (in seconds)
        self._grdf_scan_interval = int(config.get("grdf.scan_interval"))

        # MQTT configuration
        self._mqtt_broker = config.get("mqtt.broker")
        self._mqtt_port = int(config.get("mqtt.port"))
        mqtt_username = config.get("mqtt.username")
        mqtt_password = config.get("mqtt.password")
        self._mqtt_keepalive = int(config.get("mqtt.keepalive"))

        self._mqtt_base_topic = config.get("mqtt.base_topic")

        # Initialize MQTT client
        self._mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self._mqtt_client.username_pw_set(mqtt_username, mqtt_password)

        # Set up MQTT callbacks
        self._mqtt_client.on_connect = self.on_connect
        self._mqtt_client.on_disconnect = self.on_disconnect

        # Initialize Gazpar
        self._gazpar = list[Gazpar]()
        for grdf_device_config in config.get("grdf.devices"):
            self._gazpar.append(Gazpar(grdf_device_config, self._mqtt_client, self._mqtt_base_topic))

        # Initialize Home Assistant
        self._homeassistant = HomeAssistant(config, self._mqtt_client, self._mqtt_base_topic)

        # Set up signal handler
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        # Initialize running flag
        self._running = False

    # ----------------------------------
    def on_connect(self, client, userdata, flags, rc):  # pylint: disable=unused-argument
        logging.info(f"Connected to MQTT broker with result code {rc}")

    # ----------------------------------
    def on_disconnect(self, client, userdata, rc):  # pylint: disable=unused-argument
        logging.info("Disconnected from broker")

    # ----------------------------------
    # Graceful shutdown function
    def handle_signal(self, signum, frame):  # pylint: disable=unused-argument
        print(f"Signal {signum} received. Shutting down gracefully...")
        logging.info(f"Signal {signum} received. Shutting down gracefully...")
        self._running = False

    # ----------------------------------
    def run(self):

        # Start the network loop in a separate thread
        logging.info("Connecting to MQTT broker...")
        self._mqtt_client.connect(self._mqtt_broker, self._mqtt_port, self._mqtt_keepalive)
        self._mqtt_client.loop_start()
        logging.info("Connected to MQTT broker.")

        # Set running flag
        self._running = True

        try:
            while self._running:
                # Publish Gazpar data to MQTT
                logging.info("Publishing Gazpar data to MQTT...")
                device_names = list[str]()
                for gazpar in self._gazpar:
                    logging.info(f"Publishing data for device '{gazpar.name()}'...")
                    gazpar.publish()
                    device_names.append(gazpar.name())
                    logging.info(f"Device '{gazpar.name()}' data published to MQTT.")

                logging.info("Publishing Home Assistant data to MQTT...")
                self._homeassistant.publish(device_names)
                logging.info("Home Assistant data published to MQTT.")

                logging.info("Gazpar data published to MQTT.")

                # Publish bridge availability
                self._mqtt_client.publish(
                    f"{self._mqtt_base_topic}/bridge/availability",
                    json.dumps({"state": "online"}),
                    retain=True,
                    qos=2,
                )

                # Wait before next scan
                logging.info(f"Waiting {self._grdf_scan_interval} minutes before next scan...")

                # Check if the scan interval is 0 and leave the loop.
                if self._grdf_scan_interval == 0:
                    break

                self._await_with_interrupt(self._grdf_scan_interval * 60, 5)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Shutting down gracefully...")
            logging.info("Keyboard interrupt detected. Shutting down gracefully...")
        finally:
            # Publish bridge availability
            self._mqtt_client.publish(
                f"{self._mqtt_base_topic}/bridge/availability",
                json.dumps({"state": "offline"}),
                retain=True,
                qos=2,
            )

            self.dispose()

    # ----------------------------------
    def dispose(self):
        # Dispose of Gazpar.
        for gazpar in self._gazpar:
            gazpar.dispose()

        # Stop the network loop
        logging.info("Disconnecting from MQTT broker...")
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()
        logging.info("Disconnected from MQTT broker.")

    # ----------------------------------
    def _await_with_interrupt(self, total_sleep_time: int, check_interval: int):
        elapsed_time = 0
        while elapsed_time < total_sleep_time:
            time.sleep(check_interval)
            elapsed_time += check_interval
            # Check if an interrupt signal or external event requires breaking
            if not self._running:  # Assuming `running` is a global flag
                break
