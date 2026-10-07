# Distributed Environmental Monitor

This repository contains the shared MQTT contract, ESP32 firmware, and Raspberry Pi subscriber for the environmental monitor.

- `shared/` contains the canonical protocol contract.
- `embedded/` contains the PlatformIO firmware project.
- `pi/` contains the Raspberry Pi subscriber container.
- `docs/` contains architecture and development/deployment documentation.

The Mosquitto broker is existing infrastructure on the Raspberry Pi and is not deployed by this repository.
