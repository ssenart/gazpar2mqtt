import pygazpar
import paho.mqtt.client as mqtt
import json
import datetime
import traceback
import logging
from gazpar2mqtt import __version__
from gazpar2mqtt import config_utils
from typing import Any


# ----------------------------------
availability_payload = [
    {
        "topic": "gazpar2mqtt/bridge/state",
        "value_template": "{{ value_json.state }}"
    },
    {
        "topic": "gazpar2mqtt/unknown/availability",
        "value_template": "{{ value_json.state }}"
    }
]

# ----------------------------------
device_payload = {
    "identifiers": ["gazpar2mqtt_unknown"],
    "manufacturer": "gazpar2mqtt",
    "model": "gazpar2mqtt",
    "name": "unknown",
    "sw_version": __version__,
    "via_device": "gazpar2mqtt_bridge",
}

# ----------------------------------
original_payload = {
    "name": "Gazpar2MQTT",
    "sw": __version__,
    "url": "https://github.com/ssenart/gazpar2mqtt",
}

# ----------------------------------
attribution = "Data provided by GrDF"


# ----------------------------------
class Gazpar:

    # ----------------------------------
    def __init__(self, config: config_utils.ConfigLoader, mqqtt_client: mqtt.Client, mqtt_base_topic: str, mqtt_device_name: str):
        self._config = config
        self._mqtt_client = mqqtt_client
        self._mqtt_base_topic = mqtt_base_topic
        self._mqtt_device_name = mqtt_device_name
        self._selectByFrequency = {
            pygazpar.Frequency.HOURLY: Gazpar._selectHourly,
            pygazpar.Frequency.DAILY: Gazpar._selectDaily,
            pygazpar.Frequency.WEEKLY: Gazpar._selectWeekly,
            pygazpar.Frequency.MONTHLY: Gazpar._selectMonthly,
            pygazpar.Frequency.YEARLY: Gazpar._selectYearly,
        }

    # ----------------------------------
    # Publish Gaspar data to MQTT
    def publish(self):

        # GrDF configuration
        grdf_username = self._config.get("grdf.username")
        grdf_password = self._config.get("grdf.password")
        grdf_pce_identifier = str(self._config.get("grdf.pce_identifier"))
        grdf_last_days = int(self._config.get("grdf.last_days"))

        # Home Assistant configuration
        ha_discovery = self._config.get("homeassistant.discovery")
        ha_discovery_topic = self._config.get("homeassistant.discovery_topic")
        ha_device_name = self._config.get("homeassistant.device_name")
        ha_device_unique_id = self._config.get("homeassistant.device_unique_id")

        # Read Gazpar data
        available = True
        try:
            data = self._read_pygazpar_data(grdf_username, grdf_password, grdf_pce_identifier, grdf_last_days)
        except Exception:
            errorMessage = f"Error while fetching data from GrDF: {traceback.format_exc()}"
            logging.warning(errorMessage)
            data = {}
            available = False

        availability_payload[0]["topic"] = f"{self._mqtt_base_topic}/bridge/availability"
        availability_payload[1]["topic"] = f"{self._mqtt_base_topic}/{self._mqtt_device_name}/availability"

        device_payload["identifiers"] = [f"{self._mqtt_base_topic}_{ha_device_unique_id}"]
        device_payload["name"] = ha_device_name

        if ha_discovery:
            # Publish Home Assistant discovery messages
            ha_payloads = self._config.get("homeassistant.payloads")
            for ha_entity, ha_payload in ha_payloads.items():
                ha_payload["availability"] = availability_payload
                ha_payload["unique_id"] = f"{ha_device_unique_id}_{ha_entity}_{self._mqtt_base_topic}"
                ha_payload["attribution"] = attribution
                ha_payload["device"] = device_payload
                ha_payload["origin"] = original_payload
                self._mqtt_client.publish(f'{ha_discovery_topic}/sensor/{ha_device_unique_id}/{ha_entity}/config', json.dumps(ha_payload), retain=True)

        if available and data is not None and len(data) > 0:
            # Publish data to MQTT
            self._mqtt_client.publish(f"{self._mqtt_base_topic}/{self._mqtt_device_name}", json.dumps(
                {
                    "volume": data[pygazpar.Frequency.DAILY.value][0][pygazpar.PropertyName.END_INDEX.value],
                    "energy": self._compute_energy(data[pygazpar.Frequency.DAILY.value]),
                    "temperature": data[pygazpar.Frequency.DAILY.value][0][pygazpar.PropertyName.TEMPERATURE.value],
                    "username": grdf_username,
                    "pce": grdf_pce_identifier,
                    "daily": data.get(pygazpar.Frequency.DAILY.value) if not None else [],
                    "weekly": data.get(pygazpar.Frequency.WEEKLY.value) if not None else [],
                    "monthly": data.get(pygazpar.Frequency.MONTHLY.value) if not None else [],
                    "yearly": data.get(pygazpar.Frequency.YEARLY.value) if not None else []
                }), retain=True, qos=2)

        # Publish availability
        self._publish_availability(available)

    # ----------------------------------
    def dispose(self):

        # Publish availability
        self._publish_availability(False)

    # ----------------------------------
    def _publish_availability(self, available: bool):

        self._mqtt_client.publish(f"{self._mqtt_base_topic}/{self._mqtt_device_name}/availability", json.dumps({"state": "online" if available else "offline"}), retain=True, qos=2)

    # ----------------------------------
    def _read_pygazpar_data(self, grdf_username: str, grdf_password: str, grdf_pce_identifier: str, grdf_last_days: int) -> dict[str, Any]:

        # Initialize PyGazpar client
        client = pygazpar.Client(pygazpar.JsonWebDataSource(username=grdf_username, password=grdf_password))

        # Fetch gas meter data
        dataByFrequency = client.loadSince(pceIdentifier=grdf_pce_identifier, lastNDays=grdf_last_days, frequencies=[pygazpar.Frequency.DAILY, pygazpar.Frequency.WEEKLY, pygazpar.Frequency.MONTHLY, pygazpar.Frequency.YEARLY])

        # PyGazpar delivers data sorted by ascending dates.
        # Below, we reverse the order. We want most recent at the top.
        # And we select a subset of the readings by frequency.
        for frequency in pygazpar.Frequency:
            data = dataByFrequency.get(frequency.value)

            if data is not None and len(data) > 0:
                dataByFrequency[frequency.value] = self._selectByFrequency[frequency](data[::-1])
            else:
                dataByFrequency[frequency.value] = []

        return dataByFrequency

    # ----------------------------------
    def _compute_energy(self, daily_data: dict[str, Any]) -> float:
        """Compute the energy consumption from the daily data."""

        res = None

        if daily_data is not None and len(daily_data) > 0:
            currentIndex = 0
            cumulativeEnergy = 0.0

            # For low consumption, we also use the energy column in addition to the volume index columns
            # and compute more accurately the consumed energy.
            while (currentIndex < len(daily_data)) and (float(daily_data[currentIndex][pygazpar.PropertyName.START_INDEX.value]) == float(daily_data[currentIndex][pygazpar.PropertyName.END_INDEX.value])):
                cumulativeEnergy += float(daily_data[currentIndex][pygazpar.PropertyName.ENERGY.value])
                currentIndex += 1

            currentIndex = min(currentIndex, len(daily_data) - 1)

            volumeEndIndex = float(daily_data[currentIndex][pygazpar.PropertyName.END_INDEX.value])
            converterFactor = float(daily_data[currentIndex][pygazpar.PropertyName.CONVERTER_FACTOR.value])

            res = volumeEndIndex * converterFactor + cumulativeEnergy

        return res

    # ----------------------------------
    MAX_DAILY_READINGS = 14
    MAX_WEEKLY_READINGS = 20
    MAX_MONTHLY_READINGS = 24
    MAX_YEARLY_READINGS = 5

    DATE_FORMAT = "%d/%m/%Y"

    # ----------------------------------
    @staticmethod
    def _selectHourly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data

    # ----------------------------------
    @staticmethod
    def _selectDaily(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data[:Gazpar.MAX_DAILY_READINGS]

    # ----------------------------------
    @staticmethod
    def _selectWeekly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:

        res = []

        previousYearWeekDate = []

        index = 0
        for reading in data:

            weekDate = Gazpar._getIsoCalendar(reading["time_period"])

            if (index < Gazpar.MAX_WEEKLY_READINGS / 2):

                weekDate = (weekDate.weekday, weekDate.week, weekDate.year - 1)

                previousYearWeekDate.append(weekDate)

                res.append(reading)
            else:
                if (previousYearWeekDate.count((weekDate.weekday, weekDate.week, weekDate.year)) > 0):
                    res.append(reading)

            index += 1

        return res

    # ----------------------------------
    @staticmethod
    def _selectMonthly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data[:Gazpar.MAX_MONTHLY_READINGS]

    # ----------------------------------
    @staticmethod
    def _selectYearly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data[:Gazpar.MAX_YEARLY_READINGS]

    # ----------------------------------
    @staticmethod
    def _getIsoCalendar(weekly_time_period):

        date = datetime.datetime.strptime(weekly_time_period.split(" ")[1], Gazpar.DATE_FORMAT)

        return date.isocalendar()
