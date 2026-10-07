# Pool Pro Sync HA — Integration Plan

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

Status: **done** — see `API_NOTES.md` for the full captured protocol
(HTTP login/device-detail, plus a JetLinks WebSocket messaging protocol for
live property reports and writes).

## 2. Architecture

Actual architecture, updated once discovery revealed the real protocol is
WebSocket-push, not simple REST polling:

```
custom_components/poolpro_sync/
├── __init__.py          # setup, config entry lifecycle
├── manifest.json        # domain, requirements, version (iot_class: cloud_push)
├── config_flow.py       # UI-based setup (device ID, not user credentials)
├── coordinator.py       # push-based DataUpdateCoordinator fed by the websocket
├── api.py               # HTTP client + JetLinks messaging websocket client
├── const.py             # DOMAIN, default host/port, refresh interval
├── sensor.py            # temp, salt, cell status, chlorine output, etc.
├── switch.py            # pH dosing pump (the one writable boolean property)
├── select.py            # PowerMode, WorkMode (writable enum properties)
└── strings.json / translations/en.json
```

Key points:

- `api.py` has two pieces: `PoolProSyncClient` (HTTP login + device detail)
  and `PoolProSyncWebSocketClient` (maintains the persistent messaging
  WebSocket, re-authenticates and reconnects with backoff on drop).
- There's no per-user login — the app uses one fixed backend credential and
  addresses equipment purely by device ID. `config_flow.py` asks for your
  device ID (found in the app) instead of a username/password.
- `coordinator.py` is push-based: `DataUpdateCoordinator.async_set_updated_data()`
  is called whenever the websocket delivers a `REPORT_PROPERTY` batch, merged
  into a running state dict. A periodic `triggerReport` invocation
  (`FULL_REFRESH_INTERVAL_SECONDS`) requests a full snapshot so
  rarely-changing properties don't go stale.
- Writable properties (`PowerMode`, `WorkMode`, `pHSwitch`) go out as
  `WRITE_PROPERTY` messages over the same websocket — confirmed working
  against the real device during capture.

## 3. Testing strategy

- **Unit tests** for `api.py` using recorded/mocked JSON fixtures from the
  real traffic capture — never hit the live API in CI.
- **Integration tests** with `pytest-homeassistant-custom-component` for the
  config flow and coordinator against a mocked API client.
- **Manual smoke test** against a real PoolPro Sync account before each
  release.

## 4. Milestones

1. **Discovery** — done. Full HTTP + WebSocket protocol captured in
   `API_NOTES.md`.
2. **API client** — done. `api.py` implements login, device detail, and the
   WebSocket messaging client, with passing unit tests against a real
   aiohttp test server.
3. **Read-only sensors** — done. `sensor.py` covers the confirmed telemetry
   properties.
4. **Controls** — done for the properties confirmed writable so far
   (`PowerMode`, `WorkMode` via `select.py`, `pHSwitch` via `switch.py`).
   More can be added as more functions/properties get exercised and
   captured.
5. **Release** — remaining: manual smoke test against a live HA instance,
   confirm `WaterTemp` scaling, HACS validation, tag `v0.1.0`.

## 5. Known risks

- PoolPro Sync's app API is undocumented and unversioned — it can change
  without notice and silently break this integration. The coordinator
  should raise a clear HA repair/reauth issue rather than failing silently.
- Certificate pinning or anti-automation on the backend could make polling
  risky for the account — poll conservatively and cache aggressively.
