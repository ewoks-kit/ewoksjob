## Unit tests

Tests make use of [pytest](https://docs.pytest.org/en/stable/index.html) and can be run as follows

```bash
pytest .
```

Testing an installed project is done like this

```bash
pytest --pyargs <project_name>
```

Testing against a Slurm production server is done like this

```bash
python -m gevent.monkey --module pytest -xv --slurm-root-directory "/tmp_14_days" --slurm-pre-script "module load ewoks" .
```
