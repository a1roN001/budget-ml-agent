# Budget ML Agent

A local-first AI agent prototype that uses a low-cost LLM API.

The goal of this project is not just to call a model. The goal is to build and understand a small agent system with:

- conversation memory;
- provider API integration;
- token usage tracking;
- estimated cost logging;
- tool execution;
- Dockerized runtime;
- basic evaluation;
- an explicit architecture decision about Hermes Agent.

This project starts without Hermes Agent and without cloud deployment. The core agent behavior must first be implemented and understood locally.

## Non-goals

- Do not run the LLM locally.
- Do not start with Hermes Agent.
- Do not deploy to VPS before the local MVP works.
- Do not add unnecessary frameworks without justification.

## High-level architecture

```text
User
  |
  v
CLI entrypoint
  |
  v
AgentCore
  |-- conversation history
  |-- system prompt
  |-- tool router
  |-- usage tracker
  |
  v
ProviderClient
  |
  v
River AI / DeepSeek Flash API
```

The model is accessed through an external API. The local process is responsible for orchestration, memory, tool calling, logging, and evaluation.

## Model

Default model:

```text
deepseek-flash
```

The model is selected for cost efficiency and fast responses. The exact API endpoint and authentication method depend on the provider console configuration.

## Environment variables

Required variables:

```env
RIVER_API_KEY=your_api_key_here
RIVER_BASE_URL=provider_base_url
MODEL=deepseek-flash
```

Optional variables:

```env
LOG_LEVEL=INFO
INPUT_PRICE_PER_1M_TOKENS=0.15
OUTPUT_PRICE_PER_1M_TOKENS=0.60
MAX_HISTORY_MESSAGES=20
REQUEST_TIMEOUT_SECONDS=60
```

Never commit real values of `RIVER_API_KEY`.

## Local development

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Copy environment example:

```bash
cp .env.example .env
```

Fill `.env` with local API credentials.

Run smoke test:

```bash
python -m agent.main --prompt "Hello"
```

Run interactive CLI:

```bash
python -m agent.main --chat
```

## Docker

After the local MVP is stable, the project will be containerized.

Planned commands:

```bash
docker build -t budget-ml-agent .
docker run --env-file .env budget-ml-agent --prompt "Hello"
```

or:

```bash
docker compose up
```

The Docker setup must support both local development and later deployment to a VPS. If deploying to ARM-based cloud instances, architecture compatibility must be checked.

## Cost tracking

The agent logs token usage where available.

Estimated cost is calculated using configurable price values:

```env
INPUT_PRICE_PER_1M_TOKENS=0.15
OUTPUT_PRICE_PER_1M_TOKENS=0.60
```

These values are examples and must be verified against the current provider pricing.

If usage data is not returned by the provider, the system records `cost_estimate: null` instead of fabricating a value.

## Tools

The agent will support external tools. A tool is a registered Python function with:

- a name;
- a description;
- an input schema;
- a safe execution wrapper;
- tests.

Planned initial tools:

- `nlp_preprocess`: text normalization, tokenization, lemmatization;
- `usage_report`: returns session token and cost statistics.

## Evaluation

The project will include a small evaluation harness.

Metrics:

- task success rate;
- latency;
- input tokens;
- output tokens;
- estimated cost;
- tool invocation correctness.

The evaluation dataset will be stored in `data/eval/`.

## Hermes Agent decision

Hermes Agent is not used at the beginning of this project.

After the custom agent core and tool layer are working, a time-boxed spike will compare:

- custom lightweight agent;
- Hermes Agent.

The decision will be documented in:

```text
docs/adr/0001-hermes-agent-decision.md
```

Possible outcomes:

1. Keep the custom agent.
2. Adopt Hermes Agent and migrate tools into Hermes skills.
3. Use a hybrid approach.

The choice must be justified by engineering criteria, not popularity.

## Security rules

- Never commit `.env`.
- Never hardcode API keys.
- Never log full API keys.
- Run containers as a non-root user where possible.
- Validate tool inputs before execution.
- Do not allow arbitrary code execution from model output.

## Development workflow

Each GitHub issue represents one bounded unit of work.

Branch naming:

```text
issue-1-scaffold
issue-2-provider-smoke-test
issue-3-cli-chat-loop
```

Commit messages should follow conventional style:

```text
feat: add provider smoke test
fix: handle missing api key
chore: add dockerignore
docs: update architecture section
test: add tool registry tests
```

Pull requests must include:

- linked issue;
- short description;
- testing evidence;
- updated documentation if behavior changes.

## Roadmap

- [ ] M1: Core Agent MVP
- [ ] M2: Reproducible Runtime
- [ ] M3: Tool Layer
- [ ] M4: Evaluation
- [ ] M5: Hermes Decision and Deployment

## License

MIT.