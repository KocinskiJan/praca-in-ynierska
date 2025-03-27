#!/usr/bin/env python3
import os
import subprocess
import sys

# Ścieżka do USalign w warstwie AWS Lambda
USALIGN_PATH = "/opt/bin/USalign"

def find_usalign():
    """Zwraca ścieżkę do USalign w środowisku AWS Lambda."""
    if os.path.exists(USALIGN_PATH):
        return USALIGN_PATH
    raise FileNotFoundError("USalign not found in /opt/bin/. Make sure the layer is added.")

def calculate_tm_score(structure1_path, structure2_path):
    """Oblicza TM-score między dwoma strukturami przy użyciu USalign."""
    usalign_path = find_usalign()

    result = subprocess.run(
        [usalign_path, structure1_path, structure2_path, "-outfmt", "2"],
        capture_output=True,
        text=True,
        check=True,
    )

    lines = result.stdout.strip().split("\n")
    if len(lines) < 2:
        raise RuntimeError("Unexpected USalign output format")

    # Wyciągnięcie TM-score
    tm_score = float(lines[1].split("\t")[2])
    return tm_score

def main(pdb_file1, pdb_file2):
    """Funkcja główna do obliczenia TM-score między dwoma plikami PDB."""
    try:
        score = calculate_tm_score(pdb_file1, pdb_file2)
        print(f"{score:.4f}")
        return score
    except Exception as e:
        print(f"Error calculating TM-score: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tm_score.py <reference_pdb> <model_pdb>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
