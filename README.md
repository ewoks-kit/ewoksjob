# ewoksbliss

Utilities for [Ewoks](https://gitlab.esrf.fr/workflow/ewoks/ewoks) workflows in [Bliss](https://gitlab.esrf.fr/bliss/bliss)

## Installation

Install on the client side

```bash
pip install ewoksbliss[events]
```

The optional `events` install option should be used if you want the receive
ewoks events during workflow execution.

Install on the worker side

```bash
pip install ewoksbliss[worker]
```

## Getting started

Start a worker that can execute an ewoks graph

```bash
examples/worker.sh
```

On the client side

```bash
python examples/job.py
```

Adapt the three URL's as needed (ewoks events, celery message broker, celery job result storage).
