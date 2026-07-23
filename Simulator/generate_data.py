import random
import time
import json
from datetime import datetime, timezone
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

DEVICE_ID = "bioband-001"
TOPIC = "bioband/readings"

# --- AWS IoT connection setup ---
ENDPOINT = "a1ne3ky7j2v0zf-ats.iot.us-east-1.amazonaws.com"
CERTS_PATH = "/Users/shivsharma/Documents/Bioband-Aws/certs"

CERT_FILE = f"{CERTS_PATH}/34d6009d6c9a24a2f934df4ca57cd895eb34a777f28985c4bf932bc7b318b2ce-certificate.pem.crt"
KEY_FILE = f"{CERTS_PATH}/34d6009d6c9a24a2f934df4ca57cd895eb34a777f28985c4bf932bc7b318b2ce-private.pem.key"
ROOT_CA = f"{CERTS_PATH}/AmazonRootCA1.pem"

mqtt_client = AWSIoTMQTTClient(DEVICE_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, KEY_FILE, CERT_FILE)

mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureOfflinePublishQueueing(-1)
mqtt_client.configureDrainingFrequency(2)
mqtt_client.configureConnectDisconnectTimeout(10)
mqtt_client.configureMQTTOperationTimeout(5)

# --- Simulator logic (same as before) ---
baseline = {
    "heart_rate": 72,
    "spo2": 98,
    "temperature": 98.6
}

def generate_reading(anomaly=False):
    if anomaly:
        heart_rate = random.choice([45, 190])
        spo2 = random.randint(80, 88)
        temperature = round(random.uniform(101.5, 104.0), 1)
    else:
        heart_rate = baseline["heart_rate"] + random.randint(-5, 5)
        spo2 = baseline["spo2"] + random.randint(-1, 1)
        temperature = round(baseline["temperature"] + random.uniform(-0.3, 0.3), 1)

    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "heart_rate": heart_rate,
        "spo2": spo2,
        "temperature": temperature
    }

def run_simulator(interval_seconds=3, anomaly_chance=0.1):
    print("Connecting to AWS IoT Core...")
    mqtt_client.connect()
    print(f"Connected. Publishing to topic '{TOPIC}' (Ctrl+C to stop)\n")

    try:
        while True:
            is_anomaly = random.random() < anomaly_chance
            reading = generate_reading(anomaly=is_anomaly)
            payload = json.dumps(reading)
            mqtt_client.publish(TOPIC, payload, 1)
            print(f"Published: {reading}")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopping simulator, disconnecting...")
        mqtt_client.disconnect()

if __name__ == "__main__":
    run_simulator()