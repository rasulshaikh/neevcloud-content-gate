"""Keyword cannibalisation detection.

Each URL owns exactly one keyword cluster. A new post must claim an
unclaimed cluster. If its cluster is already owned AND its content
overlaps the owner, the system forces a consolidate/differentiate
decision instead of silently shipping a competing URL.
"""

from gate.checks import CheckResult


def check_cannibalisation(post, published, index, config) -> CheckResult:
    cfg = config["cannibalisation"]
    owners = [p for p in published if p.cluster_id == post.cluster_id and p.slug != post.slug]
    metrics = {"cluster_id": post.cluster_id, "existing_owners": [p.slug for p in owners]}
    if not owners:
        return CheckResult("cannibalisation", "PASS", [], metrics)

    sims = {p.slug: s for p, s in index.similarities(post)}
    worst = max(owners, key=lambda p: sims.get(p.slug, 0))
    overlap = sims.get(worst.slug, 0)
    metrics["owner_similarity"] = round(overlap, 3)

    if overlap >= cfg["fail_threshold"]:
        return CheckResult(
            "cannibalisation",
            "FAIL",
            [
                f"cluster '{post.cluster_id}' already owned by '{worst.slug}' "
                f"with content overlap {overlap:.2f}: consolidate, do not publish"
            ],
            metrics,
        )
    return CheckResult(
        "cannibalisation",
        "FLAG",
        [
            f"cluster '{post.cluster_id}' already owned by '{worst.slug}': "
            "confirm intent differs or merge"
        ],
        metrics,
    )
