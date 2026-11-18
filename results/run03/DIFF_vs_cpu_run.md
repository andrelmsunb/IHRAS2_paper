# Colab run vs. published CPU run

RUN_ID run03. identical: 66; within tolerance: 93; OUT OF TOLERANCE: 11; time (hardware): 7; missing or non-numeric: 43

| Key | Published (CPU) | This run | abs. diff | Status |
|---|---|---|---|---|
| auroc.Atelectasis | 0.654438 | 0.654442 | 3.28565e-06 | within tolerance |
| auroc.Atelectasis_ci | [0.6455761352800856, 0.6631201813836048] | [0.6455793097383226, 0.6631226759835133] | --- | missing or non-numeric |
| auroc.Cardiomegaly | 0.832707 | 0.832703 | 4.22264e-06 | within tolerance |
| auroc.Cardiomegaly_ci | [0.8215118608117303, 0.8423340271427686] | [0.8215083929522431, 0.84232956914665] | --- | missing or non-numeric |
| auroc.Consolidation | 0.66137 | 0.661371 | 6.65758e-07 | within tolerance |
| auroc.Consolidation_ci | [0.6505982338730933, 0.6714966687829328] | [0.6505978269268174, 0.671498119847237] | --- | missing or non-numeric |
| auroc.Edema | 0.759258 | 0.759253 | 4.89915e-06 | within tolerance |
| auroc.Edema_ci | [0.7483976366746167, 0.770939607021939] | [0.7483932727141722, 0.7709342136908269] | --- | missing or non-numeric |
| auroc.Effusion | 0.756181 | 0.756177 | 3.93118e-06 | within tolerance |
| auroc.Effusion_ci | [0.7496850774976924, 0.7638634580802944] | [0.7496813088858847, 0.7638601635149311] | --- | missing or non-numeric |
| auroc.Emphysema | 0.569836 | 0.569828 | 8.66717e-06 | within tolerance |
| auroc.Emphysema_ci | [0.5492916794274114, 0.5896037889061027] | [0.5492793918308602, 0.5895930887829907] | --- | missing or non-numeric |
| auroc.Fibrosis | 0.643946 | 0.643946 | 5.98963e-07 | within tolerance |
| auroc.Fibrosis_ci | [0.62675531266972, 0.6609675569991685] | [0.6267553932748327, 0.6609725228574657] | --- | missing or non-numeric |
| auroc.Hernia | 0.760912 | 0.76091 | 1.32209e-06 | within tolerance |
| auroc.Hernia_ci | [0.7116588702945916, 0.806983805983308] | [0.7116576630559038, 0.8069851468364257] | --- | missing or non-numeric |
| auroc.Infiltration | 0.603441 | 0.603438 | 2.22851e-06 | within tolerance |
| auroc.Infiltration_ci | [0.5963477410281183, 0.6113894121351608] | [0.5963469421988694, 0.6113863153873694] | --- | missing or non-numeric |
| auroc.Mass | 0.694479 | 0.694466 | 1.28699e-05 | within tolerance |
| auroc.Mass_ci | [0.6823829454050615, 0.70678056528275] | [0.6823704008612904, 0.70676706768174] | --- | missing or non-numeric |
| auroc.Nodule | 0.572519 | 0.57251 | 8.84618e-06 | within tolerance |
| auroc.Nodule_ci | [0.5601391429547697, 0.5857299400793553] | [0.5601305567585543, 0.5857221780095012] | --- | missing or non-numeric |
| auroc.Pleural_Thickening | 0.63832 | 0.638323 | 2.96853e-06 | within tolerance |
| auroc.Pleural_Thickening_ci | [0.6257778672980602, 0.6512228663792008] | [0.6257808248231951, 0.6512273628366897] | --- | missing or non-numeric |
| auroc.Pneumonia | 0.607772 | 0.607766 | 5.24356e-06 | within tolerance |
| auroc.Pneumonia_ci | [0.5899614839060378, 0.6240296629129914] | [0.589954831587099, 0.6240262318546821] | --- | missing or non-numeric |
| auroc.Pneumothorax | 0.601797 | 0.6018 | 2.72955e-06 | within tolerance |
| auroc.Pneumothorax_ci | [0.5842760506475206, 0.6193235204715594] | [0.5842789998508763, 0.6193240299193353] | --- | missing or non-numeric |
| binary.densenet_multi.f1 | 0.810416 | 0.810452 | 3.52435e-05 | within tolerance |
| binary.densenet_multi.precision | 0.938808 | 0.938786 | 2.23554e-05 | within tolerance |
| binary.densenet_multi.recall | 0.712918 | 0.712985 | 6.7443e-05 | within tolerance |
| binary.densenet_multi.specificity | 0.639015 | 0.63884 | 0.000174642 | within tolerance |
| binary.resnet50_multi.f1 | 0.32883 | 0.328574 | 0.000255993 | within tolerance |
| binary.resnet50_multi.precision | 0.973879 | 0.973748 | 0.00013102 | within tolerance |
| binary.resnet50_multi.recall | 0.19781 | 0.197631 | 0.000179848 | within tolerance |
| binary.resnet50_multi.specificity | 0.958784 | 0.95861 | 0.000174642 | within tolerance |
| cls.densenet_multi.exact_match | 0.109823 | 0.109803 | 1.99171e-05 | within tolerance |
| cls.densenet_multi.f1 | 0.334228 | 0.334318 | 8.98222e-05 | within tolerance |
| cls.densenet_multi.f1_ci | [0.32914398532116906, 0.3396692136962430 | [0.3292529835362955, 0.3397310899085247] | --- | missing or non-numeric |
| cls.densenet_multi.macro.f1 | 0.246924 | 0.246983 | 5.91366e-05 | within tolerance |
| cls.densenet_multi.macro.precision | 0.237527 | 0.237555 | 2.85375e-05 | within tolerance |
| cls.densenet_multi.macro.recall | 0.331095 | 0.331158 | 6.28443e-05 | within tolerance |
| cls.densenet_multi.macro.specificity | 0.875198 | 0.875188 | 9.88855e-06 | within tolerance |
| cls.densenet_multi.mean_auroc | 0.703412 | 0.703409 | 2.91879e-06 | within tolerance |
| cls.densenet_multi.per_image_f1_mean | 0.307302 | 0.307362 | 5.94554e-05 | within tolerance |
| cls.densenet_multi.precision | 0.285747 | 0.28581 | 6.31156e-05 | within tolerance |
| cls.densenet_multi.precision_ci | [0.28083787886286776, 0.2909424357074904 | [0.28092328346824313, 0.2910071335327773 | --- | missing or non-numeric |
| cls.densenet_multi.recall | 0.402522 | 0.402658 | 0.00013532 | within tolerance |
| cls.densenet_multi.recall_ci | [0.3942026339925172, 0.41117110687994013 | [0.39440144963469953, 0.4113035776154637 | --- | missing or non-numeric |
| cls.densenet_multi.specificity | 0.881794 | 0.881791 | 3.17958e-06 | within tolerance |
| cls.densenet_multi.specificity_ci | [0.8782113766212979, 0.8853612889403036] | [0.8782083601148611, 0.8853599149790162] | --- | missing or non-numeric |
| cls.densenet_nih.f1 | 0.339514 | 0.339511 | 3.0632e-06 | within tolerance |
| cls.densenet_nih.f1_ci | [0.33496868616497344, 0.3445005612736657 | [0.3349453511526542, 0.3444974708680922] | --- | missing or non-numeric |
| cls.densenet_nih.macro.f1 | 0.233675 | 0.233685 | 1.00234e-05 | within tolerance |
| cls.densenet_nih.macro.precision | 0.197868 | 0.197888 | 1.97926e-05 | within tolerance |
| cls.densenet_nih.macro.recall | 0.295223 | 0.295198 | 2.46729e-05 | within tolerance |
| cls.densenet_nih.macro.specificity | 0.86219 | 0.862211 | 2.10105e-05 | within tolerance |
| cls.densenet_nih.mean_auroc | 0.668355 | 0.668352 | 2.99871e-06 | within tolerance |
| cls.densenet_nih.mean_auroc_vs_no_finding | 0.764519 | 0.764515 | 3.10366e-06 | within tolerance |
| cls.densenet_nih.per_image_f1_mean | 0.303351 | 0.303339 | 1.21256e-05 | within tolerance |
| cls.densenet_nih.precision | 0.282295 | 0.282309 | 1.36083e-05 | within tolerance |
| cls.densenet_nih.precision_ci | [0.27804419053518004, 0.2868041765285335 | [0.2780821725228176, 0.28679166671243866 | --- | missing or non-numeric |
| cls.densenet_nih.recall | 0.425824 | 0.425784 | 4.05959e-05 | within tolerance |
| cls.densenet_nih.recall_ci | [0.4178890980874008, 0.43466142991786433 | [0.41787484856439705, 0.4346075616651779 | --- | missing or non-numeric |
| cls.densenet_nih.specificity | 0.87281 | 0.872831 | 2.06673e-05 | within tolerance |
| cls.densenet_nih.specificity_ci | [0.8692984183526025, 0.8763310707213716] | [0.8693252505798502, 0.8763627736746302] | --- | missing or non-numeric |
| cls.resnet50_multi.exact_match | 0.153302 | 0.153243 | 5.97514e-05 | within tolerance |
| cls.resnet50_multi.f1 | 0.17187 | 0.171808 | 6.28083e-05 | within tolerance |
| cls.resnet50_multi.f1_ci | [0.1650804107179553, 0.178664008136994] | [0.16495549351339275, 0.1785210468033493 | --- | missing or non-numeric |
| cls.resnet50_multi.macro.f1 | 0.149632 | 0.149621 | 1.09982e-05 | within tolerance |
| cls.resnet50_multi.macro.precision | 0.619856 | 0.619505 | 0.000350928 | within tolerance |
| cls.resnet50_multi.macro.recall | 0.091095 | 0.091116 | 2.09724e-05 | within tolerance |
| cls.resnet50_multi.macro.specificity | 0.994182 | 0.994185 | 3.07622e-06 | within tolerance |
| cls.resnet50_multi.mean_auroc | 0.797185 | 0.797147 | 3.78263e-05 | within tolerance |
| cls.resnet50_multi.per_image_f1_mean | 0.206489 | 0.206422 | 6.67699e-05 | within tolerance |
| cls.resnet50_multi.precision | 0.680109 | 0.680082 | 2.61668e-05 | within tolerance |
| cls.resnet50_multi.precision_ci | [0.6685504604332226, 0.6925538376784411] | [0.6686181869425188, 0.6926351140829584] | --- | missing or non-numeric |
| cls.resnet50_multi.recall | 0.098364 | 0.0983234 | 4.05959e-05 | within tolerance |
| cls.resnet50_multi.recall_ci | [0.09400559003741722, 0.1026095586384937 | [0.09400524614900213, 0.1025964953291690 | --- | missing or non-numeric |
| cls.resnet50_multi.specificity | 0.994565 | 0.994566 | 1.58979e-06 | within tolerance |
| cls.resnet50_multi.specificity_ci | [0.9942594501832588, 0.9948726305748492] | [0.994259404604865, 0.9948689268184501] | --- | missing or non-numeric |
| cv.f1_cv_percent | 1.20989 | 1.20886 | 0.00103393 | within tolerance |
| cv.f1_cv_percent_ddof0 | 1.08216 | 1.08123 | 0.000924778 | within tolerance |
| cv.f1_mean | 0.339497 | 0.339494 | 3.10692e-06 | within tolerance |
| cv.folds | [{'f1': 0.33489176553252437, 'precision' | [{'f1': 0.3349189189189189, 'precision': | --- | missing or non-numeric |
| fair.2025.age_0_24 | {'f1': 0.32245411113904954, 'n': 6782, ' | {'f1': 0.32250276632129565, 'n': 6782, ' | --- | missing or non-numeric |
| fair.2025.age_25_49 | {'f1': 0.3407680136319377, 'n': 18004, ' | {'f1': 0.3407783829839029, 'n': 18004, ' | --- | missing or non-numeric |
| fair.2025.age_50_74 | {'f1': 0.34917196171928216, 'n': 22290,  | {'f1': 0.349150687379248, 'n': 22290, 'p | --- | missing or non-numeric |
| fair.2025.age_75_plus | {'f1': 0.2797957981543295, 'n': 3126, 'p | {'f1': 0.279736764561438, 'n': 3126, 'pr | --- | missing or non-numeric |
| fair.2025.max_cohen_h_age | {'f1': 0.14962434875425856, 'precision': | {'f1': 0.1497112326898744, 'precision':  | --- | missing or non-numeric |
| fair.2025.sex_F | {'f1': 0.33610030477983993, 'n': 22558,  | {'f1': 0.33608801774231517, 'n': 22558,  | --- | missing or non-numeric |
| fair.2025.sex_M | {'f1': 0.3421462491758793, 'n': 27650, ' | {'f1': 0.34215052941401325, 'n': 27650,  | --- | missing or non-numeric |
| fair.article.age_18_40 | {'f1': 0.33420009905894005, 'n': 13846,  | {'f1': 0.33422768925947327, 'n': 13846,  | --- | missing or non-numeric |
| fair.article.age_41_65 | {'f1': 0.3481853352054061, 'n': 25679, ' | {'f1': 0.3481756838660148, 'n': 25679, ' | --- | missing or non-numeric |
| fair.article.age_66_plus | {'f1': 0.3228201590117616, 'n': 7937, 'p | {'f1': 0.3227735787052251, 'n': 7937, 'p | --- | missing or non-numeric |
| fair.article.chi2_age | {'df': 2, 'p': 1.787844893783062e-39, 's | {'df': 2, 'p': 1.7878448937830622e-39, ' | --- | missing or non-numeric |
| fair.article.max_cohen_h_age | {'f1': 0.05372971304186125, 'precision': | {'f1': 0.05380908113476823, 'precision': | --- | missing or non-numeric |
| fair.article.sex_F | {'f1': 0.33610030477983993, 'n': 22558,  | {'f1': 0.33608801774231517, 'n': 22558,  | --- | missing or non-numeric |
| fair.article.sex_M | {'f1': 0.3421462491758793, 'n': 27650, ' | {'f1': 0.34215052941401325, 'n': 27650,  | --- | missing or non-numeric |
| fair.f1.age_18_40 | 0.3342 | 0.334228 | 2.75902e-05 | within tolerance |
| fair.f1.age_41_65 | 0.348185 | 0.348176 | 9.65134e-06 | within tolerance |
| fair.f1.age_66_plus | 0.32282 | 0.322774 | 4.65803e-05 | within tolerance |
| fair.f1.sex_F | 0.3361 | 0.336088 | 1.2287e-05 | within tolerance |
| fair.f1.sex_M | 0.342146 | 0.342151 | 4.28024e-06 | within tolerance |
| report.all_findings_mentioned | 38 | 61 | 23 | OUT OF TOLERANCE |
| report.bleu4_mean | 0.0137399 | 0.017877 | 0.00413708 | within tolerance |
| report.bleu4_sd | 0.00551567 | 0.0119175 | 0.00640188 | within tolerance |
| report.finding_mention_recall | 0.825772 | 0.887709 | 0.0619369 | OUT OF TOLERANCE |
| report.rouge_l_mean | 0.0503664 | 0.0611736 | 0.0108073 | OUT OF TOLERANCE |
| report.rouge_l_sd | 0.0294995 | 0.0378688 | 0.0083693 | within tolerance |
| report.time_sd | 40.74 | 6.80643 | 33.9335 | OUT OF TOLERANCE |
| report.words_mean | 131.85 | 189.36 | 57.51 | OUT OF TOLERANCE |
| repr.ks_age.p | 6.98602e-37 | 6.98602e-37 | 8.10182e-51 | within tolerance |
| robust.f1_clean | 0.325417 | 0.325371 | 4.59953e-05 | within tolerance |
| robust.noise_10db.degradation_pct | 52.5131 | 52.5064 | 0.00671288 | within tolerance |
| robust.noise_20db.degradation_pct | 29.1905 | 29.1805 | 0.0100098 | within tolerance |
| robust.noise_30db.degradation_pct | 0.585925 | 0.612962 | 0.0270373 | within tolerance |
| robust.photometric_20.degradation_pct | 5.05551 | 5.04209 | 0.0134216 | within tolerance |
| robust.photometric_20_neg.degradation_pct | 1.92246 | 1.9086 | 0.0138645 | within tolerance |
| robust.photometric_40.degradation_pct | 9.7637 | 9.80746 | 0.0437566 | within tolerance |
| robust.photometric_40_neg.degradation_pct | 5.34703 | 5.34791 | 0.000883022 | within tolerance |
| robust.threshold_-10.f1 | 0.227874 | 0.227886 | 1.17328e-05 | within tolerance |
| test.anova_f1.F | 1059.6 | 1043.92 | 15.6813 | OUT OF TOLERANCE |
| test.anova_f1.p | 3.18665e-14 | 3.4831e-14 | 2.96446e-15 | within tolerance |
| test.anova_precision.F | 6078.38 | 6087.14 | 8.7589 | OUT OF TOLERANCE |
| test.anova_precision.p | 9.19621e-19 | 9.11717e-19 | 7.90329e-21 | within tolerance |
| test.anova_recall.F | 3907.84 | 3897.6 | 10.2426 | OUT OF TOLERANCE |
| test.anova_recall.p | 1.29804e-17 | 1.31861e-17 | 2.05699e-19 | within tolerance |
| test.anova_specificity.F | 18818.6 | 18604.5 | 214.091 | OUT OF TOLERANCE |
| test.anova_specificity.p | 1.04845e-21 | 1.12293e-21 | 7.448e-23 | within tolerance |
| test.mcnemar_vs_multi.n01 | 1774 | 1775 | 1 | OUT OF TOLERANCE |
| test.mcnemar_vs_multi.p | 1.18966e-19 | 1.38703e-19 | 1.97362e-20 | within tolerance |
| test.mcnemar_vs_resnet.n10 | 4514 | 4511 | 3 | OUT OF TOLERANCE |
| test.mcnemar_vs_resnet.p | 7.55663e-277 | 2.26498e-276 | 1.50932e-276 | within tolerance |
| test.ttest_vs_multi.d | -0.0120525 | -0.0122704 | 0.000217915 | within tolerance |
| test.ttest_vs_multi.p | 0.00692349 | 0.00597181 | 0.000951676 | within tolerance |
| test.ttest_vs_multi.t | -2.70061 | -2.74944 | 0.0488286 | within tolerance |
| test.ttest_vs_resnet.d | 0.223699 | 0.22384 | 0.000140737 | within tolerance |
| test.ttest_vs_resnet.t | 50.1246 | 50.1561 | 0.0315352 | within tolerance |
| test.wilcoxon_vs_multi.p | 0.240743 | 0.219 | 0.0217429 | within tolerance |
| time.classification | 0.060414 | 0.00791308 | 0.0525009 | time (hardware) |
| time.classification_total_s.densenet_multi | 5154.71 | --- | --- | missing or non-numeric |
| time.classification_total_s.densenet_nih | 3033.26 | 397.3 | 2635.96 | time (hardware) |
| time.classification_total_s.resnet50_multi | 21954 | 705.181 | 21248.8 | time (hardware) |
| time.gradcam | 0.216387 | 0.0616387 | 0.154748 | time (hardware) |
| time.llm | 183.809 | 28.497 | 155.312 | time (hardware) |
| time.segmentation | 1.87699 | 0.0992674 | 1.77772 | time (hardware) |
| time.total | 185.963 | 28.6659 | 157.297 | time (hardware) |
| xai.fused.false_positive_rate | 0.489986 | 0.489987 | 1.1072e-06 | within tolerance |
| xai.gradcam.anatomical_coverage | 0.809726 | 0.80969 | 3.6269e-05 | within tolerance |
| xai.gradcam.false_positive_rate | 0.853742 | 0.853751 | 8.76442e-06 | within tolerance |
| xai.gradcampp.anatomical_coverage | 0.907306 | 0.907281 | 2.53211e-05 | within tolerance |
| xai.gradcampp.false_positive_rate | 0.767458 | 0.767444 | 1.48711e-05 | within tolerance |
| xai.tau_table | {'0.10': {'anatomical_coverage': 1.0, 'f | {'0.10': {'anatomical_coverage': 1.0, 'f | --- | missing or non-numeric |
