#!/usr/bin/env python3

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, SCRIPT_DIR)
os.chdir(REPO_ROOT)

from static_cardiac_auscultation import generate as gen_cardiac_auscultation
from static_constitutions import generate as gen_constitutions
from static_counterfactual import generate as gen_counterfactual
from static_dpo_toxicity import generate as gen_dpo_toxicity
from static_dual_bayesian_resnet import generate as gen_dual_bayesian_resnet
from static_ecg import generate as gen_ecg
from static_eval_llm_judge import generate as gen_eval_llm_judge
from static_faithful import generate as gen_faithful
from static_helpmed import generate as gen_helpmed
from static_icl_ensemble import generate as gen_icl_ensemble
from static_lingoly_one import generate as gen_lingoly_one
from static_lingolytoo import generate as gen_lingolytoo
from static_llm_landscape_med import generate as gen_llm_landscape_med
from static_llm_shared_weaknesses import generate as gen_llm_shared_weaknesses
from static_multimodal import generate as gen_multimodal
from static_multimodal_cardiomegaly import generate as gen_multimodal_cardiomegaly
from static_mwm import generate as gen_mwm
from static_sae import generate as gen_sae


def main():
    generators = [
        ("cardiac_auscultation", gen_cardiac_auscultation),
        ("constitutions", gen_constitutions),
        ("counterfactual", gen_counterfactual),
        ("dpo_toxicity", gen_dpo_toxicity),
        ("dual_bayesian_resnet", gen_dual_bayesian_resnet),
        ("ecg", gen_ecg),
        ("eval_llm_judge", gen_eval_llm_judge),
        ("faithful", gen_faithful),
        ("helpmed", gen_helpmed),
        ("icl_ensemble", gen_icl_ensemble),
        ("lingoly_one", gen_lingoly_one),
        ("lingolytoo", gen_lingolytoo),
        ("llm_landscape_med", gen_llm_landscape_med),
        ("llm_shared_weaknesses", gen_llm_shared_weaknesses),
        ("multimodal", gen_multimodal),
        ("multimodal_cardiomegaly", gen_multimodal_cardiomegaly),
        ("mwm", gen_mwm),
        ("sae", gen_sae),
    ]

    print(f"Generating {len(generators)} v2 static publication images...")
    failed = []
    for name, fn in generators:
        try:
            fn()
        except Exception as exc:
            failed.append((name, str(exc)))
            print(f"failed {name}: {exc}")

    if failed:
        print("Failures:")
        for name, message in failed:
            print(f" - {name}: {message}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
