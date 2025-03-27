import sys
from Bio.PDB import PDBParser
import math
import numpy as np


def calculate_distance(atom1, atom2):
    return (atom1 - atom2)

def calculate_lddt(model, reference, cutoff=15.0):
    total_score = 0
    valid_residue_count = 0

    for model_chain in model:
        reference_chain = reference[model_chain.id] if model_chain.id in reference else None
        if not reference_chain:
            continue

        for model_residue in model_chain:
            if model_residue.id[0] != " ":
                continue

            reference_residue = reference_chain[model_residue.id] if model_residue.id in reference_chain else None
            if not reference_residue:
                continue

            model_atoms = {atom.get_name(): atom for atom in model_residue}
            reference_atoms = {atom.get_name(): atom for atom in reference_residue}

            common_atoms = set(model_atoms.keys()) & set(reference_atoms.keys())

            if len(common_atoms) < 4:
                continue

            distances = []
            for atom_name in common_atoms:
                d = calculate_distance(model_atoms[atom_name].get_coord(), reference_atoms[atom_name].get_coord())
                distances.append(d)

            residue_score = sum(1 for d in distances if np.isscalar(d) and d < 0.5) / len(distances)
            total_score += residue_score
            valid_residue_count += 1

    return total_score / valid_residue_count if valid_residue_count else 0.0

def main(model_pdb, reference_pdb):
    parser = PDBParser(QUIET=True)

    try:
        print(f"[DEBUG] Parsowanie pliku: {reference_pdb}")
        reference_structure = parser.get_structure("reference", reference_pdb)
    except Exception as e:
        print(f"[ERROR] Nie udało się sparsować pliku referencyjnego {reference_pdb}: {e}")
        sys.exit(1)

    try:
        print(f"[DEBUG] Parsowanie pliku: {model_pdb}")
        model_structure = parser.get_structure("model", model_pdb)
    except Exception as e:
        print(f"[ERROR] Nie udało się sparsować pliku modelowego {model_pdb}: {e}")
        sys.exit(1)

    lddt_score = calculate_lddt(model_structure[0], reference_structure[0])
    print(f"{lddt_score:.4f}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python lddt.py model.pdb reference.pdb")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])