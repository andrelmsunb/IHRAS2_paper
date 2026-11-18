# Computed vs. reported values

MATCH 11 | MISMATCH 0 | NOT COMPUTED 45

| Item | Reported (2026) | Computed | Tolerance | Status | Precursor (2025) |
|---|---|---|---|---|---|
| sample.n | 5.017e+04 | 5.017e+04 | 0 | **MATCH** | 5.013e+04 |
| sample.largest_stratum | 9605 | 9605 | 0 | **MATCH** | 9677 |
| sample.per_stratum_formula_n | 370 | 370 | 0 | **MATCH** |  |
| repr.ks_age.D | 0.034 | 0.03406 | 0.005 | **MATCH** |  |
| repr.ks_age.p | 0 | 2.248e-35 | 0.05 | **MATCH** |  |
| repr.chi2_sex.stat | 40.4 | 40.38 | 0.1 | **MATCH** |  |
| repr.chi2_sex.p | 0 | 2.086e-10 | 0.05 | **MATCH** |  |
| repr.chi2_pathology.stat | 909.8 | 909.8 | 0.1 | **MATCH** |  |
| repr.chi2_pathology.p | 0 | 4.031e-186 | 0.05 | **MATCH** |  |
| fig2.Infiltration | 1.473e+04 | 1.473e+04 | 0 | **MATCH** |  |
| fig2.Hernia | 227 | 227 | 0 | **MATCH** |  |
| cls.densenet_nih.precision | 0.915 | --- | 0.01 | **NOT COMPUTED** | 0.25 |
| cls.densenet_nih.recall | 0.908 | --- | 0.01 | **NOT COMPUTED** | 0.53 |
| cls.densenet_nih.f1 | 0.911 | --- | 0.01 | **NOT COMPUTED** | 0.34 |
| cls.densenet_nih.specificity | 0.934 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.densenet_multi.precision | 0.892 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.densenet_multi.recall | 0.885 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.densenet_multi.f1 | 0.888 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.densenet_multi.specificity | 0.923 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.resnet50_multi.precision | 0.878 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.resnet50_multi.recall | 0.871 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.resnet50_multi.f1 | 0.874 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.resnet50_multi.specificity | 0.919 | --- | 0.01 | **NOT COMPUTED** |  |
| cls.densenet_nih.mean_auroc | 0.911 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Pneumothorax | 0.967 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Cardiomegaly | 0.943 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Effusion | 0.924 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Pneumonia | 0.891 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Atelectasis | 0.887 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Consolidation | 0.876 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Fibrosis | 0.834 | --- | 0.01 | **NOT COMPUTED** |  |
| auroc.Hernia | 0.823 | --- | 0.01 | **NOT COMPUTED** |  |
| cv.f1_mean | 0.911 | --- | 0.01 | **NOT COMPUTED** |  |
| cv.f1_cv_percent | 0.24 | --- | 0.05 | **NOT COMPUTED** |  |
| test.ttest_vs_multi.t | 3.247 | --- | 0.1 | **NOT COMPUTED** |  |
| test.ttest_vs_multi.d | 0.847 | --- | 0.1 | **NOT COMPUTED** |  |
| test.ttest_vs_resnet.t | 4.891 | --- | 0.1 | **NOT COMPUTED** |  |
| test.ttest_vs_resnet.d | 1.234 | --- | 0.1 | **NOT COMPUTED** |  |
| xai.fused.localization_accuracy | 0.891 | --- | 0.01 | **NOT COMPUTED** |  |
| xai.gradcam.localization_accuracy | 0.847 | --- | 0.01 | **NOT COMPUTED** |  |
| xai.gradcampp.localization_accuracy | 0.863 | --- | 0.01 | **NOT COMPUTED** |  |
| xai.fused.false_positive_rate | 0.047 | --- | 0.01 | **NOT COMPUTED** |  |
| xai.fused.anatomical_coverage | 0.956 | --- | 0.01 | **NOT COMPUTED** |  |
| robust.noise_20db.degradation_pct | 3.2 | --- | 1 | **NOT COMPUTED** |  |
| robust.noise_10db.degradation_pct | 12.8 | --- | 1 | **NOT COMPUTED** |  |
| robust.photometric_40.degradation_pct | 7.3 | --- | 1 | **NOT COMPUTED** |  |
| fair.f1.age_18_40 | 0.918 | --- | 0.01 | **NOT COMPUTED** |  |
| fair.f1.age_41_65 | 0.911 | --- | 0.01 | **NOT COMPUTED** |  |
| fair.f1.age_66_plus | 0.907 | --- | 0.01 | **NOT COMPUTED** |  |
| fair.f1.sex_M | 0.913 | --- | 0.01 | **NOT COMPUTED** |  |
| fair.f1.sex_F | 0.909 | --- | 0.01 | **NOT COMPUTED** |  |
| time.classification | 0.23 | --- | 0.25 | **NOT COMPUTED** | 0.57 |
| time.gradcam | 0.15 | --- | 0.25 | **NOT COMPUTED** | 1.878 |
| time.segmentation | 0.31 | --- | 0.25 | **NOT COMPUTED** | 12.75 |
| time.llm | 1.42 | --- | 0.25 | **NOT COMPUTED** | 4.216 |
| time.total | 2.11 | --- | 0.25 | **NOT COMPUTED** |  |
