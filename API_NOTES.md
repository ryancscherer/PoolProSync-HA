# PoolPro Sync API Notes (reverse-engineered)

PoolPro Sync's backend is a **JetLinks**-based IoT platform (a Chinese
open-source IoT device management stack). The app talks to it over plain
HTTP/WebSocket, not the `apiali.crystalas.com` HTTPS host (that host appears
to be unrelated background/analytics traffic — every capture showed it only
as an empty `CONNECT` tunnel).

## Base URL

- `http://47.236.42.212:8850/api/` — plain HTTP, confirmed via full packet
  capture (headers + bodies).
- Also seen: `gac1/gac2/bgac/s1/s2/bs1/er.dcloud.net.cn` — DCloud/uni-app
  framework infrastructure (the app is built on uni-app/HBuilder). Unrelated
  to the pool data API.

## Authentication

`POST /api/authorize/login`

Request body:
```json
{
  "username": "websocket",
  "password": "qushiyun@IOT123",
  "remember": false,
  "expires": 3600000,
  "verifyCode": "",
  "verifyKey": ""
}
```

This is a fixed, non-account-specific login baked into the app itself —
there's no separate "your PoolPro Sync account" credential involved in
talking to this API. Response (trimmed):

```json
{
  "message": "success",
  "result": {
    "token": "<session token>",
    "expires": 3600000,
    "userId": "...",
    "user": { "username": "websocket", "...": "..." }
  },
  "status": 200
}
```

- `result.token` is used as:
  - the `X-Access-Token` header on subsequent HTTP requests, and
  - the path segment in the messaging WebSocket URL:
    `ws://<host>:<port>/api/messaging/{token}`
- The app re-logs-in fairly often (observed several times per session) —
  treat the token as short-lived and re-authenticate on WebSocket reconnect.

## Device detail (metadata/schema)

`GET /api/device-instance/{device_id}/detail`

Header: `X-Access-Token: {token}`

`{device_id}` is a MAC-like identifier (e.g. `AABBCC112233`) found in the
PoolPro Sync app's device details screen — used as-is, not looked up via a
separate "list my devices" call (not implemented here — see below).

Response `result.metadata` is a JSON-encoded string containing the full
JetLinks "thing model": a `properties` array (id, name, value type, unit,
read/write/report capability) plus `functions` (invokable commands) and
`events`. This is effectively the device's full schema — see
`custom_components/poolpro_sync/sensor.py`, `switch.py`, and `select.py` for
the subset currently wired up as HA entities. Confirmed device in this
capture: product `SLIMLINE`, a salt chlorinator ("SL系列盐氯机").

Key properties confirmed live (via the WebSocket, see below):

| Property | Type/Unit | Capability | Notes |
|---|---|---|---|
| `WaterTemp` | int, celsiusDegrees | read, report | **confirmed** raw value is tenths of a degree (raw `200` == `20.0C`, sane pool temp vs. an absurd `200C` otherwise) — sensor.py divides by 10 |
| `SaltLevel` | int, ppm | read, report | |
| `internal_temperature` | int, celsiusDegrees | read, report | same tenths-of-a-degree scaling applied by inference (shares WaterTemp's unit type), not independently cross-checked |
| `CellStatus` | enum ON/OFF/PURGE | read, report | |
| `PumpStatus` | enum ON/OFF | read, report | not writable |
| `PowerMode` | enum AUTO/OFF/ON | read, write, report | write confirmed working |
| `WorkMode` | enum NULL/SPA/WINTER/BOOST/BACKWASH/SALT_TEST/SALT_ADD | read, write, report | |
| `pHStatus` | enum ON/OFF | read, report | |
| `pHSwitch` | enum, values `"0"`/`"1"` (not "OFF"/"ON") | read, write, report | |
| `ActualOutput` / `OutputSetPoint` | int, percent | read(/write), report | |
| `ChlorineProduction` | int, gramme | read, report | |
| `COPPER_LEVEL` | float, ppm, scale 2 | read, write, report | mineral/copper systems |
| `Fault` | int | report | fault/alarm code |
| `WIFI_RSSI` | int | read, report | |

Many more properties exist for timers (`T1_On HH/MM`, `P1_On HH/MM`, etc.),
LCD brightness/contrast, socket assignments, and factory-menu settings — see
the full `metadata` blob for the complete list.

## Real-time messaging (WebSocket)

`GET ws://{host}:{port}/api/messaging/{token}` — upgrades to a persistent
WebSocket (`101 Switching Protocols`). This is the primary way to get live
data; polling the detail endpoint isn't necessary.

### Subscribe to property reports

```json
{
  "type": "sub",
  "topic": "/device/{productId}/{deviceId}/**",
  "parameter": { "headers": { "async": false } },
  "id": "<timestamp-ms>"
}
```

The server then pushes messages as properties change:

```json
{
  "payload": {
    "deviceId": "...",
    "messageType": "REPORT_PROPERTY",
    "properties": { "WaterTemp": 215, "SaltLevel": 3693, "...": "..." },
    "timestamp": 1790593755812
  },
  "topic": "/device/{productId}/{deviceId}/message/property/report",
  "type": "result"
}
```

Properties arrive in batches, not all at once — the integration merges
incoming batches into a running state dict rather than expecting a single
full snapshot per message.

### Request an immediate full snapshot

Invoke the device's `triggerReport` function via the message-sender topic:

```json
{
  "type": "sub",
  "topic": "/device-message-sender/{productId}/{deviceId}",
  "parameter": {
    "messageType": "INVOKE_FUNCTION",
    "inputs": [],
    "timestamp": "<timestamp-ms>",
    "functionId": "triggerReport",
    "deviceId": "{deviceId}",
    "headers": { "async": false }
  },
  "id": "<timestamp-ms>"
}
```

This triggers a burst of `REPORT_PROPERTY` messages covering (most of) the
full property set. The integration calls this on connect and then
periodically (`FULL_REFRESH_INTERVAL_SECONDS` in `const.py`) to avoid stale
values for properties that don't change often.

**Confirmed: this can time out.** Multiple captures show the reply arriving
~10 seconds later as a failure, not a property burst:

```json
{"payload":{"code":"TIME_OUT","deviceId":"1CC3ABE2DD82","functionId":"triggerReport",
"message":"error.code.time_out","messageType":"INVOKE_FUNCTION_REPLY","success":false,...}}
```

The same timeout behavior was also observed on `optionRequest` (the
menu-navigation function used for remote button-press emulation) — this
looks like a genuine device-side latency/reliability characteristic (the
physical controller being slow or unresponsive over its own MQTT link to
the gateway), not something wrong with the request itself. The integration
doesn't currently retry on timeout — it just waits for the next periodic
`triggerReport` call, which is a reasonable way to handle an
intermittent/flaky device response. `api.py` logs these failures at debug
level for visibility (`INVOKE_FUNCTION_REPLY` with `success: false`).

Separately, across every capture so far (dozens of sessions, both
successful and timed-out `triggerReport` calls), `ChlorineProduction`,
`COPPER_LEVEL`, and `WIFI_RSSI` have **never once appeared** in a
`REPORT_PROPERTY` batch — even in sessions where `triggerReport` succeeded
and other properties came through fine. That's strong evidence this
particular unit's firmware simply doesn't populate those three properties
(no copper ionizer installed, `WIFI_RSSI` not wired up in this firmware
build, etc.) rather than it being a timing/reliability issue. If so, those
three sensor entities will stay at `unknown` indefinitely on this hardware,
which is expected behavior, not a bug.

### Write a property

Confirmed working — captured toggling `PowerMode` from `AUTO` to `OFF` and
back through the real app:

```json
{
  "type": "sub",
  "topic": "/device-message-sender/{productId}/{deviceId}",
  "parameter": {
    "messageType": "WRITE_PROPERTY",
    "header": { "async": false },
    "deviceId": "{deviceId}",
    "messageId": "<timestamp-ms>",
    "timestamp": "<timestamp-ms>",
    "properties": { "PowerMode": "OFF" }
  },
  "id": "<timestamp-ms>"
}
```

Reply:

```json
{
  "payload": {
    "messageType": "WRITE_PROPERTY_REPLY",
    "properties": { "PowerMode": "OFF" },
    "success": true
  },
  "type": "result"
}
```

Followed shortly by a `REPORT_PROPERTY` message confirming the new value.

Also confirmed working: writing `ReriodSet` (pump run cycle,
`DOUBLE_CYCLE`/`SINGLE_CYCLE`) via the same mechanism.

## Still open

1. Whether there's a legitimate "list my devices" call, or the device ID is
   just something you copy once from the app — the integration currently
   just asks for it during setup rather than trying to enumerate it.
2. ~~Confirm `WaterTemp` scaling~~ — done. Live device confirmed raw `200` ==
   20.0C. `internal_temperature`'s scaling is still inferred, not
   independently confirmed.
3. Traffic capture while using functions/timers not yet exercised (schedule
   changes, factory menu, firmware `upgrade` function).
4. Token lifetime / whether a proactive refresh is needed vs. just
   reconnect-and-relogin on drop (current implementation just re-logs-in on
   every WebSocket reconnect, which is simple and has worked in testing).
5. ~~Entities aren't yet grouped under a Home Assistant device~~ — done.
