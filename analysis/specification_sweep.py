#!/usr/bin/env python3
"""Specification sweep for the sampling and representativeness results
(article Sec. 3.2).

Purpose: check, transparently, whether ANY reasonable reading of the article
reproduces the reported values (n = 50,133; largest stratum 9,677; KS of age
p = 0.847; chi-square of sex p = 0.247; chi-square of pathologies p = 0.052).
Every combination is reported, matching or not, so that the result is not
selected after the fact.

Dimensions swept
  strata definition   full label string | first label only | any-finding (binary)
                      | without view position | without sex
  age binning         25-year bins | 25-year bins starting at 1
  cap                 370 (article) | Eq. (6) per stratum (proportional n_s)
  seed                0..9
  test reference      population | population minus sample (independent)

    python analysis/specification_sweep.py --metadata Data_Entry_2017_v2020.csv
"""

import argparse
import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ihras import data                    # noqa: E402
from ihras.config import FINDINGS        # noqa: E402

TARGET = dict(n=50_133, largest=9_677, ks_p=0.847, sex_p=0.247, path_p=0.052)


def strata_columns(df, how):
    d = df.copy()
    d["first_label"] = d["Finding Labels"].str.split("|").str[0]
    d["any_finding"] = (d["Finding Labels"] != "No Finding").astype(int)
    base = {"full": ["age_bin", "Finding Labels", "Patient Gender", "View Position"],
            "first": ["age_bin", "first_label", "Patient Gender", "View Position"],
            "binary": ["age_bin", "any_finding", "Patient Gender", "View Position"],
            "no_view": ["age_bin", "Finding Labels", "Patient Gender"],
            "no_sex": ["age_bin", "Finding Labels", "View Position"]}[how]
    return d, base


def draw(d, cols, cap_rule, seed):
    rng = np.random.default_rng(seed)
    parts = []
    for _, g in d.groupby(cols):
        k = len(g) if cap_rule == "370" and len(g) <= 370 else (
            370 if cap_rule == "370" else int(np.ceil(data.per_stratum_size(len(g)))))
        k = min(k, len(g))
        parts.append(g.iloc[rng.choice(len(g), k, replace=False)] if k < len(g) else g)
    return pd.concat(parts)


def tests(sample, ref):
    ks = stats.ks_2samp(sample["Patient Age"], ref["Patient Age"])
    s, r = (x["Patient Gender"].value_counts().sort_index() for x in (sample, ref))
    sex = stats.chisquare(s.values, (r / r.sum() * s.sum()).values)
    cs = np.array([sample[f].sum() for f in FINDINGS], float)
    cr = np.array([ref[f].sum() for f in FINDINGS], float)
    path = stats.chisquare(cs, cr / cr.sum() * cs.sum())
    return ks.statistic, ks.pvalue, sex.pvalue, path.pvalue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--out", default="outputs/specification_sweep.csv")
    a = ap.parse_args()
    pop = data.load_metadata(a.metadata)
    rows = []
    for how, shift, cap in itertools.product(("full", "first", "binary", "no_view", "no_sex"),
                                             (0, 1), ("370", "eq6")):
        p = pop.copy()
        p["age_bin"] = ((p["Patient Age"] - shift).clip(lower=0) // 25).astype(int)
        d, cols = strata_columns(p, how)
        largest = int(d.groupby(cols).size().max())
        for seed in range(10):
            smp = draw(d, cols, cap, seed)
            for ref_name, ref in (("population", pop),
                                  ("complement", pop[~pop["Image Index"].isin(smp["Image Index"])])):
                D, ksp, sexp, pathp = tests(smp, ref)
                rows.append(dict(strata=how, age_shift=shift, cap=cap, seed=seed, reference=ref_name,
                                 n=len(smp), largest_stratum=largest, ks_D=D, ks_p=ksp,
                                 sex_p=sexp, pathology_p=pathp))
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    df.to_csv(a.out, index=False)
    print("specifications evaluated:", len(df))
    print("n == 50,133:", int((df.n == TARGET["n"]).sum()),
          "| largest == 9,677:", int((df.largest_stratum == TARGET["largest"]).sum()))
    print("KS p > 0.05:", int((df.ks_p > 0.05).sum()), "| sex p > 0.05:", int((df.sex_p > 0.05).sum()),
          "| pathology p > 0.05:", int((df.pathology_p > 0.05).sum()))
    print("all three p > 0.05 simultaneously:",
          int(((df.ks_p > 0.05) & (df.sex_p > 0.05) & (df.pathology_p > 0.05)).sum()))
    print("closest n to 50,133:", df.iloc[(df.n - TARGET["n"]).abs().argmin()][
        ["strata", "age_shift", "cap", "n", "largest_stratum"]].to_dict())
    print("range of p-values: KS [%.1e, %.1e]  sex [%.1e, %.1e]  pathology [%.1e, %.1e]" % (
        df.ks_p.min(), df.ks_p.max(), df.sex_p.min(), df.sex_p.max(),
        df.pathology_p.min(), df.pathology_p.max()))


if __name__ == "__main__":
    main()
