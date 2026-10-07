# Architecture

The ESP32 reads a DHT22 temperature and humidity sensor and publishes one JSON measurement to the existing Mosquitto broker over Wi-Fi.

The Raspberry Pi runs the Python subscriber in Docker. The container connects to Mosquitto on the Pi host using host networking, subscribes to the shared measurement filter, validates messages, and prints readings to its terminal.

The MQTT contract in `shared/mqtt/contract.json` is the protocol source of truth. The firmware keeps only the small topic and schema constants it needs in a tracked header, which is checked against the JSON contract by focused tests and review. The Python subscriber reads the JSON contract directly at runtime.

Mosquitto, persistence, dashboards, alerts, and other processing are outside this repository's application scope.
