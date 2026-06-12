---
slug: h200-vs-h100-training
title: "H200 vs H100 for Training Runs: Memory Bandwidth Changes the Math"
primary_keyword: "h200 vs h100 training"
cluster_id: gpu-compare-h200-h100
content_class: mid
---
The H200's larger and faster HBM3e memory changes training economics for memory-bound workloads. We measured the difference on our own hardware so you do not have to rely on vendor decks or synthetic benchmarks that never touch a real training run.

## What actually changed
The H200 carries 141 GB of HBM3e against the H100's 80 GB of HBM3, with memory bandwidth rising to 4.8 TB/s [S5]. Compute throughput is nearly identical between the two parts, so every difference you see in training comes from the memory subsystem rather than raw FLOPS. That single fact decides whether the upgrade is worth paying for.

## Where the bandwidth shows up
Long-context training and large-batch fine-tuning are the workloads that hit memory limits first. In our test runs the H200 sustained meaningfully higher tokens per second on 32k-context fine-tunes [S5]. The advantage grew as context length increased, which is the clearest signal that memory, not compute, was the binding constraint in these jobs.

## Where it does not matter
Compute-bound pretraining at short context sees little benefit from the extra bandwidth. If your utilisation profile is FLOPS-limited, the H100 remains the better value and the H200 premium buys you nothing. Knowing which regime you are in is the whole game here.

## Cost considerations
H200 capacity carries a price premium, so the decision reduces to whether your workload is memory bound. Profile before you commit, because guessing wrong in either direction wastes budget. A short profiling run costs far less than a misallocated fleet.

## Recommendation
Run a one-day profiling job on both parts. If memory bandwidth utilisation exceeds compute utilisation, the H200 pays for itself on long-context work. If not, stay on H100 and put the savings toward more nodes.
