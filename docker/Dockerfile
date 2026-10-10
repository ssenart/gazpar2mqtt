# The builder image, used to build the virtual environment
FROM python:3.12-bookworm AS builder

RUN pip install uv==0.13.0

# The virtual environment is created in /app/.venv with the Python of the image, from the locked versions.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./
COPY LICENSE ./

COPY gazpar2mqtt/ /app/gazpar2mqtt

RUN uv sync --locked --no-dev

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm AS runtime

# Environment variables
# GRDF_USERNAME: The username to use to authenticate to the GRDF API
# GRDF_PASSWORD: The password to use to authenticate to the GRDF API
# GRDF_PCE_IDENTIFIER: The identifier of the PCE to use to fetch the data
# GRDF_SCAN_INTERVAL: The interval in minutes between two scans of the GRDF API
# GRDF_LAST_DAYS: The number of days to fetch when fetching the data
# MQTT_BROKER: The hostname of the MQTT broker
# MQTT_PORT: The port of the MQTT broker
# MQTT_USERNAME: The username to use to authenticate to the MQTT broker
# MQTT_PASSWORD: The password to use to authenticate to the MQTT broker

# Install the required system dependencies: envsubst
RUN apt-get update && apt-get install -y gettext-base

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY docker/entrypoint.sh /app
RUN  chmod +x /app/entrypoint.sh
COPY gazpar2mqtt/ /app/gazpar2mqtt
RUN  mkdir /app/config
RUN  mkdir /app/log
COPY README.md /app
COPY CHANGELOG.md /app
COPY LICENSE /app
COPY config/configuration.template.yaml /app
COPY config/secrets.template.yaml /app

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
