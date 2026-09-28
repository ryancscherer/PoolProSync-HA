"""Constants for the PoolPro Sync integration."""

DOMAIN = "poolpro_sync"

CONF_DEVICE_ID = "device_id"
CONF_PRODUCT_ID = "product_id"
CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_HOST = "47.236.42.212"
DEFAULT_PORT = 8850
DEFAULT_PRODUCT_ID = "SLIMLINE"

# Full-state refresh interval. The device pushes property updates on its own
# schedule, but not every property changes often enough to guarantee a
# recent value for every entity, so we periodically ask for everything.
FULL_REFRESH_INTERVAL_SECONDS = 60
