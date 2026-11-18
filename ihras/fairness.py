"""Subgroup performance (Ref: Sec. 4.4, Fig. 12; 2025 Tables 4-5).

Tests: chi-square of per-image exact-match correctness across subgroups, and
the maximum pairwise Cohen's h of precision, recall, F1, and specificity, as in
the precursor (2025 Sec. 4.1.3).  ASSUMPTIONS.md, A10.
"""

import itertools

import numpy as np
from scipy import stats

from .classify import metrics
from .stats import cohen_h


def subgroups(df, age_groups):
    g = {}
    for lo, hi in age_groups:
        key = "age_%d_%s" % (lo, "plus" if hi >= 200 else hi)
        g[key] = ((df["Patient Age"] >= lo) & (df["Patient Age"] <= hi)).values
    for s in ("M", "F"):
        g["sex_" + s] = (df["Patient Gender"] == s).values
    return g


def subgroup_metrics(y, p, groups, thr):
    out = {}
    for name, mask in groups.items():
        if mask.sum():
            out[name] = dict(metrics(y[mask], p[mask], thr), n=int(mask.sum()))
    return out


def max_cohen_h(per_group, keys):
    res = {}
    for metric in ("precision", "recall", "f1", "specificity"):
        vals = [per_group[k][metric] for k in keys if k in per_group]
        res[metric] = max((cohen_h(a, b) for a, b in itertools.combinations(vals, 2)), default=0.0)
    return res


def correctness_chi2(y, p, thr, masks):
    correct = ((np.nan_to_num(p) >= thr).astype(int) == y).all(axis=1)
    table = np.array([[int((correct & m).sum()), int((~correct & m).sum())] for m in masks])
    table = table[table.sum(axis=1) > 0]
    if len(table) < 2 or (table.sum(axis=0) == 0).any():
        return dict(stat=float("nan"), p=float("nan"), df=0, note="degenerate table")
    chi = stats.chi2_contingency(table)
    return dict(stat=float(chi.statistic), p=float(chi.pvalue), df=int(chi.dof))
