"""Readability scoring. Reported, lightly enforced.

The audience is senior and technical, so we do not chase low grade
levels. We flag the extremes: unreadably dense (grade > max) or
suspiciously simplistic for a technical pillar.
"""

import textstat

from gate.checks import CheckResult


def check_readability(post, config) -> CheckResult:
    cfg = config["readability"]
    grade = textstat.flesch_kincaid_grade(post.body)
    ease = textstat.flesch_reading_ease(post.body)
    metrics = {"fk_grade": round(grade, 1), "flesch_ease": round(ease, 1)}

    if grade > cfg["max_grade"]:
        return CheckResult(
            "readability",
            "FLAG",
            [f"FK grade {grade:.1f} above {cfg['max_grade']}: simplify sentence structure"],
            metrics,
        )
    return CheckResult("readability", "PASS", [], metrics)
