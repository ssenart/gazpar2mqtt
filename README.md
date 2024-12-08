# Gazpar2MQTT
Gazpar2MQTT is a gateway that reads data from the GrDF (French gas provider) meter and posts it to a MQTT queue.

It is compatible with [Lovelace Garpar Card](https://github.com/ssenart/lovelace-gazpar-card) with version >= 1.3.11-alpha.3.

![Lovelace Garpar Card](images/gazpar-card.png)

Gazpar2MQTT is using [PyGazpar](https://github.com/ssenart/PyGazpar) library to retrieve GrDF data.

## Installation

Gazpar2MQTT can be installed on any host as a standalone program. However, the preferred way is to use its Docker container.

### 1. Using source files

The project requires [Poetry](https://python-poetry.org/) tool for dependency and package management.

```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2mqtt.git

$ cd gazpar2mqtt

$ poetry install

$ poetry shell

```

### 2. Using PIP package

```sh
$ cd /path/to/my_install_folder/

$ mkdir gazpar2mqtt

$ cd gazpar2mqtt

$ python -m venv .venv

$ source .venv/bin/activate

$ pip install gazpar2mqtt

```

### 3. Using Dockerfile

The following steps permit to build the Docker image based on the local source files.

1. Clone the repo locally:
```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2mqtt.git
```
2. Edit the docker-compose.yaml file by setting the environment variables corresponding to your GrDF account and MQTT setup:

```yaml
    environment:
      - GRDF_USERNAME=<GrDF account username>
      - GRDF_PASSWORD=<GrDF account password>
      - GRDF_PCE_IDENTIFIER=<GrDF PCE meter identifier>
      - MQTT_BROKER=<MQTT broker ip adcress>
```
3. Build the image:
```sh
$ docker compose build
```
4. Run the container:
```sh
$ docker compose up -d
```

### 4. Using Docker Hub

The following steps permits to run a container from an existing image available in the Docker Hub repository.

1. Copy and save the following docker-compose.yaml file:

```yaml
services:
  gazpar2mqtt:
    image: ssenart/gazpar2mqtt:latest  
    container_name: gazpar2mqtt
    restart: unless-stopped
    network_mode: bridge
    user: "1000:1000"    
    volumes:
      - ./gazpar2mqtt/config:/app/config
      - ./gazpar2mqtt/log:/app/log
    environment:
      - GRDF_USERNAME=<GrDF account username>
      - GRDF_PASSWORD=<GrDF account password>
      - GRDF_PCE_IDENTIFIER=<GrDF PCE meter identifier>
      - MQTT_BROKER=<MQTT broker ip adcress>
```

Edit the environment variable section according to your setup.

2. Run the container:
```sh
$ docker compose up -d
```

## Usage

### Command line

```sh
$ python -m gazpar2mqtt --config /path/to/configuration.yaml --secrets /path/to/secrets.yaml
```

### Configuration file

The default configuration file is below.

```yaml
logging:
  file: log/gazpar2mqtt.log
  console: true  
  level: debug
  format: '%(asctime)s %(levelname)s [%(name)s] %(message)s'

grdf:
  scan_interval: ${GRDF_SCAN_INTERVAL} # Number of minutes between each data retrieval (0 means no scan: a single data retrieval at startup, then stops).
  devices:
  - name: gazpar
    username: "!secret grdf.username"
    password: "!secret grdf.password"
    pce_identifier: "!secret grdf.pce_identifier"
    last_days: ${GRDF_LAST_DAYS} # Number of days of data to retrieve

mqtt:
  broker: "!secret mqtt.broker"
  port: "!secret mqtt.port"
  username: "!secret mqtt.username"
  password: "!secret mqtt.password"
  keepalive: 60
  base_topic: gazpar2mqtt

homeassistant:
  discovery: true
  discovery_topic: homeassistant
  devices:    
  - device_name: gazpar
    device_unique_id: "0x52e31847e180405"
    payloads:
      card: 
        object_id: gazpar_card
        device_class: energy
        enabled_by_default: true
        icon: mdi:fire
        state_class: total_increasing
        state_topic: gazpar2mqtt/gazpar
        unit_of_measurement: kWh
        json_attributes_topic: gazpar2mqtt/gazpar
        value_template: "{{ value_json.energy }}"

      energy: 
        object_id: gazpar_energy
        device_class: energy
        enabled_by_default: true
        icon: mdi:fire
        state_class: total_increasing
        state_topic: gazpar2mqtt/gazpar
        unit_of_measurement: kWh
        value_template: "{{ value_json.energy }}"

      volume: 
        object_id: gazpar_volume
        device_class: gas
        enabled_by_default: true
        icon: mdi:fire
        state_class: total_increasing
        state_topic: gazpar2mqtt/gazpar
        unit_of_measurement: "m³"
        value_template: "{{ value_json.volume }}"
      
      temperature: 
        object_id: gazpar_temperature
        device_class: temperature
        enabled_by_default: true
        icon: mdi:thermometer
        state_class: measurement
        state_topic: gazpar2mqtt/gazpar
        unit_of_measurement: "°C"
        value_template: "{{ value_json.temperature }}"   
```

The default secret file:

```yaml
grdf.username: ${GRDF_USERNAME}
grdf.password: ${GRDF_PASSWORD}
grdf.pce_identifier: ${GRDF_PCE_IDENTIFIER}

mqtt.broker: ${MQTT_BROKER}
mqtt.port: ${MQTT_PORT}
mqtt.username: ${MQTT_USERNAME}
mqtt.password: ${MQTT_PASSWORD}
```

### Environment variable for Docker

In a Docker environment, the configurations files are instantiated by replacing the environment variables below in the template files:

| Environment variable | Description | Required | Default value |
|---|---|---|---|
| GRDF_USERNAME  |  GrDF account user name  | Yes | - |
| GRDF_PASSWORD  |  GrDF account password (avoid using special characters) | Yes | - |
| GRDF_PCE_IDENTIFIER  | GrDF meter PCI identifier  | Yes | - |
| GRDF_SCAN_INTERVAL  | Period in minutes to refresh meter data (0 means one single refresh and stop) | No | 480 (8 hours) |
| GRDF_LAST_DAYS | Number of days of history data to retrieve  | No | 1095 (3 years) |
| MQTT_BROKER  | MQTT broker IP address  | Yes | - |
| MQTT_BROKER  | MQTT broker port number  | No | 1883 |
| MQTT_USERNAME  | MQTT broker account user name  | No | "" |
| MQTT_PASSWORD  | MQTT broker account password  | No | "" |

You can setup them directly in a docker-compose.yaml file (environment section) or from a Docker command line (-e option).

## Publish a new image on Docker Hub

1. List all local images

```sh
$ docker image ls
```

2. Build a new local image

```sh
$ docker compose build
```

3. Tag the new built image with the version number

```sh
$ docker image tag ssenart/gazpar2mqtt:latest ssenart/gazpar2mqtt:0.1.0
```

4. Login in Docker Hub

```sh
$ docker login
```

5. Push all the tagged local images to Docker Hub

```sh
$ docker push --all-tags ssenart/gazpar2mqtt
```

All the gazpar2mqtt images are available [here](https://hub.docker.com/repository/docker/ssenart/gazpar2mqtt/general).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Project status
Gazpar2MQTT has been initiated for integration with [Home Assistant](https://www.home-assistant.io/).

Since it relies on MQTT, it can be used with any other Home Controllers that works with MQTT technology.

A compatible Home Assistant Lovelace Card is available [here](https://github.com/ssenart/lovelace-gazpar-card)

An alternative is using Home Assistant integration custom component available [here](https://github.com/ssenart/home-assistant-gazpar).

