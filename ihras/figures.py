"""Figures regenerated from COMPUTED results (outputs/results.json).

Each figure mirrors the corresponding figure of the article but is drawn from
the values computed by this package, never from the article.  Figures that
depend on a stage that has not run are skipped.
"""

import json
import os

import matplotlib
import matplotlib.ticker
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np                # noqa: E402

from .config import FINDINGS, MODELS, TAU_GRID, SNR_DB, PHOTOMETRIC, TAU_OVERLAP   # noqa: E402

# Validated categorical palette (fixed order), recessive ink and grid.
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
LABEL = {"densenet_nih": "DenseNet-121 (NIH)", "densenet_multi": "DenseNet-121 (multi)",
         "resnet50_multi": "ResNet-50 (multi)"}
METRIC = {"precision": "Precision", "recall": "Recall", "f1": "F1-score",
          "specificity": "Specificity"}

plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6,
                     "legend.frameon": False, "font.family": "DejaVu Sans"})


def _style(ax, grid="y"):
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)


def _save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, name)
    fig.savefig(p, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def _err(v, ci):
    return np.array([[x - c[0], c[1] - x] if c else [0, 0] for x, c in zip(v, ci)]).T


def _reports(out):
    p = os.path.join(os.path.dirname(out), "reports.jsonl")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf8") as f:
        return [json.loads(l) for l in f if l.strip()]


def fig2_distribution(R, out):
    """Manuscript Fig. 2: findings in the stratified sample (computed counts)."""
    vals = [R.get("fig2." + f) for f in FINDINGS]
    if any(v is None for v in vals):
        return None
    order = np.argsort(vals)
    names = [FINDINGS[i].replace("_", " ") for i in order]
    counts = [vals[i] for i in order]
    fig, ax = plt.subplots(figsize=(3.5, 3.6))
    bars = ax.barh(names, counts, color=C1, height=0.68)
    for b, c in zip(bars, counts):
        ax.text(b.get_width() * 1.02, b.get_y() + b.get_height() / 2, "{:,}".format(int(c)),
                va="center", fontsize=6.5, color=INK)
    ax.set_xlabel("Images in the stratified sample (n = {:,})".format(int(R.get("sample.n", 0))))
    ax.set_xlim(0, max(counts) * 1.18)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5000))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "{:,}".format(int(v))))
    _style(ax, "x")
    fig.tight_layout()
    return _save(fig, out, "fig2_pathology_distribution.png")


def fig3_cnn(R, out):
    mets = ("precision", "recall", "f1", "specificity")
    keys = [k for k in MODELS if "cls.%s.f1" % k in R]
    if not keys:
        return None
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    w = 0.26
    for k, (key, col) in enumerate(zip(keys, (C1, C2, C3))):
        v = [R["cls.%s.%s" % (key, m)] for m in mets]
        ci = [R.get("cls.%s.%s_ci" % (key, m)) for m in mets]
        x = np.arange(4) + (k - (len(keys) - 1) / 2) * w
        ax.bar(x, v, w * 0.92, yerr=_err(v, ci), capsize=1.5, color=col, label=LABEL[key],
               error_kw=dict(ecolor=INK, elinewidth=0.6))
        for xi, vi in zip(x, v):
            ax.text(xi, vi + 0.025, "%.3f" % vi, ha="center", fontsize=5.8, color=INK)
    ax.set_xticks(range(4))
    ax.set_xticklabels([METRIC[m] for m in mets])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Micro-averaged value (95% CI)")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=7)
    _style(ax)
    return _save(fig, out, "fig3_cnn_comparison.png")


def fig4_tau(R, out):
    """Two panels with one axis each (no dual axis)."""
    t = R.get("xai.tau_table") or {}
    xs = [x for x in TAU_GRID if t.get("%.2f" % x)]
    if not xs:
        return None
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4), sharex=True)
    for ax, key, title, col, base in (
            (axes[0], "localization_accuracy", "Localization accuracy (pointing game)", C1,
             R.get("xai.gradcam.localization_accuracy")),
            (axes[1], "false_positive_rate", "False-positive rate (map outside box)", C2,
             R.get("xai.gradcam.false_positive_rate"))):
        ys = [t["%.2f" % x][key] for x in xs]
        ax.plot(xs, ys, "-o", color=col, lw=1.6, ms=4)
        if base is not None:
            ax.axhline(base, color=INK2, lw=0.8, ls="--")
            ax.text(xs[-1], base, " Grad-CAM", va="bottom", ha="right", fontsize=6.5, color=INK2)
        ax.axvline(TAU_OVERLAP, color=GRID, lw=1.0, zorder=0)
        ax.set_title(title, fontsize=7.5, color=INK)
        ax.set_xlabel(r"$\tau_{\mathrm{overlap}}$")
        ax.set_ylim(0, 1)
        _style(ax)
    fig.tight_layout()
    return _save(fig, out, "fig4_tau_sensitivity.png")


def fig5_auroc(R, out):
    items = [(f, R["auroc." + f], R.get("auroc.%s_ci" % f)) for f in FINDINGS if "auroc." + f in R]
    if not items:
        return None
    items.sort(key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(3.5, 3.6))
    v = [x[1] for x in items]
    ax.barh([f.replace("_", " ") for f, _, _ in items], v, xerr=_err(v, [x[2] for x in items]),
            capsize=1.5, color=C1, height=0.68, error_kw=dict(ecolor=INK, elinewidth=0.6))
    for i, x in enumerate(v):
        ax.text(0.505, i, "%.3f" % x, va="center", fontsize=6, color="white")
    ax.axvline(np.mean(v), color=INK2, ls="--", lw=0.8)
    ax.text(np.mean(v), len(v) - 0.4, " mean %.3f" % np.mean(v), fontsize=6.5, color=INK2)
    ax.set_xlabel("AUROC, DenseNet-121 (NIH) (95% CI)")
    ax.set_xlim(0.5, 0.9)
    _style(ax, "x")
    fig.tight_layout()
    return _save(fig, out, "fig5_auroc_pathology.png")


def fig6_cv(R, out):
    folds = R.get("cv.folds")
    if not folds:
        return None
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    n = len(folds)
    for m, col in zip(("precision", "recall", "f1", "specificity"), (C1, C2, C3, "#eda100")):
        ys = [f[m] for f in folds]
        ax.plot(range(1, n + 1), ys, "-o", color=col, lw=1.6, ms=4, label=METRIC[m])
        ax.text(n + 0.15, ys[-1], METRIC[m], va="center", fontsize=6.5, color=INK)
    ax.set_xticks(range(1, n + 1))
    ax.set_xlim(0.7, n + 1.3)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Cross-validation fold (patient-grouped)")
    ax.set_ylabel("Micro-averaged value")
    _style(ax)
    return _save(fig, out, "fig6_cv_folds.png")


def fig8_explainability(R, out):
    methods = [("gradcam", "Grad-CAM", C1), ("gradcampp", "Grad-CAM++", C2),
               ("fused", r"Fused ($\tau$=%.2f)" % TAU_OVERLAP, C3)]
    mets = [("localization_accuracy", "Localization accuracy\n(higher is better)"),
            ("false_positive_rate", "False-positive rate\n(lower is better)"),
            ("anatomical_coverage", "Anatomical coverage\n(by construction for fused)")]
    if not all("xai.%s.%s" % (m, k) in R for m, _, _ in methods for k, _ in mets):
        return None
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    w = 0.26
    for k, (m, lab, col) in enumerate(methods):
        v = [R["xai.%s.%s" % (m, key)] for key, _ in mets]
        x = np.arange(3) + (k - 1) * w
        ax.bar(x, v, w * 0.92, color=col, label=lab)
        for xi, vi in zip(x, v):
            ax.text(xi, vi + 0.02, "%.3f" % vi, ha="center", fontsize=5.8, color=INK)
    ax.set_xticks(range(3))
    ax.set_xticklabels([l for _, l in mets])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Value (n = %d NIH boxes)" % R.get("xai.gradcam.n", 0))
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=7)
    _style(ax)
    return _save(fig, out, "fig8_explainability_bars.png")


def fig9_reports(R, out):
    rows = [r for r in _reports(out) if r.get("complete")]
    if not rows:
        return None
    from .report import bleu4, rouge_l
    b = [bleu4(r["report"], r["reference"]) for r in rows]
    g = [rouge_l(r["report"], r["reference"]) for r in rows]
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    bp = ax.boxplot([b, g], vert=True, widths=0.45, patch_artist=True, showfliers=False,
                    medianprops=dict(color=INK, lw=1))
    for patch, col in zip(bp["boxes"], (C1, C2)):
        patch.set_facecolor(col)
        patch.set_alpha(0.35)
        patch.set_edgecolor(col)
    rng = np.random.default_rng(0)
    for i, (vals, col) in enumerate(((b, C1), (g, C2)), start=1):
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(vals)), vals, s=8, color=col, zorder=3)
        ax.text(i + 0.3, np.mean(vals), "mean %.3f\n(SD %.3f)" % (np.mean(vals), np.std(vals, ddof=1)),
                fontsize=6.5, color=INK, va="center")
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["BLEU-4", "ROUGE-L"])
    ax.set_xlim(0.5, 2.9)
    ax.set_ylim(0, max(0.2, 1.15 * max(b + g)))     # scores are low; full 0-1 range hides them
    ax.set_ylabel("Score vs. rule-based reference")
    ax.set_title("%d of %d reports complete" % (R.get("report.n_complete", len(rows)),
                                                 R.get("report.n", len(rows))),
                 fontsize=7.5, color=INK)
    _style(ax)
    return _save(fig, out, "fig9_report_quality.png")


def fig10_time(R, out):
    stages = [("CNN classification", "time.classification"), ("Grad-CAM", "time.gradcam"),
              ("Segmentation (PSPNet)", "time.segmentation"), ("LLM report", "time.llm")]
    if not all(R.get(k) is not None for _, k in stages):
        return None
    secs = [r["seconds"] for r in _reports(out)]
    sd = [0, 0, 0, float(np.std(secs, ddof=1)) if len(secs) > 1 else 0]
    v = [R[k] for _, k in stages]
    fig, ax = plt.subplots(figsize=(3.5, 2.2))
    ax.barh([s for s, _ in stages][::-1], v[::-1], xerr=sd[::-1], color=C1, height=0.6,
            capsize=1.5, error_kw=dict(ecolor=INK, elinewidth=0.6))
    for i, x in enumerate(v[::-1]):
        e = sd[::-1][i]
        ax.text((x + e) * 1.15 if x > 0 else 0.01, i, "%.2f s" % x, va="center", fontsize=6.5,
                color=INK)
    ax.set_xscale("log")
    ax.set_xlim(right=max(v[i] + sd[i] for i in range(4)) * 8)
    ax.set_xlabel("Mean seconds per image (CPU, log scale)")
    _style(ax, "x")
    fig.tight_layout()
    return _save(fig, out, "fig10_processing_time.png")


def fig11_robustness(R, out):
    v = [R.get("robust.noise_%ddb.degradation_pct" % s) for s in SNR_DB]
    if any(x is None for x in v):
        return None
    tags = [("photometric_%d" % round(abs(d) * 100)) + ("_neg" if d < 0 else "") for d in PHOTOMETRIC]
    pv = [R.get("robust.%s.degradation_pct" % t) for t in tags]
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.3), sharey=True)
    ax = axes[0]
    ax.plot(SNR_DB, v, "-o", color=C1, lw=1.6, ms=4)
    for s, y in zip(SNR_DB, v):
        ax.text(s, y + 3, "%.1f%%" % y, ha="center", fontsize=6.5, color=INK)
    ax.invert_xaxis()
    ax.set_xticks(SNR_DB)
    ax.set_xlabel("Additive Gaussian noise, SNR (dB)")
    ax.set_ylabel("Relative F1 degradation (%)")
    _style(ax)
    ax = axes[1]
    if all(x is not None for x in pv):
        labels = ["%+d%%" % round(d * 100) for d in PHOTOMETRIC]
        ax.bar(labels, pv, color=C2, width=0.55)
        for i, y in enumerate(pv):
            ax.text(i, y + 1.5, "%.1f%%" % y, ha="center", fontsize=6.5, color=INK)
        ax.set_xlabel("Contrast/brightness change")
    _style(ax)
    axes[0].set_ylim(0, max(v + [x for x in pv if x is not None]) * 1.2)
    fig.tight_layout()
    return _save(fig, out, "fig11_robustness.png")


def fig12_demographic(R, out):
    groups = [("18–40 y", "fair.f1.age_18_40"), ("41–65 y", "fair.f1.age_41_65"),
              ("66+ y", "fair.f1.age_66_plus"), ("Male", "fair.f1.sex_M"),
              ("Female", "fair.f1.sex_F")]
    if not all(k in R for _, k in groups):
        return None
    v = [R[k] for _, k in groups]
    fig, ax = plt.subplots(figsize=(3.5, 2.4))
    ax.bar([g for g, _ in groups], v, color=[C1] * 3 + [C2] * 2, width=0.6)
    for i, y in enumerate(v):
        ax.text(i, y + 0.01, "%.3f" % y, ha="center", fontsize=6.5, color=INK)
    if "cls.densenet_nih.f1" in R:
        ax.axhline(R["cls.densenet_nih.f1"], color=INK2, ls="--", lw=0.8)
        ax.text(4.4, R["cls.densenet_nih.f1"], "overall", fontsize=6.5, color=INK2, va="bottom",
                ha="right")
    ax.set_ylim(0, max(v) * 1.3)
    ax.set_ylabel("Micro F1, DenseNet-121 (NIH)")
    _style(ax)
    return _save(fig, out, "fig12_demographic.png")


# ------------------------------------------------------- new analyses (T22-T26)
C4 = "#8a5cd1"     # fourth categorical colour (same palette family)
EXT_LABEL = {"densenet_pc": "PadChest", "densenet_chex": "CheXpert",
             "densenet_mimic_ch": "MIMIC-CXR (CheXpert labels)",
             "densenet_mimic_nb": "MIMIC-CXR (NegBio labels)"}


def fig8b_explainability_ci(R, out):
    """Fig. 8 with patient-grouped bootstrap 95% CIs and the fusion applied to
    Grad-CAM++ (stage xai_stats)."""
    methods = [("gradcam", "Grad-CAM", C1), ("gradcampp", "Grad-CAM++", C2),
               ("fused", r"Fused Grad-CAM ($\tau$=%.2f)" % TAU_OVERLAP, C3),
               ("fusedpp", r"Fused Grad-CAM++ ($\tau$=%.2f)" % TAU_OVERLAP, C4)]
    mets = [("localization_accuracy", "Localization accuracy\n(higher is better)"),
            ("false_positive_rate", "False-positive rate\n(lower is better)")]
    if not all("xai.ci.%s.%s" % (m, k) in R for m, _, _ in methods for k, _ in mets):
        return None
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    w = 0.2
    for k, (m, lab, col) in enumerate(methods):
        v = [R["xai.ci.%s.%s" % (m, key)] for key, _ in mets]
        ci = [R.get("xai.ci.%s.%s_ci" % (m, key)) for key, _ in mets]
        x = np.arange(len(mets)) + (k - 1.5) * w
        ax.bar(x, v, w * 0.92, color=col, label=lab, yerr=_err(v, ci), capsize=1.5,
               error_kw=dict(ecolor=INK, elinewidth=0.6))
        for xi, vi, c in zip(x, v, ci):
            ax.text(xi, (c[1] if c else vi) + 0.02, "%.3f" % vi, ha="center", fontsize=5.4, color=INK)
    ax.set_xticks(range(len(mets)))
    ax.set_xticklabels([l for _, l in mets])
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Value (95%% CI; n = %d boxes)" % R.get("xai.ci.n_boxes", 0))
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=6.5)
    _style(ax)
    return _save(fig, out, "fig8b_explainability_ci.png")


def fig13_external(R, out):
    """Cross-dataset validation (stage external): mean AUROC of each external
    model and of DenseNet-121 (NIH) on the same findings, with 95% CIs."""
    keys = [k for k in EXT_LABEL if "ext.%s.mean_auroc" % k in R]
    if not keys:
        return None
    fig, ax = plt.subplots(figsize=(4.2, 0.55 * len(keys) + 0.9))
    for i, k in enumerate(keys):
        for dy, pre, col, lab in ((0.17, "ext.%s" % k, C2, "trained without NIH"),
                                  (-0.17, "ext.%s.ref_nih" % k, C1, "DenseNet-121 (NIH)")):
            v, ci = R[pre + ".mean_auroc"], R.get(pre + ".mean_auroc_ci")
            ax.errorbar(v, i + dy, xerr=_err([v], [ci]), fmt="o", color=col, ms=4,
                        elinewidth=0.8, capsize=1.5, label=lab if i == 0 else None)
            ax.text(v, i + dy + 0.12, "%.3f" % v, fontsize=5.6, color=col, ha="center")
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(["%s\n(%d findings)" % (EXT_LABEL[k], len(R.get("ext.%s.findings" % k, [])))
                        for k in keys], fontsize=6.5)
    ax.set_xlabel("Mean AUROC on NIH sample, same findings (95% CI)")
    # Legend above the axes, so that it never covers a data point or its label.
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=6.3)
    _style(ax, "x")
    fig.tight_layout()
    return _save(fig, out, "fig13_external_validation.png")


def fig14_ablation(R, out):
    """Prompt ablation (stage ablation): hallucination rate (Wilson 95% CI) and
    recall of input findings per prompt arm and LLM."""
    models = R.get("ablation.models") or []
    arms = R.get("ablation.arms") or []
    if not models or not arms:
        return None
    import re
    tags = [re.sub(r"[^a-z0-9]+", "_", m.split("/")[-1].lower()).strip("_") for m in models]
    names = {"plain": "Plain", "crispe": "CRISPE", "crispe_snomed": "CRISPE +\nSNOMED CT"}
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4))
    w = 0.8 / len(models)
    for k, (m, t) in enumerate(zip(models, tags)):
        col = (C1, C2, C3, C4)[k % 4]
        x = np.arange(len(arms)) + (k - (len(models) - 1) / 2) * w
        hr = [R.get("ablation.%s.%s.hallucination_rate" % (t, a), np.nan) for a in arms]
        ci = [R.get("ablation.%s.%s.hallucination_rate_ci" % (t, a)) for a in arms]
        axes[0].bar(x, hr, w * 0.92, color=col, yerr=_err(hr, ci), capsize=1.5,
                    error_kw=dict(ecolor=INK, elinewidth=0.6), label=m.split("/")[-1])
        rc = [R.get("ablation.%s.%s.recall" % (t, a), np.nan) for a in arms]
        axes[1].bar(x, rc, w * 0.92, color=col)
    for ax, lab in zip(axes, ("Reports with a hallucinated finding", "Recall of input findings")):
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels([names.get(a, a) for a in arms], fontsize=6.5)
        ax.set_ylim(0, 1)
        ax.set_ylabel(lab, fontsize=7)
        _style(ax)
    axes[0].legend(fontsize=6, loc="upper right")
    fig.tight_layout()
    return _save(fig, out, "fig14_prompt_ablation.png")


def make_all(R, out):
    made = [f(R, out) for f in (fig2_distribution, fig3_cnn, fig4_tau, fig5_auroc, fig6_cv,
                                fig8_explainability, fig9_reports, fig10_time,
                                fig11_robustness, fig12_demographic,
                                fig8b_explainability_ci, fig13_external, fig14_ablation)]
    print("figures:", [m for m in made if m])
