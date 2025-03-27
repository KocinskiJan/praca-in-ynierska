#! /usr/bin/env python
import numpy as np
from Bio import PDB

from torsion import calculate_torsion_angles


def calculate_mcq(angles1, angles2):
    """
    Calculate Mean of Circular Quantities (MCQ) between two sets of torsion angles.

    Args:
        angles1: Dictionary of angles from first structure {residue_id: {angle_name: value}}
        angles2: Dictionary of angles from second structure {residue_id: {angle_name: value}}

    Returns:
        float: MCQ value in degrees
    """
    differences = []

    # Collect angular differences for matching residues and angle types
    for res_id in angles1:
        if res_id in angles2:
            for angle_name in angles1[res_id]:
                if angle_name in angles2[res_id]:
                    # Convert to radians and calculate minimum difference
                    angle1 = np.radians(angles1[res_id][angle_name])
                    angle2 = np.radians(angles2[res_id][angle_name])
                    abs_diff = abs(angle1 - angle2)
                    min_diff = min(abs_diff, 2 * np.pi - abs_diff)
                    differences.append(min_diff)

    if not differences:
        return None

    # Calculate sums of sines and cosines
    sum_sin = sum(np.sin(diff) for diff in differences)
    sum_cos = sum(np.cos(diff) for diff in differences)

    # Calculate MCQ using arctan2
    mcq = np.degrees(np.arctan2(sum_sin, sum_cos))

    return mcq


def main(pdb_file1, pdb_file2):
    """Calculate MCQ between torsion angles of two structures."""
    parser = PDB.PDBParser(QUIET=True)

    # Load structures
    structure1 = parser.get_structure("struct1", pdb_file1)
    structure2 = parser.get_structure("struct2", pdb_file2)

    # Calculate torsion angles
    angles1 = calculate_torsion_angles(structure1)
    angles2 = calculate_torsion_angles(structure2)

    # Calculate MCQ
    mcq = calculate_mcq(angles1, angles2)

    if mcq is not None:
        print(f"{mcq:.4f}")
    else:
        print("nan")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python mcq.py <pdb_file1> <pdb_file2>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
