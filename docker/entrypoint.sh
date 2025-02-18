#!/bin/sh

# Check/Set default values to optional environment variables
: "${GRDF_USERNAME:?GRDF_USERNAME is required and not set.}"
: "${GRDF_PASSWORD:?GRDF_PASSWORD is required and not set.}"
: "${GRDF_PCE_IDENTIFIER:?GRDF_PCE_IDENTIFIER is required and not set.}"
: "${GRDF_SCAN_INTERVAL:="480"}" # 8 hours
: "${GRDF_LAST_DAYS:="1095"}" # 3 years

: "${MQTT_BROKER:?MQTT_BROKER is required and not set.}"
: "${MQTT_PORT:="1883"}" # Default MQTT port
: "${MQTT_USERNAME:="\"\""}" # No user
: "${MQTT_PASSWORD:="\"\""}" # No password

# Display environment variables
echo "GRDF_USERNAME: ${GRDF_USERNAME}"
echo "GRDF_PASSWORD: ***************"
echo "GRDF_PCE_IDENTIFIER: ${GRDF_PCE_IDENTIFIER}"
echo "GRDF_SCAN_INTERVAL: ${GRDF_SCAN_INTERVAL}"
echo "GRDF_LAST_DAYS: ${GRDF_LAST_DAYS}"
echo "MQTT_BROKER: ${MQTT_BROKER}"
echo "MQTT_PORT: ${MQTT_PORT}"
echo "MQTT_USERNAME: ${MQTT_USERNAME}"
echo "MQTT_PASSWORD: ***************"

# Export environment variables
export GRDF_USERNAME GRDF_PASSWORD GRDF_PCE_IDENTIFIER GRDF_SCAN_INTERVAL GRDF_LAST_DAYS MQTT_BROKER MQTT_PORT MQTT_USERNAME MQTT_PASSWORD

# Instantiate the template config
if [ ! -e /app/config/configuration.yaml ]; then
    envsubst < "/app/configuration.template.yaml" > "/app/config/configuration.yaml"
fi

# Instantiate the template secrets
if [ ! -e /app/config/secrets.yaml ]; then
    envsubst < "/app/secrets.template.yaml" > "/app/config/secrets.yaml"
fi

# Run the gazpar2mqtt python program
cd /app

python3 -m gazpar2mqtt --config config/configuration.yaml --secrets config/secrets.yaml
