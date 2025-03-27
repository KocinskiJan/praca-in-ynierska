import os
import time
import psutil
import itertools
import subprocess
import tkinter as tk
import csv
from tkinter import filedialog
from threading import Thread
from queue import Queue, Empty

def choose_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory()

def monitor_resource_usage(pid, interval, result_queue):
    process = psutil.Process(pid)
    max_memory = 0
    cpu_percentages = []

    try:
        while process.is_running():
            mem = process.memory_info().rss / (1024 * 1024)  # MB
            max_memory = max(max_memory, mem)
            cpu = process.cpu_percent(interval=interval)
            cpu_percentages.append(cpu)
    except psutil.NoSuchProcess:
        pass

    avg_cpu = sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else 0
    result_queue.put((avg_cpu, max_memory))

def run_script(script, file1, file2):
    start_time = time.time()

    process = subprocess.Popen(
        ["python", os.path.join(os.path.dirname(__file__), script), file1, file2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    result_queue = Queue()
    monitor_thread = Thread(target=monitor_resource_usage, args=(process.pid, 0.1, result_queue))
    monitor_thread.start()

    stdout, stderr = process.communicate()
    monitor_thread.join()

    end_time = time.time()
    exec_time = end_time - start_time

    try:
        avg_cpu, max_mem = result_queue.get_nowait()
    except Empty:
        avg_cpu, max_mem = 0, 0

    if process.returncode == 0:
        result = stdout.strip()
    else:
        result = f"Błąd: {stderr.strip()}"

    return result, exec_time, avg_cpu, max_mem

def main():
    folder = choose_folder()
    if not folder:
        print("❌ Nie wybrano folderu.")
        return

    scripts = ["rmsd.py", "mcq.py", "tm_score.py", "lddt.py", "inf.py", "torsion.py"]
    pdb_files = [f for f in os.listdir(folder) if f.endswith(".pdb")]

    csv_path = os.path.join(os.path.dirname(__file__), "local_benchmark_results.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Skrypt", "Plik 1", "Plik 2", "Czas [s]", "CPU [%]", "RAM [MB]"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for script in scripts:
            for file1, file2 in itertools.combinations(pdb_files, 2):
                path1 = os.path.join(folder, file1)
                path2 = os.path.join(folder, file2)
                print(f"\n🚀 {script}: {file1} vs {file2}")

                result, exec_time, avg_cpu, max_ram = run_script(script, path1, path2)

                writer.writerow({
                    "Skrypt": script,
                    "Plik 1": file1,
                    "Plik 2": file2,
                    "Czas [s]": round(exec_time, 4),
                    "CPU [%]": round(avg_cpu, 2),
                    "RAM [MB]": round(max_ram, 2)
                })

if __name__ == "__main__":
    main()
