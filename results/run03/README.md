# run03: final run reported in the article

This folder holds the lightweight evidence package of **run03**, the run whose values are printed in the manuscript. It was produced by `colab/03_merge.ipynb` as `evidence_light_run03.zip`. The full package, with the large files, is archived separately. The large files are listed with their SHA-256 checksums in `LARGE_FILES.sha256`.

## Contents

| File or folder | Content |
|---|---|
| `results.json` | Every computed value (classification, AUROC, cross-validation, tests, explainability, robustness, fairness, official split `split.*`, cross-dataset `ext.*`, reports `report.*`, prompt ablation `ablation.*`, timing `timing.*`) |
| `COMPARISON.md` | Computed values against the values printed in the article |
| `DIFF_vs_cpu_run.md` | run03 against the earlier CPU reference run (`results/cpu_reference/`) |
| `RUN_INFO.json` | Jobs, sessions, GPUs, code hash, data checksums, and comparison counts |
| `merge_provenance.json`, `DATA_MANIFEST.json` | Provenance of the merged job folders and checksums of the NIH metadata |
| `tables/` | Per-item tables: `ablation_per_report.csv`, `report_fidelity_per_report.csv`, `xai_per_box.csv`, `timing_per_item.csv` |
| `figures/` | Figures generated from `results.json` |
| `logs/` | Log and `.done` marker of every job |
| `env/` | Package versions and code checksums of every Colab session |

## Execution

| Track | Hardware | Jobs |
|---|---|---|
| A | NVIDIA L4 (sampling, NIH predictions, 100 reports, 1.5B ablation); NVIDIA A100 40 GB (7B ablation) | A_tests, A0–A3 |
| B | NVIDIA L4 | B_tests, B0–B5 |
| M | CPU only | M1–M6 |

**Library versions:** torch 2.14.1, numpy 2.4.6, scikit-learn 1.9.0, scipy 1.17.1, transformers 5.22.1, torchxrayvision 1.5.7.

**Code hash:** all 18 jobs ran the same pipeline code, hash `693002c2455aef2d` (51 files).

**Track A sessions:** track A was resumed twice within the same run. The first resume followed a transient Google Drive error. The second followed an out-of-memory error when loading the 7B model in float32 on the L4. Finished jobs are skipped on resume, and the ablation checkpoint resumes per model and arm.

## Comparison with the article

`COMPARISON.md` reports **79 MATCH and 12 MISMATCH** against the reference values in use at the time of the run. All 12 mismatches are explained:
- 3 are processing times, which depend on the hardware;
- 3 are report metrics that changed because the run03 prompt carries the SNOMED CT expressions with the most affected region;
- 6 are test statistics affected by GPU/CPU numerical differences of about 1e-5 in the predicted probabilities. These change 1 to 3 McNemar discordant pairs and the ANOVA F by less than 2%; every p-value stays below 1e-12.

`ihras/reference_values.py` was later updated to the final manuscript. All 135 reference values now match this `results.json` within the declared tolerances.

## Code changes after run03

After run03, the files below were edited or added outside `colab/`. None of these changes alters a computed value:
- `ihras/figures.py`: the legend of Fig. 13 was moved above the axes;
- `ihras/reference_values.py`: the reference values were updated to the final manuscript;
- `CITATION.cff`: the final authors and ORCIDs were added;
- `README.md`;
- `results/run03/` (this folder) was added.

The pipeline code hash of this repository therefore differs from the run03 hash (`693002c2455aef2d`); it is computed over the same files and in the same way as in the notebooks.
