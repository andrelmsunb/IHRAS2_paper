"""Unit tests and an end-to-end smoke test on synthetic data.

    python -m pytest tests -q
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# analysis/ holds standalone scripts (e.g. merge_jobs.py) that the tests import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))

from ihras import data, stats, classify, explain, report   # noqa: E402


def test_eq6_sample_size():
    n = data.per_stratum_size(9677)                            # 369.53
    assert round(n) == 370 and np.ceil(n) == 370               # article: 370


def test_metrics_micro():
    y = np.array([[1, 0], [0, 1], [1, 1]])
    p = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3]])
    m = classify.metrics(y, p, 0.5)
    # TP=3, FP=0, FN=1, TN=2
    assert m["precision"] == 1.0 and abs(m["recall"] - 0.75) < 1e-12
    assert abs(m["f1"] - 6 / 7) < 1e-12 and m["specificity"] == 1.0


def test_fusion_keeps_only_selected_regions():
    cam = np.zeros((10, 10)); cam[2:5, 2:5] = 1.0
    masks = np.zeros((2, 10, 10), bool); masks[0, 1:6, 1:6] = True; masks[1, 7:, 7:] = True
    fused, sel, ious = explain.fuse(cam, masks, tau_overlap=0.30)
    assert list(sel) == [0] and fused[2:5, 2:5].sum() == 9 and fused[7:, 7:].sum() == 0


def test_fleiss_kappa_perfect_agreement():
    table = np.array([[5, 0], [0, 5], [5, 0]])
    assert abs(stats.fleiss_kappa(table) - 1.0) < 1e-12


def test_bleu_rouge_identity():
    s = "Findings consistent with effusion in the right lung."
    assert report.rouge_l(s, s) == 1.0 and report.bleu4(s, s) > 0.99


def test_smoke_pipeline():
    import run_all
    out = run_all.main(["--smoke-test"])
    res = json.load(open(os.path.join(out, "results.json")))
    assert res["sample.n"] == 48
    assert "cls.densenet_nih.f1" in res and "xai.gradcam.localization_accuracy" in res
    assert os.path.exists(os.path.join(out, "COMPARISON.md"))
    # Per-box explainability table (input of the bootstrap CIs, T26)
    import pandas as pd
    box = pd.read_csv(os.path.join(out, "xai_per_box.csv"))
    assert {"image", "patient", "finding", "method", "hit", "fpr", "coverage"} <= set(box.columns)
    assert {"gradcam", "gradcampp", "fused_0.30", "fusedpp_0.30"} <= set(box["method"])
    assert "xai.fusedpp.localization_accuracy" in res


def test_predict_stage_runs_only_selected_models():
    import run_all
    out = run_all.main(["--smoke-test", "--stages", "sampling,predict", "--models", "densenet_nih"])
    assert os.path.exists(os.path.join(out, "predictions_densenet_nih.npz"))
    assert not os.path.exists(os.path.join(out, "predictions_densenet_multi.npz"))


def test_prediction_cache_must_match_manifest(tmp_path):
    import pandas as pd
    import pytest
    import run_all
    out = run_all.main(["--smoke-test", "--stages", "sampling,predict", "--models", "densenet_nih"])
    df = pd.read_csv(os.path.join(out, "sample_manifest.csv"))
    a = type("Args", (), {"out": out})()
    # A cache listing other images (e.g. from another sample) must be rejected
    np.savez_compressed(os.path.join(out, "predictions_densenet_nih.npz"),
                        p=np.zeros((len(df), 14)), names=df["Image Index"].values[::-1])
    with pytest.raises(ValueError):
        run_all.predict_cached(a, None, "densenet_nih", df)


def _job(root, name, results, files=None):
    """Create a fake job folder with a results.json and optional files."""
    d = root / name
    d.mkdir()
    (d / "results.json").write_text(json.dumps(results))
    for fn, content in (files or {}).items():
        (d / fn).write_text(content)
    return str(d)


def test_merge_jobs_combines_keys_and_artifacts(tmp_path):
    import merge_jobs
    a = _job(tmp_path, "a", {"x": 1, "shared": 2.0}, {"sample_manifest.csv": "m", "t.csv": "1"})
    b = _job(tmp_path, "b", {"y": 3, "shared": 2.0, "nan": float("nan")}, {"sample_manifest.csv": "m"})
    prov = merge_jobs.merge(str(tmp_path / "dst"), [a, b])
    res = json.load(open(tmp_path / "dst" / "results.json"))
    assert res["x"] == 1 and res["y"] == 3 and res["shared"] == 2.0
    assert prov["keys"]["x"] == a and prov["keys"]["y"] == b
    assert (tmp_path / "dst" / "t.csv").read_text() == "1"


def test_merge_jobs_rejects_conflicts_and_different_samples(tmp_path):
    import pytest
    import merge_jobs
    a = _job(tmp_path, "a", {"k": 1}, {"sample_manifest.csv": "m1"})
    b = _job(tmp_path, "b", {"k": 2}, {"sample_manifest.csv": "m1"})
    with pytest.raises(SystemExit, match="conflicting"):
        merge_jobs.merge(str(tmp_path / "dst"), [a, b])
    assert not (tmp_path / "dst").exists()            # nothing written on failure
    c = _job(tmp_path, "c", {"z": 1}, {"sample_manifest.csv": "m2"})
    with pytest.raises(SystemExit, match="different sample manifests"):
        merge_jobs.merge(str(tmp_path / "dst"), [a, c])


# ------------------------------------------------------------- new analyses
def test_fidelity_negation_rules():
    from ihras import fidelity
    aff, neg = fidelity.mentions("No pneumothorax or pleural effusion. Mild cardiomegaly.")
    assert aff == {"Cardiomegaly"} and neg == {"Pneumothorax", "Effusion"}
    aff, _ = fidelity.mentions("There is no effusion, but atelectasis is present.")
    assert aff == {"Atelectasis"}
    aff, neg = fidelity.mentions("Pneumothorax is not seen. Pneumonia cannot be excluded.")
    assert neg == {"Pneumothorax"} and aff == {"Pneumonia"}
    s = fidelity.score_report("Findings: atelectasis and a small nodule. No edema.",
                              ["Atelectasis", "Edema"])
    assert s["recall"] == 0.5 and s["hallucinated"] == "Nodule" and s["contradicted"] == "Edema"
    aff, _ = fidelity.mentions("Reduced left ventricular mass. A 2 cm mass in the right lung.")
    assert aff == {"Mass"} and not fidelity.mentions("Reduced left ventricular mass.")[0]


def test_findings_from_prompt_roundtrip():
    from ihras import fidelity
    case = dict(age=50, sex="F", view="PA", region=None,
                findings=[("Pleural_Thickening", 0.61), ("Mass", 0.57)])
    for arm in ("plain", "crispe", "crispe_snomed"):
        prompt = report.build_arm_prompt(case, {}, arm)
        assert fidelity.findings_from_prompt(prompt) == ["Pleural_Thickening", "Mass"]
    assert "SNOMED" not in report.build_arm_prompt(case, {}, "crispe")
    assert "SNOMED" in report.build_arm_prompt(case, {}, "crispe_snomed")
    assert report.build_arm_prompt(case, {}, "crispe_snomed") == report.build_prompt(case, {})


def test_predict_multi_equals_predict():
    import torch
    torch.manual_seed(0)
    m1, _ = classify.load_model("densenet_nih", pretrained=False)
    m2, _ = classify.load_model("densenet_pc", pretrained=False)
    imgs = [np.random.default_rng(i).normal(size=(1, 224, 224)).astype(np.float32) for i in range(5)]
    multi = classify.predict_multi({"a": m1, "b": m2}, imgs, batch_size=2)
    assert np.allclose(multi["a"], classify.predict(m1, imgs, batch_size=2), equal_nan=True)
    assert np.allclose(multi["b"], classify.predict(m2, imgs, batch_size=2), equal_nan=True)


def test_new_stages_smoke():
    import run_all
    out = run_all.main(["--smoke-test", "--stages",
                        "sampling,predict,explain,external,official,xai_stats,ablation,timing,figures",
                        "--models", "densenet_nih,densenet_pc,densenet_chex"])
    res = json.load(open(os.path.join(out, "results.json")))
    assert "ext.densenet_pc.mean_auroc" in res and "ext.densenet_pc.delta_mean_auroc_ci" in res
    assert res["split.n_images"] == 16 and "split.densenet_nih.f1" in res
    assert "xai.ci.fused.localization_accuracy_ci" in res
    assert "xai.test.gradcam_vs_fused.hit_mcnemar_p_holm" in res
    tag = run_all._model_tag(run_all.C.ABLATION_MODELS[0])
    assert "ablation.%s.crispe_snomed.hallucination_rate" % tag in res
    assert "ablation.%s.plain_vs_crispe_snomed.hallucination_mcnemar_p_holm" % tag in res
    assert "timing.classification_s" in res and res["timing.n_reports"] == 2
    for fn in ("ablation_per_report.csv", "timing_per_item.csv", "official_test_manifest.csv",
               "predictions_densenet_pc__official_test.npz", "figures/fig8b_explainability_ci.png",
               "figures/fig13_external_validation.png", "figures/fig14_prompt_ablation.png"):
        assert os.path.exists(os.path.join(out, fn)), fn


def test_holm():
    """Holm adjustment: step-down, monotone, capped at 1."""
    import pytest
    from ihras import stats
    adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06})
    assert stats.holm({"x": 0.6, "y": 0.9}) == {"x": 1.0, "y": 1.0}


def test_snomed_map_and_expression():
    """Every finding and segmenter structure has a verified code; the prompt
    carries compositional expressions with the concept names."""
    import os
    from ihras import config as C, report
    smap = report.load_snomed_map(os.path.join(os.path.dirname(__file__), "..", "resources",
                                               "snomed_map.csv"))
    for term in C.FINDINGS + C.ANATOMY:
        assert smap[term]["sctid"].isdigit() and smap[term]["display"], term
    e = report.snomed_expression("Pneumonia", "Right Lung", smap)
    assert e == ("233604007 |Pneumonia (disorder)| : 363698007 |Finding site| = "
                 "3341006 |Right lung structure (body structure)|")
    assert report.snomed_expression("Pneumonia", None, smap) == "233604007 |Pneumonia (disorder)|"
    case = dict(age=50, sex="F", view="PA", region="Right Lung", findings=[("Pneumonia", 0.7)])
    assert "Finding site" in report.build_prompt(case, smap)
    assert "Most affected region: Right Lung" in report.build_plain_prompt(case)
