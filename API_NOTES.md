# PoolPro Sync API Notes (reverse-engineered)

> Filled in from real HTTP transaction captures. Request/response bodies are
> still TODO — captures so far show method/URL/status/size only, not full
> headers or JSON payloads.

## Base URL

- `http://47.236.42.212:8850/api/` — **plain HTTP, not HTTPS.** Confirmed via
  packet capture: the app talks directly to this raw IP, not a hostname.
- `https://apiali.crystalas.com` also appears in captures, but every
  observed connection to it was a `CONNECT` tunnel with 0 bytes transferred —
  likely unrelated background/analytics traffic, not the real data API. Not
  yet confirmed either way.
- Several `dcloud.net.cn` subdomains (`gac1`, `gac2`, `bgac`, `s1`, `s2`,
  `bs1`, `er`) also show up — these are DCloud/uni-app framework
  infrastructure (the app is built on uni-app/HBuilder), used for framework
  update checks and analytics. Not the pool data API.

## Authentication

- Flow type: username/password POST → returns a token used in later requests
  (exact response shape not yet captured).
- Login endpoint: `POST http://47.236.42.212:8850/api/authorize/login`
  - Observed: 200 response, ~1.84 KB body. One capture also showed a failed
    attempt (`Code 0`, 119 B) — possibly a retry/transient drop.
  - Request body: `TODO` — need to capture full request (likely
    `{"username": ..., "password": ...}` or similar).
  - Response body: `TODO` — need full JSON. Almost certainly contains the
    token/session id used in the `/api/messaging/{token}` WebSocket URL and
    probably an auth header/cookie used by later requests.
- Token storage: `TODO` — need headers from a post-login request to see if
  it's a bearer header, custom header, or cookie.
- Token expiry / refresh endpoint: `TODO`

**Security note (not our bug, just an observation):** login credentials are
sent over **unencrypted HTTP** directly to an IP address. Worth being aware
of, but out of scope to fix — just don't reuse a sensitive password for this
account.

## Endpoints

### Device detail / telemetry

- `GET http://47.236.42.212:8850/api/device-instance/{device_id}/detail`
- Observed: `GET /api/device-instance/1CC3ABE2DD82/detail` → 200, 32.26 KB
  response.
- `{device_id}` looks like a MAC address (`1CC3ABE2DD82`) — likely the pool
  controller's hardware identifier, obtained from a device-list call we
  haven't captured yet (or possibly hardcoded from account/device pairing
  done once at setup).
- Response body: `TODO` — this is the big one; the 32 KB body almost
  certainly contains all current pool status fields (temp, pH, chlorine,
  pump state, etc). Need the full JSON.
- Is there a separate "list my devices" call to discover `{device_id}`
  values, or is it fixed per account? `TODO`

### Real-time updates

- `GET ws://47.236.42.212:8850/api/messaging/{token}` — WebSocket upgrade
  (101 Switching Protocols).
- Observed token in URL: `ec4d3a9fbdaf3a153b06efddc0c84467` — looks like it
  could be the session token from login, or a separate messaging-channel id.
- Message format over the socket: `TODO` — need to capture actual WS frames
  to see if this pushes live telemetry (would let the HA integration avoid
  polling entirely and just listen).

### Controls (if any)

| Action | Method | Endpoint | Payload |
|---|---|---|---|
| Pump on/off | `TODO` | `TODO` | `TODO` |
| Heater setpoint | `TODO` | `TODO` | `TODO` |
| Lights | `TODO` | `TODO` | `TODO` |

Not yet captured — need a traffic capture while toggling a control in the
app.

## Polling behavior observed in the app

- The device detail endpoint was hit repeatedly (multiple captures show it
  called every session); exact interval not yet measured precisely.
- No rate limiting (429s) observed so far.

## Quirks / gotchas

- Certificate pinning: not directly tested yet — the real API traffic
  bypasses this question entirely since it's plain HTTP, not HTTPS. Pinning
  may still apply to the `apiali.crystalas.com` HTTPS calls if those turn
  out to matter.
- The app appears to retry the login call — saw one immediate duplicate
  `POST /api/authorize/login` in a single session.
- Capturing this traffic requires disabling any active VPN (e.g. ExpressVPN)
  first, since Android only allows one active VPN interface — PCAPdroid's
  non-root capture mode needs that slot.

## Still needed

1. Full request/response **headers + JSON body** for:
   - `POST /api/authorize/login`
   - `GET /api/device-instance/{device_id}/detail`
2. Whether there's a "list devices" call, or `device_id` is fixed per
   account.
3. WebSocket message format on `/api/messaging/{token}`.
4. Traffic capture while toggling a control (pump/heater/lights) in the app,
   if the app supports any.
