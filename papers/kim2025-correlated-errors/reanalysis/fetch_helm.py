"""Independently re-download per-instance HELM MMLU predictions.

The authors' repo ships data/helm/all_mmlu_data_limitedcols.csv as a Git LFS
pointer whose object 404s on GitHub. This script rebuilds the equivalent from
the public source they used: storage.googleapis.com/crfm-helm-public.

Resumable: skips files already on disk. Writes raw/<model>__<subject>.{pred,inst}.json
"""
import json, os, sys, time
import urllib.request, urllib.error

BASE = ("https://storage.googleapis.com/crfm-helm-public/mmlu/benchmark_output/runs/"
        "{v}/mmlu:subject={subj},method=multiple_choice_joint,model={model},"
        "eval_split=test,groups=mmlu_{subj}/{fname}")

VERSIONS = ['v1.0.0','v1.1.0','v1.2.0','v1.3.0','v1.4.0','v1.5.0','v1.6.0',
            'v1.7.0','v1.8.0','v1.9.0','v1.10.0','v1.11.0','v1.12.0','v1.13.0']

# Deliberately spanning providers, families and the accuracy range.
# Includes the pair Kim et al. flag as anomalous (text-unicorn / palmyra-x-v3,
# 0.9987 agreement when both wrong, no publicly stated relationship).
MODELS = [
    "google_text-unicorn@001", "writer_palmyra-x-v3",
    "meta_llama-3.1-8b-instruct-turbo", "meta_llama-3.1-70b-instruct-turbo",
    "meta_llama-3.1-405b-instruct-turbo",
    "anthropic_claude-3-5-sonnet-20241022", "anthropic_claude-3-haiku-20240307",
    "openai_gpt-4o-2024-08-06", "openai_gpt-4o-mini-2024-07-18",
    "openai_gpt-3.5-turbo-0125",
    "google_gemini-1.5-pro-002", "google_gemma-2-27b",
    "qwen_qwen2.5-72b-instruct-turbo", "qwen_qwen1.5-7b",
    "mistralai_mistral-large-2407", "mistralai_mistral-7b-v0.1",
    "01-ai_yi-34b", "allenai_olmo-7b", "microsoft_phi-3-medium-4k-instruct",
    "deepseek-ai_deepseek-llm-67b-chat", "cohere_command-r-plus",
    "databricks_dbrx-instruct",
]

SUBJECTS = ["philosophy", "moral_scenarios", "high_school_psychology",
            "professional_medicine", "college_physics", "formal_logic",
            "econometrics", "machine_learning", "world_religions",
            "high_school_mathematics"]

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
VERMAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version_map.json")


def get(url, timeout=60):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def main():
    os.makedirs(RAW, exist_ok=True)
    vermap = json.load(open(VERMAP)) if os.path.exists(VERMAP) else {}
    ok = miss = skip = 0
    for m in MODELS:
        for subj in SUBJECTS:
            pf = os.path.join(RAW, f"{m}__{subj}.pred.json")
            inf = os.path.join(RAW, f"{m}__{subj}.inst.json")
            if os.path.exists(pf) and os.path.exists(inf):
                skip += 1
                continue
            # try the model's known-good version first, then all
            tries = ([vermap[m]] if m in vermap else []) + \
                    [v for v in VERSIONS if v != vermap.get(m)]
            got = False
            for v in tries:
                pred = get(BASE.format(v=v, subj=subj, model=m,
                                       fname="display_predictions.json"))
                if pred is None:
                    continue
                inst = get(BASE.format(v=v, subj=subj, model=m,
                                       fname="instances.json"))
                if inst is None:
                    continue
                json.dump(pred, open(pf, "w"))
                json.dump(inst, open(inf, "w"))
                vermap[m] = v
                json.dump(vermap, open(VERMAP, "w"), indent=1)
                got = True
                ok += 1
                break
            if not got:
                miss += 1
                print(f"MISS {m} {subj}", flush=True)
        print(f"...{m} done (ok={ok} miss={miss} skip={skip})", flush=True)
    print(f"DONE ok={ok} miss={miss} skip={skip}")


if __name__ == "__main__":
    main()
