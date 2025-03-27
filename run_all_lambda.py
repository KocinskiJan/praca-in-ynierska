import time
import json
import requests
import psutil
import os
import csv
import tkinter as tk
from tkinter import filedialog
from itertools import combinations

# Konfiguracja
API_URL = "https://lnpogz6s05.execute-api.us-east-1.amazonaws.com/prod"
S3_BUCKET = "rna-files"
ALLOWED_SCRIPTS = [
    "inf.py",
    "lddt-lambda.py",
    "mcq.py",
    "rmsd.py",
    "tm_score_lambda.py",
    "torsion.py"
]
CSV_FILE = "lambda_benchmark_results.csv"

# Wybór folderu z plikami
root = tk.Tk()
root.withdraw()
folder_path = filedialog.askdirectory(title="Wybierz folder z plikami PDB")

if not folder_path:
    print("❌ Nie wybrano folderu.")
    exit()

pdb_files = sorted([
    f for f in os.listdir(folder_path)
    if f.lower().endswith(".pdb")
])

if len(pdb_files) < 2:
    print("❌ W folderze musi znajdować się przynajmniej 2 pliki .pdb")
    exit()

# Przygotowanie pliku CSV
with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["script", "pdb1", "pdb2", "exec_time_s", "api_time_s", "ram_used_mb", "cpu_percent", "result"])

# Funkcja wywołująca API i zbierająca metryki
def invoke_lambda(script, pdb1, pdb2):
    print(f"\n🚀 Uruchamianie: {script} dla pary {pdb1} i {pdb2}")
    payload = {
        "script": script,
        "s3_bucket": S3_BUCKET,
        "pdb1_key": pdb1,
        "pdb2_key": pdb2
    }

    process = psutil.Process(os.getpid())
    cpu_before = psutil.cpu_percent(interval=None)
    ram_before = process.memory_info().rss / 1024 / 1024
    time_start = time.time()

    result_text = ""
    exec_time = None
    api_time = None
    ram_delta = None
    cpu_percent = None

    try:
        api_start = time.time()
        response = requests.post(API_URL, json=payload)
        api_end = time.time()
        time_end = time.time()

        ram_after = process.memory_info().rss / 1024 / 1024
        cpu_after = psutil.cpu_percent(interval=None)

        exec_time = time_end - time_start
        api_time = api_end - api_start
        ram_delta = ram_after - ram_before
        cpu_percent = cpu_after  # może być przybliżone w krótkich zadaniach

        if response.status_code == 200:
            result_text = response.json().get("body", "").strip()
            print("✅ Sukces:", result_text[:200], "...")
        else:
            result_text = f"HTTP {response.status_code}: {response.text}"
            print("❌ Błąd HTTP:", result_text)

    except Exception as e:
        result_text = str(e)
        print("❌ Wyjątek:", result_text)

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            script,
            pdb1,
            pdb2,
            round(exec_time, 3) if exec_time else "",
            round(api_time, 3) if api_time else "",
            round(ram_delta, 3) if ram_delta else "",
            round(cpu_percent, 2) if cpu_percent is not None else "",
            result_text
        ])

# Wykonanie dla każdej pary plików i skryptów
for pdb1, pdb2 in combinations(pdb_files, 2):
    for script in ALLOWED_SCRIPTS:
        invoke_lambda(script, pdb1, pdb2)

print(f"\n📁 Wyniki zapisane do: {CSV_FILE}")
