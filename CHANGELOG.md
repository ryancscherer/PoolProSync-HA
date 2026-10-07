# Changelog

All notable changes to this project are documented here.

## 0.2.0

- Removed `Chlorine Production`, `Copper Level`, and `Wi-Fi Signal` sensors —
  confirmed across dozens of captured sessions that this hardware's firmware
  never reports them, so they stayed permanently unknown.
- Fixed `Controller Temperature` reporting an implausible value — it was
  incorrectly scaled the same way as `Water Temperature`; confirmed it
  should not be scaled.
- Setup no longer asks for a "Product ID" field — it's detected
  automatically from the same device-detail call used to validate your
  device ID.
- Renamed project display name to "Pool Pro Sync HA".

## 0.1.2

- Added debug logging when a device function call (e.g. the periodic full
  state refresh) times out, instead of failing silently.

## 0.1.1

- Fixed the integration version not updating in HACS after a code change
  (manifest version bump) and corrected stale repository URLs.

## 0.1.0

- Initial working release: HACS-installable integration with live telemetry
  (water temperature, salt level, cell/pump status, chlorine output, fault
  code) and controls (power mode, work mode, pH pump) for PoolPro Sync
  salt chlorinators, built from a fully reverse-engineered cloud API.
  See [`API_NOTES.md`](API_NOTES.md) for the protocol documentation.
