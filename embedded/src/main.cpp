#include <Arduino.h>
#include <DHT.h>
#include <PubSubClient.h>

#if defined(ARDUINO_ARCH_RENESAS)
#include <WiFiS3.h>
#else
#include <WiFi.h>
#endif

#include "secrets.h"

namespace {
constexpr int mqttSchemaVersion = 1;
constexpr char mqttTopicTemplate[] = "environment/v1/%s/measurements";
constexpr unsigned long publishIntervalMs =
    config::measurementIntervalSeconds * 1000UL;

bool isValidDeviceId() {
    const size_t deviceIdLength = strlen(config::deviceId);
    if (deviceIdLength == 0 || deviceIdLength >= 64) {
        return false;
    }

    for (size_t index = 0; index < deviceIdLength; ++index) {
        const char character = config::deviceId[index];
        if (!(isalnum(character) || character == '-' || character == '_')) {
            return false;
        }
    }
    return true;
}
}

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(config::dhtPin, DHT22);
unsigned long lastPublishAt = 0;

void connectWifi() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }

    WiFi.begin(config::wifiSsid, config::wifiPassword);
    Serial.print("Connecting to Wi-Fi");
    for (int attempt = 0; attempt < 20 && WiFi.status() != WL_CONNECTED; ++attempt) {
        delay(500);
        Serial.print('.');
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("Wi-Fi connected");
    } else {
        Serial.println("Wi-Fi connection failed");
    }
}

void connectMqtt() {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    if (mqttClient.connected()) {
        return;
    }

    mqttClient.setServer(config::mqttBrokerHost, config::mqttBrokerPort);
    Serial.print("Connecting to MQTT");
    const bool connected = strlen(config::mqttUsername) == 0
        ? mqttClient.connect(config::deviceId)
        : mqttClient.connect(
            config::deviceId,
            config::mqttUsername,
            config::mqttPassword);
    if (connected) {
        Serial.println(" connected");
    } else {
        Serial.print(" failed, state=");
        Serial.println(mqttClient.state());
    }
}

void publishReading() {
    if (!mqttClient.connected()) {
        return;
    }

    if (!isValidDeviceId()) {
        Serial.println("Invalid device ID");
        return;
    }

    const float temperature = dht.readTemperature();
    const float humidity = dht.readHumidity();
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("DHT22 read failed");
        return;
    }

    char topic[128];
    const int topicLength = snprintf(
        topic, sizeof(topic), mqttTopicTemplate, config::deviceId);
    if (topicLength < 0 || static_cast<size_t>(topicLength) >= sizeof(topic)) {
        Serial.println("MQTT topic is too long");
        return;
    }

    char payload[180];
    const int payloadLength = snprintf(
        payload,
        sizeof(payload),
        "{\"schema_version\":%d,\"temperature_c\":%.2f,\"humidity_percent\":%.2f,\"device_id\":\"%s\"}",
        mqttSchemaVersion,
        temperature,
        humidity,
        config::deviceId);
    if (payloadLength < 0 || static_cast<size_t>(payloadLength) >= sizeof(payload)) {
        Serial.println("MQTT payload is too long");
        return;
    }

    if (mqttClient.publish(topic, payload)) {
        Serial.print("Published: ");
        Serial.println(payload);
    } else {
        Serial.println("MQTT publish failed");
    }
}

void setup() {
    Serial.begin(115200);
    dht.begin();
    connectWifi();
    connectMqtt();
}

void loop() {
    connectWifi();
    connectMqtt();
    mqttClient.loop();

    const unsigned long now = millis();
    if (now - lastPublishAt >= publishIntervalMs) {
        lastPublishAt = now;
        publishReading();
    }

    delay(50);
}
