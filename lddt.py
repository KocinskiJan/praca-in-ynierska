#! /usr/bin/env python
import sys

import numpy as np
from Bio.PDB import PDBParser


def extract_phosphorus_atoms(structure):
    atoms = []
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.get_name() == "P":
                        atoms.append(atom)
    return atoms


def calculate_lddt(reference_structure, model_structure):
    """
    Calculate the local Distance Difference Test (lDDT) score.

    :param reference_structure: PDB structure of the reference
    :param model_structure: PDB structure of the model
    :return: lDDT score (0-1, where 1 is perfect agreement)
    """
    ref_atoms = list(reference_structure.get_atoms())
    model_atoms = list(model_structure.get_atoms())

    if len(ref_atoms) != len(model_atoms):
        raise ValueError(
            "Number of atoms in reference and model structures do not match"
        )

    ref_coords = np.array([atom.coord for atom in ref_atoms])
    model_coords = np.array([atom.coord for atom in model_atoms])

    # Calculate pairwise distances between all atoms efficiently
    # This creates a 2D array where entry (i,j) is the distance between atom i and atom j
    ref_distances = np.linalg.norm(ref_coords[:, None] - ref_coords, axis=2)
    model_distances = np.linalg.norm(model_coords[:, None] - model_coords, axis=2)

    # Create a mask for interactions: atoms within 5A and not on the diagonal (self-interaction)
    interaction_mask = (ref_distances <= 5) & ~np.eye(len(ref_atoms), dtype=bool)

    # Exclude interactions between atoms in the same residue
    for i, atom in enumerate(ref_atoms):
        # Create a boolean array: True if atoms are in different residues, False otherwise
        different_residue = ~np.array(
            [atom.parent.id == ref_atoms[j].parent.id for j in range(len(ref_atoms))]
        )
        # Update the interaction mask to only include atoms in different residues
        interaction_mask[i] &= different_residue

    thresholds = [0.5, 1, 2, 4]
    scores = []

    for threshold in thresholds:
        preserved_interactions = np.abs(ref_distances - model_distances) < threshold
        score = np.sum(preserved_interactions[interaction_mask]) / np.sum(
            interaction_mask
        )
        scores.append(score)

    return np.mean(scores)


def main(reference_pdb, model_pdb):
    parser = PDBParser()
    reference_structure = parser.get_structure("reference", reference_pdb)
    model_structure = parser.get_structure("model", model_pdb)

    lddt_score = calculate_lddt(reference_structure, model_structure)
    print(f"{lddt_score:.4f}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lddt.py <reference_pdb> <model_pdb>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
