import os
import sys
from pathlib import Path
import celery


def configure_app(app: celery.Celery):
    _module = os.environ.get("CELERY_CONFIG_MODULE")
    if _module:
        path = Path(_module)
        if path.is_file():
            parent = str(path.parent.absolute())
            if parent not in sys.path:
                sys.path.append(parent)
            _module = path.stem
        app.config_from_object(_module, force=True)
    else:
        # Warning: calling with silent=True causes sphinx doc
        # building to fail.
        try:
            import celeryconfig  # noqa F401
        except ImportError:
            pass
        else:
            app.config_from_object("celeryconfig", force=True)
