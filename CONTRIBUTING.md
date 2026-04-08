# Contribution guide

You can find the common Python package contribution guide [here](https://github.com/ewoks-kit/.github/blob/main/shared/CONTRIBUTING.md).

## Production tests

Testing against a Slurm production server is done like this

```bash
python -m gevent.monkey --module pytest -xv --slurm-root-directory "/tmp_14_days" --slurm-pre-script "module load ewoks" .
```

## Examples: sqlite3

Cleanup existing results

```bash
rm -rf scripts/results
```

Start worker

```bash
scripts/worker.sh --sql --pool=process --loglevel=info
```

Run examples

```bash
scripts/runjobs.sh --sql
```

Submit Ewoks workflow

```bash
source scripts/config.sh --redis
ewoksjob submit demo --test --wait inf
```

## Examples: redis

Cleanup existing results

```bash
rm -rf scripts/results
```

Start Redis server

```bash
redis-server
```

Start worker

```bash
scripts/worker.sh --redis --pool=process --loglevel=info
```

Start monitor (optional)

```bash
scripts/monitor.sh --redis
```

Run examples

```bash
scripts/runjobs.sh --redis
```

Submit Ewoks workflow

```bash
source scripts/config.sh --redis
ewoksjob submit demo --test --wait inf
```
