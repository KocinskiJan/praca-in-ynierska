#! /usr/bin/env python
import os
import shutil
import subprocess
import sys
import urllib.request


def prepare_usalign():
    """Find USalign in PATH or download and compile if not present"""
    # First check if USalign is in PATH
    usalign_path = shutil.which("USalign")
    if usalign_path:
        return usalign_path

    # If not in PATH, check current directory
    if os.path.exists("USalign"):
        return "./USalign"

    # Download and compile
    if not os.path.exists("USalign.cpp"):
        url = "https://zhanggroup.org/US-align/bin/module/USalign.cpp"
        urllib.request.urlretrieve(url, "USalign.cpp")

    subprocess.run(
        ["g++", "-static", "-O3", "-ffast-math", "-o", "USalign", "USalign.cpp"],
        check=True,
    )
    return "./USalign"


def calculate_tm_score(structure1_path, structure2_path):
    """Calculate TM-score between two structures using USalign"""
    prepare_usalign()

    usalign_path = prepare_usalign()
    result = subprocess.run(
        [usalign_path, structure1_path, structure2_path, "-outfmt", "2"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Get the second line and split by tabs
    lines = result.stdout.strip().split("\n")
    if len(lines) < 2:
        raise RuntimeError("Unexpected USalign output format")

    # Extract TM-score from the third column
    tm_score = float(lines[1].split("\t")[2])
    return tm_score


def main(pdb_file1, pdb_file2):
    """Main function to calculate TM-score between two PDB files"""
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
