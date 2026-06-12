from dataclasses import dataclass, field


@dataclass
class CheckResult:
    name: str
    status: str  # PASS | FLAG | FAIL
    reasons: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "check": self.name,
            "status": self.status,
            "reasons": self.reasons,
            "metrics": self.metrics,
        }
