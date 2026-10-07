# Development and Deployment

## Laptop

1. Copy `embedded/include/secrets.h.example` to `embedded/include/secrets.h`.
2. Fill in local Wi-Fi, broker, optional MQTT account, device, interval, and DHT22 pin settings. Keep the real secrets file untracked.
3. Build and flash either target from the repository root with `pio run -d embedded -e esp32 -t upload` or `pio run -d embedded -e uno_r4_wifi -t upload`.

## Raspberry Pi

Use VS Code Remote SSH to open the repository on the Pi. Copy `pi/.env.example` to a protected local `.env`, set the broker host and topic filter, and start only the subscriber:

```text
docker compose -f pi/compose.yaml --env-file pi/.env up --build
```

The broker must already be running on the Pi. Configure it independently of this repository, including any publish-only sensor and read-only subscriber accounts. Keep the password database, ACLs, and host-specific configuration in protected system files outside Git.

## Acceptance checks

- Confirm the ESP32 connects to Wi-Fi and prints successful MQTT publishing.
- Repeat the firmware check with the UNO R4 WiFi.
- Confirm the Pi subscriber prints readings from the ESP32.
- Send a malformed payload and confirm the subscriber reports it without terminating.
- Confirm local settings and passwords are absent from `git status`.
