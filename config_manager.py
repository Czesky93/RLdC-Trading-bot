import json
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            raise FileNotFoundError("Configuration file not found.")
        with open(self.config_file, 'r') as file:
            return json.load(file)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any):
        self.config_data[key] = value
        self._save_config()

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config_data, file, indent=4)

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        # Implement specific validation logic here
        # Example: check for required fields
        required_fields = ['api_key', 'api_secret']
        return all(field in config for field in required_fields)

    @staticmethod
    def secure_secret_handling(secret: str) -> str:
        # Placeholder for secure secret handling logic
        # Example: return an obfuscated version of the secret
        return "***REDACTED***"
        
# Backward compatibility adapter
class BackwardCompatibilityAdapter:
    def __init__(self, legacy_config: Dict[str, Any]):
        self.legacy_config = legacy_config

    def get_legacy_value(self, key: str) -> Any:
        # Implement logic to retrieve values from legacy config
        return self.legacy_config.get(key)

# Example usage
if __name__ == '__main__':
    config_manager = ConfigManager('config.json')
    if ConfigManager.validate_config(config_manager.config_data):
        api_key = ConfigManager.secure_secret_handling(config_manager.get('api_key'))
        print(f'Configured API Key: {api_key}')
    else:
        print('Invalid configuration. Please check the settings.');
