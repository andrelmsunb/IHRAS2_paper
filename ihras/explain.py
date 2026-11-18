"""Grad-CAM, Grad-CAM++, anatomical segmentation, and deterministic fusion.

Ref: Sec. 3.1, Eqs. (1)-(4).  Segmentation: TorchXRayVision PSPNet trained on
ChestX-Det, whose 14 targets are exactly the anatomical structures listed in
the precursor (2025 Sec. 3.3); see ASSUMPTIONS.md, A3.
"""

import numpy as np
import torch
import torch.nn.functional as F

from .config import CAM_BINARIZATION, TAU_OVERLAP


def _device(module):
    """Device that holds the parameters of ``module`` (CPU or a GPU)."""
    return next(module.parameters()).device


def _target_layer(model):
    if hasattr(model, "features"):          # DenseNet: last dense block output
        return model.features
    return model.model.layer4               # TorchXRayVision ResNet wraps torchvision


def _cam(model, x, class_idx, plus=False):
    acts, grads = {}, {}
    layer = _target_layer(model)

    def hook(module, inputs, output):
        # Return a clone so that later in-place ops (DenseNet's ReLU) do not
        # touch the hooked tensor; capture its gradient with a tensor hook.
        acts["a"] = output.detach()
        out = output.clone()
        out.register_hook(lambda g: grads.__setitem__("g", g.detach()))
        return out

    h = layer.register_forward_hook(hook)
    try:
        model.zero_grad()
        x = x.clone().requires_grad_(True)
        score = model(x)[0, class_idx]
        score.backward()
    finally:
        h.remove()
    a, g = acts["a"][0], grads["g"][0]                 # (K, h, w)
    if not plus:
        alpha = g.mean(dim=(1, 2))                     # Eq. (1)
    else:                                              # Grad-CAM++ (Chattopadhay 2018)
        g2, g3 = g ** 2, g ** 3
        denom = 2 * g2 + (a * g3).sum(dim=(1, 2), keepdim=True)
        w = g2 / torch.where(denom != 0, denom, torch.ones_like(denom))
        alpha = (w * F.relu(g)).sum(dim=(1, 2))
    cam = F.relu((alpha[:, None, None] * a).sum(0))    # Eq. (2)
    cam = F.interpolate(cam[None, None], size=x.shape[-2:], mode="bilinear",
                        align_corners=False)[0, 0]
    cam = cam - cam.min()
    return (cam / cam.max()).detach().cpu().numpy() if cam.max() > 0 else cam.detach().cpu().numpy()


def gradcam(model, image, class_idx):
    # The input follows the model to its device, so the same call works on CPU
    # and GPU; _cam always returns a CPU numpy array.
    return _cam(model, torch.from_numpy(image)[None].to(_device(model)), class_idx, plus=False)


def gradcampp(model, image, class_idx):
    return _cam(model, torch.from_numpy(image)[None].to(_device(model)), class_idx, plus=True)


def load_segmenter(device="cpu"):
    """TorchXRayVision PSPNet (ChestX-Det, 14 anatomical structures) on ``device``."""
    import torchxrayvision as xrv
    return xrv.baseline_models.chestx_det.PSPNet().eval().to(device)


@torch.no_grad()
def segment(segmenter, image_512, threshold=0.5):
    """Binary masks (14, 512, 512) of the anatomical structures."""
    out = segmenter(torch.from_numpy(image_512)[None].to(_device(segmenter)))
    return (torch.sigmoid(out[0]) > threshold).cpu().numpy()


def resize_mask(masks, shape):
    t = torch.from_numpy(masks.astype(np.float32))[None]
    return (F.interpolate(t, size=shape, mode="nearest")[0].numpy() > 0.5)


def iou(a, b):
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter / union) if union else 0.0


def fuse(cam, masks, tau_overlap=TAU_OVERLAP, tau_bin=CAM_BINARIZATION):
    """Eqs. (3)-(4): keep the Grad-CAM map only inside the union of the regions
    whose IoU with the binarized map is >= tau_overlap.  Returns the fused map,
    the selected region indices, and the IoU of every region."""
    m_bin = cam > tau_bin
    ious = np.array([iou(m_bin, s) for s in masks])
    selected = np.flatnonzero(ious >= tau_overlap)
    union = masks[selected].any(axis=0) if len(selected) else np.zeros_like(m_bin)
    return cam * union, selected, ious


def most_affected_region(cam, masks):
    """Region holding the largest share of saliency mass (used in the prompt)."""
    mass = [(cam * s).sum() for s in masks]
    return int(np.argmax(mass)) if np.max(mass) > 0 else None
