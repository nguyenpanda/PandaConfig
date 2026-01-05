import pytest
import yaml
import shutil
from pathlib import Path
from deepdiff import DeepDiff 

from src.PandaConfig import PandaConfig  

TEST_FILE_PATH = Path(__file__).resolve()
TEST_DIR = TEST_FILE_PATH.parent / 'data'

CASES_DIR = TEST_DIR / 'cases'
EXPECT_DIR = TEST_DIR / 'expect'
ACTUAL_DIR = TEST_DIR / 'actual'

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

def get_test_cases():
    """
    Scans for subdirectories in data/cases/.
    Returns directory names (e.g., ['01', '02']).
    """
    if not CASES_DIR.exists():
        return []
    
    case_dirs = [
        d.name for d in CASES_DIR.iterdir() 
        if d.is_dir() and not d.name.startswith('_')
    ]
    return sorted(case_dirs)

class TestPandaConfigE2E:

    @classmethod
    def setup_class(cls):
        """Clean actual directory before running."""
        EXPECT_DIR.mkdir(parents=True, exist_ok=True)
        CASES_DIR.mkdir(parents=True, exist_ok=True)
        
        if ACTUAL_DIR.exists():
            shutil.rmtree(ACTUAL_DIR)
        ACTUAL_DIR.mkdir(parents=True, exist_ok=True)

    def _save_actual(self, case_name, data):
        """Saves result as {case_name}.yaml (flattened structure)."""
        out_path = ACTUAL_DIR / f"{case_name}.yaml"
        with open(out_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
        return out_path

    @pytest.mark.parametrize("case_name", get_test_cases())
    def test_e2e_folder_structure(self, case_name):
        """
        1. Look into cases/{case_name}/
        2. Load test.yaml as entry point.
        3. Compare result with expect/{case_name}.yaml
        """
        case_folder = CASES_DIR / case_name
        entry_point = case_folder / "test.yaml"
        expect_path = EXPECT_DIR / f"{case_name}.yaml"
        
        if not entry_point.exists():
            pytest.fail(f"Entry point missing: {entry_point} does not exist.")

        agent = PandaConfig(conf_path=entry_point, config_func=MOCK_FUNCS)
        actual_data = agent.config

        actual_file_path = self._save_actual(case_name, actual_data)

        if not expect_path.exists():
            pytest.fail(
                f"Missing expected output: {expect_path}\n"
                f"Generated result saved to: {actual_file_path}\n"
                f"Action: Review {actual_file_path} and move it to {EXPECT_DIR}"
            )

        with open(expect_path, 'r', encoding='utf-8') as f:
            expected_data = yaml.safe_load(f)

        diff = DeepDiff(expected_data, actual_data, ignore_order=False, report_repetition=True)

        if diff:
            pytest.fail(
                f"\n[!] Config Mismatch in Case '{case_name}'\n"
                f"{'='*60}\n"
                f"{diff.pretty()}\n"
                f"{'='*60}\n"
                f"Entry Point: {entry_point}\n"
                f"Expected:    {expect_path}\n"
                f"Actual:      {actual_file_path}\n"
            )
            