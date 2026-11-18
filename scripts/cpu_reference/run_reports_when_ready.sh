#!/usr/bin/env bash
# Wait for the DenseNet-NIH predictions, then generate the LLM reports in a
# separate output folder (merged into outputs/results.json afterwards).
# Helper used for the published CPU reference run (see README, "How the released
# outputs were produced"); its outputs are archived in results/.
# Usage: NIH_DIR=/path/to/NIH bash scripts/cpu_reference/<script>.sh
cd "$(dirname "$0")/../.."                 # run from the package root
NIH_DIR="${NIH_DIR:?set NIH_DIR to the NIH ChestX-ray14 folder}"
until [ -f outputs/predictions_densenet_nih.npz ]; do sleep 60; done
sleep 30                                   # let the file finish writing
mkdir -p outputs_report
cp outputs/sample_manifest.csv outputs/predictions_densenet_nih.npz outputs_report/
python -I -X utf8 run_all.py --nih-dir "$NIH_DIR" \
  --out outputs_report --stages report --llm-backend local \
  --llm-model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --llm-max-tokens 1024 \
  --report-n 100 --threads 4
echo "exit=$?"
