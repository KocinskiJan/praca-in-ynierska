#! /usr/bin/env python
import sys

from rnapolis.annotator import extract_base_interactions
from rnapolis.common import LeontisWesthof
from rnapolis.parser import read_3d_structure


def calculate_inf(interactions1, interactions2):
    """Calculate INF score between two sets of interactions."""
    set1 = set(interactions1)
    set2 = set(interactions2)

    tp = len(set1 & set2)
    fn = len(set1 - set2)
    fp = len(set2 - set1)

    if tp == 0:
        return 0.0

    return (tp / (tp + fn) * tp / (tp + fp)) ** 0.5


def extract_interactions(interactions):
    """Extract different types of base interactions."""
    canonical_pairs = []
    non_canonical_pairs = []
    stacking_pairs = []

    # Process base pairs
    for pair in interactions.basePairs:
        if pair.lw == LeontisWesthof.cWW:
            seq = f"{pair.nt1.name}-{pair.nt2.name}"
            if seq in ["A-U", "U-A", "G-C", "C-G", "G-U", "U-G"]:
                canonical_pairs.append((pair.nt1, pair.nt2, None))
            else:
                non_canonical_pairs.append((pair.nt1, pair.nt2, pair.lw))
        else:
            non_canonical_pairs.append((pair.nt1, pair.nt2, pair.lw))

    # Process stacking interactions
    for stack in interactions.stackings:
        stacking_pairs.append((stack.nt1, stack.nt2, None))

    return canonical_pairs, non_canonical_pairs, stacking_pairs


def process_structure(pdb_file):
    """Process PDB file to extract different types of interactions."""
    with open(pdb_file) as f:
        structure = read_3d_structure(f)
        interactions = extract_base_interactions(structure)
        return extract_interactions(interactions)


def main(pdb_file1, pdb_file2, mode="all"):
    canonical1, non_canonical1, stacking1 = process_structure(pdb_file1)
    canonical2, non_canonical2, stacking2 = process_structure(pdb_file2)

    # Calculate INF scores for each interaction type
    canonical_inf = calculate_inf(canonical1, canonical2)
    non_canonical_inf = calculate_inf(non_canonical1, non_canonical2)
    stacking_inf = calculate_inf(stacking1, stacking2)
    all_interactions1 = canonical1 + non_canonical1 + stacking1
    all_interactions2 = canonical2 + non_canonical2 + stacking2
    all_inf = calculate_inf(all_interactions1, all_interactions2)

    # Return score based on mode
    if mode == "canonical":
        print(f"{canonical_inf:.4f}")
    elif mode == "non-canonical":
        print(f"{non_canonical_inf:.4f}")
    elif mode == "stacking":
        print(f"{stacking_inf:.4f}")
    else:  # 'all' is default
        print(f"{all_inf:.4f}")


if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python inf.py <reference_pdb> <model_pdb> [mode]")
        print("mode can be: canonical, non-canonical, stacking, all (default)")
        sys.exit(1)
    mode = sys.argv[3] if len(sys.argv) == 4 else "all"
    main(sys.argv[1], sys.argv[2], mode)
