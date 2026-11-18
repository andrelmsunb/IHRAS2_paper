"""Descriptive statistics of the generated reports (Sec. 4.3).

Adds to outputs/results.json:
  report.bleu4_sd, report.rouge_l_sd      dispersion of the lexical metrics
  report.time_sd                          SD of generation time per report (s)
  report.n_with_findings                  reports whose input had >= 1 finding
  report.finding_mention_recall           mean fraction of input findings named
  report.all_findings_mentioned           reports naming every input finding
  report.words_mean                       mean report length (words)

A finding counts as "named" when the first six letters of its first word occur
in the report (case-insensitive), e.g. "infilt" for Infiltration.  This is a
lexical check of fidelity to the input, not a clinical judgement.

Run:  python -I analysis/report_fidelity.py [outputs]
"""
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ihras.report import bleu4, rouge_l  # noqa: E402


def main(out="outputs"):
    root = os.path.join(os.path.dirname(HERE), out)
    rows = [json.loads(l) for l in open(os.path.join(root, "reports.jsonl"), encoding="utf8")]
    b = [bleu4(x["report"], x["reference"]) for x in rows]
    r = [rouge_l(x["report"], x["reference"]) for x in rows]
    cov, all_named = [], 0
    for x in rows:
        ref = x["reference"]
        if ref.startswith("No acute"):
            continue
        names = [n.strip() for n in ref.replace("Findings consistent with ", "")
                 .split(" in the ")[0].rstrip(".").split(",")]
        text = x["report"].lower()
        hit = [n for n in names if n.split()[0][:6] in text]
        cov.append(len(hit) / len(names))
        all_named += len(hit) == len(names)
    res_path = os.path.join(root, "results.json")
    res = json.load(open(res_path, encoding="utf8"))
    res.update({
        "report.bleu4_sd": st.stdev(b), "report.rouge_l_sd": st.stdev(r),
        "report.time_sd": st.stdev([x["seconds"] for x in rows]),
        "report.n_with_findings": len(cov),
        "report.finding_mention_recall": st.mean(cov),
        "report.all_findings_mentioned": all_named,
        "report.words_mean": st.mean(len(x["report"].split()) for x in rows),
    })
    json.dump(res, open(res_path, "w", encoding="utf8"), indent=1, sort_keys=True)
    for k in sorted(res):
        if k.startswith("report."):
            print(k, res[k])


if __name__ == "__main__":
    main(*sys.argv[1:])
