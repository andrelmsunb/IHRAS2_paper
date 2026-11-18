"""SNOMED CT mapping, CRISPE prompt, LLM report generation, lexical metrics.

Ref: Sec. 3.1 (Eq. (5), CRISPE, DeepSeek-R1) and Sec. 4.3.  The prompt
components are those published in the precursor (2025 Table 2).  The SNOMED CT
map ``resources/snomed_map.csv`` covers the 14 findings and the 14 segmented
structures; every code was checked against the SNOMED CT International Edition
2025-02-01 on the HL7 terminology server tx.fhir.org (ASSUMPTIONS.md, A11).
The prompt carries one compositional expression per finding, with the most
affected region as its finding site.
"""

import json
import os
import re
from collections import Counter
from math import exp, log

import pandas as pd

from .config import LLM_API_MODEL, LLM_LOCAL_MODEL, SNOMED_FINDING_SITE

CRISPE = {
    "Capacity": "You have deep knowledge of clinical report writing using SNOMED CT, "
                "based exclusively on the informed findings.",
    "Role": "Act as a board-certified clinical radiologist preparing an official diagnostic "
            "report, with accurate and clear communication of findings.",
    "Statement": "Write a radiological report using SNOMED CT with: Patient Metadata Section, "
                 "Findings Interpretation, Anatomical Localization.",
    "Personality": "Professional, concise clinical tone using complete sentences with standard "
                   "medical report structure.",
    "Experiment": "Provide a single report.",
}


def load_snomed_map(path):
    m = pd.read_csv(path, dtype=str).fillna("")
    return {r["term"]: r for _, r in m.iterrows()}


def snomed_triple(finding, region, smap):
    """Eq. (5): (c_ID, n_ID, r) with r = Finding Site."""
    c = smap.get(finding, {}).get("sctid", "")
    n = smap.get(region, {}).get("sctid", "") if region else ""
    return (c, n, SNOMED_FINDING_SITE)


def _concept(term, smap):
    """'<sctid> |<display>|' for a term of the map, or None if it has no code."""
    r = smap.get(term, {})
    if not r.get("sctid"):
        return None
    return "%s |%s|" % (r["sctid"], r.get("display") or term)


def snomed_expression(finding, region, smap):
    """The triple of Eq. (5) written as a SNOMED CT compositional-grammar
    expression with the concept names, so that the language model receives the
    meaning of each code, e.g.
    ``233604007 |Pneumonia (disorder)| : 363698007 |Finding site| = 3341006 |Right lung structure (body structure)|``.
    Without a coded region only the finding concept is written."""
    c = _concept(finding, smap) or finding
    n = _concept(region, smap) if region else None
    if n is None:
        return c
    return "%s : %s |Finding site| = %s" % (c, SNOMED_FINDING_SITE, n)


# CRISPE components without any reference to SNOMED CT (ablation arm "crispe").
CRISPE_NO_SNOMED = dict(
    CRISPE,
    Capacity="You have deep knowledge of clinical report writing, based exclusively on the "
             "informed findings.",
    Statement="Write a radiological report with: Patient Metadata Section, Findings "
              "Interpretation, Anatomical Localization.",
)


def _case_facts(case):
    """Patient metadata and findings sentence shared by every prompt variant."""
    return ("Patient: %s-year-old %s; view position: %s. Findings (probability): %s. "
            "Most affected region: %s."
            % (case["age"], {"M": "male", "F": "female"}.get(case["sex"], case["sex"]),
               case["view"],
               "; ".join("%s (%.2f)" % (f, p) for f, p in case["findings"]) or "none",
               case["region"] or "not applicable"))


def build_prompt(case, smap, include_snomed=True):
    """``case``: dict with age, sex, view, findings [(name, prob)], region.

    ``include_snomed=True`` is the IHRAS prompt used in the article (CRISPE plus
    SNOMED CT triples); ``False`` gives the CRISPE prompt with every SNOMED CT
    element removed (ablation arm "crispe")."""
    insight = _case_facts(case)
    if include_snomed:
        insight += " SNOMED CT concepts: %s." % ("; ".join(
            snomed_expression(f, case["region"], smap) for f, _ in case["findings"]) or "none")
    parts = dict(CRISPE if include_snomed else CRISPE_NO_SNOMED, Insight=insight)
    order = ("Capacity", "Role", "Insight", "Statement", "Personality", "Experiment")
    return "\n".join("%s: %s" % (k, parts[k]) for k in order)


def build_plain_prompt(case):
    """Minimal prompt with the same facts and no CRISPE structure (ablation arm "plain")."""
    return "Write a chest radiograph report. " + _case_facts(case)


def build_arm_prompt(case, smap, arm):
    """Prompt of one ablation arm: "plain", "crispe" or "crispe_snomed" (= IHRAS)."""
    if arm == "plain":
        return build_plain_prompt(case)
    if arm == "crispe":
        return build_prompt(case, smap, include_snomed=False)
    if arm == "crispe_snomed":
        return build_prompt(case, smap, include_snomed=True)
    raise ValueError(arm)


_LOCAL = {}


def _local_model(name, dtype="float32"):
    """Load a local causal LM once per process and dtype (CPU if no GPU).

    float32 is the setting of the published run; bfloat16 halves memory and is
    much faster on recent GPUs (its outputs can differ slightly)."""
    if (name, dtype) not in _LOCAL:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(name)
        tok.padding_side = "left"              # batched generation continues on the right
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        device = "cuda" if torch.cuda.is_available() else "cpu"
        lm = AutoModelForCausalLM.from_pretrained(name, torch_dtype=getattr(torch, dtype))
        _LOCAL[(name, dtype)] = (tok, lm.to(device).eval())
    return _LOCAL[(name, dtype)]


def generate(prompt, backend="api", model=None, max_tokens=1024):
    """backend 'api': DeepSeek API (OpenAI-compatible; key in DEEPSEEK_API_KEY).
    backend 'local': Hugging Face transformers, greedy decoding."""
    if backend == "api":
        import requests
        r = requests.post("https://api.deepseek.com/chat/completions", timeout=300,
                          headers={"Authorization": "Bearer " + os.environ["DEEPSEEK_API_KEY"]},
                          json={"model": model or LLM_API_MODEL, "max_tokens": max_tokens,
                                "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    if backend == "local":
        tok, lm = _local_model(model or LLM_LOCAL_MODEL)
        enc = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                      add_generation_prompt=True, return_tensors="pt",
                                      return_dict=True)
        ids = enc["input_ids"].to(lm.device)       # dict return is stable across versions
        out = lm.generate(ids, attention_mask=enc["attention_mask"].to(lm.device),
                          max_new_tokens=max_tokens, do_sample=False,
                          pad_token_id=tok.eos_token_id)
        return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
    if backend == "echo":                      # offline smoke test only
        return "Findings Interpretation: " + prompt.split("Findings (probability): ")[1].split(".")[0]
    raise ValueError(backend)


def generate_batch(prompts, backend="local", model=None, max_tokens=1024, batch_size=8,
                   dtype="float32"):
    """Generate one completion per prompt.  Returns (texts, seconds_per_prompt).

    With the local backend, prompts are left-padded and decoded greedily in
    batches, which multiplies GPU throughput.  Greedy decoding is deterministic,
    but padding can change floating-point sums, so a batched output may differ
    slightly from the unbatched one; every ablation arm uses the same method.
    Seconds per prompt are the batch time divided by the batch size and must not
    be used as latency (the timing stage measures unbatched generation)."""
    import time
    if backend != "local":
        texts, secs = [], []
        for p in prompts:
            t0 = time.time()
            texts.append(generate(p, backend, model=model, max_tokens=max_tokens))
            secs.append(time.time() - t0)
        return texts, secs
    tok, lm = _local_model(model or LLM_LOCAL_MODEL, dtype)
    texts, secs = [], []
    for i in range(0, len(prompts), batch_size):
        chunk = prompts[i:i + batch_size]
        t0 = time.time()
        enc = tok.apply_chat_template([[{"role": "user", "content": p}] for p in chunk],
                                      add_generation_prompt=True, return_tensors="pt",
                                      return_dict=True, padding=True)
        ids = enc["input_ids"].to(lm.device)
        out = lm.generate(ids, attention_mask=enc["attention_mask"].to(lm.device),
                          max_new_tokens=max_tokens, do_sample=False,
                          pad_token_id=tok.pad_token_id)
        texts += tok.batch_decode(out[:, ids.shape[1]:], skip_special_tokens=True)
        secs += [(time.time() - t0) / len(chunk)] * len(chunk)
    return texts, secs


def strip_reasoning(text):
    """DeepSeek-R1 emits <think>...</think>; keep the final report only.  The
    distilled models omit the opening tag, so everything up to the closing tag
    is removed.  Returns '' if generation stopped inside the reasoning."""
    if "</think>" in text:
        return text.split("</think>", 1)[1].strip()
    if "<think>" in text:
        return ""
    return text.strip()


def rule_based_reference(case):
    """Synthetic reference used for lexical metrics (Sec. 4.3)."""
    if not case["findings"]:
        return "No acute cardiopulmonary abnormality is identified."
    names = ", ".join(f.replace("_", " ").lower() for f, _ in case["findings"])
    loc = " in the %s" % case["region"].lower() if case["region"] else ""
    return "Findings consistent with %s%s." % (names, loc)


# ---------------------------------------------------------- lexical metrics
def _tokens(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def bleu4(candidate, reference):
    c, r = _tokens(candidate), _tokens(reference)
    if not c:
        return 0.0
    logs = []
    for n in range(1, 5):
        cn = Counter(tuple(c[i:i + n]) for i in range(len(c) - n + 1))
        rn = Counter(tuple(r[i:i + n]) for i in range(len(r) - n + 1))
        match = sum(min(v, rn[k]) for k, v in cn.items())
        total = max(sum(cn.values()), 1)
        logs.append(log((match + 1) / (total + 1)))          # add-one smoothing
    bp = 1.0 if len(c) > len(r) else exp(1 - len(r) / len(c))
    return float(bp * exp(sum(logs) / 4))


def rouge_l(candidate, reference):
    c, r = _tokens(candidate), _tokens(reference)
    if not c or not r:
        return 0.0
    dp = [[0] * (len(r) + 1) for _ in range(len(c) + 1)]
    for i in range(len(c)):
        for j in range(len(r)):
            dp[i + 1][j + 1] = dp[i][j] + 1 if c[i] == r[j] else max(dp[i][j + 1], dp[i + 1][j])
    lcs = dp[-1][-1]
    p, rec = lcs / len(c), lcs / len(r)
    return float(2 * p * rec / (p + rec)) if lcs else 0.0


def save_jsonl(rows, path):
    with open(path, "w", encoding="utf8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
