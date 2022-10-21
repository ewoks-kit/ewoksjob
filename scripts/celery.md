Celery
======

Celery worker lifecycle
-----------------------

The celery worker CLI

```bash
celery -A proj worker
```

is implemented as follows

```python
# celery.bin.worker.worker

def worker(ctx, ...):
    # celery.apps.worker.Worker, derives from
    # celery.worker.worker.WorkController
    worker = ctx.obj.app.Worker(...)
    worker.start()
    click_ctx.exit(worker.exitcode)
```

```python
# celery.worker.worker

class WorkController:

    def start(self):
        try:
            self.blueprint.start(self)  # celery.bootsteps.start
            # Install handlers for
            #   SIGINT (install_worker_int_handler)
            #   SIGTERM (install_worker_term_handler)
            #   SIGQUIT (install_worker_term_hard_handler)    
            #
            # Start all worker "steps":
            #   - celery.worker.components.Hub.start
            #   - celery.worker.components.Pool.start
            #       -> BasePool.start -> on_start
            #   - celery.worker.consumer.consumer.Consumer.start
            #       Start all consumer "steps": the last one is the event loop
            #       -> check BasePool.did_start_ok -> can raise WorkerLostError (derives from Exception)
            #       -> run the Hub's event loop indefininitely:
            #               Redis: celery.worker.loops.asynloop
            #               Sql: celery.worker.loops.synloop
            #       -> every iteration it checks celery.state:
            #           should_stop -> raise WorkerShutdown (derives from SystemExit)
            #           should_terminate -> raise WorkerTerminate (derives from SystemExit)
        except WorkerTerminate:
            self.terminate()  # -> self.stop(terminate=True)
        except Exception as exc:
            logger.critical('Unrecoverable error: %r', exc, exc_info=True)
            self.stop(exitcode=EX_FAILURE)  # -> self.stop(terminate=False)
        except SystemExit as exc:
            self.stop(exitcode=exc.code)  # -> self.stop(terminate=False)
        except KeyboardInterrupt:
            self.stop(exitcode=EX_FAILURE)  # -> self.stop(terminate=False)

    def stop(self, terminate=False):
        # Close all worker "steps"
        #   - celery.worker.components.Pool.stop
        #       -> BasePool.stop -> on_stop
        #   - celery.worker.consumer.consumer.Consumer.stop
        #   - celery.worker.components.Hub.stop
```

Celery worker stopping
----------------------

* Revoking a job: `BasePool.terminate_job`
* SIGINT: for the first time see `install_worker_int_handler`
            Warm shutdown: set `celery.state.should_stop`
          for subsequent times see `install_worker_term_hard_handler`
            Cold shutdown: set `celery.state.should_terminate`
* SIGTERM: `install_worker_term_handler
            Warm shutdown: set `celery.state.should_stop`
* SIGQUIT: `install_worker_term_hard_handler`
            Cold shutdown: set `celery.state.should_terminate`

The signal handlers set the `celery.state` globals and the `asynloop`
or `synloop` event loop raises a `WorkerShutdown` or `WorkerTerminate`.
These are captured in `celery.worker.worker.WorkController`. As a result
the worker pool and the event loop are stopped.

After the event loop stopped, signals that have handlers like SIGINT
and SIGTERM have no effect anymore (`celery.state` globals are still set
but the event loop is not turning them into SystemExit exceptions anymore).
