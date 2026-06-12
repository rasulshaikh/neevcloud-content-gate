---
slug: llama3-deployment-guide
title: "Deploying Llama 3 70B in Production: A Capacity Planning Guide"
primary_keyword: "llama 3 70b deployment"
cluster_id: model-deploy-llama3
content_class: mid
---
Llama 3 70B needs careful capacity planning before it earns a place in production. This guide covers memory budgets, quantisation trade-offs and autoscaling.

## Memory budget
In FP16 the weights alone need roughly 140 GB, which means multi-GPU tensor parallelism on anything smaller than an H100 80GB pair [S4].

## Quantisation trade-offs
AWQ and GPTQ cut memory at a small quality cost. For customer-facing applications, validate on your own evaluation set before committing.

## Serving stack
vLLM with paged attention is the default choice for high-throughput serving. Configure max model length to your real context needs, not the maximum.

## Autoscaling
Scale on queue depth and time-to-first-token, not GPU utilisation. Utilisation lies under continuous batching.
