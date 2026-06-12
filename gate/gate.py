"""Quality gate orchestrator.

Runs every check against an incoming post, aggregates results into a
verdict: PASS, FLAG (route to human review) or FAIL (block, return to
generation with reasons).

Verdict logic:
  - any check returns FAIL  -> post FAILS
  - any check returns FLAG  -> post is FLAGGED for human review
  - all checks PASS         -> post PASSES (publish path, sampled review)
"""

from dataclasses import dataclass, field

from gate.corpus import Post, load_corpus
from gate.embeddings import CorpusIndex
from gate.checks.near_duplicate import check_near_duplicate
from gate.checks.cannibalisation import check_cannibalisation
from gate.checks.structure import check_structure
from gate.checks.readability import check_readability
from gate.checks.claims import check_claims
from gate.checks.confidentiality import check_confidentiality

SEVERITY_ORDER = {"PASS": 0, "FLAG": 1, "FAIL": 2}


@dataclass
class GateReport:
    slug: str
    verdict: str
    checks: list = field(default_factory=list)

    def to_dict(self):
        return {
            "slug": self.slug,
            "verdict": self.verdict,
            "checks": [c.to_dict() for c in self.checks],
        }


class QualityGate:
    def __init__(self, published_dir: str, config: dict):
        self.config = config
        self.published = load_corpus(published_dir)
        self.index = CorpusIndex(self.published)

    def evaluate(self, post: Post) -> GateReport:
        checks = [
            check_near_duplicate(post, self.index, self.config),
            check_cannibalisation(post, self.published, self.index, self.config),
            check_structure(post, self.config),
            check_readability(post, self.config),
            check_claims(post, self.config),
            check_confidentiality(post, self.config),
        ]
        verdict = max((c.status for c in checks), key=lambda s: SEVERITY_ORDER[s])
        return GateReport(slug=post.slug, verdict=verdict, checks=checks)

    def evaluate_batch(self, incoming_dir: str):
        batch = load_corpus(incoming_dir)
        return [self.evaluate(p) for p in batch]
