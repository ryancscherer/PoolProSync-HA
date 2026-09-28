# PoolPro Sync → Home Assistant

A custom [HACS](https://hacs.xyz/) integration that exposes PoolPro Sync pool
data and controls in Home Assistant.

PoolPro Sync has no public/documented API — only a cloud-backed mobile app.
This project works by reverse-engineering that app's cloud API traffic and
wrapping it in a standard Home Assistant `custom_component`.

## Status

🚧 Pre-alpha — API not yet documented. See [`PLAN.md`](PLAN.md) for the
project roadmap and [`API_NOTES.md`](API_NOTES.md) for reverse-engineering
notes as they're captured.

## Repo layout

```
custom_components/poolpro_sync/   # the Home Assistant integration
tests/                            # pytest suite
PLAN.md                           # project plan / roadmap
API_NOTES.md                      # reverse-engineered API documentation
```

## Installation (once released)

1. Add this repository to HACS as a custom repository.
2. Install "PoolPro Sync" from HACS.
3. Restart Home Assistant.
4. Add the integration via Settings → Devices & Services → Add Integration →
   "PoolPro Sync", and sign in with your PoolPro Sync account credentials.

## Development

See [`PLAN.md`](PLAN.md) for the full build plan and milestones.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
```

## Disclaimer

This is an unofficial, community integration. It is not affiliated with or
endorsed by PoolPro Sync. It relies on an undocumented API that may change
without notice.
