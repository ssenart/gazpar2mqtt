import socket
import threading

import pytest

from gazpar2mqtt import config_utils
from gazpar2mqtt.bridge import Bridge


# ----------------------------------
# Minimal fake MQTT broker: answers the first connection with the given CONNACK result code
def _fake_broker(connack_rc: int) -> int:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)

    def serve():
        conn, _ = server.accept()
        with conn:
            conn.recv(1024)  # CONNECT packet
            conn.sendall(bytes([0x20, 0x02, 0x00, connack_rc]))  # CONNACK packet
            # Keep the connection open until the client sends DISCONNECT (0xE0 0x00), then close it as a broker does
            received = b""
            while not received.endswith(b"\xe0\x00"):
                chunk = conn.recv(1024)
                if not chunk:
                    break
                received += chunk
        server.close()

    threading.Thread(target=serve, daemon=True).start()
    return server.getsockname()[1]


# ----------------------------------
def _config(port: int) -> config_utils.ConfigLoader:
    config = config_utils.ConfigLoader()
    config.config = {
        "grdf": {"scan_interval": 0, "devices": []},
        "mqtt": {
            "broker": "127.0.0.1",
            "port": port,
            "username": "",
            "password": "",
            "keepalive": 60,
            "base_topic": "gazpar2mqtt",
        },
        "homeassistant": {"discovery": False},
    }
    return config


# ----------------------------------
def test_run_succeeds_when_broker_accepts_connection():
    bridge = Bridge(_config(_fake_broker(connack_rc=0)))
    bridge.run()


# ----------------------------------
def test_run_fails_when_broker_refuses_connection():
    bridge = Bridge(_config(_fake_broker(connack_rc=5)))

    with pytest.raises(ConnectionRefusedError, match="not authorised"):
        bridge.run()


# ----------------------------------
def test_run():

    # Load configuration
    config = config_utils.ConfigLoader("tests/config/configuration.yaml", "tests/config/secrets.yaml")
    config.load_secrets()
    config.load_config()

    bridge = Bridge(config)
    bridge.run()
