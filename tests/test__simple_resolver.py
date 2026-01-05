import pytest
from pathlib import Path

from src.PandaConfig.resolver import ConfigResolver
from src.PandaConfig.default_func import DEFAULT_FUNC


def mock_add(*args):
    """Adds arguments (supports strings converted to int or native ints)."""
    return sum(int(a) for a in args)

def mock_upper(text):
    return str(text).upper()

def mock_join(*args):
    return "-".join(str(a) for a in args)

def mock_json(*args):
    """Returns a complex dict structure."""
    return {"key": args[0], "value": args[1]}

def mock_list(*args):
    """Returns a list of arguments."""
    return list(args)


class TestConfigResolver:
    
    @pytest.fixture
    def config_funcs(self):
        """Returns a dict of functions to inject into Resolver."""
        return {
            "add": (mock_add, -1),
            "upper": (mock_upper, 1),
            "join": (mock_join, -1),
            "mk_json": (mock_json, 2),
            "mk_list": (mock_list, -1),
        }

    def test_resolve_basic_variables(self, config_funcs):
        data = {
            "host": "localhost",
            "port": 8080,
            "url": "http://$host:$port/api",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["host"] == "localhost"
        assert result["url"] == "http://localhost:8080/api"

    def test_resolve_variable_scope_ordering(self, config_funcs):
        """Ensure variables defined earlier are available to later keys."""
        data = {
            "root": "/var/www",
            "user": "panda",
            "site_path": "$root/$user/html", 
            "index": "$site_path/index.html",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["site_path"] == "/var/www/panda/html"
        assert result["index"] == "/var/www/panda/html/index.html"

    def test_resolve_undefined_variable(self, config_funcs):
        data = {"path": "$unknown_var/folder"}
        resolver = ConfigResolver(data, config_funcs)
        
        with pytest.raises(NameError, match="is not defined"):
            resolver.resolve()

    def test_resolve_simple_function(self, config_funcs):
        data = {"res": "$(upper hello)"}
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["res"] == "HELLO"

    def test_resolve_function_argument_count_mismatch(self, config_funcs):
        # 'upper' expects 1 arg, give it 2
        data = {"res": "$(upper hello world)"}
        resolver = ConfigResolver(data, config_funcs)
        
        with pytest.raises(TypeError, match="takes 1 args"):
            resolver.resolve()

    def test_resolve_mixed_vars_and_funcs(self, config_funcs):
        """Test combining $var inside $(func)."""
        data = {
            "x": "10",
            "y": "20",
            "sum": "$(add $x $y 5)",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["sum"] == 35 

    def test_resolve_multiple_functions_same_line(self, config_funcs):
        """Test logic: 'Start $(func) Middle $(func) End'."""
        data = {
            "msg": "Prefix $(upper a) Middle $(upper b) Suffix",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["msg"] == "Prefix A Middle B Suffix"

    def test_resolve_whitespace_robustness(self, config_funcs):
        """Test that extra spaces inside function calls are ignored."""
        data = {
            "clean": "$(  join    apple   banana   )",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["clean"] == "apple-banana"

    def test_resolve_nested_functions(self, config_funcs):
        """Test $(func1 $(func2))."""
        data = {
            "val": "$(upper $(join a b))",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["val"] == "A-B"

    def test_resolve_deep_function_nesting(self, config_funcs):
        """Test 3 levels of nesting."""
        data = {
            "val": "$(upper $(join $(upper x) y))",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        assert result["val"] == "X-Y"

    def test_resolve_inside_nested_dictionaries(self, config_funcs):
        """Ensure resolver traverses into child dictionaries."""
        data = {
            "server": {
                "host": "localhost",
                "details": {
                    "url": "http://$host/api",
                    "status": "$(upper active)",
                }
            }
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["server"]["details"]["url"] == "http://localhost/api"
        assert result["server"]["details"]["status"] == "ACTIVE"

    def test_resolve_inside_lists(self, config_funcs):
        """Ensure resolver traverses into lists."""
        data = {
            "base": "item",
            "items": [
                "static",
                "$base-1",
                "$(upper $base)",
            ]
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["items"] == ["static", "item-1", "ITEM"]

    def test_resolve_list_of_lists(self, config_funcs):
        """Ensure resolver traverses lists of lists."""
        data = {
            "val": "10",
            "matrix": [
                ["$val", "$(add $val 1)"],
                ["$(add $val 2)", 100],
            ]
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["matrix"][0] == ["10", 11]
        assert result["matrix"][1] == [12, 100]

    def test_resolve_return_type_preservation(self, config_funcs):
        """Test that if the WHOLE string is a function, native type is preserved."""
        data = {
            "num": "$(add 10 20)",
            "list": "$(mk_list a b)",
            "dict": "$(mk_json id 1)",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["num"] == 30
        assert isinstance(result["num"], int)
        
        assert result["list"] == ["a", "b"]
        assert isinstance(result["list"], list)
        
        assert result["dict"] == {"key": "id", "value": "1"}
        assert isinstance(result["dict"], dict)

    def test_resolve_interpolation_forces_string(self, config_funcs):
        """
        If a function returns a complex type (int/list), but is embedded 
        in a string, it must be cast to string.
        """
        data = {
            "str_interpolated": "Result: $(add 1 2)",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["str_interpolated"] == "Result: 3"
        assert isinstance(result["str_interpolated"], str)

    def test_pass_complex_type_to_function(self, config_funcs):
        """Test passing a resolved list/int into another function."""
        data = {
            "c": 10,
            "res": "$(join $(mk_list a b) $c)",
        }
        resolver = ConfigResolver(data, config_funcs)
        result = resolver.resolve()
        
        assert result["res"] == f"['a', 'b']-{10}"
        

class TestConfigResolverIntegration:
    """
    Integration tests using the real DEFAULT_FUNC logic.
    """

    @pytest.fixture
    def resolver(self):
        """Helper to create a resolver with the real default functions."""
        def _create(data):
            return ConfigResolver(data, DEFAULT_FUNC)
        return _create

    def test_abspath_resolution(self, resolver):
        data = {
            "base": "test_folder",
            "full_path": "$(abspath $base)",
        }
        res = resolver(data).resolve()
        
        expected = str(Path("test_folder").absolute())
        assert res["full_path"] == expected

    def test_glob_expansion(self, resolver, tmp_path):
        """Test dynamic file discovery using glob."""
        (tmp_path / "config.json").touch()
        (tmp_path / "data.csv").touch()
        (tmp_path / "script.py").touch()
        
        data = {
            "files": "$(glob " + str(tmp_path) + " *.csv)",
        }
        res = resolver(data).resolve()
        
        assert isinstance(res["files"], list)
        assert len(res["files"]) == 1
        assert str(tmp_path / "data.csv") in res["files"]

    def test_rglob_recursive(self, resolver, tmp_path):
        """Test recursive globbing."""
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "root_test.txt").touch()
        (sub / "deep_test.txt").touch()
        
        data = {
            "all_txt": "$(rglob " + str(tmp_path) + " *.txt)",
        }
        res = resolver(data).resolve()
        
        assert len(res["all_txt"]) == 2
        assert str(sub / "deep_test.txt") in res["all_txt"]

    def test_find_ancestor_logic(self, resolver, tmp_path):
        """Test finding project root/ancestor."""
        project = tmp_path / "project"
        src = project / "src"
        mod = src / "module"
        mod.mkdir(parents=True)
        
        data = {
            "current": str(mod),
            "root": "$(find_ancestor $current project)",
        }
        res = resolver(data).resolve()
        
        assert res["root"] == str(project)

    def test_list_creation(self, resolver):
        data = {
            "single": "$(list item1)",
            "implicit_str": "item1",
        }
        res = resolver(data).resolve()
        
        assert res["single"] == ["item1"]
        assert isinstance(res["single"], list)
        assert isinstance(res["implicit_str"], str)

    def test_filter_startswith(self, resolver):
        """
        Test: filter(startswith(prefix), list)
        This tests higher-order function usage in the resolver.
        """
        data = {
            "raw_items": ["apple", "banana", "apricot", "cherry"],
            "a_fruits": "$(filter $(startswith a) $raw_items)",
        }
        
        res = resolver(data).resolve()
        
        assert res["a_fruits"] == ["apple", "apricot"]

    def test_filter_not_endswith(self, resolver):
        """Test combining filter with notendswith."""
        data = {
            "files": ["main.py", "test.py", "README.md", "config.yml"],
            "non_code": "$(filter $(notendswith .py) $files)",
        }
        res = resolver(data).resolve()
        
        assert "README.md" in res["non_code"]
        assert "config.yml" in res["non_code"]
        assert "main.py" not in res["non_code"]

    def test_strftime_conversion(self, resolver):
        """Test formatting a date string."""
        fake_now = "2025-01-01 12:00:00.000000"
        
        data = {
            "raw_time": fake_now,
            "formatted": "$(strftime $raw_time %Y-%m-%d)",
        }
        res = resolver(data).resolve()
        
        assert res["formatted"] == "2025-01-01"

    def test_dynamic_now(self, resolver):
        """Test that $(now) returns a value."""
        data = {"started_at": "$(now)"}
        res = resolver(data).resolve()
        
        assert isinstance(res["started_at"], str)
        assert len(res["started_at"]) > 0

    def test_complex_glob_filter_chain(self, resolver, tmp_path):
        """
        Scenario: Find all files, filter only those starting with 'prod_', 
        and return them as a list.
        """
        (tmp_path / "prod_db.json").touch()
        (tmp_path / "dev_db.json").touch()
        (tmp_path / "prod_cache.log").touch()
        (tmp_path / "readme.txt").touch()

        data = {
            "all_files": "$(glob " + str(tmp_path) + " *)",
            "json_only": "$(filter $(endswith .json) $all_files)",
        }
        
        res = resolver(data).resolve()
        
        assert len(res["json_only"]) == 2
        assert any("prod_db.json" in p for p in res["json_only"])
        assert any("dev_db.json" in p for p in res["json_only"])
        assert not any("readme.txt" in p for p in res["json_only"])

    def test_logic_not(self, resolver):
        data = {
            "is_true": True,
            "is_false": "$(not $is_true)",
        }
        
        res = resolver(data).resolve()
        assert res["is_false"] is False