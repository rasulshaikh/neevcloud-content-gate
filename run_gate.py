#!/usr/bin/env python3
"""CLI entrypoint.

Usage:
    python run_gate.py --published sample_corpus/published --incoming sample_corpus/incoming

Evaluates every post in --incoming against the corpus in --published and
prints a verdict table plus a JSON report (gate_report.json) that the
orchestrator (n8n) consumes to route posts: PASS -> publish queue,
FLAG -> human review queue, FAIL -> back to generation with reasons.
"""

import argparse
import json

import yaml

from gate.gate import QualityGate

STATUS_ICON = {"PASS": "PASS", "FLAG": "FLAG", "FAIL": "FAIL"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--published", required=True)
    ap.add_argument("--incoming", required=True)
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--out", default="gate_report.json")
    args = ap.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    gate = QualityGate(args.published, config)
    reports = gate.evaluate_batch(args.incoming)

    print(f"\n{'POST':<42} {'VERDICT':<8} REASONS")
    print("-" * 110)
    for r in reports:
        reasons = [reason for c in r.checks for reason in c.reasons]
        first = reasons[0] if reasons else "all checks passed"
        print(f"{r.slug:<42} {STATUS_ICON[r.verdict]:<8} {first}")
        for extra in reasons[1:]:
            print(f"{'':<51} {extra}")

    with open(args.out, "w") as f:
        json.dump([r.to_dict() for r in reports], f, indent=2)
    print(f"\nFull report written to {args.out}")

    counts = {}
    for r in reports:
        counts[r.verdict] = counts.get(r.verdict, 0) + 1
    print("Summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
