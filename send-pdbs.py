import os
import requests
import mimetypes
import tkinter as tk
from tkinter import filedialog

# Konfiguracja
API_URL = "https://hslp11so7j.execute-api.us-east-1.amazonaws.com/Get_files"
BUCKET_NAME = "rna-files"  

# Okno dialogowe do wyboru folderu
root = tk.Tk()
root.withdraw() 
folder_path = filedialog.askdirectory(title="Wybierz folder z plikami PDB")

if not folder_path:
    print(" Nie wybrano folderu. Zamykanie programu.")
    exit(1)

# Przeglądaj folder i filtruj pliki .pdb
for filename in os.listdir(folder_path):
    if not filename.lower().endswith(".pdb"):
        print(f"❌ Pominięto plik (niewłaściwe rozszerzenie): {filename}")
        continue

    filepath = os.path.join(folder_path, filename)

    # Krok 1: Pobierz pre-signed URL z API
    response = requests.post(API_URL, json={
        "bucket": BUCKET_NAME,
        "paths": [filename]
    })

    if response.status_code != 200:
        print(f"❌ Błąd podczas pobierania URL dla {filename}: {response.text}")
        continue

    url_data = response.json()

    # Oczekujemy, że API zwróci np. { "urls": { "filename.pdb": "https://presigned-url" } }
    upload_url = url_data.get("urls", {}).get(filename)

    if not upload_url:
        print(f"❌ Brak URL w odpowiedzi API dla {filename}.")
        continue

    # Wysyłanie plików na S3 przez pre-signed URL
    with open(filepath, 'rb') as f:
        file_data = f.read()
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        upload_response = requests.put(upload_url, data=file_data)


    if upload_response.status_code == 200:
        print(f"✅ Przesłano: {filename}")
    else:
        print(f"❌ Błąd podczas przesyłania {filename}: {upload_response.status_code}, {upload_response.text}")