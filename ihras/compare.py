"""Compare COMPUTED results with the values REPORTED in the article.

Writes outputs/COMPARISON.md: for each reported item, the computed value, the
reported value, the declared tolerance, and the status MATCH, MISMATCH, or
NOT COMPUTED (e.g., image data or human ratings not available).
"""

import json
import os

from .reference_values import ARTICLE_2026, PRECURSOR_2025, tolerance_for


def compare(results):
    rows = []
    for key, ref in ARTICLE_2026.items():
        got = results.get(key)
        if got is None:
            status = "NOT COMPUTED"
        else:
            status = "MATCH" if abs(float(got) - float(ref)) <= tolerance_for(key) else "MISMATCH"
        rows.append(dict(item=key, reported=ref, computed=got, tolerance=tolerance_for(key),
                         status=status, precursor_2025=PRECURSOR_2025.get(key)))
    return rows


def write_report(rows, path):
    counts = {s: sum(r["status"] == s for r in rows) for s in ("MATCH", "MISMATCH", "NOT COMPUTED")}
    lines = ["# Computed vs. reported values", "",
             "MATCH %(MATCH)d | MISMATCH %(MISMATCH)d | NOT COMPUTED %(NOT COMPUTED)d" % counts, "",
             "| Item | Reported (2026) | Computed | Tolerance | Status | Precursor (2025) |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        comp = "---" if r["computed"] is None else ("%.4g" % r["computed"])
        pre = "" if r["precursor_2025"] is None else ("%.4g" % r["precursor_2025"])
        lines.append("| %s | %.4g | %s | %.3g | **%s** | %s |" % (
            r["item"], r["reported"], comp, r["tolerance"], r["status"], pre))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        f.write("\n".join(lines) + "\n")
    return counts


def main(results_path, out_path):
    with open(results_path, encoding="utf8") as f:
        results = json.load(f)
    counts = write_report(compare(results), out_path)
    print("comparison written to", out_path, counts)
