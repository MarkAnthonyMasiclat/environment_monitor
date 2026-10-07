import json
import math
import os
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt


def load_contract(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as contract_file:
        contract = json.load(contract_file)
    if not isinstance(contract, dict):
        raise ValueError("MQTT contract must be a JSON object")
    return contract


def parse_reading(payload: bytes, schema_version: int = 1) -> dict[str, Any]:
    message = json.loads(payload.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("payload must be a JSON object")
    if set(message) != {
        "schema_version",
        "device_id",
        "temperature_c",
        "humidity_percent",
    }:
        raise ValueError("payload fields do not match the MQTT contract")
    if (
        isinstance(message.get("schema_version"), bool)
        or message.get("schema_version") != schema_version
    ):
        raise ValueError("unsupported schema_version")

    device_id = message.get("device_id")
    temperature = message.get("temperature_c")
    humidity = message.get("humidity_percent")
    if not isinstance(device_id, str) or not device_id:
        raise ValueError("device_id must be a non-empty string")
    if (
        not isinstance(temperature, (int, float))
        or isinstance(temperature, bool)
        or not math.isfinite(temperature)
    ):
        raise ValueError("temperature_c must be numeric")
    if (
        not isinstance(humidity, (int, float))
        or isinstance(humidity, bool)
        or not math.isfinite(humidity)
    ):
        raise ValueError("humidity_percent must be numeric")
    if not 0 <= humidity <= 100:
        raise ValueError("humidity_percent must be between 0 and 100")

    return message


def on_connect(
    client: mqtt.Client,
    userdata: dict[str, Any],
    flags: dict[str, Any],
    reason_code: mqtt.ReasonCode,
    properties: mqtt.Properties | None,
) -> None:
    if reason_code == 0:
        client.subscribe(userdata["subscriber_filter"])
        print(f"Subscribed to {userdata['subscriber_filter']}", flush=True)
    else:
        print(f"MQTT connection failed: {reason_code}", flush=True)


def on_message(
    client: mqtt.Client,
    userdata: dict[str, Any],
    message: mqtt.MQTTMessage,
) -> None:
    try:
        reading = parse_reading(message.payload, userdata["schema_version"])
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        print(f"Invalid MQTT message: {error}", flush=True)
        return

    print(
        f"device={reading['device_id']} temperature={reading['temperature_c']:.2f} C "
        f"humidity={reading['humidity_percent']:.2f}%",
        flush=True,
    )


def main() -> None:
    contract_path = Path(os.environ.get("MQTT_CONTRACT_PATH", "shared/mqtt/contract.json"))
    contract = load_contract(contract_path)
    settings = {
        "subscriber_filter": contract["subscriber_filter"],
        "schema_version": contract["schema_version"],
    }

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=settings)
    username = os.environ.get("MQTT_USERNAME")
    if username:
        client.username_pw_set(username, os.environ.get("MQTT_PASSWORD", ""))
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(os.environ["MQTT_BROKER"], int(os.environ.get("MQTT_PORT", "1883")))
    client.loop_forever()


if __name__ == "__main__":
    main()
