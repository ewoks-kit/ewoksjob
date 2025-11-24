import os
import sys

from ._patch import patch_environment


def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv

    # Modify arguments
    if "worker" in argv:
        if "-A" not in argv:
            argv = argv[:1] + ["-A", "ewoksjob.apps.ewoks"] + argv[1:]
        if "--loglevel" not in argv and "-l" not in argv:
            argv += ["--loglevel", "INFO"]
    elif "monitor" in argv:
        argv[argv.index("monitor")] = "flower"

    # Celery does not support explicit argv passing
    sys.argv = argv

    # When needed, patch the environment
    patch_environment(argv)

    # Ewoksjob loader when no loader defined
    os.environ.setdefault("CELERY_LOADER", "ewoksjob.config.EwoksLoader")

    # Call celery main
    from celery.__main__ import main as _main

    sys.exit(_main())


if __name__ == "__main__":
    main()
