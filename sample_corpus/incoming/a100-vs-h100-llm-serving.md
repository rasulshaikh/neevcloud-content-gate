---
slug: a100-vs-h100-llm-serving
title: "A100 vs H100 for LLM Serving: Throughput, Cost and Which One Wins"
primary_keyword: "a100 vs h100 llm serving"
cluster_id: gpu-compare-h100-a100-serving
content_class: mid
---
Deciding between the NVIDIA A100 and H100 for LLM serving comes down to throughput per rupee rather than raw specs. Vendor benchmarks rarely match production, so we benchmarked both GPUs on our own cluster running Llama 3 70B with vLLM under realistic serving conditions.

## Benchmark setup
We ran identical vLLM configurations on 8x H100 SXM and 8x A100 80GB nodes in our Noida data centre. We swept batch sizes from 1 through 64, used FP8 on the H100 and FP16 on the A100, and held the model, prompt distribution and context length constant across both runs. Each configuration ran for thirty minutes after warm-up so the numbers reflect sustained serving rather than a cold burst.

## Throughput results
The H100 delivered far higher tokens per second at batch 32. At low batch sizes the gap narrows sharply because the workload becomes memory bound rather than compute bound, and the H100's compute advantage goes underused. Teams serving small batches at tight latency will not see the full speed-up, which matters when you size capacity.

## Cost per million tokens
On current on-demand pricing, the H100 wins on cost per million tokens for sustained high-batch serving, while the A100 stays cheaper for bursty low-batch workloads. The crossover point sits around batch 16 in our tests, though your own traffic shape will move it. Model the cost against your real batch distribution before you commit to a fleet.

## When the A100 still wins
Fine-tuning smaller models, development environments and latency-insensitive batch jobs remain cheaper on A100 capacity. There is no reason to pay the H100 premium for workloads that never saturate it. Many teams run a mixed fleet for exactly this reason.

## Recommendation
Serve production traffic on H100, and keep A100 pools for training experiments and overflow capacity. Profile your batch distribution first, because the right answer depends on how your traffic actually arrives, not on the headline throughput number.
