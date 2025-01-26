# Home Assistant Add-on: Gazpar2MQTT add-on

## Configuration

The configuration permits to define multiple devices if you have multiple GrDF meters (meter1 and meter2 in the example above).

```yaml
  scan_interval: 480 # Number of minutes between each data retrieval (0 means no scan: a single data retrieval at startup, then stops).
  devices:
    - name: meter1 # Name of the device in home assistant. It will be used as the entity_id: sensor.{{name}}.
      username: "" # Email address used to connect to the GrDF website.
      password: "" # Password used to connect to the GrDF website.
      pce_identifier: "" # PCE identifier of the meter. It should be a positive integer.
      last_days: 365 # Number of days of data to retrieve
    - name: meter2 # Name of the device in home assistant. It will be used as the entity_id: sensor.{{name}}.
      username: "" # Email address used to connect to the GrDF website.
      password: "" # Password used to connect to the GrDF website.
      pce_identifier: "" # PCE identifier of the meter. It should be a positive integer.
      last_days: 365 # Number of days of data to retrieve      
  mqtt:
    broker: "core-mosquitto" # MQTT broker IP address/hotname or mosquitto addon (see https://developers.home-assistant.io/docs/add-ons/communication/)
    port: 1883 # MQTT broker port.
    username: ""
    password: ""
    keepalive: 60
    base_topic: gazpar2mqtt
```

| Name                     | Description                                                                                                                                      | Required | Default value |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | -------- | ------------- |
| scan_interval            | Period in minutes to refresh meter data (0 means one single refresh and stop)                                                                    | No       | 480 (8 hours) |
| devices[].name           | Name of the device in Home Assistant                                                                                                             | Yes      | -             |
| devices[].username       | GrDF account user name                                                                                                                           | Yes      | -             |
| devices[].password       | GrDF account password (avoid using special characters)                                                                                           | Yes      | -             |
| devices[].pce_identifier | GrDF meter PCE identifier                                                                                                                        | Yes      | -             |
| devices[].last_days      | Number of days of history data to retrieve                                                                                                       | No       | 365 days      |
| mqtt[].broker            | MQTT broker IP address/hotname or mosquitto addon (see https://developers.home-assistant.io/docs/add-ons/communication/)                             | No       | "core-mosquitto" |
| mqtt[].port              | MQTT broker port number                                                                                                                               | No       | 1883|
| mqtt[].username          | MQTT broker user name                             | No       | "" |
| mqtt[].password          | MQTT broker password                            | No       | "" |
| mqtt[].keepalive         | MQTT broker keepalive                             | No       | 60 |
| mqtt[].base_topic        | MQTT base topic                             | No       | "gazpar2mqtt" |


