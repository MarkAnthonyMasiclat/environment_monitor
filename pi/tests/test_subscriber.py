import re
import unittest
from pathlib import Path

from pi.subscriber.app import load_contract, parse_reading

CONTRACT_PATH = Path(__file__).parents[2] / "shared" / "mqtt" / "contract.json"
FIRMWARE_PATH = Path(__file__).parents[2] / "embedded" / "src" / "main.cpp"


class ParseReadingTests(unittest.TestCase):
    def test_accepts_environment_reading(self) -> None:
        reading = parse_reading(
            b'{"schema_version":1,"temperature_c":22.5,"humidity_percent":48.0,"device_id":"esp32"}'
        )

        self.assertEqual(reading["temperature_c"], 22.5)
        self.assertEqual(reading["humidity_percent"], 48.0)

    def test_rejects_missing_temperature(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading(b'{"humidity_percent":48.0}')

    def test_rejects_non_object_payload(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading(b"[]")

    def test_loads_shared_contract(self) -> None:
        contract = load_contract(CONTRACT_PATH)
        self.assertEqual(contract["subscriber_filter"], "environment/v1/+/measurements")

    def test_rejects_wrong_schema_version(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading(
                b'{"schema_version":2,"temperature_c":22.5,"humidity_percent":48.0,"device_id":"esp32"}'
            )

    def test_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading(
                b'{"schema_version":1,"temperature_c":22.5,"humidity_percent":48.0,"device_id":"esp32","extra":true}'
            )

    def test_rejects_non_finite_values(self) -> None:
        with self.assertRaises(ValueError):
            parse_reading(
                b'{"schema_version":1,"temperature_c":NaN,"humidity_percent":48.0,"device_id":"esp32"}'
            )

    def test_firmware_protocol_matches_contract(self) -> None:
        contract = load_contract(CONTRACT_PATH)
        firmware = FIRMWARE_PATH.read_text(encoding="utf-8")
        schema_match = re.search(r"mqttSchemaVersion = (\d+);", firmware)
        topic_match = re.search(r'mqttTopicTemplate\[\] = "([^"]+)";', firmware)

        self.assertIsNotNone(schema_match)
        self.assertIsNotNone(topic_match)
        self.assertEqual(int(schema_match.group(1)), contract["schema_version"])
        self.assertEqual(
            topic_match.group(1).replace("%s", "{device_id}"),
            contract["topic"],
        )


if __name__ == "__main__":
    unittest.main()
