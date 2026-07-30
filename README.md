# overdrive_mqtt

# Overdrive Vehicle Integration for Home Assistant

A high-performance, local-push custom component for Home Assistant that integrates vehicle telemetry data using an MQTT data stream. This integration uses a centralized data coordinator design to process incoming JSON payloads efficiently, parsing metrics into separate Home Assistant entities while natively filtering out invalid telemetry values.

---

## Key Features

* **Centralized Data Handling**: Parses single, multi-nested JSON telemetry messages once, preventing state update race conditions.
* **Dual-Topic Monitoring**: Listens to an explicit telemetry stream while monitoring a dedicated network availability wire (`online` / `offline`).
* **Telemetry Sanitization**: Automatically drops invalid data frames and missing payload flags (`65535`, `1048575`, `-10011`, etc.), displaying them cleanly as `Unknown` or `Unavailable` in the UI.
* **Map Diagnostics**: Integrates coordinates (`lat`, `lon`), heading data, and elevation maps natively into Home Assistant `device_tracker` schemas.
* **HACS Ready**: Styled to match HACS community specifications for seamless local installation and maintenance.

---

## File Structure

For HACS deployment, place the files inside your Home Assistant `custom_components/` directory as follows:

```text
custom_components/
  overdrive_mqtt/
    __init__.py          # Sets up MQTT entries & routes events
    binary_sensor.py     # Parses connectivity, doors, windows, & seatbelts
    config_flow.py       # Configures user UI entry points
    const.py             # Global constants & invalid value telemetry maps
    device_tracker.py    # Extracts vehicle coordinate/GPS positions
    manifest.json        # Core HACS & Home Assistant integration metadata
    sensor.py            # Extracts numerical and textual metrics (Odometer, SoC, Tyres)
```

---

## Installation

### Method 1: Via HACS (Recommended)
1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and choose **Custom repositories**.
3. Paste the URL of your repository containing these files.
4. Set the category to **Integration** and click **Add**.
5. Find **Overdrive Vehicle Integration** in the list and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual Installation
1. Download the `overdrive_mqtt` folder.
2. Copy the folder into your Home Assistant directory under `custom_components/`.
3. Restart Home Assistant.

---

## Setup & Configuration

1. In Home Assistant, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom-right corner.
3. Search for **Overdrive Vehicle Integration**.
4. Configure your specific MQTT topics:
   * **Telemetry Topic** (Default: `overdrive/vehicle/telemetry`)
   * **Availability Topic** (Default: `overdrive/vehicle/telemetry/availability`)
5. Click **Submit**.

---

## Handled Telemetry Entities

### 📊 Sensors
* **Battery State of Charge**: State value (`soc`) matching `%` scaling constraints.
* **Odometer**: Cumulative driven track distance (`odometer`) mapped to `total_increasing`.
* **EV Range**: Expected remaining driving distance (`ev_range_km`).
* **12V Voltage**: Auxiliary vehicle control system battery potential (`volt_12v`).
* **Selected Gear**: Real-time transmission choice indicator (`gear`).
* **Speed**: Instantaneous target vehicle speed tracking (`speed`).
* **Tyre Pressures & Temperatures**: Individual parameters for all four wheels (`tyre_p_fl`, `tyre_t_fl`, etc.).

### 🔒 Binary Sensors
* **Network Status**: Dedicated `connectivity` device class tracked from the availability topic.
* **Charging & Parking States**: Instantaneous operational constraints (`is_charging`, `is_parked`).
* **Doors & Windows**: Safety and security states unpacked directly from nested data arrays.
* **Seatbelts**: Driver and passenger occupancy safety monitors (`seatbelt`).

### 🗺️ Device Tracker
* Maps vehicle telemetry coordinates (`lat`, `lon`) along with `elevation` and `heading` directly onto standard Home Assistant map cards.
