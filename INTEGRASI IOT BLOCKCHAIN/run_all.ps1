# Skrip PowerShell untuk Menjalankan Semua Komponen Proyek
# Pastikan Anda menjalankan skrip ini dari root direktori "INTEGRASI IOT BLOCKCHAIN"

Write-Host "--- Memulai Proyek Integrasi IoT & Blockchain ---" -ForegroundColor Yellow

# --- Langkah 1: Memulai Ganache ---
Write-Host "1. Memulai Ganache CLI di latar belakang..."
Start-Process node -ArgumentList "$env:APPDATA\npm\node_modules\ganache\dist\node\cli.js" -WindowStyle Minimized
Write-Host "Menunggu Ganache untuk siap..."
Start-Sleep -Seconds 10

# --- Langkah 2: Deploy Smart Contract ---
Write-Host "2. Men-deploy Smart Contract menggunakan Truffle..."
Push-Location -Path ".\truffle-project"
truffle migrate --network development
Pop-Location

# --- Langkah 3: Ekstrak Alamat Kontrak ---
Write-Host "3. Mengekstrak alamat Smart Contract..."
$contractJsonPath = ".\truffle-project\build\contracts\Inventory.json"
if (-not (Test-Path $contractJsonPath)) {
    Write-Host "Error: File JSON Kontrak tidak ditemukan di $contractJsonPath. Pastikan deployment berhasil." -ForegroundColor Red
    exit 1
}
$contractJson = Get-Content -Raw -Path $contractJsonPath | ConvertFrom-Json
$networkIds = $contractJson.networks.PSObject.Properties | ForEach-Object { $_.Name }
if (-not $networkIds) {
    Write-Host "Error: Tidak dapat menemukan network ID di file JSON kontrak." -ForegroundColor Red
    exit 1
}
$latestNetworkId = $networkIds | Select-Object -Last 1
$contractAddress = $contractJson.networks.$latestNetworkId.address

if ($contractAddress) {
    $env:CONTRACT_ADDRESS = $contractAddress
    Write-Host "Alamat Kontrak berhasil di-set: $contractAddress" -ForegroundColor Green
} else {
    Write-Host "Error: Gagal mendapatkan alamat kontrak untuk network ID $latestNetworkId." -ForegroundColor Red
    exit 1
}

# --- Langkah 4: Menjalankan Backend ---
Write-Host "4. Menjalankan server Backend Flask..."
Start-Job -ScriptBlock {
    param($contractAddr)
    $env:CONTRACT_ADDRESS = $contractAddr
    python backend/app.py
} -ArgumentList $contractAddress | Out-Null
Write-Host "Backend berjalan di background job."

# --- Langkah 5: Menjalankan Simulator IoT ---
Write-Host "5. Menjalankan Simulator Perangkat IoT..."
Start-Job -ScriptBlock { python iot_simulator.py } | Out-Null
Write-Host "Simulator IoT berjalan di background job."

# --- Langkah 6: Menjalankan Frontend ---
Write-Host "6. Menjalankan Dashboard Frontend Streamlit..."
Start-Sleep -Seconds 5
Start-Process streamlit -ArgumentList "run frontend/dashboard.py"

Write-Host ""
Write-Host "--- Semua Layanan Telah Dimulai ---" -ForegroundColor Green
Write-Host "Dashboard Streamlit akan terbuka di browser Anda."
Write-Host "Anda dapat melihat output dari background jobs dengan 'Get-Job | Receive-Job'."
Write-Host "Untuk menghentikan semua background jobs, jalankan 'Get-Job | Stop-Job'."