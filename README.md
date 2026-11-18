# Budget ML Agent

A local-first AI agent prototype built around a low-cost LLM API.

The goal of this project is not simply to call a model API. The goal is to build a small, reproducible agent system with:

- conversation memory;
- tool execution;
- token and cost tracking;
- containerized runtime;
- evaluation;
- a clear engineering decision about whether to adopt Hermes Agent or keep a custom lightweight agent.

This repository is intentionally started without Hermes Agent and without cloud deployment. First, the core agent behavior must be understood and implemented locally.

## Project Status

Current phase: **Local MVP development**.

The project follows a staged roadmap:

1. Core agent API integration.
2. CLI chat loop with memory.
3. Usage and cost tracking.
4. Dockerized reproducible runtime.
5. Tool layer and function calling.
6. Evaluation harness.
7. Hermes Agent spike and architecture decision.
8. Optional VPS deployment.

## High-Level Architecture
