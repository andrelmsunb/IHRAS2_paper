"""Parameters taken from the article, with their source.

Ref tags point to the IHRAS manuscript (Elsevier cas-dc version).  "2025" tags
point to the precursor, Rodrigues et al., Bioengineering 12(8):795 (2025),
which describes the same sample and models in more detail.  Choices that the
article leaves open are documented in ASSUMPTIONS.md.
"""

SEED = 42  # global seed (Python, NumPy, PyTorch); not stated in the article

# --- NIH ChestX-ray14 (Ref: Sec. 3.2) ---------------------------------------
FINDINGS = ("Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
            "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass", "Nodule",
            "Pleural_Thickening", "Pneumonia", "Pneumothorax")
NIH_IMAGES, NIH_PATIENTS = 112_120, 30_805

# --- Stratified sampling (Ref: Sec. 3.2, Eq. (6); 2025 Sec. 3.1) ------------
AGE_BIN_YEARS = 25
STRATA = ("age_bin", "Finding Labels", "Patient Gender", "View Position")
Z, P_EST, MARGIN = 1.96, 0.5, 0.05
PER_STRATUM_CAP = 370          # "all available samples" for smaller strata (2025)

# --- Classification (Ref: Sec. 3.2; 2025 Sec. 3.2 and 4.1.1) ----------------
MODELS = {                      # TorchXRayVision weights, used with default config
    "densenet_nih": "densenet121-res224-nih",
    "densenet_multi": "densenet121-res224-all",
    "resnet50_multi": "resnet50-res512-all",
}
# --- External validation (new analysis, T23) --------------------------------
# TorchXRayVision weights trained WITHOUT NIH ChestX-ray14: evaluating them on
# the NIH images is a cross-dataset validation free of train/test leakage by
# construction.  Only the findings that each model predicts are compared.
EXTERNAL_MODELS = {
    "densenet_pc": "densenet121-res224-pc",              # PadChest (Spain); all 14 NIH findings
    "densenet_chex": "densenet121-res224-chex",          # CheXpert (Stanford); 7 NIH findings
    "densenet_mimic_ch": "densenet121-res224-mimic_ch",  # MIMIC-CXR, CheXpert labeler; 7 findings
    "densenet_mimic_nb": "densenet121-res224-mimic_nb",  # MIMIC-CXR, NegBio labeler; 7 findings
}
ALL_MODELS = {**MODELS, **EXTERNAL_MODELS}

DECISION_THRESHOLD = 0.55       # 2025 Sec. 4.1.1 (maximizes F1); not stated in 2026
CV_FOLDS = 5                    # Ref: Sec. 3.3
CI_LEVEL = 0.95
BOOTSTRAP_B = 1000              # not stated; see ASSUMPTIONS.md

# --- Explainability and fusion (Ref: Sec. 3.1, Eqs. (1)-(4), Table 2) -------
TAU_OVERLAP = 0.30
TAU_GRID = (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
CAM_BINARIZATION = 0.50         # threshold of M_bin on the [0, 1]-normalized map; not stated
ANATOMY = ("Left Clavicle", "Right Clavicle", "Left Scapula", "Right Scapula",
           "Left Lung", "Right Lung", "Left Hilus Pulmonis", "Right Hilus Pulmonis",
           "Heart", "Aorta", "Facies Diaphragmatica", "Mediastinum", "Weasand",
           "Spine")                     # 2025 Sec. 3.3 = TorchXRayVision PSPNet targets

# --- Robustness (Ref: Sec. 3.3, Sec. 4.4) -----------------------------------
SNR_DB = (30, 20, 10)
PHOTOMETRIC = (-0.40, -0.20, 0.20, 0.40)   # relative contrast/brightness change
HPARAM_PERTURB = 0.10                      # +-10% (Table 3); applied to the threshold

# --- Fairness (Ref: Sec. 4.4, Fig. 12) ---------------------------------------
AGE_GROUPS_ARTICLE = ((18, 40), (41, 65), (66, 200))
AGE_GROUPS_2025 = ((0, 24), (25, 49), (50, 74), (75, 200))

# --- Report generation (Ref: Sec. 3.1; 2025 Sec. 3.4, Table 2) --------------
LLM_API_MODEL = "deepseek-reasoner"                    # DeepSeek-R1 via API
LLM_LOCAL_MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
SNOMED_FINDING_SITE = "363698007"                      # Ref: Sec. 3.1

# --- Processing time (new analysis, T22) ------------------------------------
TIMING_N_IMAGES = 500           # images timed for classification, Grad-CAM, segmentation
TIMING_N_REPORTS = 10           # LLM reports timed (unbatched, as in the report stage)

# --- Prompt ablation and report fidelity (new analysis, T25) ----------------
ABLATION_N = 200                # images; every arm is generated for the same images
ABLATION_ARMS = ("plain", "crispe", "crispe_snomed")
ABLATION_MODELS = ("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
                   "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
