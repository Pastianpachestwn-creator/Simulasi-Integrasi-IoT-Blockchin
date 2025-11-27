import streamlit as st
import requests
import pandas as pd
import time

# --- Konfigurasi ---
BACKEND_URL = "http://127.0.0.1:5001"

# --- Fungsi untuk mengambil data ---
def get_inventory_data():
    try:
        response = requests.get(f"{BACKEND_URL}/api/inventory")
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke backend: {e}")
        return None

def get_contract_info():
    try:
        response = requests.get(f"{BACKEND_URL}/api/contract")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # Don't show error for this one, as it's less critical
        return None

# --- UI Dashboard ---
def main():
    st.set_page_config(
        page_title="Dashboard Inventaris IoT & Blockchain",
        page_icon="📦",
        layout="wide"
    )

    st.title("📦 Dashboard Inventaris IoT & Blockchain")
    st.markdown("Menampilkan data inventaris real-time yang diterima dari perangkat IoT dan dicatat di blockchain.")

    # --- Menampilkan Info Kontrak ---
    contract_info = get_contract_info()
    if contract_info:
        st.sidebar.title("🔗 Info Blockchain")
        st.sidebar.info(f"""
            **Alamat Kontrak:** 
            `{contract_info.get('contract_address', 'N/A')}`
            **URL Ganache:** 
            `{contract_info.get('ganache_url', 'N/A')}`
        """)

    # --- Placeholder untuk data ---
    data_placeholder = st.empty()

    while True:
        inventory_data = get_inventory_data()

        with data_placeholder.container():
            if inventory_data is None:
                st.warning("Tidak dapat mengambil data inventaris. Pastikan backend berjalan.")
            elif not inventory_data:
                st.info("Belum ada data inventaris yang diterima dari perangkat IoT.")
            else:
                st.subheader("Status Inventaris Real-Time")
                df = pd.DataFrame(inventory_data)
                # Reorder columns for better readability
                df = df[['rfid', 'name', 'lastUpdated']]
                df['lastUpdated'] = pd.to_datetime(df['lastUpdated']).dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(df, use_container_width=True)

        time.sleep(5) # Auto-refresh setiap 5 detik

if __name__ == '__main__':
    main()
