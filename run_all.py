#!/usr/bin/env python3
"""Run the IHRAS reproducibility pipeline and compare with the article.

    python run_all.py --nih-dir /data/NIH --stages all
    python run_all.py --nih-dir /data/NIH --stages sampling        # metadata only
    python run_all.py --smoke-test                                # synthetic data, ~1 min

Stages (ordered): sampling, classify, explain, robustness, fairness, report,
human, figures, compare.  Results accumulate in outputs/results.json; the
comparison with the article is written to outputs/COMPARISON.md.

New analyses (not part of ``all``; run them explicitly):
  predict     cache predictions of the models in --models (also external ones)
  external    cross-dataset validation of weights trained without NIH (T23)
  official    evaluation on the official NIH test split, test_list.txt (T24)
  xai_stats   bootstrap CIs and paired tests of the explainability metrics (T26)
  ablation    prompt ablation of the LLM reports with fidelity metrics (T25)
  timing      per-item processing time on the current hardware, in isolation (T22)

Parallel jobs: the stage ``predict`` only computes and
caches the predictions of the models listed in ``--models``, so that each model
can run in its own job/output folder.  The folders are combined afterwards with
analysis/merge_jobs.py, and ``classify`` then computes every metric from the
cached predictions without running the models again.

The NIH directory must contain Data_Entry_2017.csv (or _v2020), BBox_List_2017.csv,
test_list.txt, and the image folders (images_001 ... images_012).
"""

import argparse
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# TorchXRayVision prints a Unicode progress bar while downloading weights;
# the default Windows console encoding (cp1252) cannot print it.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from ihras import config as C                                   # noqa: E402
from ihras import data, stats, classify, explain, localization  # noqa: E402
from ihras import robustness, fairness, report, compare         # noqa: E402
from ihras import fidelity                                      # noqa: E402

STAGES = ("sampling", "classify", "explain", "robustness", "fairness", "report",
          "human", "figures", "compare")
# Execution order, including stages that run only when requested explicitly
# (``--stages all`` keeps the original set above).
ORDER = (("sampling", "predict") + STAGES[1:5]
         + ("external", "official", "xai_stats") + STAGES[5:7]
         + ("ablation", "timing") + STAGES[7:])


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


class Store:
    def __init__(self, out):
        self.path = os.path.join(out, "results.json")
        self.d = json.load(open(self.path)) if os.path.exists(self.path) else {}

    def put(self, **kw):
        self.d.update({k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                       for k, v in kw.items()})
        json.dump(self.d, open(self.path, "w"), indent=1, default=float)


def metadata_path(nih):
    for n in ("Data_Entry_2017.csv", "Data_Entry_2017_v2020.csv"):
        if os.path.exists(os.path.join(nih, n)):
            return os.path.join(nih, n)
    raise FileNotFoundError("Data_Entry_2017*.csv not found in " + nih)


# ------------------------------------------------------------------ stages
def stage_sampling(a, S):
    pop = data.load_metadata(metadata_path(a.nih_dir))
    sample, info = data.stratified_sample(pop, seed=a.seed)
    sample.to_csv(os.path.join(a.out, "sample_manifest.csv"), index=False)
    rep = stats.representativeness(sample, pop, C.FINDINGS)
    counts_pop = {f: int(pop[f].sum()) for f in C.FINDINGS}
    counts_smp = {f: int(sample[f].sum()) for f in C.FINDINGS}
    S.put(**{"sample.n": info["n"], "sample.largest_stratum": info["largest_stratum"],
             "sample.n_strata": info["n_strata"],
             "sample.per_stratum_formula_n": info["formula_n_largest_ceil"],
             "metadata_file": os.path.basename(metadata_path(a.nih_dir))}, **rep,
          **{"fig2." + f: v for f, v in counts_smp.items()},
          **{"population." + f: v for f, v in counts_pop.items()})
    print("sampling:", info, rep)


def _images(a, df, size):
    """Yield preprocessed images in manifest order, loaded by parallel workers."""
    from torch.utils.data import DataLoader
    idx = data.index_images(a.nih_dir)
    ds = data.XrvImageDataset([idx[n] for n in df["Image Index"]], size)
    loader = DataLoader(ds, batch_size=None, shuffle=False, num_workers=a.workers,
                        persistent_workers=False)
    for img in loader:
        yield img.numpy() if hasattr(img, "numpy") else img


def load_cached(a, key, df, tag=""):
    """Cached predictions of model ``key`` for ``df`` (None if not cached).

    A cache is accepted only if it lists exactly the images of ``df``, in the
    same order, so that predictions from another sample are never mixed in.
    ``tag`` distinguishes other image sets (e.g. "__official_test")."""
    cache = os.path.join(a.out, "predictions_%s%s.npz" % (key, tag))
    if not os.path.exists(cache):
        return None
    z = np.load(cache, allow_pickle=True)              # file written by this pipeline
    if "names" in z.files and not np.array_equal(z["names"].astype(str),
                                                 df["Image Index"].values.astype(str)):
        raise ValueError("%s does not match its image manifest" % cache)
    return z["p"]


def predict_group(a, S, keys, df, tag=""):
    """Predictions of every model in ``keys`` for ``df``, computing the missing ones.

    Models with the same input size share one pass over the images.  The total
    time of a pass is stored only when it holds a single model of the main
    sample (key time.classification_total_s.<model>, as in the original run)."""
    out = {}
    missing = []
    for k in keys:
        p = load_cached(a, k, df, tag)
        if p is None:
            missing.append(k)
        else:
            out[k] = p
    for size in sorted({classify.input_size(k) for k in missing}):
        group = [k for k in missing if classify.input_size(k) == size]
        models = {k: classify.load_model(k, pretrained=not a.smoke_test)[0] for k in group}
        t0 = time.time()
        preds = classify.predict_multi(models, _images(a, df, size), a.device, a.batch_size)
        elapsed = time.time() - t0
        for k, p in preds.items():
            np.savez_compressed(os.path.join(a.out, "predictions_%s%s.npz" % (k, tag)),
                                p=p, names=df["Image Index"].values)
            out[k] = p
        if len(group) == 1 and not tag:
            S.put(**{"time.classification_total_s.%s" % group[0]: elapsed})
        else:
            S.put(**{"time.predict_pass_total_s.%s%s" % ("+".join(group), tag): elapsed})
        del models
    return out


def predict_cached(a, S, key, df):
    """Predictions of model ``key`` for the main sample, in manifest order: read
    from outputs/predictions_<key>.npz when present (for example copied from
    another job), computed and cached otherwise."""
    p = load_cached(a, key, df)
    if p is not None:
        return p
    cache = os.path.join(a.out, "predictions_%s.npz" % key)
    model, size = classify.load_model(key, pretrained=not a.smoke_test)
    t0 = time.time()
    p = classify.predict(model, _images(a, df, size), a.device, a.batch_size)
    np.savez_compressed(cache, p=p, names=df["Image Index"].values)
    S.put(**{"time.classification_total_s.%s" % key: time.time() - t0})
    return p


def stage_predict(a, S):
    """Compute and cache the predictions of the models in ``--models`` only
    (no metrics): one model per job when the run is split across sessions."""
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    _check_models(a.models)
    for key, p in predict_group(a, S, a.models, df).items():
        print("predict: %s -> %d x %d" % (key, *p.shape))


def _check_models(keys):
    unknown = [k for k in keys if k not in C.ALL_MODELS]
    if unknown:
        raise ValueError("unknown model(s) %s; choose from %s" % (unknown, ", ".join(C.ALL_MODELS)))


def stage_classify(a, S):
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    y = data.labels_matrix(df)
    groups = df["Patient ID"].values
    preds, per_image = {}, {}
    for key in C.MODELS:
        p = predict_cached(a, S, key, df)
        preds[key] = p
        m = classify.metrics(y, p, C.DECISION_THRESHOLD, "micro")
        mm = classify.metrics(y, p, C.DECISION_THRESHOLD, "macro")
        thr, _ = classify.best_threshold(y, p)
        ci = {k: stats.bootstrap_ci(lambda i, k=k: classify.metrics(y[i], p[i])[k], len(y),
                                    a.bootstrap, a.seed, groups) for k in m}
        auc = classify.per_class_auroc(y, p)
        S.put(**{"cls.%s.%s" % (key, k): v for k, v in m.items()},
              **{"cls.%s.%s_ci" % (key, k): v for k, v in ci.items()},
              **{"cls.%s.macro.%s" % (key, k): v for k, v in mm.items()},
              **{"cls.%s.best_threshold" % key: thr,
                 "cls.%s.mean_auroc" % key: float(np.mean(list(auc.values()))) if auc else None},
              **{"binary.%s.%s" % (key, k): v for k, v in classify.binary_abnormal(y, p).items()})
        if key == "densenet_nih":
            S.put(**{"auroc." + f: v for f, v in auc.items()})
            for f, v in auc.items():
                j = C.FINDINGS.index(f)
                S.put(**{"auroc.%s_ci" % f: stats.bootstrap_ci(
                    lambda i, j=j: classify.roc_auc_score(y[i, j], p[i, j])
                    if 0 < y[i, j].sum() < len(i) else np.nan, len(y), a.bootstrap, a.seed, groups)})
            folds = classify.cross_validated_metrics(y, p, groups)
            f1s = np.array([r["f1"] for r in folds])
            S.put(**{"cv.folds": folds, "cv.f1_mean": f1s.mean(),
                     "cv.f1_cv_percent": 100 * f1s.std(ddof=1) / f1s.mean(),
                     "cv.f1_cv_percent_ddof0": 100 * f1s.std() / f1s.mean()})
        per_image[key] = classify.per_image_f1(y, p)
    # Table 4: unit = image (per-image F1) for paired t / Wilcoxon; exact-match
    # correctness for McNemar; fold-level micro-F1 for ANOVA (ASSUMPTIONS A6)
    for other, tag in (("densenet_multi", "vs_multi"), ("resnet50_multi", "vs_resnet")):
        r = stats.paired_tests(per_image["densenet_nih"], per_image[other])
        exact = lambda p: ((np.nan_to_num(p) >= C.DECISION_THRESHOLD).astype(int) == y).all(axis=1)
        mc = stats.mcnemar(exact(preds["densenet_nih"]), exact(preds[other]))
        S.put(**{"test.ttest_%s.t" % tag: r["t"], "test.ttest_%s.p" % tag: r["p"],
                 "test.ttest_%s.d" % tag: r["d"], "test.ttest_%s.n" % tag: r["n"],
                 "test.wilcoxon_%s.p" % tag: r["wilcoxon_p"], "test.mcnemar_%s.p" % tag: mc["p"],
                 "test.mcnemar_%s.n01" % tag: mc["n01"], "test.mcnemar_%s.n10" % tag: mc["n10"]})
    for key in C.MODELS:
        S.put(**{"cls.%s.exact_match" % key: float(
                     ((np.nan_to_num(preds[key]) >= C.DECISION_THRESHOLD).astype(int) == y).all(axis=1).mean()),
                 "cls.%s.per_image_f1_mean" % key: float(np.mean(per_image[key]))})
    folds = classify.cv_folds(y, groups)
    for metric in ("precision", "recall", "f1", "specificity"):
        g = [[classify.metrics(y[te], preds[k][te])[metric] for _, te in folds] for k in C.MODELS]
        an = stats.anova(*g)
        S.put(**{"test.anova_%s.F" % metric: an["F"], "test.anova_%s.p" % metric: an["p"],
                 "test.anova_%s.df" % metric: an["df"]})
    print("classify: done")


def stage_explain(a, S):
    import pandas as pd
    import torch
    boxes = localization.load_bboxes(os.path.join(a.nih_dir, "BBox_List_2017.csv"))
    if a.limit:
        boxes = boxes.head(a.limit)
    idx = data.index_images(a.nih_dir)
    model, size = classify.load_model("densenet_nih", pretrained=not a.smoke_test)
    model.to(a.device)                      # Grad-CAM and segmentation follow --device
    out_idx = classify.output_index(model)
    seg = explain.load_segmenter(a.device) if not a.smoke_test else None
    rows = {m: [] for m in ["gradcam", "gradcampp"] + ["fused_%.2f" % t for t in C.TAU_GRID]
            + ["fusedpp_%.2f" % t for t in C.TAU_GRID]}
    per_box = []        # one row per (box, method): input for bootstrap CIs and paired tests
    box_id = 0          # running index of the evaluated boxes (aligns methods per box)
    t_cam, t_seg = [], []
    for _, b in boxes.iterrows():
        if b["Finding Label"] not in C.FINDINGS or b["Image Index"] not in idx:
            continue
        j = out_idx[C.FINDINGS.index(b["Finding Label"])]
        if j is None:
            continue
        img = data.load_xrv_image(idx[b["Image Index"]], size)
        t0 = time.time()
        cam = explain.gradcam(model, img, j)
        t_cam.append(time.time() - t0)
        campp = explain.gradcampp(model, img, j)
        t0 = time.time()
        if seg is not None:
            masks = explain.resize_mask(explain.segment(seg, data.load_xrv_image(
                idx[b["Image Index"]], 512)), cam.shape)
        else:
            masks = np.zeros((len(C.ANATOMY),) + cam.shape, bool)
            masks[4, :, : cam.shape[1] // 2] = True
        t_seg.append(time.time() - t0)
        gt = localization.box_mask(cam.shape, b)
        anat = masks.any(axis=0)
        maps = {"gradcam": cam, "gradcampp": campp}
        for t in C.TAU_GRID:
            maps["fused_%.2f" % t] = explain.fuse(cam, masks, tau_overlap=t)[0]
            # Same fusion applied to Grad-CAM++ (new analysis; keys xai.fusedpp.*)
            maps["fusedpp_%.2f" % t] = explain.fuse(campp, masks, tau_overlap=t)[0]
        for method, m in maps.items():
            r = localization.evaluate_map(m, gt, anat)
            rows[method].append(r)
            # NIH file names start with the patient ID (e.g. 00000013_005.png -> 13)
            per_box.append(dict(box=box_id, image=b["Image Index"],
                                patient=int(b["Image Index"].split("_")[0]),
                                finding=b["Finding Label"], method=method, **r))
        box_id += 1
    summ = {k: localization.summarize(v) for k, v in rows.items() if v}
    tau_table = {"%.2f" % t: summ.get("fused_%.2f" % t) for t in C.TAU_GRID}
    best = summ.get("fused_%.2f" % C.TAU_OVERLAP, {})
    pd.DataFrame(per_box).to_csv(os.path.join(a.out, "xai_per_box.csv"), index=False)
    S.put(**{"xai.fusedpp.%s" % k: v
             for k, v in summ.get("fusedpp_%.2f" % C.TAU_OVERLAP, {}).items()},
          **{"xai.fusedpp_tau_table": {"%.2f" % t: summ.get("fusedpp_%.2f" % t)
                                       for t in C.TAU_GRID},
             "xai.device": str(a.device)})
    S.put(**{"xai.gradcam.%s" % k: v for k, v in summ.get("gradcam", {}).items()},
          **{"xai.gradcampp.%s" % k: v for k, v in summ.get("gradcampp", {}).items()},
          **{"xai.fused.%s" % k: v for k, v in best.items()},
          **{"xai.tau_table": tau_table,
             "time.gradcam": float(np.mean(t_cam)) if t_cam else None,
             "time.segmentation": float(np.mean(t_seg)) if t_seg else None})
    print("explain:", summ.get("gradcam"), best)


def stage_robustness(a, S):
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    df = df.sample(n=min(a.robust_n, len(df)), random_state=a.seed)
    y = data.labels_matrix(df)
    model, size = classify.load_model("densenet_nih", pretrained=not a.smoke_test)
    clean = list(_images(a, df, size))
    p0 = classify.predict(model, clean, a.device, a.batch_size)
    f0 = classify.metrics(y, p0)["f1"]
    rng = np.random.default_rng(a.seed)
    res = {}
    for snr in C.SNR_DB:
        p = classify.predict(model, [robustness.add_noise_snr(x, snr, rng) for x in clean],
                             a.device, a.batch_size)
        res["robust.noise_%ddb.degradation_pct" % snr] = robustness.degradation_pct(f0, classify.metrics(y, p)["f1"])
    for d in C.PHOTOMETRIC:
        p = classify.predict(model, [robustness.photometric(x, d) for x in clean], a.device, a.batch_size)
        tag = ("photometric_%d" % round(abs(d) * 100)) + ("_neg" if d < 0 else "")
        res["robust.%s.degradation_pct" % tag] = robustness.degradation_pct(f0, classify.metrics(y, p)["f1"])
    for sign in (-1, 1):
        thr = C.DECISION_THRESHOLD * (1 + sign * C.HPARAM_PERTURB)
        res["robust.threshold_%+d.f1" % (sign * 10)] = classify.metrics(y, p0, thr)["f1"]
    S.put(**res, **{"robust.n_images": len(df), "robust.f1_clean": f0})
    print("robustness:", res)


def stage_fairness(a, S):
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    y = data.labels_matrix(df)
    p = np.load(os.path.join(a.out, "predictions_densenet_nih.npz"))["p"]
    for tag, ages in (("article", C.AGE_GROUPS_ARTICLE), ("2025", C.AGE_GROUPS_2025)):
        g = fairness.subgroups(df, ages)
        per = fairness.subgroup_metrics(y, p, g, C.DECISION_THRESHOLD)
        age_keys = [k for k in per if k.startswith("age_")]
        S.put(**{"fair.%s.%s" % (tag, k): v for k, v in per.items()},
              **{"fair.%s.max_cohen_h_age" % tag: fairness.max_cohen_h(per, age_keys),
                 "fair.%s.chi2_age" % tag: fairness.correctness_chi2(
                     y, p, C.DECISION_THRESHOLD, [g[k] for k in age_keys])})
        if tag == "article":
            S.put(**{"fair.f1.%s" % k: v["f1"] for k, v in per.items()})
    sx = fairness.subgroups(df, ())
    S.put(**{"fair.chi2_sex": fairness.correctness_chi2(y, p, C.DECISION_THRESHOLD,
                                                         [sx["sex_M"], sx["sex_F"]])})
    print("fairness: done")


def _subset_evaluation(a, y, p, cols, groups, prefix):
    """Metrics of predictions ``p`` restricted to finding columns ``cols``:
    micro precision/recall/F1/specificity at the article threshold, mean and
    per-finding AUROC, and patient-grouped bootstrap CIs of F1 and mean AUROC."""
    pm = classify.mask_columns(p, cols)
    m = classify.subset_metrics(y, p, cols)
    out = {"%s.%s" % (prefix, k): v for k, v in m.items()}
    out["%s.f1_ci" % prefix] = stats.bootstrap_ci(
        lambda i: classify.subset_metrics(y[i], p[i], cols)["f1"], len(y), a.bootstrap, a.seed, groups)
    out["%s.mean_auroc" % prefix] = classify.mean_auroc(y, pm)
    out["%s.mean_auroc_ci" % prefix] = stats.bootstrap_ci(
        lambda i: classify.mean_auroc(y[i], pm[i]), len(y), a.bootstrap, a.seed, groups)
    out.update({"%s.auroc.%s" % (prefix, f): v for f, v in classify.per_class_auroc(y, pm).items()})
    return out


def stage_external(a, S):
    """T23: cross-dataset validation.  Weights trained without NIH (CheXpert,
    MIMIC-CXR, PadChest) are evaluated on the NIH sample, each on the findings it
    predicts, side by side with DenseNet-121 (NIH) on exactly the same findings.
    Uses cached predictions only (run 'predict' with the external models first)."""
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    y, groups = data.labels_matrix(df), df["Patient ID"].values
    ref = load_cached(a, "densenet_nih", df)
    if ref is None:
        raise FileNotFoundError("predictions_densenet_nih.npz is required for 'external'")
    for key in C.EXTERNAL_MODELS:
        p = load_cached(a, key, df)
        if p is None:
            print("external: %s not cached, skipped" % key)
            continue
        cols = classify.predicted_columns(p)
        res = _subset_evaluation(a, y, p, cols, groups, "ext.%s" % key)
        res.update(_subset_evaluation(a, y, ref, cols, groups, "ext.%s.ref_nih" % key))
        pm, rm = classify.mask_columns(p, cols), classify.mask_columns(ref, cols)
        # Paired difference (external - NIH-trained) on the same images and findings
        res["ext.%s.delta_mean_auroc" % key] = classify.mean_auroc(y, pm) - classify.mean_auroc(y, rm)
        res["ext.%s.delta_mean_auroc_ci" % key] = stats.bootstrap_ci(
            lambda i: classify.mean_auroc(y[i], pm[i]) - classify.mean_auroc(y[i], rm[i]),
            len(y), a.bootstrap, a.seed, groups)
        res["ext.%s.findings" % key] = [C.FINDINGS[j] for j in cols]
        res["ext.%s.weights" % key] = C.EXTERNAL_MODELS[key]
        S.put(**res)
        print("external: %s  %d findings  mean AUROC %.3f (NIH-trained %.3f)"
              % (key, len(cols), res["ext.%s.mean_auroc" % key], res["ext.%s.ref_nih.mean_auroc" % key]))


def stage_official(a, S):
    """T24: evaluation on the official patient-wise NIH test split (test_list.txt).
    Predicts the models in --models on those images (a GPU job), then evaluates
    each one on the findings it predicts.  Caveat for the article: the split used
    to train the TorchXRayVision NIH weights is not documented, so this is the
    official split, not a guaranteed leakage-free test."""
    pop = data.load_metadata(metadata_path(a.nih_dir))
    _, test = data.official_split(pop, os.path.join(a.nih_dir, "test_list.txt"))
    test = test.sort_values("Image Index").reset_index(drop=True)
    test.to_csv(os.path.join(a.out, "official_test_manifest.csv"), index=False)
    y, groups = data.labels_matrix(test), test["Patient ID"].values
    _check_models(a.models)
    preds = predict_group(a, S, a.models, test, tag="__official_test")
    S.put(**{"split.n_images": len(test), "split.n_patients": int(test["Patient ID"].nunique())})
    for key in a.models:
        p = preds[key]
        cols = classify.predicted_columns(p)
        res = _subset_evaluation(a, y, p, cols, groups, "split.%s" % key)
        res["split.%s.findings" % key] = [C.FINDINGS[j] for j in cols]
        S.put(**res)
        print("official: %s  F1 %.3f  mean AUROC %.3f"
              % (key, res["split.%s.f1" % key], res["split.%s.mean_auroc" % key]))


XAI_METHODS = {"gradcam": "gradcam", "gradcampp": "gradcampp",
               "fused": "fused_%.2f" % C.TAU_OVERLAP, "fusedpp": "fusedpp_%.2f" % C.TAU_OVERLAP}
XAI_PAIRS = (("gradcam", "gradcampp"), ("gradcam", "fused"), ("gradcampp", "fused"),
             ("gradcampp", "fusedpp"), ("fused", "fusedpp"))


def stage_xai_stats(a, S):
    """T26: uncertainty of the explainability comparison (Fig. 8).  From
    xai_per_box.csv: patient-grouped bootstrap 95% CIs of pointing-game accuracy,
    false-positive rate and anatomical coverage for each method, and paired
    tests between methods on the same boxes (exact McNemar on pointing-game hits,
    Wilcoxon and bootstrap CI of the FPR difference), Holm-adjusted."""
    import pandas as pd
    from scipy import stats as sps
    box = pd.read_csv(os.path.join(a.out, "xai_per_box.csv"))
    wide = {m: box[box["method"] == col].set_index("box").sort_index()
            for m, col in XAI_METHODS.items()}
    ref_index = wide["gradcam"].index
    groups = wide["gradcam"]["patient"].values
    res = {"xai.ci.n_boxes": int(len(ref_index)), "xai.ci.n_patients": int(len(set(groups)))}
    for m, w in wide.items():
        w = w.loc[ref_index]
        for metric, col in (("localization_accuracy", "hit"), ("false_positive_rate", "fpr"),
                            ("anatomical_coverage", "coverage")):
            v = w[col].astype(float).values
            res["xai.ci.%s.%s" % (m, metric)] = float(np.nanmean(v))
            res["xai.ci.%s.%s_ci" % (m, metric)] = stats.bootstrap_ci(
                lambda i, v=v: np.nanmean(v[i]), len(v), a.bootstrap, a.seed, groups)
    raw_p = {}
    for x, z in XAI_PAIRS:
        wx, wz = wide[x].loc[ref_index], wide[z].loc[ref_index]
        mc = stats.mcnemar(wx["hit"].astype(bool).values, wz["hit"].astype(bool).values)
        d = wx["fpr"].values - wz["fpr"].values
        tag = "xai.test.%s_vs_%s" % (x, z)
        raw_p[tag] = mc["p"]
        res.update({tag + ".hit_mcnemar_p": mc["p"], tag + ".hit_n01": mc["n01"],
                    tag + ".hit_n10": mc["n10"],
                    tag + ".fpr_diff": float(d.mean()),
                    tag + ".fpr_diff_ci": stats.bootstrap_ci(lambda i: d[i].mean(), len(d),
                                                             a.bootstrap, a.seed, groups),
                    tag + ".fpr_wilcoxon_p": float(sps.wilcoxon(d).pvalue) if np.any(d) else 1.0})
    # Holm-Bonferroni adjustment of the McNemar p-values across the pairs
    for tag, p in stats.holm(raw_p).items():
        res[tag + ".hit_mcnemar_p_holm"] = p
    S.put(**res)
    print("xai_stats:", {m: round(res["xai.ci.%s.localization_accuracy" % m], 3) for m in wide})


class _RegionFinder:
    """Most affected anatomical region of a case (Sec. 3.1): the segmented
    structure that holds the largest share of the Grad-CAM saliency of the most
    probable finding.  It fills the "Most affected region" of the prompt and the
    finding site of the SNOMED CT expressions.  Models are loaded once."""

    def __init__(self, a):
        self.a = a
        self.idx = data.index_images(a.nih_dir)
        self.model, self.size = classify.load_model("densenet_nih", pretrained=not a.smoke_test)
        self.model.to(a.device)
        self.out_idx = classify.output_index(self.model)
        self.seg = explain.load_segmenter(a.device) if not a.smoke_test else None

    def __call__(self, image, found):
        if not found:
            return None                      # no finding above threshold: no region
        top = max(found, key=lambda fp: fp[1])[0]
        j = self.out_idx[C.FINDINGS.index(top)]
        if j is None:
            return None
        img = data.load_xrv_image(self.idx[image], self.size)
        cam = explain.gradcam(self.model, img, j)
        if self.seg is not None:
            masks = explain.resize_mask(explain.segment(
                self.seg, data.load_xrv_image(self.idx[image], 512)), cam.shape)
        else:                                # smoke test: one synthetic region
            masks = np.zeros((len(C.ANATOMY),) + cam.shape, bool)
            masks[4, :, : cam.shape[1] // 2] = True
        k = explain.most_affected_region(cam, masks)
        return C.ANATOMY[k] if k is not None else None


def _report_cases(a, df, p_all, full, regions=None):
    """Cases (metadata + findings above threshold + most affected region) for the
    images of ``df``, built exactly as in the report stage.  ``regions`` is a
    _RegionFinder; one is created when not given."""
    pos = full.reset_index().set_index("Image Index").loc[df["Image Index"], "index"].values
    regions = regions or _RegionFinder(a)
    cases = []
    for (_, r), i in zip(df.iterrows(), pos):
        found = [(f, float(p_all[i, j])) for j, f in enumerate(C.FINDINGS)
                 if not np.isnan(p_all[i, j]) and p_all[i, j] >= C.DECISION_THRESHOLD]
        cases.append(dict(image=r["Image Index"], age=int(r["Patient Age"]),
                          sex=r["Patient Gender"], view=r["View Position"],
                          findings=found, region=regions(r["Image Index"], found)))
    return cases


def _model_tag(name):
    """Short key-safe tag of an LLM name (e.g. deepseek_r1_distill_qwen_1_5b)."""
    import re
    return re.sub(r"[^a-z0-9]+", "_", (name or "default").split("/")[-1].lower()).strip("_")


def stage_ablation(a, S):
    """T25: prompt ablation.  The same images are reported under three prompts
    (plain, CRISPE, CRISPE + SNOMED CT = IHRAS) by each LLM in
    --ablation-models, and every report is scored for fidelity to its input
    findings (ihras/fidelity.py).  Reports are checkpointed per (model, arm) in
    ablation_reports.jsonl, so an interrupted job resumes where it stopped."""
    import pandas as pd
    full = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    df = full.sample(n=min(a.ablation_n, len(full)), random_state=a.seed)
    p_all = load_cached(a, "densenet_nih", full)
    if p_all is None:
        raise FileNotFoundError("predictions_densenet_nih.npz is required for 'ablation'")
    cases = _report_cases(a, df, p_all, full)
    smap = report.load_snomed_map(os.path.join(HERE, "resources", "snomed_map.csv"))
    path = os.path.join(a.out, "ablation_reports.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf8")] if os.path.exists(path) else []
    done = {(r["model"], r["arm"]) for r in rows}
    models = [m for m in a.ablation_models.split(",") if m]
    for model in models:
        for arm in C.ABLATION_ARMS:
            if (model, arm) in done:
                print("ablation: %s / %s already generated" % (model, arm))
                continue
            prompts = [report.build_arm_prompt(c, smap, arm) for c in cases]
            texts, secs = report.generate_batch(prompts, a.llm_backend, model=model,
                                                max_tokens=a.llm_max_tokens,
                                                batch_size=a.llm_batch_size, dtype=a.llm_dtype)
            for c, prompt, raw, sec in zip(cases, prompts, texts, secs):
                text = report.strip_reasoning(raw)
                rows.append(dict(model=model, arm=arm, image=c["image"], prompt=prompt, raw=raw,
                                 report=text, complete=bool(text), seconds_amortized=sec,
                                 input_findings=[f for f, _ in c["findings"]],
                                 region=c["region"]))
            report.save_jsonl(rows, path)                  # checkpoint after every arm
            print("ablation: %s / %s  %d reports" % (model, arm, len(prompts)), flush=True)
    # ---- per-report fidelity table and aggregate keys
    table = []
    for r in rows:
        sc = fidelity.score_report(r["report"], r["input_findings"]) if r["complete"] else {}
        ref = report.rule_based_reference(dict(findings=[(f, 0) for f in r["input_findings"]],
                                               region=r.get("region")))
        table.append(dict(model=r["model"], arm=r["arm"], image=r["image"], complete=r["complete"],
                          bleu4=report.bleu4(r["report"], ref) if r["complete"] else np.nan,
                          rouge_l=report.rouge_l(r["report"], ref) if r["complete"] else np.nan,
                          **sc))
    t = pd.DataFrame(table)
    t.to_csv(os.path.join(a.out, "ablation_per_report.csv"), index=False)
    res = {"ablation.n_images": len(cases), "ablation.arms": list(C.ABLATION_ARMS),
           "ablation.models": models, "ablation.dtype": a.llm_dtype,
           "ablation.max_tokens": a.llm_max_tokens}
    for model in models:
        mt = _model_tag(model)
        for arm in C.ABLATION_ARMS:
            g = t[(t["model"] == model) & (t["arm"] == arm)]
            c = g[g["complete"]]
            k = "ablation.%s.%s" % (mt, arm)
            nh = int(c["hallucination"].sum()) if len(c) else 0
            res.update({k + ".n": len(g), k + ".complete_rate": float(g["complete"].mean()),
                        k + ".hallucination_rate": nh / len(c) if len(c) else np.nan,
                        k + ".hallucination_rate_ci": fidelity.wilson_ci(nh, len(c)),
                        k + ".hallucinated_per_report": float(c["n_hallucinated"].mean()) if len(c) else np.nan,
                        k + ".recall": float(c["recall"].mean()) if len(c) else np.nan,
                        k + ".contradiction_rate": float(c["contradiction"].mean()) if len(c) else np.nan,
                        k + ".words_mean": float(c["words"].mean()) if len(c) else np.nan,
                        k + ".bleu4_mean": float(c["bleu4"].mean()) if len(c) else np.nan,
                        k + ".rouge_l_mean": float(c["rouge_l"].mean()) if len(c) else np.nan})
        # Paired comparisons between arms on the images complete in both arms.
        # The three comparisons of one model form a family: their p-values are
        # Holm-adjusted together (hallucination McNemar and recall Wilcoxon apart).
        raw_mc, raw_wx = {}, {}
        for x, z in (("plain", "crispe"), ("crispe", "crispe_snomed"), ("plain", "crispe_snomed")):
            gx = t[(t["model"] == model) & (t["arm"] == x)].set_index("image")
            gz = t[(t["model"] == model) & (t["arm"] == z)].set_index("image")
            both = gx.index[gx["complete"].values & gz.loc[gx.index, "complete"].values]
            if not len(both):
                continue
            mc = stats.mcnemar(gx.loc[both, "hallucination"].astype(bool).values,
                               gz.loc[both, "hallucination"].astype(bool).values)
            k = "ablation.%s.%s_vs_%s" % (mt, x, z)
            res.update({k + ".n_pairs": len(both), k + ".hallucination_mcnemar_p": mc["p"],
                        k + ".hallucination_n01": mc["n01"], k + ".hallucination_n10": mc["n10"]})
            raw_mc[k] = mc["p"]
            rx, rz = gx.loc[both, "recall"].values, gz.loc[both, "recall"].values
            ok = ~np.isnan(rx) & ~np.isnan(rz)
            if ok.sum() and np.any(rx[ok] != rz[ok]):
                from scipy import stats as sps
                res[k + ".recall_wilcoxon_p"] = float(sps.wilcoxon(rx[ok], rz[ok]).pvalue)
                raw_wx[k] = res[k + ".recall_wilcoxon_p"]
        for k, p in stats.holm(raw_mc).items():
            res[k + ".hallucination_mcnemar_p_holm"] = p
        for k, p in stats.holm(raw_wx).items():
            res[k + ".recall_wilcoxon_p_holm"] = p
    S.put(**res)
    print("ablation: done")


def stage_timing(a, S):
    """T22: per-item processing time on the current hardware, measured in
    isolation (run this job alone on its machine).  Definitions follow the
    original stages: classification = image loading + preprocessing + forward
    pass per image (batched); Grad-CAM = one map; segmentation = loading at 512
    px + PSPNet + resizing the masks; LLM = one unbatched report.  GPU work is
    synchronized before each clock reading.  Raw times go to timing_per_item.csv."""
    import pandas as pd
    import torch
    cuda = str(a.device).startswith("cuda")
    sync = torch.cuda.synchronize if cuda else (lambda: None)
    full = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    df = full.sample(n=min(a.timing_n, len(full)), random_state=a.seed)
    idx = data.index_images(a.nih_dir)
    model, size = classify.load_model("densenet_nih", pretrained=not a.smoke_test)
    model.to(a.device)
    items = []
    # Warm-up (CUDA context, cuDNN autotuning, file cache) excluded from the timings
    classify.predict(model, _images(a, df.head(min(8, len(df))), size), a.device, a.batch_size)
    sync()
    t0 = time.time()
    p = classify.predict(model, _images(a, df, size), a.device, a.batch_size)
    sync()
    t_cls = (time.time() - t0) / len(df)
    items += [dict(stage="classification", seconds=t_cls)]
    seg = explain.load_segmenter(a.device) if not a.smoke_test else None
    out_idx = classify.output_index(model)
    t_cam, t_seg = [], []
    for name in df["Image Index"]:
        img = data.load_xrv_image(idx[name], size)
        j = out_idx[C.FINDINGS.index("Effusion")]       # any predicted class; cost is the same
        sync(); t0 = time.time()
        cam = explain.gradcam(model, img, j)
        sync(); t_cam.append(time.time() - t0)
        if seg is not None:
            sync(); t0 = time.time()
            explain.resize_mask(explain.segment(seg, data.load_xrv_image(idx[name], 512)), cam.shape)
            sync(); t_seg.append(time.time() - t0)
    items += [dict(stage="gradcam", seconds=s) for s in t_cam]
    items += [dict(stage="segmentation", seconds=s) for s in t_seg]
    cases = _report_cases(a, df.head(a.timing_reports), p, df.reset_index(drop=True))
    smap = report.load_snomed_map(os.path.join(HERE, "resources", "snomed_map.csv"))
    t_llm = []
    for c in cases:
        prompt = report.build_prompt(c, smap)
        t0 = time.time()
        report.generate(prompt, a.llm_backend, model=a.llm_model, max_tokens=a.llm_max_tokens)
        sync(); t_llm.append(time.time() - t0)
    items += [dict(stage="llm", seconds=s) for s in t_llm]
    pd.DataFrame(items).to_csv(os.path.join(a.out, "timing_per_item.csv"), index=False)
    mean = lambda v: float(np.mean(v)) if v else None
    sd = lambda v: float(np.std(v, ddof=1)) if len(v) > 1 else None
    res = {"timing.device": str(a.device),
           "timing.gpu": torch.cuda.get_device_name(0) if cuda else None,
           "timing.torch_threads": torch.get_num_threads(), "timing.n_images": len(df),
           "timing.n_reports": len(t_llm), "timing.llm_model": a.llm_model,
           "timing.llm_backend": a.llm_backend,
           "timing.classification_s": t_cls,
           "timing.gradcam_s": mean(t_cam), "timing.gradcam_sd": sd(t_cam),
           "timing.segmentation_s": mean(t_seg), "timing.segmentation_sd": sd(t_seg),
           "timing.llm_s": mean(t_llm), "timing.llm_sd": sd(t_llm)}
    parts = [res[k] for k in ("timing.classification_s", "timing.gradcam_s",
                              "timing.segmentation_s", "timing.llm_s")]
    res["timing.total_s"] = sum(parts) if all(v is not None for v in parts) else None
    S.put(**res)
    print("timing:", {k: v for k, v in res.items() if k.endswith("_s")})


def stage_report(a, S):
    import pandas as pd
    df = pd.read_csv(os.path.join(a.out, "sample_manifest.csv")).sample(
        n=min(a.report_n, 10 ** 9), random_state=a.seed)
    p_all = np.load(os.path.join(a.out, "predictions_densenet_nih.npz"))["p"]
    full = pd.read_csv(os.path.join(a.out, "sample_manifest.csv"))
    pos = full.reset_index().set_index("Image Index").loc[df["Image Index"], "index"].values
    smap = report.load_snomed_map(os.path.join(HERE, "resources", "snomed_map.csv"))
    rows, times, bleu, rouge = [], [], [], []
    regions = _RegionFinder(a)               # most affected region of each case (Sec. 3.1)
    for (_, r), i in zip(df.iterrows(), pos):
        found = [(f, float(p_all[i, j])) for j, f in enumerate(C.FINDINGS)
                 if not np.isnan(p_all[i, j]) and p_all[i, j] >= C.DECISION_THRESHOLD]
        case = dict(age=int(r["Patient Age"]), sex=r["Patient Gender"], view=r["View Position"],
                    findings=found, region=regions(r["Image Index"], found))
        prompt = report.build_prompt(case, smap)
        t0 = time.time()
        raw = report.generate(prompt, a.llm_backend, model=a.llm_model,
                              max_tokens=a.llm_max_tokens)
        times.append(time.time() - t0)
        text = report.strip_reasoning(raw)
        ref = report.rule_based_reference(case)
        if text:
            bleu.append(report.bleu4(text, ref))
            rouge.append(report.rouge_l(text, ref))
        rows.append(dict(image=r["Image Index"], prompt=prompt, raw=raw, report=text,
                         reference=ref, seconds=times[-1], complete=bool(text),
                         region=case["region"]))
        report.save_jsonl(rows, os.path.join(a.out, "reports.jsonl"))   # checkpoint
        print("report %d/%d  %.1f s  complete=%s" % (len(rows), len(df), times[-1], bool(text)),
              flush=True)
    S.put(**{"report.n": len(rows), "report.n_complete": len(bleu),
             "report.n_with_region": sum(r["region"] is not None for r in rows),
             "report.bleu4_mean": float(np.mean(bleu)) if bleu else None,
             "report.rouge_l_mean": float(np.mean(rouge)) if rouge else None,
             "time.llm": float(np.mean(times)), "report.backend": a.llm_backend,
             "report.model": a.llm_model or (C.LLM_API_MODEL if a.llm_backend == "api"
                                             else C.LLM_LOCAL_MODEL),
             "report.max_tokens": a.llm_max_tokens})
    print("report: %d reports, %d complete" % (len(rows), len(bleu)))


def stage_human(a, S):
    """Optional: analyses of human ratings, if the authors provide the files
    (templates in resources/templates)."""
    import pandas as pd
    d = a.ratings_dir
    if not d or not os.path.isdir(d):
        print("human: no ratings directory; items stay NOT COMPUTED")
        return
    f = os.path.join(d, "heatmap_relevance.csv")       # items x raters (0/1)
    if os.path.exists(f):
        r = pd.read_csv(f, index_col=0).values
        table = np.stack([(r == 0).sum(axis=1), (r == 1).sum(axis=1)], axis=1)
        S.put(**{"human.fleiss_kappa": stats.fleiss_kappa(table)})
    f = os.path.join(d, "confidence_scores.csv")       # items x raters (numeric)
    if os.path.exists(f):
        S.put(**{"human.icc_2_1": stats.icc_2_1(pd.read_csv(f, index_col=0).values)})
    f = os.path.join(d, "review_times.csv")            # columns: manual_s, ihras_s
    if os.path.exists(f):
        t = pd.read_csv(f)
        r = stats.paired_tests(t["manual_s"], t["ihras_s"])
        S.put(**{"human.review_time_reduction_pct": 100 * (1 - t["ihras_s"].mean() / t["manual_s"].mean()),
                 "human.review_time.p": r["p"], "human.review_time.wilcoxon_p": r["wilcoxon_p"]})


def stage_figures(a, S):
    from ihras import figures
    figures.make_all(S.d, os.path.join(a.out, "figures"))


def stage_compare(a, S):
    S.put(**{"time.classification": S.d.get("time.classification_total_s.densenet_nih", 0)
             / max(S.d.get("sample.n", 1), 1) if "time.classification_total_s.densenet_nih" in S.d else None})
    if all(S.d.get(k) is not None for k in ("time.classification", "time.gradcam",
                                             "time.segmentation", "time.llm")):
        S.put(**{"time.total": sum(S.d[k] for k in ("time.classification", "time.gradcam",
                                                     "time.segmentation", "time.llm"))})
    compare.main(S.path, os.path.join(a.out, "COMPARISON.md"))


# ------------------------------------------------------------- smoke data
def make_smoke_dataset(root, n=48, seed=0):
    """Synthetic NIH-like metadata and images: validates the pipeline only."""
    import pandas as pd
    from PIL import Image
    rng = np.random.default_rng(seed)
    os.makedirs(os.path.join(root, "images_001", "images"), exist_ok=True)
    rows, boxes = [], []
    for i in range(n):
        name = "%08d_000.png" % i
        Image.fromarray(rng.integers(0, 255, (256, 256), dtype=np.uint8)).save(
            os.path.join(root, "images_001", "images", name))
        labs = [f for f in C.FINDINGS if rng.random() < 0.15] or ["No Finding"]
        rows.append([name, "|".join(labs), 0, i // 2, int(rng.integers(5, 90)),
                     rng.choice(["M", "F"]), rng.choice(["PA", "AP"]), 256, 256, 0.14, 0.14])
        if i < 8:
            boxes.append([name, C.FINDINGS[i % 8], 300, 300, 200, 200, "", "", ""])
    pd.DataFrame(rows, columns=["Image Index", "Finding Labels", "Follow-up #", "Patient ID",
                                "Patient Age", "Patient Gender", "View Position",
                                "OriginalImage[Width", "Height]", "OriginalImagePixelSpacing[x",
                                "y]"]).to_csv(os.path.join(root, "Data_Entry_2017.csv"), index=False)
    pd.DataFrame(boxes).to_csv(os.path.join(root, "BBox_List_2017.csv"), index=False,
                               header=["Image Index", "Finding Label", "Bbox [x", "y", "w", "h]",
                                       "", "", ""])
    # Every third image is "official test" so the 'official' stage can be smoke-tested
    open(os.path.join(root, "test_list.txt"), "w").write(
        "".join("%08d_000.png\n" % i for i in range(0, n, 3)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nih-dir")
    ap.add_argument("--out", default=os.path.join(HERE, "outputs"))
    ap.add_argument("--stages", default="all")
    ap.add_argument("--seed", type=int, default=C.SEED)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--models", default=",".join(C.MODELS),
                    help="comma-separated models for the 'predict' stage")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--workers", type=int, default=6, help="parallel image loaders")
    ap.add_argument("--threads", type=int, default=0, help="torch CPU threads (0 = default)")
    ap.add_argument("--bootstrap", type=int, default=C.BOOTSTRAP_B)
    ap.add_argument("--limit", type=int, default=0, help="limit bounding boxes (explain)")
    ap.add_argument("--robust-n", type=int, default=2000)
    ap.add_argument("--report-n", type=int, default=100)
    ap.add_argument("--llm-backend", default="api", choices=["api", "local", "echo"])
    ap.add_argument("--llm-model", default=None,
                    help="e.g. deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B for --llm-backend local")
    ap.add_argument("--llm-max-tokens", type=int, default=1024)
    ap.add_argument("--llm-batch-size", type=int, default=8, help="ablation: prompts per batch")
    ap.add_argument("--llm-dtype", default="float32", choices=["float32", "bfloat16", "float16"],
                    help="ablation: LLM weights dtype (float32 = published setting)")
    ap.add_argument("--ablation-n", type=int, default=C.ABLATION_N)
    ap.add_argument("--ablation-models", default=",".join(C.ABLATION_MODELS))
    ap.add_argument("--timing-n", type=int, default=C.TIMING_N_IMAGES)
    ap.add_argument("--timing-reports", type=int, default=C.TIMING_N_REPORTS)
    ap.add_argument("--ratings-dir")
    ap.add_argument("--smoke-test", action="store_true")
    a = ap.parse_args(argv)

    if a.smoke_test:
        import tempfile
        a.nih_dir = tempfile.mkdtemp(prefix="ihras_smoke_")
        make_smoke_dataset(a.nih_dir)
        a.out = os.path.join(a.nih_dir, "outputs")
        a.bootstrap, a.robust_n, a.report_n, a.llm_backend = 20, 16, 4, "echo"
        a.ablation_n, a.timing_n, a.timing_reports = 6, 4, 2
    if not a.nih_dir:
        ap.error("--nih-dir is required (or use --smoke-test)")
    os.makedirs(a.out, exist_ok=True)
    seed_all(a.seed)
    if a.threads:
        import torch
        torch.set_num_threads(a.threads)
    if a.smoke_test:
        a.workers = 0
    S = Store(a.out)
    a.models = [m for m in a.models.split(",") if m]
    todo = STAGES if a.stages == "all" else a.stages.split(",")
    unknown = set(todo) - set(ORDER)
    if unknown:
        ap.error("unknown stage(s): %s" % ", ".join(sorted(unknown)))
    for st in ORDER:
        if st in todo:
            print("== stage", st)
            globals()["stage_" + st](a, S)
    print("results in", a.out)
    return a.out


if __name__ == "__main__":
    main()
