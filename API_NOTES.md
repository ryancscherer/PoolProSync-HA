# PoolPro Sync API Notes (reverse-engineered)

> Fill this in as you capture real traffic from the PoolPro Sync app with a
> MITM proxy. Nothing here is confirmed yet — this is a template.

## Base URL

- `TODO` (e.g. `https://api.poolprosync.com/v1`)

## Authentication

- Flow type: `TODO` (username/password → JWT? OAuth2? API key?)
- Login endpoint: `TODO`
  - Request:
    ```json
    {}
    ```
  - Response:
    ```json
    {}
    ```
- Token storage: `TODO` (header name, cookie, bearer token?)
- Token expiry / refresh endpoint: `TODO`

## Endpoints

### List devices / pools

- `METHOD TODO /path/TODO`
- Response shape:
  ```json
  {}
  ```

### Telemetry / status

- `METHOD TODO /path/TODO`
- Fields observed (fill in as discovered):
  | Field | Type | Meaning | Units |
  |---|---|---|---|
  | | | | |

### Controls (if any)

| Action | Method | Endpoint | Payload |
|---|---|---|---|
| Pump on/off | | | |
| Heater setpoint | | | |
| Lights | | | |

## Polling behavior observed in the app

- Interval: `TODO`
- Any rate limiting seen (429s, throttling)? `TODO`

## Quirks / gotchas

- Certificate pinning? `TODO`
- Any session/device-binding behavior? `TODO`
