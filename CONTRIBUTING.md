<a href="https://github.com/ewoks-kit/.github/blob/main/shared/CONTRIBUTING.md" target="_blank">CONTRIBUTING.md</a>

## Production tests

Testing against a Slurm production server is done like this

```bash
python -m gevent.monkey --module pytest -xv --slurm-root-directory "/tmp_14_days" --slurm-pre-script "module load ewoks" .
```
