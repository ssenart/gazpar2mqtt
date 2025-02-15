import datetime
import json
import logging
import traceback
from typing import Any

import paho.mqtt.client as mqtt
import pygazpar  # type: ignore

from gazpar2mqtt import __version__


# ----------------------------------
class Gazpar:

    # ----------------------------------
    def __init__(self, config: dict[str, Any], mqqtt_client: mqtt.Client, mqtt_base_topic: str):
        self._config = config
        self._mqtt_device_name = config.get("name")
        self._mqtt_client = mqqtt_client
        self._mqtt_base_topic = mqtt_base_topic
        self._selectByFrequency = {
            pygazpar.Frequency.HOURLY: Gazpar._selectHourly,
            pygazpar.Frequency.DAILY: Gazpar._selectDaily,
            pygazpar.Frequency.WEEKLY: Gazpar._selectWeekly,
            pygazpar.Frequency.MONTHLY: Gazpar._selectMonthly,
            pygazpar.Frequency.YEARLY: Gazpar._selectYearly,
        }

    # ----------------------------------
    def name(self):
        return self._mqtt_device_name

    # ----------------------------------
    # Publish Gaspar data to MQTT
    def publish(self):

        # GrDF configuration
        grdf_username = self._config.get("username")
        grdf_password = self._config.get("password")
        grdf_pce_identifier = str(self._config.get("pce_identifier"))
        grdf_last_days = int(self._config.get("last_days"))

        # Read Gazpar data
        available = True
        try:
            data = self._read_pygazpar_data(grdf_username, grdf_password, grdf_pce_identifier, grdf_last_days)
        except Exception:  # pylint: disable=broad-except
            logging.warning(f"Error while fetching data from GrDF: {traceback.format_exc()}")
            data = {}
            available = False

        source = {"name": "gazpar2mqtt", "version": __version__}

        if available and data is not None and len(data) > 0:
            # Publish data to MQTT
            self._mqtt_client.publish(
                f"{self._mqtt_base_topic}/{self._mqtt_device_name}",
                json.dumps(
                    {
                        "volume": data[pygazpar.Frequency.DAILY.value][0][pygazpar.PropertyName.END_INDEX.value],
                        "energy": self._compute_energy(data[pygazpar.Frequency.DAILY.value]),
                        "temperature": data[pygazpar.Frequency.DAILY.value][0][pygazpar.PropertyName.TEMPERATURE.value],
                        "username": grdf_username,
                        "pce": grdf_pce_identifier,
                        "daily": (data.get(pygazpar.Frequency.DAILY.value) if not None else []),
                        "weekly": (data.get(pygazpar.Frequency.WEEKLY.value) if not None else []),
                        "monthly": (data.get(pygazpar.Frequency.MONTHLY.value) if not None else []),
                        "yearly": (data.get(pygazpar.Frequency.YEARLY.value) if not None else []),
                        "source": source,
                        "attribution": "Data provided by GrDF",
                        "timestamp": datetime.datetime.now().isoformat(),
                    }
                ),
                retain=True,
                qos=2,
            )

        # Publish availability
        self._publish_availability(available)

    # ----------------------------------
    def dispose(self):

        # Publish availability
        self._publish_availability(False)

    # ----------------------------------
    def _publish_availability(self, available: bool):

        self._mqtt_client.publish(
            f"{self._mqtt_base_topic}/{self._mqtt_device_name}/availability",
            json.dumps({"state": "online" if available else "offline"}),
            retain=True,
            qos=2,
        )

    # ----------------------------------
    def _read_pygazpar_data(
        self,
        grdf_username: str,
        grdf_password: str,
        grdf_pce_identifier: str,
        grdf_last_days: int,
    ) -> dict[str, Any]:

        # Initialize PyGazpar client
        client = pygazpar.Client(pygazpar.JsonWebDataSource(username=grdf_username, password=grdf_password))

        # Fetch gas meter data
        dataByFrequency = client.load_since(
            pce_identifier=grdf_pce_identifier,
            last_n_days=grdf_last_days,
            frequencies=[
                pygazpar.Frequency.DAILY,
                pygazpar.Frequency.WEEKLY,
                pygazpar.Frequency.MONTHLY,
                pygazpar.Frequency.YEARLY,
            ],
        )

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
    def _compute_energy(self, daily_data: dict[int, Any]) -> float | None:
        """Compute the energy consumption from the daily data."""

        res = None

        if daily_data is not None and len(daily_data) > 0:
            currentIndex = 0
            cumulativeEnergy = 0.0

            # For low consumption, we also use the energy column in addition to the volume index columns
            # and compute more accurately the consumed energy.
            startIndex = daily_data[currentIndex][pygazpar.PropertyName.START_INDEX.value]
            endIndex = daily_data[currentIndex][pygazpar.PropertyName.END_INDEX.value]

            while (
                (startIndex is not None)
                and (endIndex is not None)  # noqa: W503
                and (currentIndex < len(daily_data))  # noqa: W503
                and (float(startIndex) == float(endIndex))  # noqa: W503
            ):
                energy = daily_data[currentIndex][pygazpar.PropertyName.ENERGY.value]
                if energy is not None:
                    cumulativeEnergy += float(energy)
                currentIndex += 1
                if currentIndex < len(daily_data):
                    startIndex = daily_data[currentIndex][pygazpar.PropertyName.START_INDEX.value]
                    endIndex = daily_data[currentIndex][pygazpar.PropertyName.END_INDEX.value]

            currentIndex = min(currentIndex, len(daily_data) - 1)

            endIndex = daily_data[currentIndex][pygazpar.PropertyName.END_INDEX.value]
            converterFactorStr = daily_data[currentIndex][pygazpar.PropertyName.CONVERTER_FACTOR.value]

            if endIndex is not None:
                volumeEndIndex = float(endIndex)
            else:
                raise ValueError("End index is missing in the daily data.")

            if converterFactorStr is not None:
                converterFactor = float(converterFactorStr)
            else:
                raise ValueError("Converter factor is missing in the daily data.")

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
        return data[: Gazpar.MAX_DAILY_READINGS]

    # ----------------------------------
    @staticmethod
    def _selectWeekly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:

        res = []

        previousYearWeekDate = []

        index = 0
        for reading in data:

            weekDate = Gazpar._getIsoCalendar(reading["time_period"])

            if index < Gazpar.MAX_WEEKLY_READINGS / 2:

                weekDate = (weekDate.weekday, weekDate.week, weekDate.year - 1)

                previousYearWeekDate.append(weekDate)

                res.append(reading)
            else:
                if previousYearWeekDate.count((weekDate.weekday, weekDate.week, weekDate.year)) > 0:  # noqa: W503
                    res.append(reading)

            index += 1

        return res

    # ----------------------------------
    @staticmethod
    def _selectMonthly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data[: Gazpar.MAX_MONTHLY_READINGS]

    # ----------------------------------
    @staticmethod
    def _selectYearly(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return data[: Gazpar.MAX_YEARLY_READINGS]

    # ----------------------------------
    @staticmethod
    def _getIsoCalendar(weekly_time_period):

        date = datetime.datetime.strptime(weekly_time_period.split(" ")[1], Gazpar.DATE_FORMAT)

        return date.isocalendar()
