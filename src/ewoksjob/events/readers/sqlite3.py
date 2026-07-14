import sqlite3
from typing import Iterator

from ewoksutils import sqlite3_utils
from ewoksutils.event_utils import FIELD_TYPES

from .base import EventType
from .base import EwoksEventReader


class Sqlite3EwoksEventReader(EwoksEventReader):
    def __init__(self, uri: str, timeout: float = 10) -> None:
        """
        :param uri: for example "file:/path/to/ewoks_events.db" or "file:///path/to/ewoks_events.db".
        :param timeout: native sqlite3 busy timeout: the maximum time to wait
                        for database locks to be released by other connections.
        """
        super().__init__()
        self._uri = uri
        self._timeout = timeout
        self.__connection = None
        self.__sql_types = sqlite3_utils.python_to_sql_types(FIELD_TYPES)

    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
        super().close()

    @property
    def _connection(self):
        if self.__connection is None:
            self.__connection = sqlite3.connect(
                self._uri, uri=True, timeout=self._timeout
            )
        return self.__connection

    def wait_events(self, **kwargs) -> Iterator[EventType]:
        yield from self.poll_events(**kwargs)

    def get_events(self, **filters) -> Iterator[EventType]:
        yield from sqlite3_utils.select(
            self._connection,
            "ewoks_events",
            field_types=FIELD_TYPES,
            sql_types=self.__sql_types,
            **filters,
        )

    @staticmethod
    def _retry_get_events_exception(ex: Exception) -> bool:
        if not isinstance(ex, sqlite3.OperationalError):
            return False
        error_message = str(ex)
        if "no such table" in error_message:
            # no event was published yet.
            return True
        if "database is locked" in error_message:
            # transient lock by another connection.
            return True
        return False
