import datetime

from pathlib import Path
from typing import Callable, Optional


def path(path: str) -> str:
    return str(Path(path))


def abspath(path: str) -> str:
    return str(Path(path).absolute())


def _list(o) -> list:
    return [o]


def glob(path: str, pattern: str) -> list[str]:
    return [str(p) for p in Path(path).glob(pattern)]


def rglob(path: str, pattern: str) -> list[str]:
    return [str(p) for p in Path(path).rglob(pattern)]


def _filter(func, ls: list) -> list:
    return list(filter(func, ls))


def startswith(pattern: str) -> Callable:
    def decorator(string: str) -> bool:
        return string.startswith(pattern)
    return decorator


def notstartswith(pattern: str) -> Callable:
    def decorator(string: str) -> bool:
        return not string.startswith(pattern)
    return decorator


def endswith(pattern: str) -> Callable:
    def decorator(string: str) -> bool:
        return string.endswith(pattern)
    return decorator


def notendswith(pattern: str) -> Callable:
    def decorator(string: str) -> bool:
        return not string.endswith(pattern)
    return decorator


def _not(i: bool) -> bool:
    return not i

    
def none() -> None:
    return None


def find_ancestor(path: str, name: str) -> Optional[str]:
    p = Path(path).absolute()
    while p.parent != p:
        if p.name == name:
            return str(p)
        p = p.parent
    return None


def now() -> str:
    return str(datetime.datetime.now())


def strftime(input_str: str, input_format: str) -> str:
    datetime_obj = datetime.datetime.strptime(input_str, '%Y-%m-%d %H:%M:%S.%f')
    return datetime.datetime.strftime(datetime_obj, input_format)


DEFAULT_FUNC: dict[str, tuple[Callable, int]] = {
	'abspath': (abspath, 1),
	'list': (_list, 1),
 	'path': (path, 1),
	'glob': (glob, 2),
	'rglob': (rglob, 2),
	'none': (none, 0),
	'filter': (_filter, 2),
	'not': (_not, 1),
	'startswith': (startswith, 1),
 	'notstartswith': (notstartswith, 1),
 	'endswith': (endswith, 1),
 	'notendswith': (notendswith, 1),
    'find_ancestor': (find_ancestor, 2),
    'now': (now, 0),
    'strftime': (strftime, 2),
}
