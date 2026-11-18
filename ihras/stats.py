"""Statistical procedures of the article (Ref: Sec. 3.2, Sec. 3.3, Table 3, Table 4).

All functions compute from data.  The unit of analysis for each test is stated
explicitly, because the article does not state it (see ASSUMPTIONS.md, A6).
"""

import numpy as np
from scipy import stats


# ------------------------------------------------- representativeness (3.2)
def representativeness(sample, population, findings):
    """KS for age, chi-square for sex and for the pathology distribution
    (sample counts vs. counts expected from population proportions)."""
    ks = stats.ks_2samp(sample["Patient Age"], population["Patient Age"])
    sex_s = sample["Patient Gender"].value_counts().sort_index()
    sex_p = population["Patient Gender"].value_counts().sort_index()
    exp = sex_p / sex_p.sum() * sex_s.sum()
    chi_sex = stats.chisquare(sex_s.values, exp.values)
    cnt_s = np.array([sample[f].sum() for f in findings], float)
    cnt_p = np.array([population[f].sum() for f in findings], float)
    exp_p = cnt_p / cnt_p.sum() * cnt_s.sum()
    chi_path = stats.chisquare(cnt_s, exp_p)
    return {"repr.ks_age.D": float(ks.statistic), "repr.ks_age.p": float(ks.pvalue),
            "repr.chi2_sex.stat": float(chi_sex.statistic), "repr.chi2_sex.p": float(chi_sex.pvalue),
            "repr.chi2_pathology.stat": float(chi_path.statistic),
            "repr.chi2_pathology.p": float(chi_path.pvalue),
            "repr.chi2_pathology.df": len(findings) - 1}


# ----------------------------------------------------------- comparisons
def cohen_d_paired(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(d.mean() / d.std(ddof=1))


def paired_tests(a, b):
    """Paired t-test, Wilcoxon signed-rank, and Cohen's d_z on paired units."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = stats.ttest_rel(a, b)
    try:
        w = stats.wilcoxon(a, b)
        wp = float(w.pvalue)
    except ValueError:
        wp = float("nan")
    return dict(t=float(t.statistic), p=float(t.pvalue), wilcoxon_p=wp,
                d=cohen_d_paired(a, b), n=len(a))


def mcnemar(correct_a, correct_b):
    """Exact McNemar test on paired binary correctness."""
    a, b = np.asarray(correct_a, bool), np.asarray(correct_b, bool)
    n01 = int((a & ~b).sum())
    n10 = int((~a & b).sum())
    p = stats.binomtest(min(n01, n10), n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return dict(n01=n01, n10=n10, p=float(p))


def anova(*groups):
    f = stats.f_oneway(*groups)
    dfb = len(groups) - 1
    dfw = sum(len(g) for g in groups) - len(groups)
    return dict(F=float(f.statistic), p=float(f.pvalue), df=(dfb, dfw))


def cohen_h(p1, p2):
    return float(abs(2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))))


# --------------------------------------------------------- uncertainty
def bootstrap_ci(fn, n, b, seed, groups=None, level=0.95):
    """Percentile bootstrap of fn(indices).  If ``groups`` is given (patient
    ids), whole patients are resampled."""
    rng = np.random.default_rng(seed)
    if groups is not None:
        groups = np.asarray(groups)
        _, inv = np.unique(groups, return_inverse=True)
        order = np.argsort(inv, kind="stable")
        bounds = np.flatnonzero(np.diff(inv[order])) + 1
        members = np.split(order, bounds)            # indices of each patient, O(n log n)
    vals = []
    for _ in range(b):
        if groups is None:
            idx = rng.integers(0, n, n)
        else:
            pick = rng.integers(0, len(members), len(members))
            idx = np.concatenate([members[i] for i in pick])
        vals.append(fn(idx))
    lo, hi = np.nanquantile(vals, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def t_ci(x, level=0.95):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.5 + level / 2, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return float(x.mean() - h), float(x.mean() + h)


# ------------------------------------------------------ human agreement
def fleiss_kappa(table):
    """``table``: items x categories, counts of raters per category."""
    t = np.asarray(table, float)
    n = t.sum(axis=1)[0]
    p_j = t.sum(axis=0) / t.sum()
    p_i = ((t ** 2).sum(axis=1) - n) / (n * (n - 1))
    pbar, pe = p_i.mean(), (p_j ** 2).sum()
    return float((pbar - pe) / (1 - pe))


def icc_2_1(ratings):
    """ICC(2,1): two-way random effects, absolute agreement, single rater.
    ``ratings``: items x raters."""
    x = np.asarray(ratings, float)
    n, k = x.shape
    gm = x.mean()
    msr = k * ((x.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    msc = n * ((x.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    sse = ((x - x.mean(axis=1, keepdims=True) - x.mean(axis=0, keepdims=True) + gm) ** 2).sum()
    mse = sse / ((n - 1) * (k - 1))
    return float((msr - mse) / (msr + (k - 1) * mse + k * (msc - mse) / n))


def holm(pvalues):
    """Holm-Bonferroni adjustment.  ``pvalues`` maps a test name to its raw
    p-value; the result maps the same names to the adjusted p-values (step-down,
    monotone, capped at 1)."""
    order = sorted(pvalues, key=pvalues.get)
    adjusted, running = {}, 0.0
    for rank, name in enumerate(order):
        running = max(running, min(1.0, (len(order) - rank) * pvalues[name]))
        adjusted[name] = running
    return adjusted
