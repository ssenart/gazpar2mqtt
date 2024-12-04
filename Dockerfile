# The builder image, used to build the virtual environment
FROM python:3.12-bookworm as builder

RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm as runtime

ARG GRDF_USERNAME
RUN if [ -z "$GRDF_USERNAME" ]; then echo "ERROR: GRDF_USERNAME is not set"; exit 1; fi
ENV GRDF_USERNAME=$GRDF_USERNAME

ARG GRDF_PASSWORD
RUN if [ -z "$GRDF_PASSWORD" ]; then echo "ERROR: GRDF_PASSWORD is not set"; exit 1; fi
ENV GRDF_PASSWORD=$GRDF_PASSWORD

ARG GRDF_PCE_IDENTIFIER
RUN if [ -z "$GRDF_PCE_IDENTIFIER" ]; then echo "ERROR: GRDF_PCE_IDENTIFIER is not set"; exit 1; fi
ENV GRDF_PCE_IDENTIFIER=$GRDF_PCE_IDENTIFIER

ARG GRDF_SCAN_INTERVAL=480
ENV GRDF_SCAN_INTERVAL=$GRDF_SCAN_INTERVAL

ARG GRDF_LAST_DAYS=720
ENV GRDF_LAST_DAYS=$GRDF_LAST_DAYS

ARG MQTT_HOST
RUN if [ -z "$MQTT_HOST" ]; then echo "ERROR: MQTT_HOST is not set"; exit 1; fi
ENV MQTT_HOST=$MQTT_HOST

ARG MQTT_PORT=1883
ENV MQTT_PORT=$MQTT_PORT

ARG MQTT_USERNAME=""
ENV MQTT_USERNAME=$MQTT_USERNAME

ARG MQTT_PASSWORD=""
ENV MQTT_PASSWORD=$MQTT_PASSWORD

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY gazpar2mqtt ./gazpar2mqtt
RUN  mkdir config
RUN  mkdir log
COPY config/configuration.template.yaml config
COPY config/secrets.template.yaml config
RUN  envsubst < config/configuration.template.yaml > config/configuration.yaml
RUN  envsubst < config/secrets.template.yaml > config/secrets.yaml

ENTRYPOINT ["python", "-m", "gazpar2mqtt"]