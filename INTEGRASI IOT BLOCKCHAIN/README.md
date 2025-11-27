# Proyek Integrasi IoT & Blockchain untuk Manajemen Inventaris

Proyek ini adalah prototipe tumpukan penuh (full-stack) yang mendemonstrasikan bagaimana perangkat Internet of Things (IoT) dapat berinteraksi dengan backend, yang kemudian mencatat transaksi pada blockchain pribadi.

## Arsitektur

Arsitektur sistem terdiri dari komponen-komponen berikut:

1.  **Frontend (Streamlit)**: Dashboard web real-time untuk memantau status inventaris.
2.  **Backend (Python Flask & MQTT)**: Server API yang menyediakan data ke frontend dan mendengarkan event dari perangkat IoT melalui protokol MQTT.
3.  **IoT Simulator (Python)**: Skrip yang mensimulasikan perangkat keras IoT (seperti pembaca RFID ESP32) yang mempublikasikan data ke broker MQTT.
4.  **Smart Contract (Solidity & Truffle)**: Kontrak pintar sederhana yang berjalan di blockchain pribadi (Ganache) untuk mencatat setiap pembaruan inventaris secara immutable.
5.  **Broker MQTT**: Untuk prototipe ini, broker MQTT dijalankan secara lokal oleh backend untuk kesederhanaan. Dalam produksi, ini akan menjadi layanan terpisah (seperti Mosquitto di Raspberry Pi).
6.  **Database**: File `db.json` sederhana digunakan untuk meniru database persisten untuk status inventaris saat ini.

## Struktur Proyek

```
INTEGRASI IOT BLOCKCHAIN/
├── backend/
│   ├── app.py          # Server Flask + klien MQTT
│   └── db.json         # "Database" file JSON
├── frontend/
│   └── dashboard.py    # Aplikasi dashboard Streamlit
├── truffle-project/
│   ├── contracts/
│   │   └── Inventory.sol # Smart contract
│   ├── migrations/
│   │   └── 2_deploy_contracts.js
│   └── truffle-config.js
├── iot_simulator.py      # Skrip untuk mensimulasikan perangkat IoT
├── requirements.txt      # Dependensi Python
├── run_all.ps1           # Skrip PowerShell untuk menjalankan semua layanan
└── README.md
```

## Prasyarat Instalasi

Sebelum menjalankan proyek, pastikan Anda telah menginstal yang berikut:

1.  **Node.js dan npm**: Diperlukan untuk Truffle dan Ganache.
2.  **Truffle**: Install secara global melalui npm:
    ```bash
    npm install -g truffle
    ```
3.  **Ganache**: Install CLI Ganache secara global:
    ```bash
    npm install -g ganache
    ```
4.  **Python 3.8+**: Pastikan Python dan `pip` ada di PATH Anda.
5.  **Dependensi Python**: Install dari file `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Cara Menjalankan Proyek

Proyek ini dirancang untuk dijalankan secara lokal. Skrip `run_all.ps1` disediakan untuk mengotomatiskan proses ini di Windows PowerShell.

### Menjalankan Secara Otomatis (Windows PowerShell)

1.  Buka terminal PowerShell.
2.  Navigasi ke direktori `INTEGRASI IOT BLOCKCHAIN`.
3.  Jalankan skrip:
    ```powershell
    ./run_all.ps1
    ```

Skrip ini akan melakukan hal berikut:
- Memulai Ganache di latar belakang.
- Meng-compile dan men-deploy smart contract menggunakan Truffle.
- Mengekspor alamat kontrak yang di-deploy sebagai variabel lingkungan.
- Menjalankan server backend Flask.
- Menjalankan simulator IoT.
- Menjalankan dashboard frontend Streamlit.

### Menjalankan Secara Manual (Langkah-demi-Langkah)

Jika Anda tidak menggunakan PowerShell atau ingin menjalankan setiap layanan secara manual, ikuti langkah-langkah ini di terminal terpisah.

**Terminal 1: Jalankan Ganache**
```bash
ganache-cli
```
Biarkan ini berjalan. Catat salah satu alamat akun yang ditampilkan.

**Terminal 2: Deploy Smart Contract**
```bash
cd truffle-project
truffle migrate --network development
```
Salin alamat kontrak (`contract address`) dari output.

**Terminal 3: Jalankan Backend**
```bash
# Set variabel lingkungan dengan alamat kontrak yang Anda salin
# Windows (Command Prompt)
set CONTRACT_ADDRESS=0xYourContractAddressHere
# Windows (PowerShell)
$env:CONTRACT_ADDRESS="0xYourContractAddressHere"
# macOS/Linux
export CONTRACT_ADDRESS=0xYourContractAddressHere

cd backend
python app.py
```

**Terminal 4: Jalankan Simulator IoT**
```bash
python iot_simulator.py
```

**Terminal 5: Jalankan Frontend**
```bash
cd frontend
streamlit run dashboard.py
```

Setelah semua layanan berjalan, buka dashboard Streamlit di browser Anda (biasanya di `http://localhost:8501`) untuk melihat pembaruan inventaris secara real-time.
