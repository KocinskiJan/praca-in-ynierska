import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import itertools
import time
import csv
import psutil
from datetime import datetime

# Wybór folderu z GUI
root = tk.Tk()
root.withdraw()
folder_selected = filedialog.askdirectory(title="Wybierz folder z plikami PDB")

if not folder_selected:
    print("❌ Nie wybrano folderu.")
    exit()

# Funkcja do pobrania docker stats
def get_docker_stats(container_name):
    try:
        result = subprocess.run([
            "docker", "stats", container_name, "--no-stream",
            "--format", "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}"
        ], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"error,{e}"

# Lista plików PDB
pdb_files = [f for f in os.listdir(folder_selected) if f.endswith(".pdb")]
pdb_paths = [os.path.join(folder_selected, f) for f in pdb_files]
pdb_pairs = list(itertools.combinations(pdb_paths, 2))

# Nazwa kontenera i obrazu
container_name = "docker-image"
docker_image = "docker-image"

# Uruchomienie kontenera
print(f"🛠️  Uruchamianie kontenera {container_name} z obrazem {docker_image}...")
subprocess.run(["docker", "run", "-dit", "--name", container_name, "-v", f"{folder_selected}:/data", docker_image, "/bin/bash"])

# Przygotowanie CSV
csv_file = "docker_benchmark_results.csv"
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Plik1", "Plik2", "Miara", "Czas [s]", "RAM [MB]", "CPU", "Docker RAM"])

scripts = {
    "rmsd": "rmsd.py",
    "mcq": "mcq.py",
    "tm_score": "tm_score.py",
    "lddt": "lddt.py",
    "inf": "inf.py",
    "torsion": "torsion.py"
}

for file1, file2 in pdb_pairs:
    for measure, script in scripts.items():
        print(f"🚀 Uruchamianie: {script} dla {os.path.basename(file1)} vs {os.path.basename(file2)}")

        start = time.time()
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        try:
            result = subprocess.run([
                "docker", "exec", container_name,
                "python3", f"/app/{script}",
                f"/data/{os.path.basename(file1)}",
                f"/data/{os.path.basename(file2)}"
            ], capture_output=True, text=True, timeout=120)

            mem_after = process.memory_info().rss / (1024 * 1024)
            elapsed = round(time.time() - start, 2)
            mem_used = round(mem_after - mem_before, 2)
            output = result.stdout.strip() or result.stderr.strip()

            stats = get_docker_stats(container_name).split(",")
            cpu = stats[1] if len(stats) > 1 else "N/A"
            mem_docker = stats[2] if len(stats) > 2 else "N/A"

            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    os.path.basename(file1),
                    os.path.basename(file2),
                    measure,
                    elapsed,
                    mem_used,
                    cpu,
                    mem_docker
                ])
        except Exception as e:
            print(f"❌ Błąd: {e}")

# Zatrzymaj i usuń kontener
print(" Zatrzymywanie kontenera...")
subprocess.run(["docker", "stop", container_name])
subprocess.run(["docker", "rm", container_name])
print("✅ Zakończono.")
