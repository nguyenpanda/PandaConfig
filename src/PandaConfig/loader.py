import json
import yaml
from pathlib import Path
from typing import Any, Callable, Dict, Union, Optional

ParserFunc = Callable[[Path], Dict[str, Any]]

class ConfigLoader:
    
    _parsers: Dict[str, ParserFunc] = {}

    def __init__(self, config_path: Union[str, Path]):
        self.config_path = Path(config_path).resolve()
        
        if not self._parsers:
            self._register_defaults()

    @classmethod
    def register_parser(cls, extension: str, parser: ParserFunc) -> None:
        '''
        Register a custom parser for a specific file extension.
        
        Args:
            extension: The file extension (e.g., '.toml').
            parser: A function that takes a Path and returns a dict.
        '''
        cls._parsers[extension.lower()] = parser

    def load(self) -> Dict[str, Any]:
        '''
        Load the configuration file, resolving any 'extends' inheritance.
        '''
        if not self.config_path.exists():
            raise FileNotFoundError(f'Config file not found: {self.config_path}')

        parser = self._get_parser(self.config_path)
        try:
            current_data = parser(self.config_path)
        except Exception as e:
            raise RuntimeError(f'Failed to load config {self.config_path}: {e}') from e

        extend_file = current_data.pop('extends', None)
        
        if extend_file:
            parent_path = self.config_path.parent / extend_file
            parent_loader = ConfigLoader(parent_path)
            base_data = parent_loader.load()
            return self._deep_update(base_data, current_data)
        
        return current_data
    
    @classmethod
    def _register_defaults(cls) -> None:
        cls.register_parser('.yaml', cls._parse_yaml)
        cls.register_parser('.yml', cls._parse_yaml)
        cls.register_parser('.json', cls._parse_json)

    @staticmethod
    def _parse_yaml(file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f'Invalid YAML in {file_path}: {e}')

    @staticmethod
    def _parse_json(file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f) or {}
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in {file_path}: {e}')

    def _get_parser(self, file_path: Path) -> ParserFunc:
        ext = file_path.suffix.lower()
        parser = self._parsers.get(ext)
        
        if not parser:
            supported = ', '.join(self._parsers.keys())
            raise ValueError(f'Unsupported file extension \'{ext}\' for {file_path}. Supported: {supported}')
        
        return parser

    @staticmethod
    def _deep_update(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in update.items():
            if (
                key in base 
                and isinstance(base[key], dict) 
                and isinstance(value, dict)
            ):
                ConfigLoader._deep_update(base[key], value)
            else:
                base[key] = value
        return base

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} path=\'{self.config_path}\'>'
    