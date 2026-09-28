# PoolPro Sync → Home Assistant Integration Plan

PoolPro Sync only has a cloud-backed mobile app (no public API, no local
hub). This integration works by capturing/reverse-engineering the app's
cloud API traffic and wrapping it in a standard HACS custom component.

## 1. Discovery phase (must happen before any real code)

**Goal:** document PoolPro Sync's cloud API contract in `API_NOTES.md`.

1. **Traffic capture** — Run the PoolPro Sync app on a phone with a MITM
   proxy (mitmproxy or Proxyman) sitting in between:
   - Install a trusted CA cert on the test device, route its traffic through
     the proxy.
   - If the app pins certificates, patch/repackage the APK (Frida or
     objection) to bypass pinning, on a device/account you own, for testing
     only.
2. **Capture these flows specifically:**
   - Login / auth (OAuth, JWT, API key, or session cookie?)
   - Device/pool list retrieval
   - Telemetry pull (temp, pH, chlorine, pump status, salt level, etc.)
   - Any control/command endpoints (pump on/off, heater setpoint, lights) —
     these become HA services
   - Token refresh behavior and expiry
3. **Write it up** in `API_NOTES.md`: base URL, auth flow, endpoints,
   request/response JSON shapes, rate limits, the polling cadence the app
   itself uses.
4. **Check PoolPro Sync's Terms of Service** for reverse-engineering /
   automated-access clauses. For a personal integration the realistic risk
   is account suspension, not legal action — but know it going in.

Nothing in phase 2+ should be written until `API_NOTES.md` has real,
captured endpoint data — don't guess at the API shape.

## 2. Architecture

Standard modern HA custom integration pattern:

```
custom_components/poolpro_sync/
├── __init__.py          # setup, config entry lifecycle
├── manifest.json        # domain, requirements, version
├── config_flow.py       # UI-based setup (login credentials)
├── coordinator.py       # DataUpdateCoordinator - polls PoolPro cloud API
├── api.py               # thin async client wrapping the reverse-engineered API
├── const.py             # DOMAIN, default scan interval, etc.
├── sensor.py            # temp, pH, chlorine, salt, pump status, etc.
├── switch.py            # pump on/off, lights, if controllable
├── number.py / climate.py  # heater setpoint if applicable
├── diagnostics.py       # redacted diagnostics for bug reports
└── strings.json / translations/en.json
```

Key points:

- `api.py` owns all HTTP calls (via `aiohttp`, reusing HA's shared client
  session), token refresh, and retry/backoff on transient failures.
- `coordinator.py` polls on an interval (start conservative — 60–120s — to
  avoid rate limiting or account flags) and fans data out to all entities
  via `DataUpdateCoordinator` + `CoordinatorEntity`.
- `config_flow.py` takes credentials, validates them against the real API
  during setup, and stores them in HA's encrypted config entry storage —
  never in YAML.
- Controls (pump, lights, heater) are exposed as native HA platforms
  (`switch`, `number`, `climate`) rather than custom services, so they work
  naturally in automations/dashboards.

## 3. Testing strategy

- **Unit tests** for `api.py` using recorded/mocked JSON fixtures from the
  real traffic capture — never hit the live API in CI.
- **Integration tests** with `pytest-homeassistant-custom-component` for the
  config flow and coordinator against a mocked API client.
- **Manual smoke test** against a real PoolPro Sync account before each
  release.

## 4. Milestones

1. **Discovery** — Traffic capture + `API_NOTES.md`. No integration code yet.
2. **API client** — `api.py` + `config_flow.py`, validated against a real
   login.
3. **Read-only sensors** — Coordinator + sensors (temp, pH, chlorine, etc.)
   working end-to-end against a real HA instance.
4. **Controls** — switch/number/climate entities if the API supports writes;
   diagnostics; translations.
5. **Release** — Tests passing, HACS validation green, README complete, tag
   `v0.1.0`, submit as a HACS custom repository.

## 5. Known risks

- PoolPro Sync's app API is undocumented and unversioned — it can change
  without notice and silently break this integration. The coordinator
  should raise a clear HA repair/reauth issue rather than failing silently.
- Certificate pinning or anti-automation on the backend could make polling
  risky for the account — poll conservatively and cache aggressively.
