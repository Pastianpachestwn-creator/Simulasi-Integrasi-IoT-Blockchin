import paho.mqtt.client as mqtt
import time
import json
import random

# --- Konfigurasi ---
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'iot/inventory'

# --- Data Simulasi ---
SIMULATED_ITEMS = [
    {"rfid": "E2000017431201880480C123", "name": "Komponen Mesin A"},
    {"rfid": "A1B2C3D4E5F6789012345678", "name": "Minyak Pelumas B"},
    {"rfid": "F98765432109876543210987", "name": "Filter Udara C"},
]

# --- Logika MQTT Publisher ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

def run_simulator():
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except ConnectionRefusedError:
        print("Connection to MQTT broker failed. Is the broker running?")
        return

    client.loop_start() # Jalankan loop di background thread

    print("--- IoT RFID Simulator Started ---")
    print(f"Publishing to topic: {MQTT_TOPIC}")

    try:
        while True:
            # Pilih item secara acak untuk disimulasikan
            item_to_scan = random.choice(SIMULATED_ITEMS)
            
            payload = json.dumps(item_to_scan)
            
            result = client.publish(MQTT_TOPIC, payload)
            # Cek apakah publish berhasil
            status = result[0]
            if status == 0:
                print(f"Sent `{payload}` to topic `{MQTT_TOPIC}`")
            else:
                print(f"Failed to send message to topic {MQTT_TOPIC}")

            # Tunggu beberapa detik sebelum scan berikutnya
            time.sleep(10) 

    except KeyboardInterrupt:
        print("Simulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    run_simulator()
