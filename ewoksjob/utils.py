import sys
import importlib
from datetime import datetime

try:
    from ewokscore.utils import import_qualname
    from ewokscore.utils import instantiate_class
except ImportError:
    import_qualname = None
    instantiate_class = None

if import_qualname is None:

    def import_qualname(qualname):
        if not isinstance(qualname, str):
            raise TypeError(qualname, type(qualname))
        module_name, dot, obj_name = qualname.rpartition(".")
        if not module_name:
            raise ImportError(f"cannot import {qualname}")
        module = importlib.import_module(module_name)
        try:
            return getattr(module, obj_name)
        except AttributeError:
            raise ImportError(f"cannot import {obj_name} from {module_name}")


if instantiate_class is None:

    def instantiate_class(class_name: str, *args, **kwargs):
        cls = import_qualname(class_name)
        return cls(*args, **kwargs)


def fromisoformat(s: str) -> datetime:
    if sys.version_info < (3, 7):
        return datetime.strptime(s[:-3] + s[-2:], "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return datetime.fromisoformat(s)
