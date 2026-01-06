import pytest
import yaml
import json
import shutil
from pathlib import Path
from deepdiff import DeepDiff
from typing import Any, Callable, Dict, Tuple

# Adjust import to match your project structure
from src.PandaConfig import PandaConfig

# ==========================================
# 1. Configuration & Mocks
# ==========================================

TEST_ROOT = Path(__file__).parent

# Registry for file handlers. 
# To add TOML support later, just add: '.toml': toml.load
FILE_HANDLERS = {
    'loaders': {
        '.json': json.load,
        '.yaml': yaml.safe_load,
        '.yml': yaml.safe_load,
    },
    'dumpers': {
        '.json': lambda data, f: json.dump(data, f, indent=4, ensure_ascii=False),
        '.yaml': lambda data, f: yaml.dump(data, f, sort_keys=False, allow_unicode=True),
        '.yml': lambda data, f: yaml.dump(data, f, sort_keys=False, allow_unicode=True),
    }
}

# Mock functions for variable interpolation tests
def mock_upper(text): return str(text).upper()
def mock_join(*args): return "-".join(str(a) for a in args)
def mock_add(*args): return sum(int(a) for a in args)
def mock_now(): return "2026-01-01 12:00:00.000000"

MOCK_FUNCS = {
    "upper": (mock_upper, 1),
    "join": (mock_join, -1),
    "add": (mock_add, -1),
    "now": (mock_now, 0),
}

# ==========================================
# 2. Dynamic Discovery Logic
# ==========================================

def get_test_scenarios() -> list[Tuple[str, str]]:
    """
    Scans the root directory for any folder containing 'data/cases'.
    Returns a list of tuples: (format_name, case_id)
    Example: [('yaml', '01'), ('yaml', '02'), ('json', '01')]
    """
    scenarios = []
    
    # Iterate over all directories in root (e.g., yaml, json, toml...)
    for format_dir in TEST_ROOT.iterdir():
        if not format_dir.is_dir() or format_dir.name.startswith(('.', '__')):
            continue
            
        cases_dir = format_dir / 'data' / 'cases'
        if not cases_dir.exists():
            continue

        # Found a format folder; now list its cases
        for case_dir in cases_dir.iterdir():
            if case_dir.is_dir() and not case_dir.name.startswith('_'):
                scenarios.append((format_dir.name, case_dir.name))
    
    return sorted(scenarios)

# ==========================================
# 3. Universal Test Class
# ==========================================

class TestUniversalE2E:
    
    @classmethod
    def setup_class(cls):
        """Pre-test cleanup: ensure 'actual' folders exist and are clean."""
        for format_dir in TEST_ROOT.iterdir():
            if (format_dir / 'data' / 'cases').exists():
                actual_dir = format_dir / 'data' / 'actual'
                if actual_dir.exists():
                    shutil.rmtree(actual_dir)
                actual_dir.mkdir(parents=True, exist_ok=True)

    def _find_entry_point(self, case_path: Path) -> Path:
        """Finds test.json, test.yaml, etc. based on registered loaders."""
        supported_exts = list(FILE_HANDLERS['loaders'].keys())
        
        for ext in supported_exts:
            entry = case_path / f"test{ext}"
            if entry.exists():
                return entry
                
        pytest.fail(f"No entry point (test{supported_exts}) found in {case_path}")

    def _load_file(self, path: Path) -> Any:
        """Loads a file using the correct loader for its extension."""
        ext = path.suffix.lower()
        loader = FILE_HANDLERS['loaders'].get(ext)
        if not loader:
            pytest.fail(f"No loader registered for extension: {ext}")
            
        with open(path, 'r', encoding='utf-8') as f:
            return loader(f)

    def _save_file(self, path: Path, data: Any) -> None:
        """Saves a file using the correct dumper for its extension."""
        ext = path.suffix.lower()
        dumper = FILE_HANDLERS['dumpers'].get(ext)
        if not dumper:
            pytest.fail(f"No dumper registered for extension: {ext}")
            
        with open(path, 'w', encoding='utf-8') as f:
            dumper(data, f)

    @pytest.mark.parametrize("format_name, case_id", get_test_scenarios())
    def test_e2e(self, format_name, case_id):
        """
        Generic E2E test runner.
        1. Locates the case folder dynamically.
        2. Detects the file format.
        3. Runs PandaConfig.
        4. Compares Actual vs Expected.
        """
        # Paths
        base_dir = TEST_ROOT / format_name / 'data'
        case_dir = base_dir / 'cases' / case_id
        expect_dir = base_dir / 'expect'
        actual_dir = base_dir / 'actual'
        
        # 1. Detect Entry Point
        entry_point = self._find_entry_point(case_dir)
        ext = entry_point.suffix.lower()
        
        # 2. Run Logic
        agent = PandaConfig(conf_path=entry_point, config_func=MOCK_FUNCS)
        actual_data = agent.config
        
        # 3. Save Actual Result (for debugging)
        actual_path = actual_dir / f"{case_id}{ext}"
        self._save_file(actual_path, actual_data)
        
        # 4. Load Expectation
        expect_path = expect_dir / f"{case_id}{ext}"
        
        if not expect_path.exists():
            pytest.fail(
                f"Missing expected output for {format_name}/{case_id}.\n"
                f"Expected file: {expect_path}\n"
                f"Generated actual: {actual_path}\n"
                f"Review the actual file and move it to the 'expect' folder if correct."
            )
            
        expected_data = self._load_file(expect_path)

        # 5. Compare
        diff = DeepDiff(expected_data, actual_data, ignore_order=False, report_repetition=True)
        
        if diff:
            pytest.fail(
                f"\n[!] Mismatch in {format_name} Case '{case_id}'\n"
                f"{'='*60}\n"
                f"{diff.pretty()}\n"
                f"{'='*60}\n"
                f"File: {entry_point}\n"
                f"Expected: {expect_path}\n"
                f"Actual:   {actual_path}\n"
            )