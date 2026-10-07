# Pool Pro Sync HA

A custom [HACS](https://hacs.xyz/) integration that exposes PoolPro Sync
pool controller data and controls in Home Assistant.

PoolPro Sync has no public/documented API — only a cloud-backed mobile app.
This project works by reverse-engineering that app's cloud API traffic
(a JetLinks-based IoT backend) and wrapping it in a standard Home Assistant
`custom_component`.

## Status

Working. Live telemetry (water temperature, salt level, cell/pump status,
chlorine output, fault code) and controls (power mode, work mode, pH pump)
are confirmed functioning against a real device. See
[`API_NOTES.md`](API_NOTES.md) for the full reverse-engineered protocol and
[`PLAN.md`](PLAN.md) for the project history/roadmap.

## Repo layout

```
custom_components/poolpro_sync/   # the Home Assistant integration
tests/                            # pytest suite
PLAN.md                           # project plan / roadmap
API_NOTES.md                      # reverse-engineered API documentation
```

## Installation

1. Add this repository (`https://github.com/ryancscherer/PoolProSync-HA`) to
   HACS as a custom repository, category **Integration**.
2. Install "PoolPro Sync" from HACS.
3. Restart Home Assistant.
4. Add the integration via Settings → Devices & Services → Add Integration →
   "PoolPro Sync".
5. Enter your pool controller's **device ID** — a MAC-like string (e.g.
   `AABBCC112233`) found in the PoolPro Sync app's device details screen.
   There's no account login involved: the app uses a fixed backend
   credential, not a personal one, and your device model is detected
   automatically — nothing else to look up.

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
