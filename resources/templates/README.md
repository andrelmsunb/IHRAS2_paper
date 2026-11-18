# Input formats for the human-rating analyses

Place the filled files in one folder and run
`python run_all.py --nih-dir <NIH> --stages human,compare --ratings-dir <folder>`.

| File | Format | Computes |
|---|---|---|
| `heatmap_relevance.csv` | rows = heatmaps; first column = heatmap id; one column per radiologist; 1 = clinically relevant, 0 = not | Fleiss' κ; share judged relevant |
| `confidence_scores.csv` | rows = heatmaps; one column per radiologist; numeric confidence | ICC(2,1) |
| `review_times.csv` | columns `case_id, manual_s, ihras_s` (seconds per case) | % reduction; paired *t* and Wilcoxon *p* |

Example `heatmap_relevance.csv`:

```
heatmap_id,R1,R2,R3,R4,R5
00000003_000_Hernia,1,1,1,0,1
```
