"""BountyBench Native harness: run BountyBench's own exploit_workflow with WhiteRabbit.

WhiteRabbit is served through an OpenAI-compatible endpoint (SGLang), so BountyBench
talks to it as `openai/whiterabbitneo-v3` via OPENAI_BASE_URL (see patches/). Requires
setup_bountybench.sh to have vendored BountyBench, plus a running Docker daemon to spin
up the Kali and target containers.
"""
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "vendor" / "bountybench"
VENV_PYTHON = VENDOR / ".venv311" / "bin" / "python"
MODEL = "openai/whiterabbitneo-v3"
SUCCESS_MARKER = "Exploit successful!"


@dataclass(frozen=True)
class ExploitTask:
    repo: str  # target system, e.g. "lunary"
    bounty_number: str  # bounty index within the repo, e.g. "0"

    @property
    def task_dir(self) -> str:
        return f"bountytasks/{self.repo}"

    @property
    def name(self) -> str:
        return f"{self.repo}:{self.bounty_number}"


def list_exploit_tasks() -> list[ExploitTask]:
    """Every (repo, bounty) that ships an exploit lane (a bounty_<n>/exploit_files/ dir)."""
    tasks = []
    for bounty_dir in sorted((VENDOR / "bountytasks").glob("*/bounties/bounty_*")):
        if (bounty_dir / "exploit_files").is_dir():
            repo = bounty_dir.parents[1].name
            number = bounty_dir.name.removeprefix("bounty_")
            tasks.append(ExploitTask(repo=repo, bounty_number=number))
    return tasks


def build_command(task: ExploitTask, phase_iterations: int) -> list[str]:
    return [
        str(VENV_PYTHON),
        "-m",
        "workflows.runner",
        "--workflow-type",
        "exploit_workflow",
        "--task_dir",
        task.task_dir,
        "--bounty_number",
        task.bounty_number,
        "--model",
        MODEL,
        "--phase_iterations",
        str(phase_iterations),
    ]


def run_task(
    task: ExploitTask,
    base_url: str,
    api_key: str,
    phase_iterations: int,
    runs_dir: Path,
) -> dict:
    """Run one exploit task through BountyBench and report whether the verifier passed."""
    env = {**os.environ, "OPENAI_BASE_URL": base_url, "OPENAI_API_KEY": api_key}
    # BountyBench's api-key verification requires a .env file to exist in its tree.
    (VENDOR / ".env").write_text(f"OPENAI_API_KEY={api_key}\nOPENAI_BASE_URL={base_url}\n")

    proc = subprocess.run(
        build_command(task, phase_iterations),
        cwd=VENDOR,
        env=env,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr

    runs_dir.mkdir(exist_ok=True)
    (runs_dir / f"bountybench-native__{task.repo}__{task.bounty_number}.log").write_text(output)

    solved = SUCCESS_MARKER in output
    if solved:
        status = "solved"
    elif proc.returncode == 0:
        status = "not_solved"
    else:
        # Non-zero exit without a success marker means BountyBench could not run the
        # task to completion (setup/build/container failure) rather than the exploit
        # failing verification, so report it as an infrastructure error.
        status = "infra_error"

    return {
        "harness": "bountybench-native",
        "model": "whiterabbitneo-v3",
        "task": task.name,
        "status": status,
        "solved": solved,
        "exit_code": proc.returncode,
    }
