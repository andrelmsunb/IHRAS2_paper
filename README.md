# IHRAS: reproducibility package

Code accompanying the article *Synergistic Integration of Deep Learning and
Large Language Models for Explainable and Standardized Chest-Radiograph
Diagnostics* (IHRAS).

**Principle.** Every result is **computed** from public data (NIH
ChestX-ray14) and public model weights (TorchXRayVision). The values reported
in the article appear only in `ihras/reference_values.py`, which serves as the
reference for an automatic comparison. The `COMPARISON.md` of each run lists each
reported item as **MATCH**, **MISMATCH**, or **NOT COMPUTED**, within a
declared tolerance. No reported value is ever written as an output.

## Reproduction outcome

The full pipeline was run end to end on the 112,120 NIH images with
`Data_Entry_2017.csv`. The first submitted version of the article reported
values (e.g. micro F1 0.911, SNOMED CT accuracy 96.3%, 2.11 s per image on a
V100) that this package does **not** reproduce; they are kept in
`ORIGINAL_SUBMISSION` for transparency. The article was corrected to the
computed values (`ARTICLE_2026`). The values printed in the final manuscript come
from the run **run03** on Google Colab (notebooks in `colab/`; NVIDIA L4 for the
vision stages and the 1.5B model, A100 40 GB for the 7B model, CPU for the
statistics). All 135 reference values match run03 within the declared tolerances.
The lightweight evidence package of run03 (results, per-item tables, figures, logs,
and session environments) is in `results/run03/`.

| Group | Main computed values (run03) |
|---|---|
| Sampling (Sec. 3.2, Fig. 2) | n = 50,208; 3,489 strata; KS D = 0.035; χ² sex 41.3, pathologies 914.2 (sample is, by design, not representative) |
| Classification (Sec. 4.1, Fig. 3) | DenseNet-121 NIH micro F1 0.340 (0.335–0.345), AUROC 0.668; multi-source 0.334; ResNet-50 0.172 |
| Official NIH test split (Sec. 4.1) | DenseNet-121 NIH AUROC 0.672 (0.662–0.681), F1 0.281; 25,596 images |
| Cross-validation (Fig. 6) | patient-grouped 5-fold, F1 CV 1.2% |
| Explainability (Figs. 4, 8b) | pointing game: Grad-CAM 0.208, Grad-CAM++ 0.253, fused 0.161, fused Grad-CAM++ 0.215; FPR 0.854 / 0.767 / 0.490 / 0.501; 984 boxes, 726 patients |
| Robustness, fairness (Figs. 11, 12) | F1 loss 0.6 / 29.2 / 52.5% at 30 / 20 / 10 dB; Cohen's h ≤ 0.10 |
| Cross-dataset weights (Fig. 13) | PadChest, CheXpert, MIMIC-CXR weights on NIH: mean AUROC 0.617–0.648, 0.021–0.079 below the NIH weights |
| Reports (Fig. 9) | 100 reports, DeepSeek-R1-Distill-Qwen-1.5B (local); BLEU-4 0.018, ROUGE-L 0.061; 88.8% of input findings named; 11% with a finding absent from the input |
| Prompt ablation (Fig. 14) | 200 images; 7B: unsupported findings 25.5% (plain), 27.1% (CRISPE), 10.0% (CRISPE + SNOMED CT), Holm p < 1e-4; 1.5B: 13.5 / 14.5 / 11.0%, not significant |
| Time per image, NVIDIA L4 | classification 0.009 s, Grad-CAM 0.061 s, segmentation 0.100 s, LLM 32.5 s; total 32.6 s |

**Not reproducible with public data**, and therefore removed from the article:
human ratings (κ, ICC, the 150- and 100-report reviews, review time) and
SNOMED CT mapping accuracy. `resources/snomed_map.csv` maps the 14 findings and
the 14 segmented structures to SNOMED CT concepts checked against the
International Edition 2025-02-01 (tx.fhir.org); the prompt carries each finding
as a compositional expression with its most affected region.

**Code changes after run03.** Two files were edited after run03 finished, so
their hash differs from the one recorded in the run03 evidence: the legend of
Fig. 13 was moved above the axes (`ihras/figures.py`, drawing only), and the
reference values were updated to the final manuscript
(`ihras/reference_values.py`, comparison only). Neither change affects any
computed value.

### Earlier CPU reference run

`results/cpu_reference/` holds an earlier end-to-end run on a CPU-only
workstation. Its vision results agree with run03 to within about 1e-5; its
reports were generated with an earlier SNOMED CT map (three codes, no region in
the prompt), and its timing is for CPU. Its `COMPARISON.md` was produced against
the reference values of that time (`ARTICLE_2026_SUPERSEDED` keeps the report
and timing values that run03 replaced).

#### How the CPU reference outputs were produced

Reference machine: AMD Ryzen 7 PRO 5750GE (16 threads), CPU only, Python
3.11.9, PyTorch 2.12.0+cpu, torchvision 0.27, torchxrayvision 1.5.7,
transformers 5.22.2, scikit-learn 1.9.0, SciPy 1.17.1, NumPy 2.4.6.

```bash
python run_all.py --nih-dir <NIH> --threads 12 --workers 6 \n       --stages sampling,classify,explain,robustness,fairness,figures,compare
python run_all.py --nih-dir <NIH> --out outputs_report --stages report \
       --llm-backend local --llm-model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
       --llm-max-tokens 1024 --report-n 100 --threads 12
python analysis/merge_results.py        # copies report.* and time.llm into outputs/
python analysis/report_fidelity.py      # report dispersion and finding-mention rate
python analysis/paired_details.py       # McNemar counts, exact match, no-finding AUROC
python run_all.py --nih-dir <NIH> --stages figures,compare
```

The report stage was run alone, after the vision pipeline, so that its timing
is not inflated by CPU contention (two contended reports were discarded;
`reports_contended.jsonl`, not versioned). Generation takes about 3 min per
report on this CPU.

The commands above write to the working folders `outputs/` and
`outputs_report/`; the released copies are archived in `results/cpu_reference/`
and `results/cpu_reference_report/`. The shell helpers used to chain them on the
reference machine are in `scripts/cpu_reference/` (set `NIH_DIR` before use).

### Earlier metadata-only run (v2020 metadata)


Command: `python run_all.py --nih-dir <NIH> --stages sampling,figures,compare`.
Input: `Data_Entry_2017_v2020.csv`.

| Item | Reported | Computed |
|---|---|---|
| Sample size | 50,133 | 50,172 (ASSUMPTIONS.md, A1) |
| KS test of age | D = 0.023, p = 0.847 | D = 0.034, p = 2×10⁻³⁵ |
| χ² test of sex | 1.34, p = 0.247 | 40.4, p = 2×10⁻¹⁰ |
| χ² test of pathologies | 23.7, p = 0.052 | 909.8, p = 4×10⁻¹⁸⁶ |
| Fig. 2: Infiltration in the sample | 19,894 | 14,730. 19,894 is the full-dataset count. |

Capping strata at 370 images makes the sample, by construction, differ from
the population. The computed tests therefore reject representativeness.

**Specification sweep.** `analysis/specification_sweep.py` evaluates 400
readings of Sec. 3.2. The dimensions swept are:
* five strata definitions;
* two age binnings;
* two cap rules;
* ten seeds;
* population vs. complement as the reference.

Every specification is reported in `results/v2020_metadata_only/specification_sweep.csv`. None
reproduces n = 50,133 or a largest stratum of 9,677. None yields a KS p-value
above 0.05; the maximum is 4.6×10⁻²². None makes the three representativeness
tests non-significant simultaneously.

## Data

All files come from the NIH Clinical Center:
https://nihcc.app.box.com/v/ChestXray-NIHCC

* `images_001` … `images_012`: 112,120 PNG images, about 42 GB.
* `Data_Entry_2017.csv` (original) or `Data_Entry_2017_v2020.csv`.
* `BBox_List_2017.csv`, `train_val_list.txt`, `test_list.txt`.

Put all of them in one folder and pass it with `--nih-dir`. The model weights
(TorchXRayVision) download automatically on first use.

## Running

```bash
python -m pip install -r requirements.txt
python run_all.py --smoke-test                               # synthetic data, validates the pipeline
python run_all.py --nih-dir /data/NIH --stages all --device cuda
python run_all.py --nih-dir /data/NIH --stages report --llm-backend api   # needs DEEPSEEK_API_KEY
python run_all.py --nih-dir /data/NIH --stages human,compare --ratings-dir ratings/
python -m pytest tests -q
```

**Parallel jobs.** A long run can be split into jobs that write to separate
output folders (e.g. two Colab GPU sessions) and are merged afterwards. Jobs
must not share one folder: `results.json` is rewritten on every update.

```bash
# job 1: sample, then cache the predictions of one model
python run_all.py --nih-dir <NIH> --out jobs/a --stages sampling,predict --models densenet_nih
# job 2: copy jobs/a/sample_manifest.csv first, then other models
python run_all.py --nih-dir <NIH> --out jobs/b --stages predict --models densenet_multi,resnet50_multi --device cuda
# job 3: explainability on the GPU (independent of the sample)
python run_all.py --nih-dir <NIH> --out jobs/c --stages explain --device cuda
# merge (checks identical sample manifests and no conflicting keys), then the metrics
python analysis/merge_jobs.py --dst outputs_merged jobs/a jobs/b jobs/c
python run_all.py --nih-dir <NIH> --out outputs_merged --stages classify,figures,compare
```

The `predict` stage only computes and caches `predictions_<model>.npz`; a cache
is accepted only if it lists exactly the images of `sample_manifest.csv`.
`merge_provenance.json` records which job produced each key and file.

**New analyses** (run explicitly; they add keys with new prefixes and never
change the original ones, so `COMPARISON.md` is unaffected):

| Stage | Purpose | Main keys / files |
|---|---|---|
| `external` | cross-dataset validation: TorchXRayVision weights trained without NIH (PadChest, CheXpert, MIMIC-CXR) on the NIH sample, each on the findings it predicts, against DenseNet-121 (NIH) on the same findings | `ext.*` |
| `official` | the models in `--models` on the official NIH test split (`test_list.txt`); the split used to train the NIH weights is undocumented, so it is not a guaranteed leakage-free test | `split.*`, `official_test_manifest.csv` |
| `xai_stats` | patient-grouped bootstrap CIs of the explainability metrics and paired tests between methods (McNemar, Wilcoxon, Holm) | `xai.ci.*`, `xai.test.*` |
| `ablation` | prompt ablation of the reports (plain / CRISPE / CRISPE + SNOMED CT) for each LLM in `--ablation-models`, scored by `ihras/fidelity.py` (recall, hallucination, contradiction; negation-aware) | `ablation.*`, `ablation_per_report.csv` |
| `timing` | per-item processing time on the current hardware, measured alone and GPU-synchronized | `timing.*`, `timing_per_item.csv` |

`analysis/report_hallucination.py` applies the same fidelity rules to an
existing `reports.jsonl` (keys `report.fid.*`).

**Google Colab.** `colab/00_data_setup.ipynb` stores NIH ChestX-ray14 in Google
Drive with a provenance manifest (checksums). `colab/01_track_a.ipynb` (A100:
NIH predictions, reports, ablation) and `colab/02_track_b.ipynb` (L4:
explainability, other models, robustness, official split, timing) run in
parallel; `colab/03_merge.ipynb` merges the jobs, computes the cross-job
statistics, and packages the evidence.

**Stages.** The stages run in this order: `sampling` → `classify` → `explain`
→ `robustness` → `fairness` → `report` → `human` → `figures` → `compare`.

**Outputs** (in `outputs/`):
* `results.json` and `COMPARISON.md`;
* `sample_manifest.csv` and `predictions_*.npz`;
* `reports.jsonl`;
* `xai_per_box.csv`: explainability metrics per bounding box and method (input
  for bootstrap confidence intervals and paired tests);
* `figures/`.

**Reference hardware.** The released outputs were computed on CPU (see
"How the released outputs were produced"). The `classify` stage took about
50 min (DenseNet-121) to 6 h (ResNet-50 at 512 px) for 50,208 images; a GPU
shortens this substantially. Grad-CAM uses gradients, so CPU runs are slower.

**Determinism.** A global seed (42) is set for Python, NumPy, and PyTorch,
together with `torch.use_deterministic_algorithms(True, warn_only=True)`. Two
sources of non-determinism remain: some cuDNN kernels, and the LLM accessed
through the API.

## Files

```
run_all.py                 pipeline, stages, smoke test
ihras/config.py            parameters with their source in the article
ihras/reference_values.py  reported values (comparison only) and tolerances
ihras/data.py              metadata, Eq. (6), stratified sampling, official split
ihras/classify.py          TorchXRayVision models, metrics, AUROC, cross-validation
ihras/explain.py           Grad-CAM, Grad-CAM++, PSPNet anatomy, fusion Eqs. (1)-(4)
ihras/localization.py      localization metrics on the NIH bounding boxes
ihras/robustness.py        noise (SNR) and photometric perturbations
ihras/fairness.py          subgroups, chi-square, Cohen's h
ihras/report.py            SNOMED CT triples, CRISPE prompt, LLM, BLEU/ROUGE-L
ihras/stats.py             KS, chi-square, t, Wilcoxon, McNemar, ANOVA, bootstrap, Fleiss kappa, ICC
ihras/figures.py           figures from computed results
ihras/compare.py           computed vs. reported
ihras/fidelity.py          fidelity of reports to their input findings (negation-aware)
analysis/                  merge of parallel jobs (merge_jobs.py), merge of report outputs, report fidelity, paired-test details, specification sweep
resources/snomed_map.csv   SNOMED CT map of the 14 findings and 14 structures (verified codes)
resources/templates/       input formats for the human-rating analyses
colab/                     Google Colab notebooks, in execution order:
                           00_data_setup, 01_track_a, 02_track_b (parallel), 03_merge
scripts/cpu_reference/     shell helpers of the published CPU reference run
results/                   released outputs of the published runs (never overwritten):
  cpu_reference/           full pipeline on CPU: results.json, COMPARISON.md, figures, reports
  cpu_reference_report/    the LLM report stage, run alone (merged into cpu_reference)
  v2020_metadata_only/     earlier metadata-only run and the specification sweep
ASSUMPTIONS.md             every gap in the article and the decision taken
```

## License

MIT (`LICENSE`). NIH ChestX-ray14 and the TorchXRayVision weights are subject
to their own terms.
