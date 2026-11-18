"""Quantitative evaluation of explanation maps (Ref: Table 2, Figs. 4, 7, 8).

The article does not define "localization accuracy", "false-positive rate",
or "anatomical coverage".  The only public localization reference for NIH
ChestX-ray14 is BBox_List_2017.csv (984 boxes, 8 findings).  Definitions
adopted (ASSUMPTIONS.md, A8):
  localization accuracy  pointing game: the map maximum falls inside the box;
  false-positive rate    share of the binarized map lying outside the box;
  anatomical coverage    share of the binarized map lying inside the union of
                         the 14 anatomical masks.
"""

import numpy as np
import pandas as pd

from .config import CAM_BINARIZATION


def load_bboxes(csv_path):
    b = pd.read_csv(csv_path)
    b = b.iloc[:, :6]
    b.columns = ["Image Index", "Finding Label", "x", "y", "w", "h"]
    b["Finding Label"] = b["Finding Label"].replace({"Infiltrate": "Infiltration"})
    return b


def box_mask(shape, box, original_size=1024):
    """Box in original 1024 px coordinates -> mask at ``shape``."""
    h, w = shape
    sy, sx = h / original_size, w / original_size
    m = np.zeros(shape, bool)
    x0, y0 = int(box["x"] * sx), int(box["y"] * sy)
    x1, y1 = int(np.ceil((box["x"] + box["w"]) * sx)), int(np.ceil((box["y"] + box["h"]) * sy))
    m[max(y0, 0):min(y1, h), max(x0, 0):min(x1, w)] = True
    return m


def evaluate_map(cam, gt_mask, anatomy_union=None, tau_bin=CAM_BINARIZATION):
    hit = bool(gt_mask.flat[int(np.argmax(cam))]) if cam.max() > 0 else False
    binm = cam > tau_bin
    nb = binm.sum()
    fpr = float((binm & ~gt_mask).sum() / nb) if nb else 0.0
    cov = float((binm & anatomy_union).sum() / nb) if (nb and anatomy_union is not None) else np.nan
    return dict(hit=hit, fpr=fpr, coverage=cov)


def summarize(rows):
    df = pd.DataFrame(rows)
    return dict(localization_accuracy=float(df["hit"].mean()),
                false_positive_rate=float(df["fpr"].mean()),
                anatomical_coverage=float(df["coverage"].mean()), n=len(df))
