import unittest
from pathlib import Path

from pi.subscriber.app import load_contract, parse_reading

CONTRACT_PATH = Path(__file__).parents[2] / "shared" / "mqtt" / "contract.json"


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


if __name__ == "__main__":
    unittest.main()
