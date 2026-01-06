import pytest
import yaml
from pathlib import Path

from src.PandaConfig.loader import ConfigLoader


class TestConfigLoader:
    
    @staticmethod
    def _create_yaml(path: Path, content: dict):
        """Helper to write dict content to a yaml file"""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(content, f)

    def test_load_simple_config(self, tmp_path):
        """Test loading a basic YAML file without inheritance."""
        config_file = tmp_path / "simple.yaml"
        data = {
            "host": "localhost", 
            "port": 8080,
            "a": [1, 2, 3, 4, 5, "6"],
            "b": {
                "bb": [1, 2, 3, 4, 5],
                "cc": ["1.py", "2.py", "3.py", "4.py", "5.py"]
            },
        }
        self._create_yaml(config_file, data)
        
        loader = ConfigLoader(config_file)
        result = loader.load()
        
        assert result == data

    def test_load_non_existent_file(self):
        """Test that missing files raise FileNotFoundError."""
        loader = ConfigLoader("non_existent.yaml")
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_invalid_yaml(self, tmp_path):
        """Test that broken YAML syntax raises RuntimeError."""
        config_file = tmp_path / "invalid.yaml"
        # Write broken YAML (e.g., mismatched brackets)
        config_file.write_text("key: value: [broken", encoding='utf-8')

        loader = ConfigLoader(config_file)
        
        # Expect RuntimeError as defined in your class
        with pytest.raises(RuntimeError) as exc:
            loader.load()
        print('[nguyenpanda]: ', exc.value)
        assert "Invalid YAML" in str(exc.value)

    def test_config_inheritance(self, tmp_path):
        """Test the 'extends' mechanism (Parent -> Child inheritance)."""
        # 1. Create Base Config (Parent)
        base_file = tmp_path / "base.yaml"
        base_data = {
            "server": {"host": "0.0.0.0", "port": 80},
            "debug": True,
            "app_name": "PandaApp"
        }
        self._create_yaml(base_file, base_data)

        # 2. Create Prod Config (Child) that overrides Base
        prod_file = tmp_path / "prod.yaml"
        prod_data = {
            "extends": "base.yaml",   # Pointer to parent
            "server": {"port": 443},   # Change only port, keep host
            "debug": False             # Overwrite completely
        }
        self._create_yaml(prod_file, prod_data)

        # 3. Load Child Config
        loader = ConfigLoader(prod_file)
        result = loader.load()

        # --- Assertions ---
        # 'extends' key should be cleaned up
        assert "extends" not in result
        
        # Deep merge check: host from base, port from prod
        assert result["server"]["host"] == "0.0.0.0"
        assert result["server"]["port"] == 443
        
        # Direct overwrite check
        assert result["debug"] is False
        
        # Inherited key check
        assert result["app_name"] == "PandaApp"

    def test_deep_update_nested_conflict(self, tmp_path):
        """
        Test the _deep_update logic explicitly to ensure 
        dictionaries are merged, not replaced.
        """
        # We pass a dummy path because we only test the static method logic
        loader = ConfigLoader(tmp_path / "dummy.yaml") 
        
        base = {
            "a": 1, 
            "nested": {
                "x": 10, 
                "y": 20
            }
        }
        
        update = {
            "a": 2, 
            "nested": {
                "x": 99
            }
        }
        
        # Logic: update 'base' with 'update'
        result = loader._deep_update(base, update)
        
        assert result["a"] == 2               # Overwritten
        assert result["nested"]["x"] == 99    # Overwritten inner key
        assert result["nested"]["y"] == 20    # Preserved inner key (Crucial)