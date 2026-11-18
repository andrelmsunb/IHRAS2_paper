"""Merge the output folders of independent pipeline jobs into one folder.

A long run can be split into jobs that execute in parallel (for example two
Colab GPU sessions), each writing to its own output folder.  The jobs cannot
share one results.json: run_all.Store rewrites the whole file on every update,
so concurrent writers would silently drop each other's keys.  This script
combines the folders afterwards and refuses to merge inconsistent inputs:

* every job that has a sample_manifest.csv must have the same one (SHA-256);
* a key computed by more than one job must have exactly the same value;
* an artifact file present in more than one job must be byte-identical.

Artifacts (cached predictions ``*.npz``, reports ``*.jsonl``, per-item tables
``*.csv``) are copied next to the merged results.json.  The file
merge_provenance.json records which job produced each key and each artifact,
with checksums.  Nothing is recomputed or edited.

Usage:
    python analysis/merge_jobs.py --dst outputs_merged jobs/sampling jobs/explain ...

Then compute the metrics that need several jobs (e.g. paired tests across
models) on the merged folder:
    python run_all.py --nih-dir <NIH> --out outputs_merged --stages classify,figures,compare
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import shutil
import sys

ARTIFACT_SUFFIXES = (".npz", ".jsonl", ".csv")
# Files that are produced per folder and must never be copied between folders.
NOT_ARTIFACTS = {"results.json", "COMPARISON.md", "merge_provenance.json"}


def sha256(path, chunk=1 << 22):
    """SHA-256 of a file, read in 4 MB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def same_value(a, b):
    """Exact equality of two JSON values; NaN equals NaN (it marks 'not defined')."""
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def merge(dst, jobs):
    """Merge ``jobs`` (folders) into ``dst``.  Returns the provenance record.

    Raises SystemExit with a readable message on any inconsistency, before
    anything is written to ``dst``."""
    for j in jobs:
        if not os.path.isdir(j):
            raise SystemExit("job folder not found: %s" % j)

    # 1. All jobs must have worked on the same sample.
    manifests = {j: sha256(os.path.join(j, "sample_manifest.csv")) for j in jobs
                 if os.path.exists(os.path.join(j, "sample_manifest.csv"))}
    if len(set(manifests.values())) > 1:
        lines = "\n".join("  %s  %s" % (h[:16], j) for j, h in manifests.items())
        raise SystemExit("jobs used different sample manifests:\n" + lines)

    # 2. Union of the result keys; a key may come from several jobs only if equal.
    merged, origin, conflicts = {}, {}, []
    dst_results = os.path.join(dst, "results.json")
    if os.path.exists(dst_results):           # merging again into an existing folder
        with open(dst_results, encoding="utf8") as f:
            merged = json.load(f)
        origin = {k: "<existing %s>" % dst for k in merged}
    for j in jobs:
        path = os.path.join(j, "results.json")
        if not os.path.exists(path):           # a job may produce artifacts only
            continue
        with open(path, encoding="utf8") as f:
            for k, v in json.load(f).items():
                if k not in merged:
                    merged[k], origin[k] = v, j
                elif not same_value(merged[k], v):
                    conflicts.append((k, origin[k], merged[k], j, v))
    if conflicts:
        lines = "\n".join("  %s: %r (%s) vs %r (%s)" % (k, va, ja, vb, jb)
                          for k, ja, va, jb, vb in conflicts)
        raise SystemExit("%d conflicting key(s); nothing was written:\n%s"
                         % (len(conflicts), lines))

    # 3. Artifacts: identical copies are allowed, different contents are not.
    artifacts = {}
    for j in jobs:
        for fn in sorted(os.listdir(j)):
            path = os.path.join(j, fn)
            if fn in NOT_ARTIFACTS or not fn.endswith(ARTIFACT_SUFFIXES) or not os.path.isfile(path):
                continue
            h = sha256(path)
            if fn in artifacts and artifacts[fn]["sha256"] != h:
                raise SystemExit("%s differs between %s and %s; nothing was written"
                                 % (fn, artifacts[fn]["job"], j))
            artifacts.setdefault(fn, {"job": j, "sha256": h, "bytes": os.path.getsize(path)})

    # 4. Everything is consistent: write.
    os.makedirs(dst, exist_ok=True)
    for fn, rec in artifacts.items():
        src = os.path.join(rec["job"], fn)
        if os.path.abspath(src) != os.path.abspath(os.path.join(dst, fn)):
            shutil.copy2(src, os.path.join(dst, fn))
    with open(dst_results, "w", encoding="utf8") as f:
        json.dump(merged, f, indent=1)
    provenance = {
        "merged_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "jobs": list(jobs),
        "sample_manifest_sha256": next(iter(manifests.values()), None),
        "keys": origin,
        "artifacts": artifacts,
    }
    with open(os.path.join(dst, "merge_provenance.json"), "w", encoding="utf8") as f:
        json.dump(provenance, f, indent=1)
    return provenance


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dst", required=True, help="merged output folder")
    ap.add_argument("jobs", nargs="+", help="job output folders, in any order")
    a = ap.parse_args(argv)
    prov = merge(a.dst, a.jobs)
    print("merged %d keys and %d artifacts from %d jobs into %s"
          % (len(prov["keys"]), len(prov["artifacts"]), len(a.jobs), a.dst))


if __name__ == "__main__":
    sys.exit(main())
