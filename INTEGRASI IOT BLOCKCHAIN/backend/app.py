from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json
import threading
from web3 import Web3
import os

# --- Konfigurasi ---
FLASK_PORT = 5001
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'iot/inventory'
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS') # Akan di-set saat deployment
GANACHE_URL = "http://127.0.0.1:7545"

# Path untuk file JSON "database" dan ABI kontrak
DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')
CONTRACT_ABI_PATH = os.path.join(os.path.dirname(__file__), '..', 'truffle-project', 'build', 'contracts', 'Inventory.json')

# --- Inisialisasi Aplikasi ---
app = Flask(__name__)
web3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Fungsi untuk memuat state dari "database" JSON
def load_db():
    if not os.path.exists(DB_PATH):
        return {'inventory': []}
    with open(DB_PATH, 'r') as f:
        return json.load(f)

# Fungsi untuk menyimpan state ke "database" JSON
def save_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# --- Logika Blockchain ---
def get_contract():
    if not CONTRACT_ADDRESS:
        print("Error: CONTRACT_ADDRESS environment variable not set.")
        return None
    with open(CONTRACT_ABI_PATH) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
    
    return web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def update_blockchain(rfid, name):
    contract = get_contract()
    if not contract:
        return False
        
    try:
        # Gunakan akun pertama dari Ganache untuk mengirim transaksi
        account = web3.eth.accounts[0]
        tx_hash = contract.functions.updateItem(rfid, name).transact({'from': account})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Blockchain updated for RFID {rfid}. Tx hash: {web3.toHex(tx_hash)}")
        return True
    except Exception as e:
        print(f"Error updating blockchain: {e}")
        return False

# --- Logika MQTT ---
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received from topic {msg.topic}: {msg.payload.decode()}")
    try:
        payload = json.loads(msg.payload.decode())
        rfid = payload.get('rfid')
        name = payload.get('name', 'Unknown Item') # Default name

        if rfid:
            # 1. Update "database" JSON
            db_data = load_db()
            inventory = db_data.get('inventory', [])
            
            # Cek apakah item sudah ada, jika ya, update. Jika tidak, tambahkan.
            item_found = False
            for item in inventory:
                if item['rfid'] == rfid:
                    item['name'] = name
                    item['lastUpdated'] = datetime.now().isoformat()
                    item_found = True
                    break
            
            if not item_found:
                inventory.append({
                    'rfid': rfid,
                    'name': name,
                    'lastUpdated': datetime.now().isoformat()
                })
            
            db_data['inventory'] = inventory
            save_db(db_data)
            print(f"Database updated for RFID {rfid}.")

            # 2. Update Blockchain
            update_blockchain(rfid, name)
            
    except json.JSONDecodeError:
        print("Error decoding MQTT message payload.")
    except Exception as e:
        print(f"An error occurred in on_message: {e}")

def run_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# --- API Endpoints ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    db_data = load_db()
    return jsonify(db_data.get('inventory', []))

@app.route('/api/contract', methods=['GET'])
def get_contract_info():
    return jsonify({
        'contract_address': CONTRACT_ADDRESS,
        'ganache_url': GANACHE_URL
    })

# --- Main ---
if __name__ == '__main__':
    # Jalankan MQTT client di thread terpisah
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()
    
    # Jalankan Flask app
    app.run(host='0.0.0.0', port=FLASK_PORT)
