import pytest
import datetime
from pathlib import Path

from src.PandaConfig.default_func import (
    path, abspath, _list, glob, rglob, _filter, _not, none, 
    startswith, notstartswith, endswith, notendswith, 
    find_ancestor, now, strftime, DEFAULT_FUNC
)


class TestDefaultFuncs:

    def test_path_conversion(self):
        """Test simple path string conversion."""
        p = "folder/file.txt"
        assert path(p) == str(Path(p))

    def test_abspath(self):
        """Test absolute path resolution."""
        p = "file.txt"
        resolved = abspath(p)
        assert resolved == str(Path(p).absolute())
        assert Path(resolved).is_absolute()

    def test_glob(self, tmp_path):
        """Test globbing files in a directory."""
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()
        (tmp_path / "c.log").touch()
        
        # Test finding .txt files
        results = glob(str(tmp_path), "*.txt")
        assert len(results) == 2
        assert str(tmp_path / "a.txt") in results
        assert str(tmp_path / "b.txt") in results

    def test_rglob(self, tmp_path):
        """Test recursive globbing."""
        sub = tmp_path / "subdir"
        sub.mkdir()
        (tmp_path / "root.py").touch()
        (sub / "nested.py").touch()
        
        results = rglob(str(tmp_path), "*.py")
        assert len(results) == 2
        assert str(tmp_path / "root.py") in results
        assert str(sub / "nested.py") in results

    def test_find_ancestor_success(self, tmp_path):
        """Test finding a specific ancestor directory by name."""
        parent = tmp_path / "parent"
        child = parent / "child"
        grandchild = child / "grandchild"
        grandchild.mkdir(parents=True)
        
        result = find_ancestor(str(grandchild), "parent")
        assert result == str(parent)

    def test_find_ancestor_self(self, tmp_path):
        """Test finding ancestor when the target IS the current directory."""
        target = tmp_path / "target"
        target.mkdir()
        
        result = find_ancestor(str(target), "target")
        assert result == str(target)

    def test_find_ancestor_failure(self, tmp_path):
        """Test finding a non-existent ancestor returns None."""
        deep_path = tmp_path / "a/b/c"
        deep_path.mkdir(parents=True)
        
        result = find_ancestor(str(deep_path), "non_existent_folder")
        assert result is None

    def test_list_wrapper(self):
        """Test wrapping a single object in a list."""
        assert _list("hello") == ["hello"]
        assert _list(123) == [123]

    def test_filter_logic(self):
        """Test _filter using one of the predicate factories."""
        data = ["apple", "banana", "cherry", "apricot"]
        
        predicate = startswith("a")
        
        result = _filter(predicate, data)
        assert result == ["apple", "apricot"]

    def test_not_logic(self):
        assert _not(True) is False
        assert _not(False) is True

    def test_none_func(self):
        assert none() is None

    def test_startswith_factory(self):
        func = startswith("pre")
        assert func("prefix") is True
        assert func("suffix") is False

    def test_notstartswith_factory(self):
        func = notstartswith("pre")
        assert func("prefix") is False
        assert func("suffix") is True

    def test_endswith_factory(self):
        func = endswith("fix")
        assert func("prefix") is True
        assert func("start") is False

    def test_notendswith_factory(self):
        func = notendswith("fix")
        assert func("prefix") is False
        assert func("start") is True

    def test_now_format(self):
        """Test 'now' returns a string that looks like a datetime."""
        t_str = now()
        assert isinstance(t_str, str)
        assert len(t_str) > 0
        assert "-" in t_str and ":" in t_str

    def test_strftime(self):
        """Test date string reformatting."""
        original = "2023-10-25 14:30:00.123456"
        target_fmt = "%Y/%m/%d"
        result = strftime(original, target_fmt)
        assert result == "2023/10/25"

    def test_strftime_invalid_input(self):
        """Test behavior on bad format (should raise ValueError)."""
        with pytest.raises(ValueError):
            strftime("invalid-date", "%Y")

    def test_default_func_integrity(self):
        """
        Verify DEFAULT_FUNC contains the expected keys and value structures.
        This ensures the ConfigResolver receives the correct mapping.
        """
        required_keys = {
            'abspath', 'list', 'path', 'glob', 'rglob', 'none',
            'filter', 'not', 'startswith', 'notstartswith',
            'endswith', 'notendswith', 'find_ancestor', 'now', 'strftime'
        }
        
        assert required_keys.issubset(DEFAULT_FUNC.keys())
        
        for key, (func, arg_count) in DEFAULT_FUNC.items():
            assert callable(func), f"Key '{key}' does not have a callable function"
            assert isinstance(arg_count, int), f"Key '{key}' arg count is not an int"
            
            if key == 'glob':
                assert arg_count == 2
            if key == 'now':
                assert arg_count == 0
            if key == 'abspath':
                assert arg_count == 1
                