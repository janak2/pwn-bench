# pwn-bench

## BountyBench Exploit matrix

| Agentic harness | [WhiteRabbitNeo V3 7B](https://ollama.com/WhiteRabbitNeo/WhiteRabbitNeo-V3-7B) |
| --- | ---: |
| [BountyBench Native](https://github.com/bountybench/bountybench) | — / 40 |
| [PwnKit](https://github.com/0sec-labs/0) | — / 40 |
| [Strix](https://github.com/usestrix/strix) | — / 40 |
| [PentAGI](https://github.com/vxcontrol/pentagi) | — / 40 |
| [BoxPwnr](https://github.com/0ca/BoxPwnr) | — / 40 |
| [Claude Code](https://github.com/anthropics/claude-code) | — / 40 |
| [OpenAI Codex CLI](https://github.com/openai/codex) | — / 40 |
| [Stanford ARTEMIS](https://github.com/Stanford-Trinity/ARTEMIS) | — / 40 |
| [PentestGPT](https://github.com/GreyDGL/PentestGPT) | — / 40 |
| [Armur Pentest Swarm AI](https://github.com/Armur-Ai/Pentest-Swarm-AI) | — / 40 |

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

`BountyBench Native` is wired up: BountyBench is vendored under `vendor/`, patched so it drives
WhiteRabbit through its OpenAI-compatible endpoint (`openai/whiterabbitneo-v3` over
`OPENAI_BASE_URL`, see `patches/`), and `bountybench_run.py` enumerates the exploit tasks and runs
them. Running a task needs a Docker daemon (BountyBench spins up the Kali and target containers)
and a live WhiteRabbit endpoint. The other nine harnesses are not implemented yet.

A minimal `react-shell` smoke test with a synthetic base64 flag task is also included; it exercises
the local matrix runner, transcript capture, and exact-answer scoring without Docker.

> ⚠️ The smoke-test harness executes model-generated shell commands on the host. Run it only inside
> a disposable container or VM. BountyBench runs agents inside its own benchmark containers.

## Run BountyBench Native

Requires [uv](https://docs.astral.sh/uv/), git, and a running Docker daemon.

```bash
./setup_bountybench.sh                        # vendor BountyBench + build its Python 3.11 env
cp .env.example .env                          # set PWNBENCH_BASE_URL and PWNBENCH_API_KEY
uv run bountybench_run.py --list              # list the exploit tasks
uv run bountybench_run.py --dry-run lunary:0  # show the command without running
uv run bountybench_run.py lunary:0            # run one task
uv run bountybench_run.py --all               # run every exploit task
```

Logs land in `runs/`, the summary in `results.json`.

## Run the smoke test

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
# Set PWNBENCH_BASE_URL and PWNBENCH_API_KEY.
uv run main.py
```

The run writes full transcripts under `runs/` and a machine-readable summary to `results.json`.
