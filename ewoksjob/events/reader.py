import os
import json
import socket
from typing import Dict, Iterable
import redis
from ewokscore.variable import Variable, VariableContainer


class RedisEwoksEventReader:
    def __init__(self, url: str):
        client_name = f"ewoks:reader:{socket.gethostname()}:{os.getpid()}"
        self._proxy = redis.Redis.from_url(url, client_name=client_name)

    def _iter_events(self, job_id=None, **filters) -> Iterable[Dict[str, str]]:
        if job_id:
            pattern = f"ewoks:{job_id}:*"
        else:
            pattern = "ewoks:*"
        keys = sorted(
            self._proxy.scan_iter(pattern), key=lambda x: int(x.decode().split(":")[-1])
        )
        for key in keys:
            event = self._proxy.hgetall(key)
            event = {k.decode(): json.loads(v) for k, v in event.items()}
            if any(event[k] != v for k, v in filters.items()):
                continue
            yield event

    def get_events(self, **filters) -> Iterable[Dict[str, str]]:
        yield from self._iter_events(**filters)

    def get_events_with_variables(self, **filters) -> Iterable[Dict[str, str]]:
        for event in self._iter_events(**filters):
            if "output_uris" in event:
                event["output_variables"] = {
                    uri["name"]: Variable(data_uri=uri["value"])
                    for uri in event["output_uris"]
                }
            if "task_uri" in event:
                event["outputs"] = VariableContainer(data_uri=event["task_uri"])
            yield event
