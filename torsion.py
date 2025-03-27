from Bio import PDB
import numpy as np
from collections import defaultdict


def calculate_torsion_angle(p1, p2, p3, p4):
    """Calculate torsion angle between four points."""
    v1 = p2 - p1
    v2 = p3 - p2
    v3 = p4 - p3

    n1 = np.cross(v1, v2)
    n2 = np.cross(v2, v3)

    # Normalize vectors
    n1 = n1 / np.linalg.norm(n1)
    n2 = n2 / np.linalg.norm(n2)

    # Calculate angle
    angle = np.arctan2(
        np.dot(np.cross(n1, n2), v2 / np.linalg.norm(v2)), np.dot(n1, n2)
    )
    return np.degrees(angle)


def get_atom_coord(residue, atom_name):
    """Get coordinates of an atom in a residue."""
    if atom_name in residue:
        return residue[atom_name].get_vector().get_array()
    return None


def calculate_torsion_angles(structure):
    """Calculate all torsion angles for each nucleotide in the structure."""
    angles = defaultdict(dict)

    for model in structure:
        for chain in model:
            prev_residue = None
            next_residue = None

            residues = list(chain)
            for i, residue in enumerate(residues):
                # Initialize variables
                O3_prev = None
                next_residue = None

                if i > 0:
                    prev_residue = residues[i - 1]
                    O3_prev = get_atom_coord(prev_residue, "O3'")
                if i < len(residues) - 1:
                    next_residue = residues[i + 1]

                res_id = f"{chain.id}:{residue.id[1]}"
                angles[res_id] = {}

                # Get atom coordinates
                P = get_atom_coord(residue, "P")
                O5 = get_atom_coord(residue, "O5'")
                C5 = get_atom_coord(residue, "C5'")
                C4 = get_atom_coord(residue, "C4'")
                C3 = get_atom_coord(residue, "C3'")
                O3 = get_atom_coord(residue, "O3'")
                C1 = get_atom_coord(residue, "C1'")
                O4 = get_atom_coord(residue, "O4'")

                # For chi angle
                if residue.resname in ["A", "G"]:  # Purines
                    N9 = get_atom_coord(residue, "N9")
                    C4_base = get_atom_coord(residue, "C4")
                    base_atoms = (O4, C1, N9, C4_base)
                else:  # Pyrimidines
                    N1 = get_atom_coord(residue, "N1")
                    C2 = get_atom_coord(residue, "C2")
                    base_atoms = (O4, C1, N1, C2)

                if next_residue:
                    P_next = get_atom_coord(next_residue, "P")
                    O5_next = get_atom_coord(next_residue, "O5'")

                # Calculate angles
                if all(x is not None for x in [O3_prev, P, O5, C5]):
                    angles[res_id]["alpha"] = calculate_torsion_angle(
                        O3_prev, P, O5, C5
                    )

                if all(x is not None for x in [P, O5, C5, C4]):
                    angles[res_id]["beta"] = calculate_torsion_angle(P, O5, C5, C4)

                if all(x is not None for x in [O5, C5, C4, C3]):
                    angles[res_id]["gamma"] = calculate_torsion_angle(O5, C5, C4, C3)

                if all(x is not None for x in [C5, C4, C3, O3]):
                    angles[res_id]["delta"] = calculate_torsion_angle(C5, C4, C3, O3)

                if all(x is not None for x in [C4, C3, O3, P_next]):
                    angles[res_id]["epsilon"] = calculate_torsion_angle(
                        C4, C3, O3, P_next
                    )

                if all(x is not None for x in [C3, O3, P_next, O5_next]):
                    angles[res_id]["zeta"] = calculate_torsion_angle(
                        C3, O3, P_next, O5_next
                    )

                if all(x is not None for x in base_atoms):
                    angles[res_id]["chi"] = calculate_torsion_angle(*base_atoms)

    return angles


def main(pdb_file1, pdb_file2):
    """Calculate and compare torsion angles for two structures."""
    parser = PDB.PDBParser(QUIET=True)

    # Load structures
    structure1 = parser.get_structure("struct1", pdb_file1)
    structure2 = parser.get_structure("struct2", pdb_file2)

    # Calculate angles
    angles1 = calculate_torsion_angles(structure1)
    angles2 = calculate_torsion_angles(structure2)

    # Print results
    print(f"Torsion angles for {pdb_file1}:")
    for res_id, angles in angles1.items():
        print(f"\nResidue {res_id}:")
        for angle_name, value in angles.items():
            print(f"  {angle_name}: {value:.1f}°")

    print(f"\nTorsion angles for {pdb_file2}:")
    for res_id, angles in angles2.items():
        print(f"\nResidue {res_id}:")
        for angle_name, value in angles.items():
            print(f"  {angle_name}: {value:.1f}°")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python torsion.py <pdb_file1> <pdb_file2>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
