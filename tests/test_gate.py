"""Sanity checks: each verdict path fires on the sample corpus."""

import os
import yaml
import pytest

from gate.gate import QualityGate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def reports():
    with open(os.path.join(ROOT, "config.yaml")) as f:
        config = yaml.safe_load(f)
    gate = QualityGate(os.path.join(ROOT, "sample_corpus/published"), config)
    out = gate.evaluate_batch(os.path.join(ROOT, "sample_corpus/incoming"))
    return {r.slug: r for r in out}


def test_near_duplicate_fails(reports):
    r = reports["a100-vs-h100-llm-serving"]
    assert r.verdict == "FAIL"
    nd = next(c for c in r.checks if c.name == "near_duplicate")
    assert nd.status == "FAIL"


def test_confidentiality_leak_fails(reports):
    r = reports["why-gpu-cloud-india"]
    assert r.verdict == "FAIL"
    conf = next(c for c in r.checks if c.name == "confidentiality")
    assert conf.status == "FAIL"
    assert conf.metrics["hits"] >= 2


def test_clean_post_not_failed(reports):
    r = reports["h200-vs-h100-training"]
    assert r.verdict in ("PASS", "FLAG")
    conf = next(c for c in r.checks if c.name == "confidentiality")
    claims = next(c for c in r.checks if c.name == "claims")
    assert conf.status == "PASS"
    assert claims.status == "PASS"
