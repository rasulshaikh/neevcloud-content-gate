"""Unsourced numeric claim detection.

Hard requirement: no number ships without a source. Every quantitative
claim (multipliers, percentages, throughput, latency, prices) must sit
in a sentence carrying a source marker [S<n>] that resolves to the fact
store. In production this check also verifies the marker against the
fact-store record (claim text vs source value). The prototype enforces
the marker discipline, which is the part LLMs reliably violate.
"""

import re

from gate.checks import CheckResult

# Two claim shapes: (a) multiplier with comparative context ("2.7x higher"),
# (b) number + unit ("4.8 TB/s", "40%"). Bare hardware configs like
# "8x H100" are descriptors, not claims, and are excluded by (a).
NUMERIC_CLAIM = re.compile(
    r"\b\d+(?:\.\d+)?x\s+(?:higher|faster|lower|slower|more|less|cheaper|better)"
    r"|\b\d+(?:\.\d+)?\s*(?:%|TB/s|GB/s|ms|Gbps|MW|tokens/s|tok/s|TFLOPS|GW|crore|lakh)\b",
    re.IGNORECASE,
)
SOURCE_MARKER = re.compile(r"\[S\d+\]")


def _sentences(text: str):
    return re.split(r"(?<=[.!?])\s+", text)


def check_claims(post, config) -> CheckResult:
    cfg = config["claims"]
    unsourced = []
    for sent in _sentences(post.body):
        if NUMERIC_CLAIM.search(sent) and not SOURCE_MARKER.search(sent):
            unsourced.append(sent.strip()[:120])

    metrics = {"unsourced_numeric_claims": len(unsourced), "examples": unsourced[:3]}

    if len(unsourced) > cfg["max_unsourced_fail"]:
        return CheckResult(
            "claims",
            "FAIL",
            [f"{len(unsourced)} numeric claims without [S#] source markers"],
            metrics,
        )
    if len(unsourced) > 0:
        return CheckResult(
            "claims",
            "FLAG",
            [f"{len(unsourced)} numeric claim(s) need source markers before publish"],
            metrics,
        )
    return CheckResult("claims", "PASS", [], metrics)
