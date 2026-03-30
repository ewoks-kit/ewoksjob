# Contribution guide

You can find the common Python package contribution guide [here](https://gitlab.esrf.fr/dau/ci/pyci/-/blob/main/CONTRIBUTING.md).

## Production tests

Testing against a Slurm production server is done like this

```bash
python -m gevent.monkey --module pytest -xv --slurm-root-directory "/tmp_14_days" --slurm-pre-script "module load ewoks" .
```
