#!/usr/bin/env python3
"""
Generate all static publication images.
Run from the repository root: python publications_webp/static_src/generate_all_static.py
"""

import sys
import os

# Add the static_src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Change to repo root for output paths
repo_root = os.path.dirname(os.path.dirname(script_dir))
os.chdir(repo_root)

# Import all generators
from static_lingolytoo import generate as gen_lingolytoo
from static_sae import generate as gen_sae
from static_constitutions import generate as gen_constitutions
from static_dpo_toxicity import generate as gen_dpo_toxicity
from static_multimodal import generate as gen_multimodal
from static_icl_ensemble import generate as gen_icl_ensemble
from static_ecg import generate as gen_ecg
from static_llm_shared_weaknesses import generate as gen_llm_shared_weaknesses
from static_lingoly_one import generate as gen_lingoly_one
from static_faithful import generate as gen_faithful
from static_eval_llm_judge import generate as gen_eval_llm_judge
from static_helpmed import generate as gen_helpmed
from static_counterfactual import generate as gen_counterfactual
from static_multimodal_cardiomegaly import generate as gen_multimodal_cardiomegaly
from static_dual_bayesian_resnet import generate as gen_dual_bayesian_resnet
from static_llm_landscape_med import generate as gen_llm_landscape_med
from static_mwm import generate as gen_mwm
from static_cardiac_auscultation import generate as gen_cardiac_auscultation

def main():
    generators = [
        ("lingolytoo", gen_lingolytoo),
        ("sae", gen_sae),
        ("constitutions", gen_constitutions),
        ("dpo_toxicity", gen_dpo_toxicity),
        ("multimodal", gen_multimodal),
        ("icl_ensemble", gen_icl_ensemble),
        ("ecg", gen_ecg),
        ("llm_shared_weaknesses", gen_llm_shared_weaknesses),
        ("lingoly_one", gen_lingoly_one),
        ("faithful", gen_faithful),
        ("eval_llm_judge", gen_eval_llm_judge),
        ("helpmed", gen_helpmed),
        ("counterfactual", gen_counterfactual),
        ("multimodal_cardiomegaly", gen_multimodal_cardiomegaly),
        ("dual_bayesian_resnet", gen_dual_bayesian_resnet),
        ("llm_landscape_med", gen_llm_landscape_med),
        ("mwm", gen_mwm),
        ("cardiac_auscultation", gen_cardiac_auscultation),
    ]

    print(f"Generating {len(generators)} static publication images...")
    print(f"Output directory: img/publications/static/")
    print("-" * 50)

    success = 0
    failed = []

    for name, gen_func in generators:
        try:
            gen_func()
            success += 1
        except Exception as e:
            print(f"FAILED: {name} - {e}")
            failed.append((name, str(e)))

    print("-" * 50)
    print(f"Generated {success}/{len(generators)} images successfully")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name, error in failed:
            print(f"  - {name}: {error}")

if __name__ == "__main__":
    main()
