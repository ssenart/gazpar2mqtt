#!/bin/sh

# # Set the default UID and GID for the appuser
# UID=${UID:-1000}  # Default UID
# GID=${GID:-1000}  # Default GID

# # Create a group and user with the provided UID and GID
# groupadd -g $GID appgroup 2>/dev/null || true
# useradd -m -u $UID -g $GID -d /app appuser 2>/dev/null || true

# # Change ownership of the home directory
# chown -R appuser:appgroup /app

# # Switch to the appuser
# exec su - appuser -c "$*"

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
echo "UID: $(id -u)"
echo "GID: $(id -g)"
# echo "UID: ${UID}"
# echo "GID: ${GID}"

# Export environment variables
export GRDF_USERNAME GRDF_PASSWORD GRDF_PCE_IDENTIFIER GRDF_SCAN_INTERVAL GRDF_LAST_DAYS MQTT_BROKER MQTT_PORT MQTT_USERNAME MQTT_PASSWORD

# Instantiate the template config
envsubst < "/app/configuration.template.yaml" > "/app/config/configuration.yaml"
envsubst < "/app/secrets.template.yaml" > "/app/config/secrets.yaml"

# Run the gazpar2mqtt python program
cd /app
python3 -m gazpar2mqtt
