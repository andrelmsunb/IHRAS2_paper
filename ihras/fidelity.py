"""Fidelity of generated reports to the findings given to the LLM (new analysis, T25).

Lexical metrics (BLEU, ROUGE) against a synthetic reference say little about
whether a report is faithful.  This module checks, for every report, which of
the 14 NIH findings it *affirms* and compares them with the findings that were
given to the LLM as input:

  recall          share of input findings that the report affirms;
  hallucination   a finding affirmed by the report that was NOT in the input;
  contradiction   an input finding that the report only mentions as negated.

A finding is "affirmed" when one of its surface forms occurs in a sentence and
is not in the scope of a negation cue.  Hedged statements ("possible
pneumonia", "cannot be excluded") count as affirmed, because they still assert
the finding to the reader.  Negation handling follows the NegEx idea (Chapman
et al., J Biomed Inform 2001) in a deliberately small, documented form: a cue
before the term in the same sentence (with no contrastive word in between), or
a post-negation phrase right after it.  It is a transparent lexical check, not
a clinical judgement; its rules are tested in tests/test_pipeline.py.
"""

import re

import numpy as np

from .config import FINDINGS

# Surface forms of each NIH finding (lower-case regular expressions).
PATTERNS = {
    "Atelectasis": r"atelecta\w*",
    "Cardiomegaly": r"cardiomegal\w*|cardiac enlargement|enlarged (?:heart|cardiac silhouette)",
    "Consolidation": r"consolidat\w*",
    "Edema": r"o?edema\w*",
    "Effusion": r"effusions?",
    "Emphysema": r"emphysem\w*",
    "Fibrosis": r"fibros\w*|fibrotic",
    "Hernia": r"hernia\w*",
    "Infiltration": r"infiltrat\w*",
    # "mass" as a lesion, not anatomy ("left ventricular mass", "muscle/body/bone mass")
    "Mass": r"(?<!ventricular )(?<!muscle )(?<!body )(?<!bone )(?<!cardiac )mass(?:es)?\b",
    "Nodule": r"nodul\w*",
    "Pleural_Thickening": r"pleural thickening|thicken\w* (?:of )?(?:the )?pleura\w*",
    "Pneumonia": r"pneumoni\w*",
    "Pneumothorax": r"pneumothora\w*",
}
_FINDING_RE = {f: re.compile(r"\b(?:%s)" % PATTERNS[f]) for f in FINDINGS}

# Negation cue before the term (searched in the part of the sentence before it).
_PRE_NEG = re.compile(r"\b(?:no|not|without|negative for|absence of|absent|free of|"
                      r"rules? out|ruled out|no evidence of|no signs? of|resolution of|"
                      r"resolved)\b")
# Words that end the scope of a preceding negation ("no effusion, but atelectasis").
_CONTRAST = re.compile(r"\b(?:but|however|although|though|except|apart from|yet)\b")
# Post-negation right after the term ("pneumothorax is not seen").
_POST_NEG = re.compile(r"^\W*(?:is|are|was|were|has been|have been)?\s*(?:not (?:seen|identified|"
                       r"present|visualized|appreciated|demonstrated|evident)|absent|"
                       r"ruled out|resolved)\b")
# Hedges that must NOT be read as negation ("cannot be excluded" asserts a possibility).
_HEDGE = re.compile(r"cannot be (?:excluded|ruled out)|can ?not be (?:excluded|ruled out)")


def _sentences(text):
    """Lower-case sentences; also splits on semicolons and line breaks (report sections)."""
    return [s for s in re.split(r"[.;\n]+", text.lower()) if s.strip()]


def mentions(text):
    """Return (affirmed, negated): sets of NIH findings affirmed or negated in ``text``.

    A finding can be in both sets if the report affirms it in one sentence and
    negates it in another; callers treat it as affirmed."""
    affirmed, negated = set(), set()
    for sent in _sentences(text):
        for f, rx in _FINDING_RE.items():
            for m in rx.finditer(sent):
                before, after = sent[:m.start()], sent[m.end():]
                cue = None
                for cue in _PRE_NEG.finditer(before):
                    pass                                   # keep the last cue before the term
                neg = cue is not None and not _CONTRAST.search(before[cue.end():])
                if _POST_NEG.match(after) and not _HEDGE.search(after[:40]):
                    neg = True
                if _HEDGE.search(after[:40]):
                    neg = False                            # hedged: still asserted
                (negated if neg else affirmed).add(f)
    return affirmed, negated


def score_report(text, input_findings):
    """Per-report fidelity of ``text`` to the list of ``input_findings`` (NIH names)."""
    affirmed, negated = mentions(text)
    given = set(input_findings)
    hallucinated = affirmed - given
    contradicted = given & (negated - affirmed)
    return dict(
        n_input=len(given),
        recall=len(given & affirmed) / len(given) if given else np.nan,
        n_hallucinated=len(hallucinated),
        hallucination=bool(hallucinated),
        hallucinated="|".join(sorted(hallucinated)),
        contradiction=bool(contradicted),
        contradicted="|".join(sorted(contradicted)),
        words=len(text.split()),
    )


def findings_from_prompt(prompt):
    """Recover the input findings from a prompt built by report.build_prompt or
    report.build_plain_prompt ("Findings (probability): A (0.61); B (0.57).")."""
    m = re.search(r"Findings \(probability\): (.*?)\.(?:\s|$)", prompt)
    if not m or m.group(1).strip() == "none":
        return []
    names = [part.rsplit(" (", 1)[0].strip() for part in m.group(1).split(";")]
    return [n for n in names if n in FINDINGS]


def wilson_ci(k, n, z=1.96):
    """Wilson score interval for a proportion k/n (used for the report-level rates)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    return (float(c - h), float(c + h))
