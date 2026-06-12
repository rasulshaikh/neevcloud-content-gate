"""Near-duplicate detection against the published corpus.

At 4,000+ URLs a year, near-duplicates are the fastest route to
'Crawled - currently not indexed' and site-level thin-content signals.
Every incoming post is compared against the full corpus before publish.
"""

from gate.checks import CheckResult


def check_near_duplicate(post, index, config) -> CheckResult:
    cfg = config["near_duplicate"]
    sims = index.similarities(post)
    top = sims[: cfg.get("top_k", 3)]
    metrics = {
        "top_matches": [
            {"slug": p.slug, "similarity": round(s, 3)} for p, s in top
        ]
    }
    if not top:
        return CheckResult("near_duplicate", "PASS", [], metrics)

    best_post, best_sim = top[0]
    if best_sim >= cfg["fail_threshold"]:
        return CheckResult(
            "near_duplicate",
            "FAIL",
            [
                f"similarity {best_sim:.2f} to published '{best_post.slug}' "
                f"exceeds fail threshold {cfg['fail_threshold']}"
            ],
            metrics,
        )
    if best_sim >= cfg["flag_threshold"]:
        return CheckResult(
            "near_duplicate",
            "FLAG",
            [
                f"similarity {best_sim:.2f} to '{best_post.slug}': "
                "human decides differentiate vs consolidate"
            ],
            metrics,
        )
    return CheckResult("near_duplicate", "PASS", [], metrics)
