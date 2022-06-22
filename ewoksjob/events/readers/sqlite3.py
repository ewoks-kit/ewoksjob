import sqlite3
from typing import Iterator
from .base import EwoksEventReader, EventType


class Sqlite3EwoksEventReader(EwoksEventReader):
    def __init__(self, uri: str, **_) -> None:
        super().__init__()
        self._uri = uri
        self.__connection = None

    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
        super().close()

    @property
    def _connection(self):
        if self.__connection is None:
            self.__connection = sqlite3.connect(self._uri, uri=True)
        return self.__connection

    def wait_events(self, **kwargs) -> Iterator[EventType]:
        yield from self.poll_events(**kwargs)

    def get_events(self, **filters) -> Iterator[EventType]:
        is_equal_filter, post_filter = self.split_filter(**filters)

        conn = self._connection
        cursor = conn.cursor()

        if is_equal_filter:
            conditions = [
                f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
                for k, v in is_equal_filter.items()
            ]
        else:
            conditions = list()

        starttime = post_filter.pop("starttime", None)
        if starttime:
            conditions.append(f"time >= '{starttime.isoformat()}'")
        endtime = post_filter.pop("endtime", None)
        if endtime:
            conditions.append(f"time <= '{endtime.isoformat()}'")

        if conditions:
            conditions = " AND ".join(conditions)
            query = f"SELECT * FROM ewoks_events WHERE {conditions}"
        else:
            query = "SELECT * FROM ewoks_events"
        try:
            cursor.execute(query)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return
        rows = cursor.fetchall()
        self._connection.commit()

        if not cursor.description:
            return

        fields = [col[0] for col in cursor.description]
        for values in rows:
            event = dict(zip(fields, values))
            if self.event_passes_filter(event, **post_filter):
                yield event
