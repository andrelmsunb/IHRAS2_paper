"""Add McNemar discordant counts, exact-match accuracy, and mean per-image F1
to an existing outputs/results.json from the cached predictions, without
re-running the classification stage (same computation as run_all.stage_classify).

Usage:  python analysis/paired_details.py [--out outputs]
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ihras import classify, data, stats, config as C   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "outputs"))
    a = ap.parse_args()
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    y = data.labels_matrix(df)
    preds = {k: np.load(os.path.join(a.out, "predictions_%s.npz" % k))["p"] for k in C.MODELS}
    exact = {k: ((np.nan_to_num(p) >= C.DECISION_THRESHOLD).astype(int) == y).all(axis=1)
             for k, p in preds.items()}
    new = {}
    for other, tag in (("densenet_multi", "vs_multi"), ("resnet50_multi", "vs_resnet")):
        mc = stats.mcnemar(exact["densenet_nih"], exact[other])
        new["test.mcnemar_%s.n01" % tag] = mc["n01"]
        new["test.mcnemar_%s.n10" % tag] = mc["n10"]
    for k, p in preds.items():
        new["cls.%s.exact_match" % k] = float(exact[k].mean())
        new["cls.%s.per_image_f1_mean" % k] = float(np.mean(classify.per_image_f1(y, p)))
    # Composition diagnostic: share of normal studies, and mean AUROC when the
    # negatives of each finding are restricted to studies with no finding.
    nf = (df["Finding Labels"] == "No Finding").values
    new["sample.no_finding_share"] = float(nf.mean())
    p = preds["densenet_nih"]
    au = [classify.roc_auc_score(y[(y[:, j] == 1) | nf, j], p[(y[:, j] == 1) | nf, j])
          for j in range(len(C.FINDINGS))]
    new["cls.densenet_nih.mean_auroc_vs_no_finding"] = float(np.mean(au))
    path = os.path.join(a.out, "results.json")
    with open(path, encoding="utf8") as f:
        R = json.load(f)
    R.update(new)
    with open(path, "w", encoding="utf8") as f:
        json.dump(R, f, indent=1)
    print(new)


if __name__ == "__main__":
    main()
