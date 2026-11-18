"""Values REPORTED in the article, used ONLY for automatic comparison.

Nothing in this file is ever written as a result.  ``ihras.compare`` reads the
COMPUTED results from outputs/results.json and compares them with these
references within a declared tolerance.

ARTICLE_2026: values of the corrected manuscript (rounded as printed), from the
final run (run03).
ARTICLE_2026_SUPERSEDED: values of an earlier draft replaced by run03.
ORIGINAL_SUBMISSION: values of the first version, kept for transparency; they
were not reproduced by this package (see README, "Reproduction outcome").
PRECURSOR_2025: values published by the same group on the same sample and
models (Rodrigues et al., Bioengineering 2025), shown for context.
"""

# Values of the version first submitted; replaced by computed values.
ORIGINAL_SUBMISSION = {
    "sample.n": 50_133, "sample.largest_stratum": 9_677,
    "repr.ks_age.D": 0.023, "repr.ks_age.p": 0.847,
    "repr.chi2_sex.stat": 1.34, "repr.chi2_sex.p": 0.247,
    "repr.chi2_pathology.stat": 23.7, "repr.chi2_pathology.p": 0.052,
    "fig2.Infiltration": 19_894, "fig2.Hernia": 227,
    "cls.densenet_nih.precision": 0.915, "cls.densenet_nih.recall": 0.908,
    "cls.densenet_nih.f1": 0.911, "cls.densenet_nih.specificity": 0.934,
    "cls.densenet_multi.precision": 0.892, "cls.densenet_multi.recall": 0.885,
    "cls.densenet_multi.f1": 0.888, "cls.densenet_multi.specificity": 0.923,
    "cls.resnet50_multi.precision": 0.878, "cls.resnet50_multi.recall": 0.871,
    "cls.resnet50_multi.f1": 0.874, "cls.resnet50_multi.specificity": 0.919,
    "cls.densenet_nih.mean_auroc": 0.911,
    "auroc.Pneumothorax": 0.967, "auroc.Cardiomegaly": 0.943, "auroc.Effusion": 0.924,
    "auroc.Pneumonia": 0.891, "auroc.Atelectasis": 0.887, "auroc.Consolidation": 0.876,
    "auroc.Fibrosis": 0.834, "auroc.Hernia": 0.823,
    "cv.f1_mean": 0.911, "cv.f1_cv_percent": 0.24,
    "test.ttest_vs_multi.t": 3.247, "test.ttest_vs_multi.d": 0.847,
    "test.ttest_vs_resnet.t": 4.891, "test.ttest_vs_resnet.d": 1.234,
    "xai.fused.localization_accuracy": 0.891, "xai.gradcam.localization_accuracy": 0.847,
    "xai.gradcampp.localization_accuracy": 0.863, "xai.fused.false_positive_rate": 0.047,
    "xai.fused.anatomical_coverage": 0.956,
    "robust.noise_20db.degradation_pct": 3.2, "robust.noise_10db.degradation_pct": 12.8,
    "robust.photometric_40.degradation_pct": 7.3,
    "fair.f1.age_18_40": 0.918, "fair.f1.age_41_65": 0.911, "fair.f1.age_66_plus": 0.907,
    "fair.f1.sex_M": 0.913, "fair.f1.sex_F": 0.909,
    "time.classification": 0.23, "time.gradcam": 0.15, "time.segmentation": 0.31,
    "time.llm": 1.42, "time.total": 2.11,
}

ARTICLE_2026 = {
    # sampling and representativeness (Sec. 3.2; p-values printed as bounds, compared at 0)
    "sample.n": 50_208,
    "sample.largest_stratum": 9_677,
    "sample.per_stratum_formula_n": 370,
    "repr.ks_age.D": 0.035, "repr.ks_age.p": 0.0,
    "repr.chi2_sex.stat": 41.3, "repr.chi2_sex.p": 0.0,
    "repr.chi2_pathology.stat": 914.2, "repr.chi2_pathology.p": 0.0,
    "fig2.Infiltration": 14_717, "fig2.Hernia": 227,
    # classification (Sec. 4.1, Fig. 3)
    "cls.densenet_nih.precision": 0.282, "cls.densenet_nih.recall": 0.426,
    "cls.densenet_nih.f1": 0.340, "cls.densenet_nih.specificity": 0.873,
    "cls.densenet_multi.precision": 0.286, "cls.densenet_multi.recall": 0.403,
    "cls.densenet_multi.f1": 0.334, "cls.densenet_multi.specificity": 0.882,
    "cls.resnet50_multi.precision": 0.680, "cls.resnet50_multi.recall": 0.098,
    "cls.resnet50_multi.f1": 0.172, "cls.resnet50_multi.specificity": 0.995,
    "cls.resnet50_multi.best_threshold": 0.15,
    "cls.densenet_nih.mean_auroc": 0.668, "cls.densenet_multi.mean_auroc": 0.703,
    "cls.resnet50_multi.mean_auroc": 0.797,
    "binary.densenet_nih.precision": 0.926, "binary.densenet_nih.recall": 0.743,
    "binary.densenet_nih.f1": 0.824,
    "sample.no_finding_share": 0.114, "cls.densenet_nih.mean_auroc_vs_no_finding": 0.765,
    # per-pathology AUROC (Sec. 4.2, Fig. 5)
    "auroc.Cardiomegaly": 0.833, "auroc.Hernia": 0.761, "auroc.Edema": 0.759,
    "auroc.Effusion": 0.756, "auroc.Emphysema": 0.570, "auroc.Nodule": 0.573,
    "auroc.Pneumothorax": 0.602, "auroc.Infiltration": 0.603,
    # cross-validation (Fig. 6)
    "cv.f1_mean": 0.340, "cv.f1_cv_percent": 1.2,
    # hypothesis tests (Table 4)
    "test.ttest_vs_multi.t": -2.75, "test.ttest_vs_multi.p": 0.006, "test.ttest_vs_multi.d": -0.012,
    "test.wilcoxon_vs_multi.p": 0.22,
    "test.mcnemar_vs_multi.n01": 1_775, "test.mcnemar_vs_multi.n10": 2_357,
    "test.ttest_vs_resnet.t": 50.2, "test.ttest_vs_resnet.d": 0.224,
    "test.mcnemar_vs_resnet.n01": 1_748, "test.mcnemar_vs_resnet.n10": 4_511,
    "test.anova_precision.F": 6_087, "test.anova_recall.F": 3_898,
    "test.anova_f1.F": 1_044, "test.anova_specificity.F": 18_605,
    # explainability (Table 2, Fig. 4, Fig. 8)
    "xai.gradcam.localization_accuracy": 0.208, "xai.gradcam.false_positive_rate": 0.854,
    "xai.gradcam.anatomical_coverage": 0.810,
    "xai.gradcampp.localization_accuracy": 0.253, "xai.gradcampp.false_positive_rate": 0.767,
    "xai.gradcampp.anatomical_coverage": 0.907,
    "xai.fused.localization_accuracy": 0.161, "xai.fused.false_positive_rate": 0.490,
    "xai.fused.anatomical_coverage": 1.000,
    "xai.fusedpp.localization_accuracy": 0.215, "xai.fusedpp.false_positive_rate": 0.501,
    # explainability with patient-grouped CIs and Holm-adjusted tests (Sec. 4.4, Fig. 8b)
    "xai.ci.n_boxes": 984, "xai.ci.n_patients": 726,
    "xai.test.fused_vs_fusedpp.fpr_wilcoxon_p": 0.50,
    # official NIH test split (Sec. 4.1, Table 5)
    "split.n_images": 25_596, "split.n_patients": 2_797,
    "split.densenet_nih.mean_auroc": 0.672, "split.densenet_nih.f1": 0.281,
    "split.densenet_nih.precision": 0.198, "split.densenet_nih.recall": 0.485,
    # weights trained without NIH images, evaluated on the NIH sample (Sec. 4.6, Fig. 13)
    "ext.densenet_pc.mean_auroc": 0.648, "ext.densenet_pc.ref_nih.mean_auroc": 0.668,
    "ext.densenet_chex.mean_auroc": 0.634, "ext.densenet_chex.ref_nih.mean_auroc": 0.696,
    "ext.densenet_mimic_ch.mean_auroc": 0.617, "ext.densenet_mimic_nb.mean_auroc": 0.620,
    "ext.densenet_pc.delta_mean_auroc": -0.021, "ext.densenet_mimic_ch.delta_mean_auroc": -0.079,
    "ext.densenet_chex.f1": 0.253, "ext.densenet_pc.f1": 0.297,
    # robustness (Sec. 4.4, Fig. 11)
    "robust.f1_clean": 0.325,
    "robust.noise_30db.degradation_pct": 0.6, "robust.noise_20db.degradation_pct": 29.2,
    "robust.noise_10db.degradation_pct": 52.5,
    "robust.photometric_20_neg.degradation_pct": 1.9, "robust.photometric_20.degradation_pct": 5.1,
    "robust.photometric_40_neg.degradation_pct": 5.3, "robust.photometric_40.degradation_pct": 9.8,
    "robust.threshold_-10.f1": 0.228, "robust.threshold_+10.f1": 0.288,
    # fairness (Fig. 12)
    "fair.f1.age_18_40": 0.334, "fair.f1.age_41_65": 0.348, "fair.f1.age_66_plus": 0.323,
    "fair.f1.sex_M": 0.342, "fair.f1.sex_F": 0.336,
    # reports (Sec. 4.5, Fig. 9); generated locally, 100 images
    "report.n": 100, "report.n_complete": 100, "report.n_with_findings": 74,
    "report.n_with_region": 74, "report.words_mean": 189.4,
    "report.bleu4_mean": 0.018, "report.rouge_l_mean": 0.061,
    "report.finding_mention_recall": 0.888, "report.all_findings_mentioned": 61,
    "report.fid.hallucination_rate": 0.11, "report.fid.contradiction_rate": 0.0,
    # prompt ablation, 200 images (Sec. 4.5, Fig. 14, Table 6); Holm-adjusted p-values
    "ablation.deepseek_r1_distill_qwen_1_5b.plain.hallucination_rate": 0.135,
    "ablation.deepseek_r1_distill_qwen_1_5b.crispe.hallucination_rate": 0.145,
    "ablation.deepseek_r1_distill_qwen_1_5b.crispe_snomed.hallucination_rate": 0.110,
    "ablation.deepseek_r1_distill_qwen_1_5b.plain.recall": 0.916,
    "ablation.deepseek_r1_distill_qwen_1_5b.crispe.recall": 0.765,
    "ablation.deepseek_r1_distill_qwen_1_5b.crispe_snomed.recall": 0.884,
    "ablation.deepseek_r1_distill_qwen_7b.plain.hallucination_rate": 0.255,
    "ablation.deepseek_r1_distill_qwen_7b.crispe.hallucination_rate": 0.271,
    "ablation.deepseek_r1_distill_qwen_7b.crispe_snomed.hallucination_rate": 0.100,
    "ablation.deepseek_r1_distill_qwen_7b.plain.recall": 0.954,
    "ablation.deepseek_r1_distill_qwen_7b.crispe.recall": 0.864,
    "ablation.deepseek_r1_distill_qwen_7b.crispe_snomed.recall": 0.935,
    "ablation.deepseek_r1_distill_qwen_7b.crispe_vs_crispe_snomed.hallucination_mcnemar_p_holm": 0.0,
    "ablation.deepseek_r1_distill_qwen_7b.plain_vs_crispe_snomed.hallucination_mcnemar_p_holm": 0.0,
    "ablation.deepseek_r1_distill_qwen_7b.crispe_vs_crispe_snomed.recall_wilcoxon_p_holm": 0.041,
    "ablation.deepseek_r1_distill_qwen_7b.plain_vs_crispe_snomed.recall_wilcoxon_p_holm": 0.16,
    "ablation.deepseek_r1_distill_qwen_1_5b.plain_vs_crispe.recall_wilcoxon_p_holm": 0.0,
    "ablation.deepseek_r1_distill_qwen_1_5b.crispe_vs_crispe_snomed.recall_wilcoxon_p_holm": 0.002,
    # processing time per image on an NVIDIA L4 GPU, 500 images and 10 reports (Sec. 4.5)
    "timing.classification_s": 0.009, "timing.gradcam_s": 0.061,
    "timing.segmentation_s": 0.100, "timing.llm_s": 32.5, "timing.total_s": 32.6,
}

# Values printed in an earlier version of the corrected manuscript and superseded
# by the final run (run03): reports generated with a prompt without the coded
# anatomical region, and processing time per image on a CPU-only workstation.
ARTICLE_2026_SUPERSEDED = {
    "report.bleu4_mean": 0.014, "report.rouge_l_mean": 0.050,
    "report.finding_mention_recall": 0.826, "report.all_findings_mentioned": 38,
    "time.classification": 0.060, "time.gradcam": 0.216, "time.segmentation": 1.877,
    "time.llm": 183.8, "time.total": 186.0,
}

PRECURSOR_2025 = {
    "sample.n": 50_133, "sample.largest_stratum": 9_677,
    "cls.densenet_nih.precision": 0.25, "cls.densenet_nih.recall": 0.53,
    "cls.densenet_nih.f1": 0.34, "cls.densenet_nih.threshold": 0.55,
    "binary.precision": 0.93, "binary.recall": 0.74, "binary.specificity": 0.55,
    "binary.f1": 0.83,
    "time.classification": 0.570, "time.gradcam": 1.878, "time.segmentation": 12.746,
    "time.llm": 4.216,
}

# Absolute tolerance used for MATCH / MISMATCH (declared, not tuned).
TOLERANCE = {"default": 0.01, "count": 0, "p": 0.05, "stat": 0.10, "time": 0.25,
             "degradation_pct": 1.0, "f1_cv_percent": 0.05}


def tolerance_for(key):
    if key.startswith(("time.", "timing.")):
        return TOLERANCE["time"]
    if key.endswith(".p"):
        return TOLERANCE["p"]
    if key.endswith(".D"):
        return 0.005                      # KS distance lives on [0, 1]
    if key.endswith((".n01", ".n10")):
        return TOLERANCE["count"]
    if key.endswith(".F"):
        return 1.0                        # printed rounded to integers
    if key == "report.words_mean":
        return 0.5                        # printed rounded to whole words
    if key.endswith(".stat") or key.endswith(".t") or key.endswith(".d"):
        return TOLERANCE["stat"]
    if key.endswith("degradation_pct"):
        return TOLERANCE["degradation_pct"]
    if key.endswith("f1_cv_percent"):
        return TOLERANCE["f1_cv_percent"]
    if key.endswith(("_p_holm", "_wilcoxon_p")):
        return TOLERANCE["p"]
    if key in ("report.n", "report.n_complete", "report.all_findings_mentioned",
               "report.n_with_findings", "report.n_with_region", "xai.ci.n_boxes",
               "xai.ci.n_patients", "split.n_images", "split.n_patients"):
        return TOLERANCE["count"]
    if key in ("sample.n", "sample.n_strata") or key.startswith(
            ("sample.largest", "sample.per_stratum", "fig2.")):
        return TOLERANCE["count"]
    return TOLERANCE["default"]
