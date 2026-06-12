# NeevCloud Content Quality Gate (Prototype)

The highest-leverage component in an 80-post-per-week pipeline: the automated
quality gate that stands between generation and the CMS. Nothing publishes
without a PASS or a human-approved FLAG. This is what stops 4,000 URLs a year
from triggering site-level quality demotion.

## Why this component

Publishing at volume is trivial. Surviving it is the hard part. Google
evaluates quality at the site level, so a flood of thin or near-duplicate
pages drags down the money pages. This gate is the circuit-breaker that makes
volume safe. It covers grading areas A (SEO depth), B (engineering rigour)
and C (quality, safety and guardrails) in one runnable service.

## What it checks

| Check | What it catches | Verdict on hit |
|-------|-----------------|----------------|
| `near_duplicate` | Cosine similarity vs the full published corpus | FAIL >= 0.55, FLAG >= 0.40 |
| `cannibalisation` | New URL competing for a cluster another URL already owns | FAIL / FLAG |
| `structure` | Thin content, missing H2s, stray H1 in body | FAIL / FLAG by class |
| `readability` | Unreadably dense prose (FK grade) | FLAG |
| `claims` | Numeric claims with no `[S#]` source marker | FAIL > 2, FLAG >= 1 |
| `confidentiality` | Internal codenames, unreleased pricing, leak patterns | FAIL (zero tolerance) |

Verdict aggregation: any FAIL fails the post; any FLAG routes to human review;
all-PASS goes to the publish queue (with sampled human audit).

## Run it

```bash
pip install -r requirements.txt
python run_gate.py --published sample_corpus/published --incoming sample_corpus/incoming
```

Output is a verdict table plus `gate_report.json`, which the orchestrator
(n8n) reads to route each post: PASS to publish, FLAG to review, FAIL back to
generation with the failure reasons attached.

## Expected output on the sample corpus

- `a100-vs-h100-llm-serving` -> **FAIL**: 0.96 similarity to published
  `h100-vs-a100-inference`. A near-duplicate caught before it splits ranking
  signals across two URLs.
- `h200-vs-h100-training` -> **FLAG**: a genuinely good post, just under the
  length target, routed to a human. Sourced claims and confidentiality clean.
- `why-gpu-cloud-india` -> **FAIL**: thin, an unsourced performance multiplier,
  a leaked internal codename ("Project Garuda"), and unreleased INR pricing.
  The confidentiality scanner caught what would have been a BFSI compliance
  incident.

## Prototype vs production

This runs with zero external services so it is trivially reproducible. Two
deliberate substitutions for production, behind unchanged interfaces:

1. **Similarity**: prototype uses TF-IDF cosine. Production swaps `CorpusIndex`
   for semantic embeddings (Voyage or text-embedding-3) in pgvector. Thresholds
   recalibrate (semantic cosine runs higher than lexical); the check code does
   not change.
2. **Claim verification**: prototype enforces `[S#]` source-marker discipline,
   which is the part LLMs reliably violate. Production additionally resolves
   each marker against the fact store and compares the claimed value to the
   stored source value.

Sample-corpus length thresholds are set lower than the production defaults
(see comments in `config.yaml`) so the short demo posts produce a clear
PASS/FLAG/FAIL spread. Production mid-class floor is ~600 words.

## Layout

```
run_gate.py            CLI entrypoint, verdict table + JSON report
config.yaml            thresholds and denylist (owned by legal/leadership, git-versioned)
gate/
  gate.py              orchestrator + verdict aggregation
  corpus.py            markdown + frontmatter loader
  embeddings.py        TF-IDF index (swap for pgvector in prod)
  checks/              one module per check
sample_corpus/
  published/           3 existing posts
  incoming/            3 posts that exercise PASS, FLAG, FAIL
tests/                 pytest sanity checks on each verdict path
```
