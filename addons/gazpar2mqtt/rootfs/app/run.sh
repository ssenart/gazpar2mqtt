#!/usr/bin/with-contenv bashio

# Load the Add-on configuration in JSON and reformat it to YAML.
GRDF_JSON="'grdf': { 'scan_interval': $(bashio::addon.config 'scan_interval'), 'devices': $(bashio::addon.config 'devices') } }"""
GRDF_CONFIG=$(echo $GRDF_JSON | yq -P)

MQTT_JSON="{ 'mqtt': $(bashio::config 'mqtt') }"
MQTT_CONFIG=$(echo $MQTT_JSON | yq -P)

# Display environment variables
bashio::log.info "GRDF_CONFIG: ${GRDF_CONFIG}"
bashio::log.info "MQTT_CONFIG: ${MQTT_CONFIG}"

# Export environment variables
export GRDF_CONFIG MQTT_CONFIG

# Instantiate the template config
if [ ! -e /app/config/configuration.yaml ]; then
    envsubst < "/app/config/configuration.template.yaml" > "/app/config/configuration.yaml"
fi

# Display the configuration file: Uncomment below for debugging
# echo "Configuration file:"
# cat /app/config/configuration.yaml

# Run the gazpar2mqtt python program
cd /app

python3 -m gazpar2mqtt --config config/configuration.yaml --secrets config/secrets.yaml
