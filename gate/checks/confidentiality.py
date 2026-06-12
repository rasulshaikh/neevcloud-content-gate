"""Confidentiality and compliance scanner.

NeevCloud sells to government and BFSI. A leaked internal codename,
unreleased price, or customer name in a public post is a business
incident, not a typo. Denylist terms and patterns hard-fail with zero
tolerance. The denylist lives in config, owned by legal/leadership,
versioned in git.
"""

import re

from gate.checks import CheckResult


def check_confidentiality(post, config) -> CheckResult:
    cfg = config["confidentiality"]
    hits = []
    text = post.body + "\n" + post.title

    for term in cfg["denylist_terms"]:
        if re.search(re.escape(term), text, re.IGNORECASE):
            hits.append(f"denylist term: '{term}'")

    for pattern in cfg["denylist_patterns"]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            hits.append(f"pattern match: '{m.group(0)}'")

    metrics = {"hits": len(hits)}
    if hits:
        return CheckResult("confidentiality", "FAIL", hits, metrics)
    return CheckResult("confidentiality", "PASS", [], metrics)
