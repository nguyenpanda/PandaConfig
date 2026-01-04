import yaml
from pathlib import Path
from typing import Any, Optional


class ConfigLoader:
    
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path).resolve()
          
    def load(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f'Config file not found: {self.config_path}')

        try:
            with open(self.config_path, 'r', encoding='utf-8') as bf:
                current_data = yaml.safe_load(bf) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML file {self.config_path}: {e}")
        
        override_file = current_data.pop('override', None)
        
        if override_file:
            parent_path = self.config_path.parent / override_file
            base_data = ConfigLoader(parent_path).load()
            return self._deep_update(base_data, current_data)
        
        return current_data

    def _deep_update(self, base_dict: dict, update_dict: dict) -> dict:
        for key, value in update_dict.items():
            if (
                key in base_dict 
                and isinstance(base_dict[key], dict) 
                and isinstance(value, dict)
            ):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(base={self.config_path.absolute()})'
        