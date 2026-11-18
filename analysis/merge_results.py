"""Merge results computed in a separate output folder into outputs/results.json.

The LLM report stage was run in ``outputs_report/`` so that it did not write to
``outputs/results.json`` concurrently with the main pipeline.  This script
copies the report keys (``report.*``, ``time.llm``) and ``reports.jsonl`` into
``outputs/``; nothing is recomputed or edited.

Usage:  python analysis/merge_results.py [--src outputs_report] [--dst outputs]
"""

import argparse
import json
import os
import shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIXES = ("report.", "time.llm")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(HERE, "outputs_report"))
    ap.add_argument("--dst", default=os.path.join(HERE, "outputs"))
    a = ap.parse_args()
    with open(os.path.join(a.src, "results.json"), encoding="utf8") as f:
        src = json.load(f)
    path = os.path.join(a.dst, "results.json")
    with open(path, encoding="utf8") as f:
        dst = json.load(f)
    moved = {k: v for k, v in src.items() if k.startswith(PREFIXES)}
    dst.update(moved)
    with open(path, "w", encoding="utf8") as f:
        json.dump(dst, f, indent=1)
    rep = os.path.join(a.src, "reports.jsonl")
    if os.path.exists(rep):
        shutil.copy(rep, os.path.join(a.dst, "reports.jsonl"))
    print("merged %d keys: %s" % (len(moved), ", ".join(sorted(moved))))


if __name__ == "__main__":
    main()
