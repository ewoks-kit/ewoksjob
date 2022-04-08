import os
import json
import socket
from typing import Dict, Iterable
import redis


class RedisEwoksEventReader:
    def __init__(self, url: str):
        client_name = f"ewoks:reader:{socket.gethostname()}:{os.getpid()}"
        self._proxy = redis.Redis.from_url(url, client_name=client_name)

    def get_job_events(self, job_id) -> Iterable[Dict[str, str]]:
        keys = sorted(
            self._proxy.scan_iter(f"ewoks:{job_id}:*"),
            key=lambda x: int(x.decode().split(":")[-1]),
        )
        for key in keys:
            yield {
                k.decode(): json.loads(v) for k, v in self._proxy.hgetall(key).items()
            }
