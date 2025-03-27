#! /usr/bin/env python
import io
import sys

import numpy as np
from Bio import PDB
from Bio.PDB import Superimposer


def extract_phosphorus_atoms(structure):
    atoms = []
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.get_name() == "P":
                        atoms.append(atom)
    return atoms


def calculate_rmsd(structure1_str, structure2_str):
    parser = PDB.PDBParser(QUIET=True)
    structure1 = parser.get_structure("structure1", io.StringIO(structure1_str))
    structure2 = parser.get_structure("structure2", io.StringIO(structure2_str))

    atoms1 = extract_phosphorus_atoms(structure1)
    atoms2 = extract_phosphorus_atoms(structure2)

    if len(atoms1) != len(atoms2):
        raise ValueError("Phosphorus atoms count mismatch")

    # Superimpose the structures
    sup = Superimposer()
    sup.set_atoms(atoms1, atoms2)
    sup.apply(atoms2)

    # Calculate RMSD after superimposition
    coords1 = np.array([atom.get_coord() for atom in atoms1])
    coords2 = np.array([atom.get_coord() for atom in atoms2])

    diff = coords1 - coords2
    rmsd = np.sqrt(np.sum(diff**2) / len(atoms1))
    return rmsd


def main(pdb_file1, pdb_file2):
    with open(pdb_file1) as f:
        with open(pdb_file2) as g:
            print(f"{calculate_rmsd(f.read(), g.read()):.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python rmsd.py <pdb1> <pdb2>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
