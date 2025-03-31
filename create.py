import time
import random
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, send_file
import threading
import json
import os
import pandas as pd
import tempfile

# Konfigurasi
TWITTER_SIGNUP_URL = "https://x.com/i/flow/signup"
EMAIL_FILE = "emails.txt"
GECKODRIVER_PATH = r"C:\\Program Files\\geckodriver\\geckodriver.exe"
FIREFOX_BINARY_PATH = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"
ACCOUNTS_DATA_FILE = "accounts_data.json"
PASSWORD = "papali778"  # Password tetap
driver_list = []
accounts = []
automation_running = False
monitor_thread = None

# Inisialisasi Flask app
app = Flask(__name__)

def load_emails():
    """Memuat daftar email dari file."""
    try:
        with open(EMAIL_FILE, "r") as file:
            emails = [line.strip() for line in file if line.strip()]
        return emails
    except FileNotFoundError:
        print("File emails.txt tidak ditemukan!")
        return []

def save_remaining_emails(emails):
    """Menyimpan kembali email yang belum digunakan."""
    with open(EMAIL_FILE, "w") as file:
        for email in emails:
            file.write(email + "\n")

def generate_random_date_of_birth():
    """Menghasilkan tanggal lahir acak."""
    tahun = random.randint(1980, 2005)
    bulan = random.choice([
        "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ])
    tanggal = random.randint(1, 28)
    return tanggal, bulan, tahun

def generate_random_username():
    """Menghasilkan nama pengguna acak."""
    words = [
        "Tiger", "Shadow", "Falcon", "Raven", "Maverick", "Blizzard", "Neon", "Echo", "Phoenix", "Storm",
        "Wolf", "Orion", "Comet", "Inferno", "Drift", "Zenith", "Vortex", "Nimbus", "Frost", "Cobra",
        "Bolt", "Lynx", "Titan", "Hawk", "Nova", "Spectre", "Blaze", "Abyss", "Viper", "Echo",
        "Rogue", "Glacier", "Cyclone", "Crimson", "Ember", "Sting", "Mistral", "Saber", "Tempest", "Vanguard",
        "Comet", "Phantom", "Onyx", "Inferno", "Storm", "Dagger", "Puma", "Scythe", "Nightfall", "Banshee",
        "Slayer", "Zephyr", "Wraith", "Scorpion", "Shatter", "Riptide", "Vortex", "Hurricane", "Gale", "Quake",
        "Blizzard", "Nightshade", "Mercury", "Tornado", "Shadowhawk", "Falconer", "Echo", "Shadowstrike", "Magma", "Fury",
        "Typhoon", "Eclipse", "Venom", "Mirage", "Inferno", "Boltstrike", "Ghost", "Omen", "Stryker", "Striker",
        "Ravenous", "Titanic", "Blaze", "Grit", "Phantom", "Talon", "Pulse", "Warden", "Volt", "Harbinger",
        "Viper", "Reaper", "Scald", "Nimbus", "Specter", "Gale", "Reign", "Stratos", "Maverick", "Shatterstorm",
        "Flare", "Tempest", "Aegis", "Gorgon", "Lurker", "Blaze", "Raptor", "Thunder", "Barrage", "Sphinx",
        "Omega", "Volt", "Zephyr", "Aether", "Luminous", "Cinder", "Marauder", "Frostbite", "Doom", "Rampage"
    ]
    # Pilih kata yang lebih pendek (maksimal 8 karakter) untuk menyisakan ruang untuk angka
    short_words = [word for word in words if len(word) <= 8]
    
    # Jika tidak ada kata pendek, potong kata yang dipilih
    if short_words:
        word = random.choice(short_words)
    else:
        word = random.choice(words)[:8]
    
    # Hitung berapa digit yang tersisa dari batasan 14 karakter
    remaining_chars = 14 - len(word)
    
    # Hasilkan angka dengan panjang yang sesuai
    max_number = 10 ** remaining_chars - 1  # Contoh: Jika remaining_chars=6, max_number=999999
    numbers = random.randint(1, max_number)
    
    username = f"{word}{numbers}"
    return username



def save_accounts_data():
    """Menyimpan semua data akun ke file JSON."""
    global accounts
    with open(ACCOUNTS_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(accounts, file, indent=4, ensure_ascii=False)
    print("Data akun disimpan ke file!")

def load_account_data():
    """Memuat data akun dari file JSON."""
    global accounts
    if os.path.exists(ACCOUNTS_DATA_FILE):
        with open(ACCOUNTS_DATA_FILE, 'r', encoding='utf-8') as file:
            accounts = json.load(file)
    else:
        accounts = []

def create_browser_instance(emails):
    """Membuka jendela browser baru dan menggunakan email dari daftar."""
    global automation_running
    
    if not automation_running:
        print("Otomatisasi telah dihentikan.")
        return None
        
    if not emails:
        print("Semua email sudah habis! Tambahkan lebih banyak email ke emails.txt.")
        return None

    email = emails.pop(0)
    save_remaining_emails(emails)

    options = Options()
    options.binary_location = FIREFOX_BINARY_PATH
    options.add_argument("--width=500")
    options.add_argument("--height=800")
    options.set_preference("dom.webdriver.enabled", False)

    service = Service(GECKODRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(TWITTER_SIGNUP_URL)

    driver_list.append(driver)

    tanggal, bulan, tahun = generate_random_date_of_birth()
    username = generate_random_username()
    password = PASSWORD  # Menggunakan password tetap

    try:
        
        buat_akun_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Buat akun']")))
        buat_akun_button.click()
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "name"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(email)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SELECTOR_1"))).send_keys(bulan)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SELECTOR_2"))).send_keys(str(tanggal))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "SELECTOR_3"))).send_keys(str(tahun))
        
        berikutnya_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Berikutnya']")))
        berikutnya_button.click()
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

    # Simpan data akun
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    account_data = {
        "id": str(int(time.time() * 1000)),  # Generate unique ID
        "timestamp": timestamp,
        "username": username,
        "email": email,
        "password": password,
        "tanggal": tanggal,
        "bulan": bulan,
        "tahun": tahun
    }
    accounts.append(account_data)
    save_accounts_data()
    
    return driver

def get_active_browsers():
    """Returns a list of active and responsive browsers, strictly limited to 3."""
    active_browsers = []
    for driver in driver_list[:]:
        try:
            # Lebih ketat dalam memeriksa status browser
            current_url = driver.current_url  # Akan gagal jika browser ditutup
            driver.execute_script("return document.readyState")  # Periksa responsivitas JavaScript
            
            # Periksa apakah browser masih terhubung dengan halaman yang benar
            if "x.com" in current_url.lower():
                active_browsers.append(driver)
        except Exception as e:
            print(f"Browser tidak aktif: {e}")
            try:
                driver_list.remove(driver)
                driver.quit()
            except:
                pass
    
    # Batasi jumlah browser aktif maksimal 3
    return active_browsers[:6]

def monitor_browsers(emails):
    """Memantau dan memelihara tepat 3 browser aktif."""
    global automation_running
    
    while automation_running:
        time.sleep(1)
        
        # Dapatkan browser aktif saat ini
        active_browsers = get_active_browsers()
        print(f"Browser Aktif: {len(active_browsers)}/{len(driver_list)}")
        
        # Bersihkan driver_list agar sesuai dengan browser aktif
        for driver in driver_list[:]:
            if driver not in active_browsers:
                try:
                    driver_list.remove(driver)
                except:
                    pass
        
        # Tambahkan browser baru jika kurang dari 3
        if len(active_browsers) < 3 and automation_running and emails:
            browsers_to_add = 3 - len(active_browsers)
            print(f"Menambahkan {browsers_to_add} browser baru...")
            
            for _ in range(browsers_to_add):
                if not automation_running or not emails:
                    break
                    
                new_driver = create_browser_instance(emails)
                if new_driver:
                    time.sleep(1)  # Jeda antar pembuatan browser

def close_all_browsers():
    """Menutup semua browser yang terbuka."""
    global driver_list
    
    print(f"Menutup {len(driver_list)} browser...")
    for driver in driver_list[:]:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error menutup browser: {e}")
        
        # Hapus dari daftar driver
        if driver in driver_list:
            driver_list.remove(driver)
    
    print("Semua browser telah ditutup.")

# HTML template sebagai string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Manager Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --google-blue: #4285f4;
            --google-green: #34a853;
            --google-yellow: #fbbc05;
            --google-red: #ea4335;
            --docs-lightgray: #f1f3f4;
            --docs-gray: #dadce0;
            --docs-darkgray: #5f6368;
            --table-hover-color: rgba(241, 243, 244, 0.5);
            --card-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
        }
        
        body {
            background-color: #fff;
            font-family: 'Google Sans', Roboto, Arial, sans-serif;
            color: #202124;
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }
        
        .dashboard-header {
            background-color: #fff;
            border-bottom: 1px solid var(--docs-gray);
            padding: 12px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .app-title {
            display: flex;
            align-items: center;
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--google-blue);
        }
        
        .app-title i {
            margin-right: 8px;
            color: var(--google-blue);
        }
        
        .card {
            border: none;
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            transition: box-shadow 0.2s ease;
            margin-bottom: 24px;
            overflow: hidden;
        }
        
        .card:hover {
            box-shadow: 0 1px 3px 0 rgba(60, 64, 67, 0.3), 0 4px 8px 3px rgba(60, 64, 67, 0.15);
        }
        
        .card-header {
            background-color: #fff;
            border-bottom: 1px solid var(--docs-gray);
            padding: 16px 20px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .card-body {
            padding: 0;
        }
        
        .stats-card {
            background-color: #fff;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            box-shadow: var(--card-shadow);
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stats-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .stats-icon {
            background-color: rgba(66, 133, 244, 0.1);
            color: var(--google-blue);
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 12px;
            font-size: 1.5rem;
        }
        
        .stats-title {
            font-size: 0.85rem;
            color: var(--docs-darkgray);
            margin-bottom: 4px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        .stats-value {
            font-size: 2rem;
            font-weight: 500;
            color: #202124;
        }
        
        /* Google Docs-like table */
        .table-container {
            overflow-x: auto;
            width: 100%;
            max-height: none; /* Hapus batasan tinggi maksimum */
            overflow-y: visible; /* Hapus overflow vertikal */
        }

        .google-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            color: #202124;
            table-layout: fixed;
        }
        
        @media (max-width: 768px) {
            .table-container {
                overflow-x: auto; /* Tetap memungkinkan scroll horizontal pada layar kecil */
            }
        }

        
        .google-table thead {
            background-color: var(--docs-lightgray);
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .google-table th {
            text-align: left;
            padding: 12px 16px;
            font-weight: 500;
            border-bottom: 1px solid var(--docs-gray);
            white-space: nowrap;
        }
        
        .google-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--docs-gray);
            vertical-align: middle;
            word-break: break-word;
        }
        
        .google-table tbody tr {
            transition: background-color 0.2s;
        }
        
        .google-table tbody tr:hover {
            background-color: var(--table-hover-color);
        }
        
        .google-table .cell-number {
            width: 48px;
            color: var(--docs-darkgray);
            text-align: center;
        }
        
        .google-table .cell-timestamp {
            width: 160px;
            color: var(--docs-darkgray);
        }
        
        .google-table .cell-actions {
            width: 100px;
            text-align: right;
            white-space: nowrap;
        }
        
        .download-btn {
            background-color: #fff;
            color: var(--google-green);
            border: 1px solid #dadce0;
            padding: 8px 16px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.2s, box-shadow 0.2s;
        }
        
        .download-btn:hover {
            background-color: rgba(52, 168, 83, 0.04);
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .download-btn i {
            margin-right: 8px;
        }
        
        .last-updated {
            color: var(--docs-darkgray);
            font-size: 13px;
        }
        
        .action-btn {
            color: var(--docs-darkgray);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1rem;
            width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s;
        }
        
        .action-btn:hover {
            background-color: rgba(95, 99, 104, 0.1);
        }
        
        .edit-btn {
            color: var(--google-blue);
        }
        
        .delete-btn {
            color: var(--google-red);
        }
        
        .control-section {
            padding: 16px 0;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 16px;
        }
        
        .automation-status {
            display: inline-flex;
            align-items: center;
            font-size: 14px;
            font-weight: 500;
            padding: 6px 16px;
            border-radius: 16px;
        }
        
        .status-running {
            background-color: rgba(52, 168, 83, 0.1);
            color: var(--google-green);
        }
        
        .status-stopped {
            background-color: rgba(95, 99, 104, 0.1);
            color: var(--docs-darkgray);
        }
        
        .automation-controls {
            display: flex;
            gap: 16px;
        }
        
        .control-btn {
            padding: 8px 24px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: background-color 0.2s, box-shadow 0.2s;
        }
        
        .start-btn {
            background-color: var(--google-blue);
            color: white;
            border: none;
        }
        
        .start-btn:hover {
            background-color: #3367d6;
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .start-btn:disabled {
            background-color: #c5cae9;
            cursor: not-allowed;
        }
        
        .stop-btn {
            background-color: white;
            color: var(--google-red);
            border: 1px solid var(--docs-gray);
        }
        
        .stop-btn:hover {
            background-color: rgba(234, 67, 53, 0.04);
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .stop-btn:disabled {
            color: var(--docs-darkgray);
            border-color: var(--docs-gray);
            cursor: not-allowed;
        }
        
        .current-time {
            color: var(--docs-darkgray);
            font-size: 14px;
        }
        
        .reload-btn {
            width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            cursor: pointer;
            transition: background-color 0.2s;
            color: var(--docs-darkgray);
        }
        
        .reload-btn:hover {
            background-color: rgba(95, 99, 104, 0.1);
        }
        
        /* Modal styles to match Google's aesthetic */
        .modal-content {
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        
        .modal-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--docs-gray);
        }
        
        .modal-title {
            font-weight: 500;
            font-size: 18px;
            color: #202124;
        }
        
        .modal-body {
            padding: 24px;
        }
        
        .modal-footer {
            padding: 16px 24px;
            border-top: 1px solid var(--docs-gray);
        }
        
        .form-label {
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--docs-darkgray);
        }
        
        .form-control, .form-select {
            padding: 8px 12px;
            border: 1px solid var(--docs-gray);
            border-radius: 4px;
            font-size: 14px;
            color: #202124;
            transition: border-color 0.2s;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--google-blue);
            box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.25);
        }
        
        .btn {
            padding: 8px 24px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 4px;
            transition: background-color 0.2s, box-shadow 0.2s;
        }
        
        .btn-secondary {
            background-color: white;
            color: #5f6368;
            border: 1px solid var(--docs-gray);
        }
        
        .btn-secondary:hover {
            background-color: var(--docs-lightgray);
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .btn-primary {
            background-color: var(--google-blue);
            border: none;
        }
        
        .btn-primary:hover {
            background-color: #3367d6;
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .btn-danger {
            background-color: var(--google-red);
            border: none;
        }
        
        .btn-danger:hover {
            background-color: #d93025;
            box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
        }
        
        .footer {
            padding: 24px 0;
            text-align: center;
            color: var(--docs-darkgray);
            font-size: 13px;
            border-top: 1px solid var(--docs-gray);
            margin-top: 40px;
        }
        
        /* Empty state */
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 48px 24px;
            text-align: center;
        }
        
        .empty-state-icon {
            font-size: 48px;
            color: var(--docs-gray);
            margin-bottom: 16px;
        }
        
        .empty-state-text {
            font-size: 16px;
            color: var(--docs-darkgray);
            max-width: 400px;
            margin: 0 auto;
        }
        
        /* Pagination styles */
        .pagination-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background-color: var(--docs-lightgray);
            border-top: 1px solid var(--docs-gray);
        }
        
        .pagination-info {
            color: var(--docs-darkgray);
            font-size: 13px;
        }
        
        .pagination-controls {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .pagination-options {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .pagination-options-label {
            color: var(--docs-darkgray);
            font-size: 13px;
        }
        
        .pagination-button {
            width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            cursor: pointer;
            transition: background-color 0.2s;
            color: var(--docs-darkgray);
            border: none;
            background: none;
        }
        
        .pagination-button:hover:not(:disabled) {
            background-color: rgba(95, 99, 104, 0.1);
        }
        
        .pagination-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pagination-button.active {
            background-color: var(--google-blue);
            color: white;
        }
        
        .pagination-page-numbers {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .pagination-select {
            padding: 6px 12px;
            border: 1px solid var(--docs-gray);
            border-radius: 4px;
            font-size: 13px;
            color: var(--docs-darkgray);
            background-color: white;
            outline: none;
        }
        
        /* Column visibility dropdown */
        .column-visibility-dropdown {
            position: relative;
            display: inline-block;
        }
        
        .column-visibility-button {
            background-color: white;
            color: var(--docs-darkgray);
            border: 1px solid var(--docs-gray);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .column-visibility-button:hover {
            background-color: var(--docs-lightgray);
        }
        
        .column-visibility-content {
            display: none;
            position: absolute;
            right: 0;
            background-color: white;
            min-width: 200px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            border-radius: 4px;
            z-index: 1000;
            padding: 8px 0;
        }
        
        .column-visibility-content.show {
            display: block;
        }
        
        .column-visibility-item {
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .column-visibility-item:hover {
            background-color: var(--docs-lightgray);
        }
        
        .column-visibility-checkbox {
            width: 18px;
            height: 18px;
            accent-color: var(--google-blue);
        }
        
        .table-toolbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background-color: white;
            border-bottom: 1px solid var(--docs-gray);
        }
        
        .table-tools {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .search-container {
            position: relative;
            display: flex;
            align-items: center;
        }
        
        .search-icon {
            position: absolute;
            left: 10px;
            color: var(--docs-darkgray);
        }
        
        .search-input {
            padding: 8px 12px 8px 32px;
            border: 1px solid var(--docs-gray);
            border-radius: 4px;
            font-size: 14px;
            width: 240px;
            transition: border-color 0.2s, width 0.2s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--google-blue);
            width: 300px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div class="app-title">
                    <i class="fas fa-user-shield"></i>
                    X Account Manager
                </div>
                <div class="d-flex align-items-center">
                    <span class="current-time me-3" id="currentTime"></span>
                    <span class="reload-btn" onclick="fetchData()">
                        <i class="fas fa-sync-alt"></i>
                    </span>
                </div>
            </div>
        </div>
    </div>

    <div class="container py-4">
        <div class="row mb-4">
            <div class="col-md-4 mb-3">
                <div class="stats-card">
                    <div class="stats-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stats-title">Total Akun</div>
                    <div class="stats-value" id="totalAccounts">0</div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="stats-card">
                    <div class="stats-icon">
                        <i class="fas fa-window-maximize"></i>
                    </div>
                    <div class="stats-title">Browser Aktif</div>
                    <div class="stats-value" id="activeBrowsers">0</div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="stats-card">
                    <div class="stats-icon">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stats-title">Akun Hari Ini</div>
                    <div class="stats-value" id="todayAccounts">0</div>
                </div>
            </div>
        </div>

        <div class="control-section">
            <div id="automationStatus" class="automation-status status-stopped">
                <i class="fas fa-circle me-2"></i> Otomatisasi Berhenti
            </div>
            <div class="automation-controls">
                <button id="startButton" class="control-btn start-btn" onclick="startSelenium()">
                    <i class="fas fa-play"></i> Mulai
                </button>
                <button id="stopButton" class="control-btn stop-btn" onclick="stopSelenium()" disabled>
                    <i class="fas fa-stop"></i> Berhenti
                </button>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <div class="d-flex align-items-center">
                    <a href="/api/accounts/download" class="download-btn me-3">
                        <i class="fas fa-download"></i> Unduh Excel
                    </a>
                    <div class="column-visibility-dropdown">
                        <button class="column-visibility-button" onclick="toggleColumnVisibility()">
                            <i class="fas fa-columns"></i> Tampilkan Kolom
                        </button>
                        <div class="column-visibility-content" id="columnVisibilityDropdown">
                            <!-- Kolom akan ditambahkan secara dinamis -->
                        </div>
                    </div>
                </div>
                <div class="last-updated" id="lastUpdated">Terakhir diperbarui: -</div>
            </div>
            <div class="table-toolbar">
                <div class="search-container">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" class="search-input" id="searchInput" placeholder="Cari akun..." oninput="applyFilters()">
                </div>
            </div>
            <div class="card-body">
                <div class="table-container">
                    <table class="google-table" id="accountsTable">
                        <thead>
                            <tr>
                                <th class="cell-number">No</th>
                                <th class="cell-timestamp" data-column="timestamp">Waktu</th>
                                <th data-column="username">Username</th>
                                <th data-column="email">Email</th>
                                <th data-column="password">Password</th>
                                <th data-column="birthdate">Tanggal Lahir</th>
                                <th class="cell-actions">Aksi</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Data will be filled dynamically -->
                        </tbody>
                    </table>
                    <div id="emptyState" class="empty-state d-none">
                        <div class="empty-state-icon">
                            <i class="fas fa-user-slash"></i>
                        </div>
                        <div class="empty-state-text">
                            Belum ada akun yang dibuat. Tekan tombol "Mulai" untuk memulai pembuatan akun.
                        </div>
                    </div>
                </div>
                <div class="pagination-container">
                    <div class="pagination-info" id="paginationInfo">
                        Menampilkan 0-0 dari 0 akun
                    </div>
                    <div class="pagination-controls">
                        <div class="pagination-page-numbers" id="paginationNumbers">
                            <!-- Halaman akan ditambahkan secara dinamis -->
                        </div>
                    </div>
                    <div class="pagination-options">
                        <span class="pagination-options-label">Akun per halaman:</span>
                        <select class="pagination-select" id="paginationSize" onchange="changePageSize()">
                            <option value="10">10</option>
                            <option value="20">20</option>
                            <option value="40">40</option>
                            <option value="60">60</option>
                            <option value="100">100</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="editModalLabel">Edit Akun</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="editForm">
                        <input type="hidden" id="editId">
                        <div class="mb-3">
                            <label for="editUsername" class="form-label">Username</label>
                            <input type="text" class="form-control" id="editUsername">
                        </div>
                        <div class="mb-3">
                            <label for="editEmail" class="form-label">Email</label>
                            <input type="email" class="form-control" id="editEmail">
                        </div>
                        <div class="mb-3">
                            <label for="editPassword" class="form-label">Password</label>
                            <input type="text" class="form-control" id="editPassword">
                        </div>
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <label for="editTanggal" class="form-label">Tanggal</label>
                                <input type="number" class="form-control" id="editTanggal" min="1" max="31">
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="editBulan" class="form-label">Bulan</label>
                                <select class="form-select" id="editBulan">
                                    <option value="Januari">Januari</option>
                                    <option value="Februari">Februari</option>
                                    <option value="Maret">Maret</option>
                                    <option value="April">April</option>
                                    <option value="Mei">Mei</option>
                                    <option value="Juni">Juni</option>
                                    <option value="Juli">Juli</option>
                                    <option value="Agustus">Agustus</option>
                                    <option value="September">September</option>
                                    <option value="Oktober">Oktober</option>
                                    <option value="November">November</option>
                                    <option value="Desember">Desember</option>
                                </select>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label for="editTahun" class="form-label">Tahun</label>
                                <input type="number" class="form-control" id="editTahun" min="1950" max="2005">
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Batal</button>
                    <button type="button" class="btn btn-primary" onclick="saveEdit()">Simpan Perubahan</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="deleteModalLabel">Konfirmasi Hapus</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Apakah Anda yakin ingin menghapus akun ini?</p>
                    <p class="fw-bold" id="deleteAccountInfo"></p>
                    <input type="hidden" id="deleteId">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Batal</button>
                    <button type="button" class="btn btn-danger" onclick="confirmDelete()">Hapus</button>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="container">
            <p>© 2025 X Account Manager Dashboard</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // State variables
        let allAccounts = [];
        let filteredAccounts = [];
        let currentPage = 1;
        let pageSize = 10;
        let columnVisibility = {
            timestamp: true,
            username: true,
            email: true, 
            password: true,
            birthdate: true
        };
        
        function updateTime() {
            const now = new Date();
            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            };
            document.getElementById('currentTime').textContent = now.toLocaleDateString('id-ID', options);
        }

        function fetchData() {
            fetch('/api/accounts')
                .then(response => response.json())
                .then(data => {
                    allAccounts = data;
                    applyFilters();
                })
                .catch(error => console.error('Error fetching accounts:', error));
                
            fetch('/api/browsers/count')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('activeBrowsers').textContent = data.count;
                    
                    // Optional: Tambahkan indikator warna jika browser tidak sesuai harapan
                    const browserCountEl = document.getElementById('activeBrowsers');
                    if (data.count < 3) {
                        browserCountEl.style.color = 'orange';
                    } else {
                        browserCountEl.style.color = 'inherit';
                    }
                })
                .catch(error => console.error('Error fetching browser count:', error));
                
            fetch('/api/automation/status')
                .then(response => response.json())
                .then(data => {
                    updateAutomationStatus(data.running);
                })
                .catch(error => console.error('Error fetching automation status:', error));
        }

        function updateAutomationStatus(isRunning) {
            const statusBadge = document.getElementById('automationStatus');
            const startButton = document.getElementById('startButton');
            const stopButton = document.getElementById('stopButton');
            
            if (isRunning) {
                statusBadge.innerHTML = '<i class="fas fa-circle me-2"></i> Otomatisasi Berjalan';
                statusBadge.classList.remove('status-stopped');
                statusBadge.classList.add('status-running');
                startButton.disabled = true;
                stopButton.disabled = false;
            } else {
                statusBadge.innerHTML = '<i class="fas fa-circle me-2"></i> Otomatisasi Berhenti';
                statusBadge.classList.remove('status-running');
                statusBadge.classList.add('status-stopped');
                startButton.disabled = false;
                stopButton.disabled = true;
            }
        }

        function applyFilters() {
            const searchValue = document.getElementById('searchInput').value.toLowerCase();
            
            if (searchValue.trim() === '') {
                filteredAccounts = [...allAccounts];
            } else {
                filteredAccounts = allAccounts.filter(account => 
                    account.username.toLowerCase().includes(searchValue) || 
                    account.email.toLowerCase().includes(searchValue)
                );
            }
            
            // Hitung total halaman berdasarkan filtered accounts
            const totalPages = Math.ceil(filteredAccounts.length / pageSize);
            
            // Sesuaikan currentPage jika melebihi total halaman
            currentPage = Math.min(currentPage, totalPages);
            currentPage = Math.max(1, currentPage);
            
            updateDashboard();
        }
        
        function truncateUsername(username) {
            return username.length > 20 ? username.substring(0, 14) + '...' : username;
        }

        function updateDashboard() {
            // Update last updated time
            const now = new Date();
            document.getElementById('lastUpdated').textContent = `Terakhir diperbarui: ${now.toLocaleTimeString()}`;
            
            // Update stats
            document.getElementById('totalAccounts').textContent = allAccounts.length;
            
            const today = new Date().toISOString().split('T')[0];
            const todayAccounts = allAccounts.filter(a => a.timestamp.startsWith(today)).length;
            document.getElementById('todayAccounts').textContent = todayAccounts;
            
            // Apply pagination
            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = Math.min(startIndex + pageSize, filteredAccounts.length);
            const paginatedAccounts = filteredAccounts.slice(startIndex, endIndex);
            
            // Update pagination info
            document.getElementById('paginationInfo').textContent = 
                `Menampilkan ${filteredAccounts.length > 0 ? startIndex + 1 : 0}-${endIndex} dari ${filteredAccounts.length} akun`;
            
            // Update pagination numbers
            updatePagination();
            
            // Update table
            const tableBody = document.getElementById('accountsTable').querySelector('tbody');
            const emptyState = document.getElementById('emptyState');
            
            if (filteredAccounts.length === 0) {
                tableBody.innerHTML = '';
                emptyState.classList.remove('d-none');
                return;
            }
            
            emptyState.classList.add('d-none');
            tableBody.innerHTML = '';
            
            paginatedAccounts.forEach((account, index) => {
                const row = document.createElement('tr');
                const truncatedUsername = truncateUsername(account.username);
                
                row.innerHTML = `
                    <td class="cell-number">${startIndex + index + 1}</td>
                    <td class="cell-timestamp copyable" ${columnVisibility.timestamp ? '' : 'style="display:none"'}>${account.timestamp}</td>
                    <td class="copyable" ${columnVisibility.username ? '' : 'style="display:none"'}>${truncatedUsername}</td>
                    <td class="copyable" ${columnVisibility.email ? '' : 'style="display:none"'}>${account.email}</td>
                    <td class="copyable" ${columnVisibility.password ? '' : 'style="display:none"'}>${account.password}</td>
                    <td class="copyable" ${columnVisibility.birthdate ? '' : 'style="display:none"'}>${account.tanggal} ${account.bulan} ${account.tahun}</td>
                    <td class="cell-actions">
                        <button class="action-btn edit-btn" onclick="openEditModal('${account.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-btn delete-btn" onclick="openDeleteModal('${account.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                // Tambahkan event listener untuk copy
                row.querySelectorAll('.copyable').forEach(cell => {
                    cell.style.cursor = 'pointer'; // Ubah kursor menjadi pointer
                    cell.addEventListener('click', () => {
                        copyToClipboard(cell.textContent);
                    });
                });
                
                tableBody.appendChild(row);
            });
            
            // Update column visibility in table header
            const headers = document.getElementById('accountsTable').querySelectorAll('th[data-column]');
            headers.forEach(header => {
                const column = header.getAttribute('data-column');
                if (columnVisibility[column]) {
                    header.style.display = '';
                } else {
                    header.style.display = 'none';
                }
            });
            
            // Setup column visibility dropdown
            setupColumnVisibility();
        }
        
        function updatePagination() {
            const totalPages = Math.ceil(filteredAccounts.length / pageSize);
            const paginationNumbers = document.getElementById('paginationNumbers');
            paginationNumbers.innerHTML = '';
            
            // Previous button
            const prevButton = document.createElement('button');
            prevButton.className = 'pagination-button';
            prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
            prevButton.disabled = currentPage === 1;
            prevButton.onclick = () => goToPage(currentPage - 1);
            paginationNumbers.appendChild(prevButton);
            
            // Page numbers
            let startPage = Math.max(1, currentPage - 2);
            let endPage = Math.min(totalPages, startPage + 4);
            
            if (endPage - startPage < 4) {
                startPage = Math.max(1, endPage - 4);
            }
            
            for (let i = startPage; i <= endPage; i++) {
                const pageButton = document.createElement('button');
                pageButton.className = `pagination-button ${i === currentPage ? 'active' : ''}`;
                pageButton.textContent = i;
                pageButton.onclick = () => goToPage(i);
                paginationNumbers.appendChild(pageButton);
            }
            
            // Next button
            const nextButton = document.createElement('button');
            nextButton.className = 'pagination-button';
            nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
            nextButton.disabled = currentPage === totalPages || totalPages === 0;
            nextButton.onclick = () => goToPage(currentPage + 1);
            paginationNumbers.appendChild(nextButton);
        }
        
        function goToPage(page) {
            currentPage = page;
            updateDashboard();
        }
        
        function changePageSize() {
            pageSize = parseInt(document.getElementById('paginationSize').value);
            
            // Hitung total halaman berdasarkan filtered accounts
            const totalPages = Math.ceil(filteredAccounts.length / pageSize);
            
            // Sesuaikan currentPage jika melebihi total halaman
            currentPage = Math.min(currentPage, totalPages);
            currentPage = Math.max(1, currentPage);
            
            updateDashboard();
        }
        
        function setupColumnVisibility() {
            const dropdown = document.getElementById('columnVisibilityDropdown');
            dropdown.innerHTML = '';
            
            const columns = [
                { key: 'timestamp', label: 'Waktu' },
                { key: 'username', label: 'Username' },
                { key: 'email', label: 'Email' },
                { key: 'password', label: 'Password' },
                { key: 'birthdate', label: 'Tanggal Lahir' }
            ];
            
            columns.forEach(column => {
                const item = document.createElement('div');
                item.className = 'column-visibility-item';
                item.innerHTML = `
                    <input type="checkbox" class="column-visibility-checkbox" id="col_${column.key}" 
                           ${columnVisibility[column.key] ? 'checked' : ''}/>
                    <label for="col_${column.key}">${column.label}</label>
                `;
                
                const checkbox = item.querySelector(`#col_${column.key}`);
                checkbox.addEventListener('change', () => {
                    columnVisibility[column.key] = checkbox.checked;
                    updateDashboard();
                });
                
                dropdown.appendChild(item);
            });
        }
        
        function toggleColumnVisibility() {
            const dropdown = document.getElementById('columnVisibilityDropdown');
            dropdown.classList.toggle('show');
            
            // Close dropdown when clicking outside
            if (dropdown.classList.contains('show')) {
                window.addEventListener('click', closeColumnVisibilityDropdown);
            }
        }
        
        function closeColumnVisibilityDropdown(e) {
            if (!e.target.matches('.column-visibility-button') && 
                !e.target.closest('.column-visibility-content')) {
                document.getElementById('columnVisibilityDropdown').classList.remove('show');
                window.removeEventListener('click', closeColumnVisibilityDropdown);
            }
        }
        
        function startSelenium() {
            fetch('/api/automation/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateAutomationStatus(true);
                    } else {
                        alert("Gagal memulai otomatisasi: " + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Terjadi kesalahan saat memulai otomatisasi");
                });
        }
        
        function stopSelenium() {
            fetch('/api/automation/stop', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateAutomationStatus(false);
                    } else {
                        alert("Gagal menghentikan otomatisasi: " + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert("Terjadi kesalahan saat menghentikan otomatisasi");
                });
        }
        
        function openEditModal(id) {
            const account = allAccounts.find(a => a.id === id);
            if (!account) return;
            
            document.getElementById('editId').value = account.id;
            document.getElementById('editUsername').value = account.username;
            document.getElementById('editEmail').value = account.email;
            document.getElementById('editPassword').value = account.password;
            document.getElementById('editTanggal').value = account.tanggal;
            document.getElementById('editBulan').value = account.bulan;
            document.getElementById('editTahun').value = account.tahun;
            
            const editModal = new bootstrap.Modal(document.getElementById('editModal'));
            editModal.show();
        }
        
        function saveEdit() {
            const id = document.getElementById('editId').value;
            const username = document.getElementById('editUsername').value;
            const email = document.getElementById('editEmail').value;
            const password = document.getElementById('editPassword').value;
            const tanggal = parseInt(document.getElementById('editTanggal').value);
            const bulan = document.getElementById('editBulan').value;
            const tahun = parseInt(document.getElementById('editTahun').value);
            
            fetch('/api/accounts/edit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id, username, email, password, tanggal, bulan, tahun
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
                    modal.hide();
                    fetchData();
                } else {
                    alert('Error saat memperbarui akun');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saat memperbarui akun');
            });
        }
        
        function openDeleteModal(id) {
            const account = allAccounts.find(a => a.id === id);
            if (!account) return;
            
            document.getElementById('deleteId').value = account.id;
            document.getElementById('deleteAccountInfo').textContent = 
                `${account.username} (${account.email})`;
            
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
            deleteModal.show();
        }
        
        function confirmDelete() {
            const id = document.getElementById('deleteId').value;
            
            fetch('/api/accounts/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
                    modal.hide();
                    fetchData();
                } else {
                    alert('Error saat menghapus akun');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error saat menghapus akun');
            });
        }
        
        
        function copyToClipboard(text) {
            const tempInput = document.createElement('input');
            tempInput.value = text;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            
            // Tampilkan tooltip sementara
            const tooltip = document.createElement('div');
            tooltip.textContent = 'Disalin!';
            tooltip.style.position = 'fixed';
            tooltip.style.top = '20px';
            tooltip.style.right = '20px';
            tooltip.style.backgroundColor = 'blue';
            tooltip.style.color = 'white';
            tooltip.style.padding = '10px';
            tooltip.style.borderRadius = '5px';
            tooltip.style.zIndex = '9999';
            document.body.appendChild(tooltip);
            
            setTimeout(() => {
                document.body.removeChild(tooltip);
            }, 1500);
        }
                

        // Update time every second
        setInterval(updateTime, 1000);
        updateTime();
        
        // Initial data fetch
        fetchData();
        
        // Refresh data every 5 seconds
        setInterval(fetchData, 5000);
        
        // Document click handler to close dropdowns
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize column visibility
            setupColumnVisibility();
        });
    </script>
</body>
</html>
'''

# Endpoint untuk mengunduh file Excel
@app.route('/api/accounts/download')
def download_accounts():
    """Generate dan unduh file Excel dengan semua data akun."""
    try:
        # Buat DataFrame Pandas dari data akun
        df = pd.DataFrame(accounts)
        
        # Buat file temporary
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            temp_filename = tmp.name
        
        # Tulis DataFrame ke file Excel
        df.to_excel(temp_filename, index=False, sheet_name='Akun X')
        
        # Kirim file untuk diunduh
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name='akun_x.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"Error saat membuat file Excel: {e}")
        return jsonify({"success": False, "error": str(e)})

# Endpoint untuk memulai selenium
@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Memulai otomatisasi selenium."""
    global automation_running, monitor_thread
    
    try:
        # Jika sudah berjalan, tidak perlu memulai lagi
        if automation_running:
            return jsonify({"success": True, "message": "Otomatisasi sudah berjalan"})
            
        # Set status ke running
        automation_running = True
        
        # Ambil email dari file
        emails = load_emails()
        if not emails:
            automation_running = False
            return jsonify({"success": False, "error": "Tidak ada email dalam emails.txt"})
        
        # Mulai thread untuk membuat browser
        for _ in range(3):
            threading.Thread(target=lambda: create_browser_instance(emails), daemon=True).start()
            time.sleep(1)  # Jeda antar pembuatan browser
        
        # Mulai thread monitoring browser
        monitor_thread = threading.Thread(target=monitor_browsers, args=(emails,), daemon=True)
        monitor_thread.start()
        
        return jsonify({"success": True})
    except Exception as e:
        automation_running = False
        print(f"Error saat memulai otomatisasi: {e}")
        return jsonify({"success": False, "error": str(e)})

# Endpoint untuk menghentikan selenium
@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Menghentikan otomatisasi selenium."""
    global automation_running
    
    try:
        # Jika sudah berhenti, tidak perlu menghentikan lagi
        if not automation_running:
            return jsonify({"success": True, "message": "Otomatisasi sudah berhenti"})
            
        # Set status ke stopped
        automation_running = False
        
        # Tutup semua browser
        close_all_browsers()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saat menghentikan otomatisasi: {e}")
        return jsonify({"success": False, "error": str(e)})

# Endpoint untuk mendapatkan status otomatisasi
@app.route('/api/automation/status')
def get_automation_status():
    """Mendapatkan status otomatisasi."""
    return jsonify({"running": automation_running})

@app.route('/api/browsers/count')
def get_browser_count():
    """Returns an accurate count of active browsers."""
    active_browsers = get_active_browsers()
    return jsonify({"count": len(active_browsers)})

def start_automation():
    """Improved start automation function to maintain exactly 3 browsers."""
    global automation_running, monitor_thread
    
    try:
        if automation_running:
            return jsonify({"success": True, "message": "Automation already running"})
            
        automation_running = True
        
        emails = load_emails()
        if not emails:
            automation_running = False
            return jsonify({"success": False, "error": "No emails in emails.txt"})
        
        # Start with at most 3 browsers
        initial_browsers = min(3, len(emails))
        for _ in range(initial_browsers):
            if create_browser_instance(emails) is None:
                break
            time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor_browsers, args=(emails,), daemon=True)
        monitor_thread.start()
        
        return jsonify({"success": True})
    except Exception as e:
        automation_running = False
        print(f"Error starting automation: {e}")
        return jsonify({"success": False, "error": str(e)})

# Flask routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/accounts')
def get_accounts():
    return jsonify(accounts)

@app.route('/api/accounts/edit', methods=['POST'])
def edit_account():
    global accounts
    data = request.json
    
    try:
        account_id = data['id']
        for i, account in enumerate(accounts):
            if account['id'] == account_id:
                accounts[i]['username'] = data['username']
                accounts[i]['email'] = data['email']
                accounts[i]['password'] = data['password']
                accounts[i]['tanggal'] = data['tanggal']
                accounts[i]['bulan'] = data['bulan']
                accounts[i]['tahun'] = data['tahun']
                break
        
        save_accounts_data()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error mengedit akun: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/accounts/delete', methods=['POST'])
def delete_account():
    global accounts
    data = request.json
    
    try:
        account_id = data['id']
        accounts = [account for account in accounts if account['id'] != account_id]
        
        save_accounts_data()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error menghapus akun: {e}")
        return jsonify({"success": False, "error": str(e)})

def open_browser():
    """Membuka browser secara otomatis."""
    url = "http://127.0.0.1:5000"
    webbrowser.open(url)

def main():
    # Load existing account data
    load_account_data()
    
    # Start Flask web server in a separate thread
    threading.Thread(target=lambda: app.run(debug=False, host='0.0.0.0', use_reloader=False), daemon=True).start()
    
    # Open web browser after a short delay
    print("Membuka dashboard web pada http://127.0.0.1:5000")
    threading.Timer(1.5, open_browser).start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program dihentikan oleh pengguna")
        automation_running = False
        close_all_browsers()

if __name__ == "__main__":
    main()