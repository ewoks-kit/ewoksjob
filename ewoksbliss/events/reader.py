import os
import json
import socket
from typing import Dict, Iterable
import redis


class RedisEwoksEventReader:
    def __init__(self, url: str):
        client_name = f"ewoks:reader:{socket.gethostname()}:{os.getpid()}"
        self._proxy = redis.Redis.from_url(url, client_name=client_name)

    def get_events(self, job_id=None, **filters) -> Iterable[Dict[str, str]]:
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
