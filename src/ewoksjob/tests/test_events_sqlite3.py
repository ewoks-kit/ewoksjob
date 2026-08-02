import sqlite3
import threading
import time

from ewokscore import events

from ..events.readers.sqlite3 import Sqlite3EwoksEventReader


def test_concurrent_read_write(sqlite3_ewoks_events):
    """Events published while a reader is polling must all be received."""
    handlers, reader = sqlite3_ewoks_events

    njobs = 4
    nevents_per_job = 20

    def publish_events(job_id):
        execinfo = _execinfo(handlers, job_id=job_id)
        for _ in range(nevents_per_job // 2):
            events.send_workflow_event(execinfo=execinfo, event="start")
            events.send_workflow_event(execinfo=execinfo, event="end")

    # Publish concurrently (first event instantiates and registers the event handlers)
    threads = [
        threading.Thread(target=publish_events, args=(str(job_id),))
        for job_id in range(njobs)
    ]
    for thread in threads:
        thread.start()

    # Poll for events concurrently
    try:
        evts = list(reader.wait_events(timeout=10))
    finally:
        for thread in threads:
            thread.join(timeout=10)

    # Check that all events were published
    assert len(evts) == njobs * nevents_per_job


def test_read_blocked_by_writer(tmp_path, sqlite3_ewoks_events):
    """A reader must retry reading while a writer locks the database."""
    lock_seconds = 0.5
    retry_period = lock_seconds / 5  # do not retry long enough
    retry_timeout = 5 * lock_seconds  # retry long enough

    # Add events to the database
    handlers, _ = sqlite3_ewoks_events
    execinfo = _execinfo(handlers)
    events.send_workflow_event(execinfo=execinfo, event="start")

    # Writer locks the database
    write_lock_acquired = threading.Event()

    def write_lock_database():
        conn = sqlite3.connect(str(tmp_path / "ewoks_events.db"))
        try:
            # Start write transaction
            conn.execute("BEGIN EXCLUSIVE")
            write_lock_acquired.set()

            # Open write transaction locks the db
            time.sleep(lock_seconds)

            # Finish transaction
            conn.commit()
        finally:
            conn.close()

    uri = f"file:{tmp_path / 'ewoks_events.db'}"

    # Read while locked: do not retry long enough
    write_lock_acquired.clear()
    thread = threading.Thread(target=write_lock_database)
    thread.start()
    try:
        assert write_lock_acquired.wait(timeout=10)
        with Sqlite3EwoksEventReader(uri=uri, timeout=retry_period) as reader:
            evts = list(reader.wait_events(timeout=retry_period))
    finally:
        thread.join(timeout=10)

    # Check that no events were read
    assert len(evts) == 0

    # Read while locked: retry long enough
    write_lock_acquired.clear()
    thread = threading.Thread(target=write_lock_database)
    thread.start()
    try:
        assert write_lock_acquired.wait(timeout=10)
        with Sqlite3EwoksEventReader(uri=uri, timeout=retry_period) as reader:
            evts = list(reader.wait_events(timeout=retry_timeout))
    finally:
        thread.join(timeout=10)

    # Check that all events were read
    assert len(evts) == 1


def test_failed_write_blocked_by_reader(tmp_path, sqlite3_ewoks_events, capsys):
    """A writer must wait for read locks to be released."""
    _test_write_blocked_by_reader(tmp_path, sqlite3_ewoks_events, capsys, succeed=False)


def test_succeeded_write_blocked_by_reader(tmp_path, sqlite3_ewoks_events, capsys):
    """A writer must wait for read locks to be released."""
    _test_write_blocked_by_reader(tmp_path, sqlite3_ewoks_events, capsys, succeed=True)


def _test_write_blocked_by_reader(
    tmp_path, sqlite3_ewoks_events, capsys, succeed: bool
):
    """A writer must wait for read locks to be released."""
    lock_seconds = 0.5
    if succeed:
        retry_timeout = 5 * lock_seconds  # retry long enough
    else:
        retry_timeout = lock_seconds / 5  # do not retry long enough

    # Add start event to the database
    handlers, reader = sqlite3_ewoks_events
    timeout_arg = {"name": "timeout", "value": retry_timeout}
    handlers[0]["arguments"].append(timeout_arg)
    execinfo = _execinfo(handlers)
    events.send_workflow_event(execinfo=execinfo, event="start")

    # Reader
    read_lock_acquired = threading.Event()

    def read_lock_database():
        conn = sqlite3.connect(str(tmp_path / "ewoks_events.db"))
        try:
            # Start read transaction
            conn.execute("BEGIN")
            conn.execute("SELECT COUNT(*) FROM ewoks_events").fetchone()
            read_lock_acquired.set()

            # Open read transaction locks the db
            time.sleep(lock_seconds)

            # Finish transaction
            conn.rollback()
        finally:
            conn.close()

    # Write while locked
    read_lock_acquired.clear()
    thread = threading.Thread(target=read_lock_database)
    thread.start()

    _ = capsys.readouterr()
    try:
        assert read_lock_acquired.wait(timeout=10)
        events.send_workflow_event(execinfo=execinfo, event="end")
    finally:
        thread.join(timeout=10)

    # Check the error log of the dropped event
    captured = capsys.readouterr()
    if succeed:
        assert "--- Logging error ---" not in captured.err
    else:
        assert "--- Logging error ---" in captured.err
        assert "sqlite3.OperationalError: database is locked" in captured.err

    # Check that the expected events were published
    evts = list(reader.wait_events(timeout=1))
    excepted = 2 if succeed else 1
    assert len(evts) == excepted


def _execinfo(handlers, job_id="123") -> dict:
    return {
        "job_id": job_id,
        "workflow_id": "456",
        "host_name": None,
        "user_name": None,
        "process_id": None,
        "handlers": handlers,
    }
