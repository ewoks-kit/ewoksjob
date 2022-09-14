from ewokscore import task_discovery


def discover_tasks_from_modules(*args, **kwargs):
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
