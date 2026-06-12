---
slug: tensor-vs-pipeline-parallelism
title: "Tensor Parallelism vs Pipeline Parallelism: Scaling LLM Training Across Multiple GPUs"
primary_keyword: "tensor parallelism vs pipeline parallelism"
cluster_id: multi-gpu-training-strategy
content_class: mid
---

Training large language models across multiple GPUs forces a choice between two dominant strategies: tensor parallelism and pipeline parallelism. The decision shapes your memory footprint, communication overhead, and ultimately your cost per training step. This guide explains the tradeoff clearly so you can match the strategy to your workload.

## What tensor parallelism does

Tensor parallelism splits individual weight matrices across GPUs. During a forward pass, each GPU holds a shard of every layer's weights and performs its portion of the matrix multiplication. The results are combined via an all-reduce collective before passing to the next layer.

The advantage is fine-grained memory distribution. A model that exceeds a single GPU's memory becomes trainable by dividing each layer rather than each stage. The tradeoff is communication volume: every layer boundary requires an all-reduce across all participating GPUs, which means high-bandwidth interconnect is not optional - it is load-bearing. On NVLink-connected nodes this overhead is manageable [S1]. Across slower interconnects it dominates runtime.

## What pipeline parallelism does

Pipeline parallelism assigns different layers to different GPUs. GPU 0 holds layers 1–8, GPU 1 holds layers 9–16, and so on. A micro-batch flows through each stage sequentially, and multiple micro-batches are in flight simultaneously to keep GPUs from stalling while waiting for upstream results.

Communication happens only at stage boundaries - one activation tensor passed forward and one gradient tensor passed backward per micro-batch. This is far less data than tensor parallelism's per-layer all-reduce, which makes pipeline parallelism tolerant of lower-bandwidth inter-node links. The cost is pipeline bubbles: GPUs idle at the start and end of each batch while the pipeline fills and drains. Megatron-LM reports bubble fraction of roughly 1/(number of stages) [S2], which grows expensive at high stage counts.

## When to use each

The choice reduces to two questions: where is your bottleneck, and what does your hardware interconnect look like?

Use tensor parallelism when your model layers are individually too large to fit in a single GPU's memory, or when you have NVLink within a node and want maximum throughput on compute-bound workloads. Tensor parallelism scales well within a node; it struggles across nodes.

Use pipeline parallelism when you are distributing across nodes connected by InfiniBand or Ethernet, where all-reduce costs would dominate. It is also the right choice when individual layers fit in memory and the goal is to accommodate a model with many layers rather than very wide layers.

In practice, large training runs combine both [S3]. Tensor parallelism handles intra-node distribution, pipeline parallelism handles inter-node. This two-dimensional approach - sometimes called 3D parallelism when data parallelism is added - is how frontier models are trained at scale.

## Memory implications

Tensor parallelism reduces the peak activation memory proportionally to the degree of parallelism. With 8-way tensor parallelism, each GPU holds roughly one-eighth of the activation memory for split layers [S1].

Pipeline parallelism reduces memory by holding fewer layers per GPU, but it requires storing activations for all in-flight micro-batches simultaneously. At high micro-batch counts the activation buffer can become the binding memory constraint rather than the weights themselves.

## Communication volume comparison

For a transformer layer with hidden dimension H and sequence length S, tensor parallelism with degree T requires two all-reduce operations per layer, each of size proportional to the batch times S times H divided by T [S1]. Pipeline parallelism requires one activation tensor of size proportional to micro-batch times S times H at each stage boundary [S2]. For large H the all-reduce volume exceeds the activation transfer volume, which is why tensor parallelism is bandwidth-hungry.

## Practical recommendation

Start with pipeline parallelism across nodes and tensor parallelism within nodes. Profile bubble fraction and all-reduce time separately. If bubble fraction exceeds 10% of step time, increase micro-batch count. If all-reduce time exceeds 15% of step time, reduce tensor parallelism degree or verify interconnect utilisation. Both numbers are measurable in one training run before you commit to a configuration.

The correct answer depends on your model architecture, hardware topology, and target batch size. These strategies are not alternatives to be chosen once - they are dimensions of a configuration space worth profiling before locking in.

## Sources

- [S1] Shoeybi et al., Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism, 2019
- [S2] Narayanan et al., Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM, 2021
- [S3] Narayanan et al., PipeSwitch: Fast Pipelined Context Switching for Deep Learning Applications, 2020
