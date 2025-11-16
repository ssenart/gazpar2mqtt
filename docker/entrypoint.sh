#!/bin/sh

# Instantiate the template config
if [ ! -e /app/config/configuration.yaml ]; then
    cp "/app/configuration.template.yaml" "/app/config/configuration.yaml"
fi

# Instantiate the template secrets
if [ ! -e /app/config/secrets.yaml ]; then
    cp "/app/secrets.template.yaml" "/app/config/secrets.yaml"
fi

# Run the gazpar2mqtt python program
cd /app

python3 -m gazpar2mqtt --config config/configuration.yaml --secrets config/secrets.yaml
