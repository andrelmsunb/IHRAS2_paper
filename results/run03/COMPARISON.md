# Computed vs. reported values

MATCH 79 | MISMATCH 12 | NOT COMPUTED 0

| Item | Reported (2026) | Computed | Tolerance | Status | Precursor (2025) |
|---|---|---|---|---|---|
| sample.n | 5.021e+04 | 5.021e+04 | 0 | **MATCH** | 5.013e+04 |
| sample.largest_stratum | 9677 | 9677 | 0 | **MATCH** | 9677 |
| sample.per_stratum_formula_n | 370 | 370 | 0 | **MATCH** |  |
| repr.ks_age.D | 0.035 | 0.03478 | 0.005 | **MATCH** |  |
| repr.ks_age.p | 0 | 6.986e-37 | 0.05 | **MATCH** |  |
| repr.chi2_sex.stat | 41.3 | 41.31 | 0.1 | **MATCH** |  |
| repr.chi2_sex.p | 0 | 1.296e-10 | 0.05 | **MATCH** |  |
| repr.chi2_pathology.stat | 914.2 | 914.2 | 0.1 | **MATCH** |  |
| repr.chi2_pathology.p | 0 | 4.532e-187 | 0.05 | **MATCH** |  |
| fig2.Infiltration | 1.472e+04 | 1.472e+04 | 0 | **MATCH** |  |
| fig2.Hernia | 227 | 227 | 0 | **MATCH** |  |
| cls.densenet_nih.precision | 0.282 | 0.2823 | 0.01 | **MATCH** | 0.25 |
| cls.densenet_nih.recall | 0.426 | 0.4258 | 0.01 | **MATCH** | 0.53 |
| cls.densenet_nih.f1 | 0.34 | 0.3395 | 0.01 | **MATCH** | 0.34 |
| cls.densenet_nih.specificity | 0.873 | 0.8728 | 0.01 | **MATCH** |  |
| cls.densenet_multi.precision | 0.286 | 0.2858 | 0.01 | **MATCH** |  |
| cls.densenet_multi.recall | 0.403 | 0.4027 | 0.01 | **MATCH** |  |
| cls.densenet_multi.f1 | 0.334 | 0.3343 | 0.01 | **MATCH** |  |
| cls.densenet_multi.specificity | 0.882 | 0.8818 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.precision | 0.68 | 0.6801 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.recall | 0.098 | 0.09832 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.f1 | 0.172 | 0.1718 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.specificity | 0.995 | 0.9946 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.best_threshold | 0.15 | 0.15 | 0.01 | **MATCH** |  |
| cls.densenet_nih.mean_auroc | 0.668 | 0.6684 | 0.01 | **MATCH** |  |
| cls.densenet_multi.mean_auroc | 0.703 | 0.7034 | 0.01 | **MATCH** |  |
| cls.resnet50_multi.mean_auroc | 0.797 | 0.7971 | 0.01 | **MATCH** |  |
| binary.densenet_nih.precision | 0.926 | 0.9261 | 0.01 | **MATCH** |  |
| binary.densenet_nih.recall | 0.743 | 0.7427 | 0.01 | **MATCH** |  |
| binary.densenet_nih.f1 | 0.824 | 0.8244 | 0.01 | **MATCH** |  |
| sample.no_finding_share | 0.114 | 0.114 | 0.01 | **MATCH** |  |
| cls.densenet_nih.mean_auroc_vs_no_finding | 0.765 | 0.7645 | 0.01 | **MATCH** |  |
| auroc.Cardiomegaly | 0.833 | 0.8327 | 0.01 | **MATCH** |  |
| auroc.Hernia | 0.761 | 0.7609 | 0.01 | **MATCH** |  |
| auroc.Edema | 0.759 | 0.7593 | 0.01 | **MATCH** |  |
| auroc.Effusion | 0.756 | 0.7562 | 0.01 | **MATCH** |  |
| auroc.Emphysema | 0.57 | 0.5698 | 0.01 | **MATCH** |  |
| auroc.Nodule | 0.573 | 0.5725 | 0.01 | **MATCH** |  |
| auroc.Pneumothorax | 0.602 | 0.6018 | 0.01 | **MATCH** |  |
| auroc.Infiltration | 0.603 | 0.6034 | 0.01 | **MATCH** |  |
| cv.f1_mean | 0.34 | 0.3395 | 0.01 | **MATCH** |  |
| cv.f1_cv_percent | 1.2 | 1.209 | 0.05 | **MATCH** |  |
| test.ttest_vs_multi.t | -2.7 | -2.749 | 0.1 | **MATCH** |  |
| test.ttest_vs_multi.p | 0.007 | 0.005972 | 0.05 | **MATCH** |  |
| test.ttest_vs_multi.d | -0.012 | -0.01227 | 0.1 | **MATCH** |  |
| test.wilcoxon_vs_multi.p | 0.24 | 0.219 | 0.05 | **MATCH** |  |
| test.mcnemar_vs_multi.n01 | 1774 | 1775 | 0 | **MISMATCH** |  |
| test.mcnemar_vs_multi.n10 | 2357 | 2357 | 0 | **MATCH** |  |
| test.ttest_vs_resnet.t | 50.1 | 50.16 | 0.1 | **MATCH** |  |
| test.ttest_vs_resnet.d | 0.224 | 0.2238 | 0.1 | **MATCH** |  |
| test.mcnemar_vs_resnet.n01 | 1748 | 1748 | 0 | **MATCH** |  |
| test.mcnemar_vs_resnet.n10 | 4514 | 4511 | 0 | **MISMATCH** |  |
| test.anova_precision.F | 6078 | 6087 | 1 | **MISMATCH** |  |
| test.anova_recall.F | 3908 | 3898 | 1 | **MISMATCH** |  |
| test.anova_f1.F | 1060 | 1044 | 1 | **MISMATCH** |  |
| test.anova_specificity.F | 1.882e+04 | 1.86e+04 | 1 | **MISMATCH** |  |
| xai.gradcam.localization_accuracy | 0.208 | 0.2083 | 0.01 | **MATCH** |  |
| xai.gradcam.false_positive_rate | 0.854 | 0.8538 | 0.01 | **MATCH** |  |
| xai.gradcam.anatomical_coverage | 0.81 | 0.8097 | 0.01 | **MATCH** |  |
| xai.gradcampp.localization_accuracy | 0.253 | 0.253 | 0.01 | **MATCH** |  |
| xai.gradcampp.false_positive_rate | 0.768 | 0.7674 | 0.01 | **MATCH** |  |
| xai.gradcampp.anatomical_coverage | 0.907 | 0.9073 | 0.01 | **MATCH** |  |
| xai.fused.localization_accuracy | 0.161 | 0.1606 | 0.01 | **MATCH** |  |
| xai.fused.false_positive_rate | 0.49 | 0.49 | 0.01 | **MATCH** |  |
| xai.fused.anatomical_coverage | 1 | 1 | 0.01 | **MATCH** |  |
| robust.f1_clean | 0.325 | 0.3254 | 0.01 | **MATCH** |  |
| robust.noise_30db.degradation_pct | 0.6 | 0.613 | 1 | **MATCH** |  |
| robust.noise_20db.degradation_pct | 29.2 | 29.18 | 1 | **MATCH** |  |
| robust.noise_10db.degradation_pct | 52.5 | 52.51 | 1 | **MATCH** |  |
| robust.photometric_20_neg.degradation_pct | 1.9 | 1.909 | 1 | **MATCH** |  |
| robust.photometric_20.degradation_pct | 5.1 | 5.042 | 1 | **MATCH** |  |
| robust.photometric_40_neg.degradation_pct | 5.3 | 5.348 | 1 | **MATCH** |  |
| robust.photometric_40.degradation_pct | 9.8 | 9.807 | 1 | **MATCH** |  |
| robust.threshold_-10.f1 | 0.228 | 0.2279 | 0.01 | **MATCH** |  |
| robust.threshold_+10.f1 | 0.288 | 0.2876 | 0.01 | **MATCH** |  |
| fair.f1.age_18_40 | 0.334 | 0.3342 | 0.01 | **MATCH** |  |
| fair.f1.age_41_65 | 0.348 | 0.3482 | 0.01 | **MATCH** |  |
| fair.f1.age_66_plus | 0.323 | 0.3228 | 0.01 | **MATCH** |  |
| fair.f1.sex_M | 0.342 | 0.3422 | 0.01 | **MATCH** |  |
| fair.f1.sex_F | 0.336 | 0.3361 | 0.01 | **MATCH** |  |
| report.n | 100 | 100 | 0 | **MATCH** |  |
| report.n_complete | 100 | 100 | 0 | **MATCH** |  |
| report.bleu4_mean | 0.014 | 0.01788 | 0.01 | **MATCH** |  |
| report.rouge_l_mean | 0.05 | 0.06117 | 0.01 | **MISMATCH** |  |
| report.finding_mention_recall | 0.826 | 0.8877 | 0.01 | **MISMATCH** |  |
| report.all_findings_mentioned | 38 | 61 | 0 | **MISMATCH** |  |
| time.classification | 0.06 | 0.007913 | 0.25 | **MATCH** | 0.57 |
| time.gradcam | 0.216 | 0.06164 | 0.25 | **MATCH** | 1.878 |
| time.segmentation | 1.877 | 0.09927 | 0.25 | **MISMATCH** | 12.75 |
| time.llm | 183.8 | 28.5 | 0.25 | **MISMATCH** | 4.216 |
| time.total | 186 | 28.67 | 0.25 | **MISMATCH** |  |
