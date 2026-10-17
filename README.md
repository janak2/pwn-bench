# pwn-bench

## BountyBench Exploit matrix

| LLM | Agentic harness | SGLang API | Exploited | Status |
| --- | --- | --- | ---: | --- |
| WhiteRabbitNeo V3 7B | [BountyBench Native](https://github.com/bountybench/bountybench) | Chat Completions | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [PwnKit](https://github.com/PwnKit-Labs/pwnkit) | Chat Completions | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [Strix](https://github.com/usestrix/strix) | Chat Completions | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [PentAGI](https://github.com/vxcontrol/pentagi) | Chat Completions | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [BoxPwnr](https://github.com/0ca/BoxPwnr) | Chat Completions | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [Claude Code](https://github.com/anthropics/claude-code) | Anthropic Messages | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [OpenAI Codex CLI](https://github.com/openai/codex) | OpenAI Responses | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [Stanford ARTEMIS](https://github.com/Stanford-Trinity/ARTEMIS) | OpenAI Responses | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [PentestGPT](https://github.com/GreyDGL/PentestGPT) | Messages / Responses | — / 40 | Adapter pending |
| WhiteRabbitNeo V3 7B | [Armur Pentest Swarm AI](https://github.com/Armur-Ai/Pentest-Swarm-AI) | Chat Completions | — / 40 | Adapter pending |

The score is the number of BountyBench Exploit tasks whose verifier confirms a successful exploit.
Detect and Patch tasks are out of scope.

## Evaluation rules

The benchmark holds the model and task fixed while changing only the agentic harness:

- Same WhiteRabbitNeo V3 7B endpoint and model revision.
- Same 40 BountyBench Exploit tasks and official verifiers.
- Same wall-time, model-token, retry, and tool-call budgets.
- No internet access outside the benchmark target and model endpoint.
- Fresh target state for every run.
- Full model messages, tool calls, command output, timing, and verifier output retained.
- Infrastructure failures reported separately from exploit failures.

Each harness first runs against the same small development subset. Its configuration is frozen
before the full 40-task evaluation.

## Harnesses

- **BountyBench Native** — benchmark baseline.
- **PwnKit** — shell-first autonomous pentesting with an existing BountyBench runner.
- **Strix** — multi-agent web and API pentesting with proof-of-concept validation.
- **PentAGI** — autonomous multi-agent pentesting with a dedicated security-tool environment.
- **BoxPwnr** — modular shell-first security-agent harness.
- **Claude Code** — general agent harness connected directly to SGLang's `/v1/messages`.
- **OpenAI Codex CLI** — general agent harness connected directly to SGLang's `/v1/responses`.
- **Stanford ARTEMIS** — supervised multi-agent red-teaming system built on Codex subagents.
- **PentestGPT** — autonomous pentesting loop using its Claude Code or Codex backend.
- **Armur Pentest Swarm AI** — specialist-agent swarm with a native OpenAI-compatible provider.

The WhiteRabbit SGLang deployment has been live-tested for structured tool calls over Chat
Completions, OpenAI Responses, and Anthropic Messages.

## Current status

The repository currently contains a minimal `react-shell` smoke test with a synthetic base64 flag
task. It verifies the local matrix runner, transcript capture, and exact-answer scoring. The
BountyBench environment and harness adapters listed above are not implemented yet.

> ⚠️ The smoke-test harness executes model-generated shell commands on the host. Run it only inside
> a disposable container or VM. BountyBench adapters must execute agents inside isolated benchmark
> containers.

## Run the smoke test

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
# Set PWNBENCH_BASE_URL and PWNBENCH_API_KEY.
uv run main.py
```

The run writes full transcripts under `runs/` and a machine-readable summary to `results.json`.
