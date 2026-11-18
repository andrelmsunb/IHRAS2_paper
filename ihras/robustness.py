"""Input perturbations (Ref: Sec. 3.3, Sec. 4.4, Fig. 11).

Images are in TorchXRayVision units ([-1024, 1024]).  Degradation is the
relative drop of micro-F1 with respect to the clean images, in percent
(ASSUMPTIONS.md, A9).
"""

import numpy as np


def add_noise_snr(img, snr_db, rng):
    """Additive Gaussian noise with SNR = 10 log10(P_signal / P_noise)."""
    x = (img + 1024.0) / 2048.0                    # to [0, 1]
    p_signal = np.mean(x ** 2)
    sigma = np.sqrt(p_signal / 10 ** (snr_db / 10))
    x = x + rng.normal(0.0, sigma, x.shape)
    return (np.clip(x, 0, 1) * 2048.0 - 1024.0).astype(np.float32)


def photometric(img, delta):
    """Contrast and brightness both scaled by (1 + delta) around mid-gray."""
    x = (img + 1024.0) / 2048.0
    x = (x - 0.5) * (1 + delta) + 0.5 + 0.5 * delta * 0.25
    return (np.clip(x, 0, 1) * 2048.0 - 1024.0).astype(np.float32)


def degradation_pct(f1_clean, f1_perturbed):
    return float(100.0 * (f1_clean - f1_perturbed) / f1_clean)
