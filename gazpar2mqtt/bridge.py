import logging
import time
import signal
import paho.mqtt.client as mqtt
from gazpar2mqtt import config_utils
from gazpar2mqtt.gazpar import Gazpar


# ----------------------------------
class Bridge:

    # ----------------------------------
    def __init__(self, config: config_utils.ConfigLoader):

        # GrDF scan interval (in seconds)
        self._grdf_scan_interval = config.get("grdf.scan_interval")

        # MQTT configuration
        self._mqtt_broker = config.get("mqtt.broker")
        self._mqtt_port = int(config.get("mqtt.port"))
        mqtt_username = config.get("mqtt.username")
        mqtt_password = config.get("mqtt.password")
        self._mqtt_keepalive = int(config.get("mqtt.keepalive"))

        mqtt_base_topic = config.get("mqtt.base_topic")
        mqtt_device_name = config.get("mqtt.device_name")

        # Initialize MQTT client
        self._mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self._mqtt_client.username_pw_set(mqtt_username, mqtt_password)

        # Set up MQTT callbacks
        self._mqtt_client.on_connect = self.on_connect
        self._mqtt_client.on_disconnect = self.on_disconnect

        # Set up signal handler
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        # Initialize Gazpar
        self._gaspar = Gazpar(config, self._mqtt_client, mqtt_base_topic, mqtt_device_name)

        # Initialize running flag
        self._running = False

    # ----------------------------------
    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected to MQTT broker with result code {rc}")

    # ----------------------------------
    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from broker")

    # ----------------------------------
    # Graceful shutdown function
    def handle_signal(self, signum, frame):
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
                self._gaspar.publish()
                logging.info("Gazpar data published to MQTT.")

                # Wait before next scan
                logging.info(f"Waiting {self._grdf_scan_interval} seconds before next scan...")

                self._await_with_interrupt(self._grdf_scan_interval, 5)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Shutting down gracefully...")
            logging.info("Keyboard interrupt detected. Shutting down gracefully...")
        finally:
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
