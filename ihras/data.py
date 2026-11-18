"""NIH ChestX-ray14 metadata, stratified sampling, and image loading.

Ref: Sec. 3.2 and Eq. (6); 2025 Sec. 3.1.  Download the official files from the
NIH Clinical Center (https://nihcc.app.box.com/v/ChestXray-NIHCC): the images
(images_001 ... images_012), Data_Entry_2017.csv (or Data_Entry_2017_v2020.csv),
BBox_List_2017.csv, train_val_list.txt, and test_list.txt.
"""

import os
from math import ceil

import numpy as np
import pandas as pd

from .config import (FINDINGS, AGE_BIN_YEARS, STRATA, Z, P_EST, MARGIN,
                     PER_STRATUM_CAP, SEED)


def load_metadata(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={c: c.strip() for c in df.columns})
    df["Patient Age"] = pd.to_numeric(df["Patient Age"].astype(str).str.extract(r"(\d+)")[0])
    labels = df["Finding Labels"].str.split("|")
    for f in FINDINGS:
        df[f] = labels.map(lambda ls, f=f: int(f in ls))
    df["age_bin"] = (df["Patient Age"] // AGE_BIN_YEARS).astype(int)
    return df


def labels_matrix(df):
    return df[list(FINDINGS)].values.astype(np.int8)


def per_stratum_size(n_pop, z=Z, p=P_EST, e=MARGIN):
    """Eq. (6): finite-population sample size."""
    return n_pop * z ** 2 * p * (1 - p) / (e ** 2 * (n_pop - 1) + z ** 2 * p * (1 - p))


def stratified_sample(df, cap=PER_STRATUM_CAP, strata=STRATA, seed=SEED):
    """Draw min(N_s, cap) images per stratum (2025 Sec. 3.1: all images of
    strata smaller than the cap are included)."""
    rng = np.random.default_rng(seed)
    parts = []
    for _, g in df.groupby(list(strata), sort=True):
        if len(g) <= cap:
            parts.append(g)
        else:
            parts.append(g.iloc[rng.choice(len(g), size=cap, replace=False)])
    out = pd.concat(parts).sort_values("Image Index").reset_index(drop=True)
    sizes = df.groupby(list(strata)).size()
    info = dict(n=len(out), n_strata=len(sizes), largest_stratum=int(sizes.max()),
                formula_n_largest=per_stratum_size(int(sizes.max())),
                formula_n_largest_ceil=ceil(per_stratum_size(int(sizes.max()))))
    return out, info


def official_split(df, test_list_path):
    """Patient-wise official NIH split (test_list.txt)."""
    with open(test_list_path) as f:
        test = set(l.strip() for l in f if l.strip())
    return df[~df["Image Index"].isin(test)], df[df["Image Index"].isin(test)]


def find_image(image_root, name):
    """NIH images are distributed in images_XXX/images/ subfolders."""
    direct = os.path.join(image_root, name)
    if os.path.exists(direct):
        return direct
    for sub in sorted(os.listdir(image_root)):
        p = os.path.join(image_root, sub, "images", name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def index_images(image_root):
    """Map file name -> path once (faster than find_image per file)."""
    idx = {}
    for root, _, files in os.walk(image_root):
        for f in files:
            if f.endswith(".png"):
                idx[f] = os.path.join(root, f)
    return idx


class XrvImageDataset:
    """Map-style dataset of preprocessed images, for a parallel DataLoader."""

    def __init__(self, paths, size):
        self.paths, self.size = list(paths), size

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        return load_xrv_image(self.paths[i], self.size)


def load_xrv_image(path, size):
    """Read a PNG and apply TorchXRayVision preprocessing: [-1024, 1024]
    normalization, single channel, center crop, resize."""
    import skimage.io
    import torchvision
    import torchxrayvision as xrv

    img = skimage.io.imread(path)
    if img.ndim == 3:
        img = img[..., :3].mean(axis=2)
    img = xrv.datasets.normalize(img, 255)[None, ...]
    t = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),
                                        xrv.datasets.XRayResizer(size)])
    return t(img).astype(np.float32)
