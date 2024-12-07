# gazpar2mqtt
Gateway that read GrDF meter data and publish them on MQTT queue.

It can be run as a standalone python program.

The preferred way is to use its Docker container.

## Installation

### Using source files

The project requires [Poetry](https://python-poetry.org/) tool for dependency and package management.

```sh
$ cd /path/to/my_install_folder/

$ git clone https://github.com/ssenart/gazpar2mqtt.git

$ cd gazpar2mqtt

$ poetry install

$ poetry shell

```

### Using PIP package

```sh
$ cd /path/to/my_install_folder/

$ mkdir gazpar2mqtt

$ cd gazpar2mqtt

$ python -m venv .venv

$ source .venv/bin/activate

$ pip install gazpar2mqtt

```

### Using Dockerfile

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
$ docker-compose up -d
```

### Using Docker Hub

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

Edit its environment variables section according to your setup.

2. Run the container:
```sh
$ docker-compose up -d
```

## Usage