import json
import logging
import time
from datetime import datetime
from threading import Event
from typing import Dict
from typing import Iterator
from typing import Optional
from typing import Tuple

from ewoksutils.datetime_utils import fromisoformat

try:
    from ewokscore.variable import Variable
    from ewokscore.variable import VariableContainer
except ImportError:
    Variable = VariableContainer = None

logger = logging.getLogger(__name__)

EventType = Dict[str, str]


class EwoksEventReader:
    """Base class for receiving ewoks events on the client side."""

    def __enter__(self) -> "EwoksEventReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        pass

    def wait_events(
        self, timeout=None, stop_event: Optional[Event] = None, **filters
    ) -> Iterator[EventType]:
        """Yield events matching the filter until timeout is reached."""
        raise NotImplementedError

    def poll_events(
        self,
        timeout=None,
        stop_event: Optional[Event] = None,
        interval: Optional[float] = None,
        **filters,
    ) -> Iterator[EventType]:
        """Yield events matching the filter until timeout is reached."""
        if interval is None:
            interval = 0.1
        else:
            interval = max(interval, 0.001)
        start = time.time()
        n = 0
        exception = None
        while True:
            try:
                events = list(self.get_events(**filters))
            except Exception as ex:
                if not self._retry_get_events_exception(ex):
                    raise
                if exception is None:
                    logger.warning("Reading events failed (keep retrying): %s", ex)
                exception = ex
            else:
                exception = None
                events = events[n:]
                n += len(events)
                yield from events

            timed_out = timeout is not None and (time.time() - start) > timeout
            stopped = stop_event is not None and stop_event.is_set()
            if timed_out or stopped:
                if exception is not None:
                    logger.error(
                        "Stop polling events (last attempt failed)",
                        exc_info=exception,
                    )
                return

            time.sleep(interval)

    def get_events(self, **filters) -> Iterator[EventType]:
        """Returns all currently available events matching the filter."""
        raise NotImplementedError

    def wait_events_with_variables(self, *args, **kwargs) -> Iterator[EventType]:
        """`get_events` with URI dereferencing."""
        for event in self.wait_events(*args, **kwargs):
            self.dereference_data_uris(event)
            yield event

    def poll_events_with_variables(self, *args, **kwargs) -> Iterator[EventType]:
        """`get_events` with URI dereferencing."""
        for event in self.poll_events(*args, **kwargs):
            self.dereference_data_uris(event)
            yield event

    def get_events_with_variables(self, *args, **kwargs) -> Iterator[EventType]:
        """`get_events` with URI dereferencing."""
        for event in self.get_events(*args, **kwargs):
            self.dereference_data_uris(event)
            yield event

    def get_full_job_events(self, **filters) -> Iterator[Tuple[EventType, ...]]:
        """Returns events grouped by "job_id". When one event matches the filter,
        all events with the "job_id" are returned.
        """
        job_id = None
        for event in self.get_events(**filters):
            if job_id != event["job_id"]:
                job_id = event["job_id"]
                yield tuple(self.get_events(job_id=job_id))

    def get_full_job_events_with_variables(
        self, **filters
    ) -> Iterator[Tuple[EventType, ...]]:
        """`get_full_job_events` with URI dereferencing."""
        job_id = None
        for event in self.get_events(**filters):
            if job_id != event["job_id"]:
                job_id = event["job_id"]
                yield tuple(self.get_events_with_variables(job_id=job_id))

    @staticmethod
    def dereference_data_uris(event: EventType) -> None:
        if Variable is None:
            raise ImportError("requires 'ewoks'")
        input_uris = event.get("input_uris")
        if input_uris:
            if isinstance(input_uris, str):
                input_uris = json.loads(input_uris)
            inputs = {
                uri["name"]: (
                    Variable(data_uri=uri["value"]) if uri["value"] else Variable()
                )
                for uri in input_uris
            }
            event["inputs"] = VariableContainer(inputs)
        task_uri = event.get("task_uri")
        if task_uri:
            event["outputs"] = VariableContainer(data_uri=task_uri)

    @staticmethod
    def event_passes_filter(
        event: EventType,
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
    ) -> bool:
        if not (starttime or endtime):
            return True
        time = fromisoformat(event["time"])
        if starttime is not None:
            if isinstance(starttime, str):
                starttime = fromisoformat(starttime)
            if time < starttime:
                return False
        if endtime is not None:
            if isinstance(endtime, str):
                endtime = fromisoformat(endtime)
            if time > endtime:
                return False
        return True

    @staticmethod
    def split_filter(
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
        **is_equal_filter,
    ) -> Tuple[dict, dict]:
        """Splits the filter

        to be applied on the list of events fetched from the database
        """
        if starttime and not isinstance(starttime, datetime):
            raise TypeError("starttime needs to be a datetime object")
        if endtime and not isinstance(endtime, datetime):
            raise TypeError("starttime needs to be a datetime object")
        post_filter = {"starttime": starttime, "endtime": endtime}
        return is_equal_filter, post_filter

    @staticmethod
    def _retry_get_events_exception(ex: Exception) -> bool:
        return True
