#!/usr/bin/env bash
# After the LLM reports finish: merge their results and redo figures + comparison.
# Helper used for the published CPU reference run (see README, "How the released
# outputs were produced"); its outputs are archived in results/.
# Usage: NIH_DIR=/path/to/NIH bash scripts/cpu_reference/<script>.sh
cd "$(dirname "$0")/../.."                 # run from the package root
NIH_DIR="${NIH_DIR:?set NIH_DIR to the NIH ChestX-ray14 folder}"
until grep -q "exit=" report_run.log 2>/dev/null; do sleep 60; done
python -I -X utf8 analysis/merge_results.py
python -I -X utf8 run_all.py --nih-dir "$NIH_DIR" --stages figures,compare
echo "exit=$?"
