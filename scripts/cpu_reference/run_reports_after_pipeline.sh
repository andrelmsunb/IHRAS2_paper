#!/usr/bin/env bash
# Generate the LLM reports only after the main pipeline has finished, so that
# the CPU is not shared and the per-report timing (Fig. 10) is not distorted.
# Helper used for the published CPU reference run (see README, "How the released
# outputs were produced"); its outputs are archived in results/.
# Usage: NIH_DIR=/path/to/NIH bash scripts/cpu_reference/<script>.sh
cd "$(dirname "$0")/../.."                 # run from the package root
NIH_DIR="${NIH_DIR:?set NIH_DIR to the NIH ChestX-ray14 folder}"
until grep -q "exit=" pipeline_run.log 2>/dev/null; do sleep 60; done
python -I -X utf8 run_all.py --nih-dir "$NIH_DIR" \
  --out outputs_report --stages report --llm-backend local \
  --llm-model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --llm-max-tokens 1024 \
  --report-n 100 --threads 12
echo "exit=$?"
