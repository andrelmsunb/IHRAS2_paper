"""Multi-label classification with TorchXRayVision models (Ref: Sec. 3.2, 4.1, 4.2).

The article (and its precursor, 2025 Sec. 3.2) uses the three models "with
their default configurations", i.e. pretrained weights without training.
Predictions are cached to outputs/predictions_<model>.npz.
"""

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from .config import FINDINGS, ALL_MODELS, CV_FOLDS, SEED, DECISION_THRESHOLD


def load_model(key, pretrained=True):
    """Pretrained TorchXRayVision models output operating-point-normalized
    probabilities (default configuration).  ``pretrained=False`` builds a
    randomly initialized DenseNet with sigmoid outputs, for the smoke test only."""
    import torchxrayvision as xrv
    size = 512 if key.startswith("resnet") else 224
    if not pretrained:
        model = xrv.models.DenseNet(num_classes=len(xrv.datasets.default_pathologies),
                                    apply_sigmoid=True)
        model.pathologies = list(xrv.datasets.default_pathologies)
        return model.eval(), 224
    if key.startswith("resnet"):
        model = xrv.models.ResNet(weights=ALL_MODELS[key])
    else:
        model = xrv.models.DenseNet(weights=ALL_MODELS[key])
    return model.eval(), size


def input_size(key):
    """Input resolution of model ``key`` (models sharing it can share one image pass)."""
    return 512 if key.startswith("resnet") else 224


def output_index(model):
    """Column of each NIH finding in the model output (NaN when absent)."""
    names = [p.replace(" ", "_") for p in model.pathologies]
    return [names.index(f) if f in names else None for f in FINDINGS]


@torch.no_grad()
def predict(model, images, device="cpu", batch_size=32):
    """``images``: iterable of (1, H, W) float arrays.  Returns (n, 14) probs."""
    return predict_multi({"m": model}, images, device, batch_size)["m"]


@torch.no_grad()
def predict_multi(models, images, device="cpu", batch_size=32):
    """Predictions of several models that share the input size, with each image
    loaded and preprocessed only once (image decoding, not the network, is the
    bottleneck on a GPU).  ``models``: {key: model}.  Returns {key: (n, 14)}.
    Every model receives exactly the batches that predict() would give it, so
    the outputs are the same as running the models one at a time."""
    idx = {k: output_index(m) for k, m in models.items()}
    for m in models.values():
        m.to(device)
    out = {k: [] for k in models}
    batch = []

    def flush():
        x = torch.from_numpy(np.stack(batch)).to(device)
        for k, m in models.items():
            p = m(x).cpu().numpy()
            # NIH findings that a model does not predict become NaN columns
            cols = [p[:, i] if i is not None else np.full(len(p), np.nan) for i in idx[k]]
            out[k].append(np.stack(cols, axis=1))
        batch.clear()

    for img in images:
        batch.append(img)
        if len(batch) == batch_size:
            flush()
    if batch:
        flush()
    return {k: np.concatenate(v) for k, v in out.items()}


# --------------------------------------------------------------- metrics
def confusion(y, p, thr):
    yhat = (p >= thr).astype(int)
    tp = ((yhat == 1) & (y == 1)).sum(axis=0)
    fp = ((yhat == 1) & (y == 0)).sum(axis=0)
    fn = ((yhat == 0) & (y == 1)).sum(axis=0)
    tn = ((yhat == 0) & (y == 0)).sum(axis=0)
    return tp, fp, fn, tn


def metrics(y, p, thr=DECISION_THRESHOLD, average="micro"):
    """Precision, recall, F1, specificity (2025 Eqs. (2)-(5)).  ``micro``
    pools TP/FP/FN/TN over all labels; ``macro`` averages per-label values."""
    tp, fp, fn, tn = confusion(y, p, thr)
    if average == "micro":
        tp, fp, fn, tn = tp.sum(), fp.sum(), fn.sum(), tn.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 * tp / (2 * tp + fp + fn)
        spec = tn / (tn + fp)
    if average == "macro":
        prec, rec, f1, spec = (np.nanmean(v) for v in (prec, rec, f1, spec))
    return dict(precision=float(prec), recall=float(rec), f1=float(f1), specificity=float(spec))


def binary_abnormal(y, p, thr=DECISION_THRESHOLD):
    """Normal vs. abnormal screening (2025 Sec. 4.1.2): abnormal if any label."""
    yb = (y.sum(axis=1) > 0).astype(int)[:, None]
    pb = np.nanmax(p, axis=1)[:, None]
    return metrics(yb, pb, thr, "micro")


def best_threshold(y, p, grid=np.round(np.arange(0.05, 0.96, 0.05), 2)):
    f1 = [metrics(y, p, t)["f1"] for t in grid]
    return float(grid[int(np.nanargmax(f1))]), dict(zip(map(float, grid), f1))


def per_class_auroc(y, p):
    out = {}
    for j, f in enumerate(FINDINGS):
        ok = ~np.isnan(p[:, j])
        if ok.sum() and 0 < y[ok, j].sum() < ok.sum():
            out[f] = float(roc_auc_score(y[ok, j], p[ok, j]))
    return out


def per_image_f1(y, p, thr=DECISION_THRESHOLD):
    """Sample-wise F1 (images with no positive and no prediction score 1)."""
    yhat = (np.nan_to_num(p) >= thr).astype(int)
    tp = (yhat & y).sum(axis=1)
    denom = yhat.sum(axis=1) + y.sum(axis=1)
    return np.where(denom == 0, 1.0, 2 * tp / np.maximum(denom, 1))


def cv_folds(y, groups, k=CV_FOLDS, seed=SEED):
    """Stratified (by number of labels) and patient-grouped folds."""
    strat = np.minimum(y.sum(axis=1), 3)
    skf = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
    return list(skf.split(np.zeros(len(y)), strat, groups))


def cross_validated_metrics(y, p, groups, k=CV_FOLDS, seed=SEED):
    """Pretrained models are not retrained: in each fold the decision threshold
    is selected on the k-1 training folds and applied to the held-out fold."""
    rows = []
    for tr, te in cv_folds(y, groups, k, seed):
        thr, _ = best_threshold(y[tr], p[tr])
        m = metrics(y[te], p[te], thr)
        m["threshold"] = thr
        rows.append(m)
    return rows


# ------------------------------------------------- evaluation on a finding subset
def predicted_columns(p):
    """Indices of the findings a model predicts (columns that are not all NaN)."""
    return np.flatnonzero(~np.isnan(p).all(axis=0))


def mask_columns(p, cols):
    """Copy of ``p`` with every column outside ``cols`` set to NaN, so that two
    models can be compared on exactly the same findings."""
    q = np.full_like(p, np.nan)
    q[:, cols] = p[:, cols]
    return q


def mean_auroc(y, p):
    """Mean AUROC over the findings that ``p`` predicts and ``y`` contains."""
    auc = per_class_auroc(y, p)
    return float(np.mean(list(auc.values()))) if auc else float("nan")


def subset_metrics(y, p, cols, thr=DECISION_THRESHOLD):
    """Micro-averaged metrics restricted to the finding columns ``cols``."""
    return metrics(y[:, cols], p[:, cols], thr, "micro")
