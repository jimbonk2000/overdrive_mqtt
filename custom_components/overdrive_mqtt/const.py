DOMAIN = "overdrive_mqtt"
DEFAULT_NAME = "Overdrive Vehicle Integration"
DEFAULT_TELEMETRY_TOPIC = "overdrive/vehicle/telemetry"
DEFAULT_AVAILABILITY_TOPIC = "overdrive/vehicle/telemetry/availability"

CONF_TELEMETRY_TOPIC = "telemetry_topic"
CONF_AVAILABILITY_TOPIC = "availability_topic"

PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]

INVALID_VALUES = {
    65535,
    1048575,
    104857.5,
    -10011,
    -2147482648,
}
