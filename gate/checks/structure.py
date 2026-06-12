"""Structural lint: the cheap, deterministic floor.

Catches thin content and malformed documents before any expensive
check runs. Thresholds vary by content class: a programmatic spec page
is legitimately shorter than an editorial pillar.
"""

import re

from gate.checks import CheckResult


def check_structure(post, config) -> CheckResult:
    cfg = config["structure"][post.content_class]
    reasons, status = [], "PASS"

    wc = post.word_count
    h1s = re.findall(r"^# (?!#)", post.body, re.MULTILINE)
    h2s = re.findall(r"^## (?!#)", post.body, re.MULTILINE)
    links = re.findall(r"\[[^\]]+\]\([^)]+\)", post.body)

    metrics = {
        "word_count": wc,
        "h2_count": len(h2s),
        "link_count": len(links),
    }

    if wc < cfg["min_words_fail"]:
        status = "FAIL"
        reasons.append(f"{wc} words is below hard floor {cfg['min_words_fail']}")
    elif wc < cfg["min_words_flag"]:
        status = "FLAG"
        reasons.append(f"{wc} words is below target {cfg['min_words_flag']}")

    if len(h1s) > 0:
        status = "FAIL"
        reasons.append("body contains an H1; title is the only H1, rendered by template")

    if len(h2s) < cfg["min_h2"]:
        status = max(status, "FLAG", key=lambda s: {"PASS": 0, "FLAG": 1, "FAIL": 2}[s])
        reasons.append(f"only {len(h2s)} H2 sections, expected >= {cfg['min_h2']}")

    return CheckResult("structure", status, reasons, metrics)
