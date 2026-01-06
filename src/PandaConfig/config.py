from .loader import ConfigLoader
from .resolver import ConfigResolver
from .default_func import DEFAULT_FUNC

import json
import yaml
from pathlib import Path
from typing import Any, Optional, Callable


class PandaConfig:
    
    def __init__(self,
        conf_path: str | Path,
        config_func: dict[str, tuple[Callable, int]] = {},
    ):
        self.conf_path = conf_path
        self.config_func = DEFAULT_FUNC | config_func
        self.config_data = None
    
    def registration(self, name: str, args_num: int):
        def decorator(func: Callable):
            self.config_func[name] = (func, args_num)
        return decorator
    
    @classmethod
    def register_parser(cls, extension: str, parser: Callable[[Path], dict]):
        """
        Register a custom file parser for a specific extension.
        Delegates to the underlying ConfigLoader.
        """
        ConfigLoader.register_parser(extension, parser)
    
    @property
    def config(self) -> dict[str, Any]:
        if self.config_data:
            return self.config_data
        
        self.loader = ConfigLoader(self.conf_path)
        self.raw_data = self.loader.load()
        resolver = ConfigResolver(self.raw_data, self.config_func)
        self.config_data = resolver.resolve()
        return self.config_data
    
    def get(self) -> dict[str, Any]:
        return self.config
    
    def json(self, indent=4) -> str:
        return json.dumps(self.config, indent=indent)
    
    def yaml(self) -> str:
        return yaml.dump(self.config, sort_keys=False, default_flow_style=False)
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(config_path={Path(self.conf_path).absolute()})'
    