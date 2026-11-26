"""Step 2: top-5 masked-LM substitutes per mention (GPU). Resumable: one .npy per chunk of 20,000 mentions.

    <arena .venv-gpu python> papers/card2023-substitution-scd/reanalysis/get_substitutes.py [--model bert-large-uncased] [--limit N]

As the paper: target replaced by ONE [MASK] (multi-piece words included), up to 50 whitespace tokens of context on each
side, top-k = 5 most probable vocabulary items excluding Snowball stopwords and '##' pieces. Not as the paper: no
continued MLM pre-training on the corpora (first pass), so substitutes come from the off-the-shelf model.
Writes work/subs_<model>/chunk_<i>.npy (int32 [n, 5] vocab ids) and DONE marker SUBS_OK.
"""
import argparse
import gzip
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

KB = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.run(["python", str(KB / "tools" / "assets.py"), "path",
                            "paper-downloads/card2023-substitution-scd"], capture_output=True, text=True,
                           check=True).stdout.strip())
C = ROOT / "corpus" / "semeval2020_ulscd_eng"
W = ROOT / "work"
CHUNK = 20000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="bert-large-uncased")
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--limit", type=int, default=0, help="only the first N mentions (speed test)")
    a = ap.parse_args()
    out = W / f"subs_{a.model.replace('/', '_')}"; out.mkdir(exist_ok=True)
    tok = {c: gzip.open(C / f"corpus{c}" / "token" / f"ccoha{c}.txt.gz", "rt", encoding="utf-8").read().splitlines()
           for c in (1, 2)}
    ments = [json.loads(l) for l in open(W / "mentions.jsonl", encoding="utf-8")]
    if a.limit:
        ments = ments[:a.limit]
    tk = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForMaskedLM.from_pretrained(a.model).cuda().eval().half()
    stop = set((HERE / "stopwords_snowball_en.txt").read_text(encoding="utf-8").split())
    vocab = tk.convert_ids_to_tokens(list(range(len(tk))))
    banned = torch.tensor([v.startswith("##") or v in stop or not any(ch.isalpha() for ch in v) or v.startswith("[")
                           for v in vocab], device="cuda")
    n_chunks = (len(ments) + CHUNK - 1) // CHUNK
    t0 = time.time(); done = 0
    for ci in range(n_chunks):
        f = out / f"chunk_{ci:04d}.npy"
        if f.exists():
            continue
        part = ments[ci * CHUNK:(ci + 1) * CHUNK]
        texts = []
        for m in part:
            ws = tok[m["corpus"]][m["line"]].split()
            p = m["pos"]
            texts.append(" ".join(ws[max(0, p - 50):p] + [tk.mask_token] + ws[p + 1:p + 51]))
        res = np.zeros((len(part), 5), dtype=np.int32)
        for b in range(0, len(texts), a.batch):
            enc = tk(texts[b:b + a.batch], return_tensors="pt", padding=True, truncation=True, max_length=256).to("cuda")
            with torch.no_grad():
                logits = model(**enc).logits
            mpos = (enc["input_ids"] == tk.mask_token_id).nonzero()
            # one mask per row; if truncation removed it, row stays zeros (counted below)
            rows = mpos[:, 0]; cols = mpos[:, 1]
            lg = logits[rows, cols].float()
            lg[:, banned] = -1e9
            top = lg.topk(5, dim=-1).indices.cpu().numpy()
            res[b + rows.cpu().numpy()] = top
        np.save(f, res)
        done += len(part)
        el = time.time() - t0
        print(f"chunk {ci + 1}/{n_chunks} saved; {done} mentions in {el:.0f}s ({done / el:.0f}/s)", flush=True)
    print("SUBS_OK")


if __name__ == "__main__":
    main()
