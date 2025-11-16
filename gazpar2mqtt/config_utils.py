import os

import yaml


class ConfigLoader:
    def __init__(self, config_file="config.yaml", secrets_file="secrets.yaml"):
        self.config_file = config_file
        self.secrets_file = secrets_file
        self.config = {}
        self.secrets = {}

    def load_secrets(self):
        """Load the secrets file."""
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, "r", encoding="utf-8") as file:
                self.secrets = yaml.safe_load(file)
        else:
            raise FileNotFoundError(f"Secrets file '{self.secrets_file}' not found.")

    def load_config(self, env_defaults: dict = {}):
        """Load the main configuration file and resolve secrets."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as file:
                self.config = yaml.safe_load(file)
            self.config = self._resolve_secrets(self.config)
            self.config = self._resolve_env_vars(self.config, env_defaults)
        else:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")

    def _resolve_secrets(self, data):
        """Recursively resolve `!secret` keys in the configuration."""
        if isinstance(data, dict):
            return {key: self._resolve_secrets(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._resolve_secrets(item) for item in data]
        if isinstance(data, str) and data.startswith("!secret"):
            secret_key = data.split(" ", 1)[1]
            if secret_key in self.secrets:
                return self.secrets[secret_key]
            raise KeyError(f"Secret key '{secret_key}' not found in secrets file.")
        return data
    
    def _resolve_env_vars(self, data, env_defaults: dict):
        """Recursively resolve `${ENV_VAR}` in the configuration."""
        if isinstance(data, dict):
            return {key: self._resolve_env_vars(value, env_defaults) for key, value in data.items()}
        if isinstance(data, list):
            return [self._resolve_env_vars(item, env_defaults) for item in data]
        if isinstance(data, str):
            data = data.strip()
            start = data.find("${")
            end = data.find("}", start)
            while start != -1 and end != -1:
                env_var = data[start + 2:end]
                env_value = os.getenv(env_var, env_defaults.get(env_var, None))
                # "" is a valid value, None means not found
                if env_value is None:
                    raise KeyError(f"Environment variable '{env_var}' not found.")
                
                if not isinstance(env_value, str):
                    # env variables are strings, but just in case you provided something else in env_defaults...
                    env_value = str(env_value)
                data = data[:start] + env_value + data[end + 1:]
                start = data.find("${")
                end = data.find("}", start)
        return data

    def get(self, key, default=None):
        """Get a configuration value."""
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            if value is None:
                return default
            if isinstance(value, str):
                # make sure strings are not empty or "none"/"null"
                value = value.strip()  # Remove leading/trailing whitespace, just to be sure
                if len(value) == 0 or value.lower() == "none" or value.lower() == "null":
                    return default
                return value
            else:
                return value
        except (KeyError, TypeError):
            return default

    def dumps(self) -> str:
        """ Dump the configuration as a YAML string, sanitizing sensitive information."""
    
        def sanitize(data, key: str | None = None):
            """ Recursively sanitize sensitive information in the configuration data. """
            if isinstance(data, dict):
                return {key: sanitize(value, key) for key, value in data.items()}
            if isinstance(data, list):
                return [sanitize(item) for item in data]
            if key is not None and (("password" in key.lower()) or ("token" in key.lower()) or ("secret" in key.lower())):
                return "******"
            return data

        # make a copy of the dict to avoid modifying the original config
        sanitized_config = sanitize(self.config)

        return yaml.dump(sanitized_config)
