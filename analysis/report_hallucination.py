"""Fidelity of existing LLM reports to their input findings (new analysis, T25).

Scores every report of a reports.jsonl written by the 'report' stage with the
negation-aware rules of ihras/fidelity.py (input findings are recovered from
the stored prompt) and adds to <out>/results.json:

  report.fid.n_complete              reports with a final answer
  report.fid.recall                  mean share of input findings affirmed
  report.fid.hallucination_rate      share of reports affirming a finding not given
  report.fid.hallucination_rate_ci   Wilson 95% CI
  report.fid.hallucinated_per_report mean number of such findings
  report.fid.contradiction_rate      share negating an input finding
  report.fid.top_hallucinated        most frequent hallucinated findings

and writes <out>/report_fidelity_per_report.csv.  The existing key
report.finding_mention_recall (report_fidelity.py, prefix match without
negation) is left untouched.

Usage:  python analysis/report_hallucination.py --out outputs
"""

import argparse
import collections
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ihras import fidelity   # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "outputs"))
    a = ap.parse_args(argv)
    with open(os.path.join(a.out, "reports.jsonl"), encoding="utf8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    table = []
    for r in rows:
        given = fidelity.findings_from_prompt(r["prompt"])
        sc = fidelity.score_report(r["report"], given) if r.get("complete", bool(r["report"])) else {}
        table.append(dict(image=r["image"], complete=bool(sc), input_findings="|".join(given), **sc))
    t = pd.DataFrame(table)
    t.to_csv(os.path.join(a.out, "report_fidelity_per_report.csv"), index=False)
    c = t[t["complete"]]
    nh = int(c["hallucination"].sum())
    top = collections.Counter(f for s in c["hallucinated"] if s for f in s.split("|"))
    res = {"report.fid.n_complete": len(c),
           "report.fid.recall": float(c["recall"].mean()),
           "report.fid.n_with_findings": int(c["recall"].notna().sum()),
           "report.fid.hallucination_rate": nh / len(c),
           "report.fid.hallucination_rate_ci": fidelity.wilson_ci(nh, len(c)),
           "report.fid.hallucinated_per_report": float(c["n_hallucinated"].mean()),
           "report.fid.contradiction_rate": float(c["contradiction"].mean()),
           "report.fid.top_hallucinated": dict(top.most_common(5))}
    path = os.path.join(a.out, "results.json")
    R = json.load(open(path, encoding="utf8")) if os.path.exists(path) else {}
    R.update(res)
    with open(path, "w", encoding="utf8") as f:
        json.dump(R, f, indent=1)
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main()
