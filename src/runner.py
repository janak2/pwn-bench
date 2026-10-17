"""Run the model x harness x task matrix and collect results."""
import json
import tempfile
from pathlib import Path

from src.harness import HARNESSES
from src.models import build_client
from src.tasks import TASKS

RUNS_DIR = Path("runs")


def run_matrix(config: dict) -> list[dict]:
    results = []
    RUNS_DIR.mkdir(exist_ok=True)

    for model_cfg in config["models"]:
        client = build_client(model_cfg)
        for harness_name in config["harnesses"]:
            harness = HARNESSES[harness_name]
            for task_name in config["tasks"]:
                task = TASKS[task_name]
                with tempfile.TemporaryDirectory() as tmp:
                    workdir = Path(tmp)
                    task.setup(workdir)
                    try:
                        outcome = harness(client, model_cfg["model"], task, workdir, config["max_steps"])
                    except Exception as e:  # one failing cell shouldn't abort the whole matrix
                        outcome = {"submitted": f"ERROR: {e}", "steps": 0, "messages": []}

                # Save the full transcript so a run can be inspected afterwards.
                (RUNS_DIR / f"{model_cfg['name']}__{harness_name}__{task_name}.json").write_text(
                    json.dumps(outcome["messages"], indent=2)
                )
                results.append(
                    {
                        "model": model_cfg["name"],
                        "harness": harness_name,
                        "task": task_name,
                        "solved": outcome["submitted"] == task.flag,
                        "submitted": outcome["submitted"],
                        "steps": outcome["steps"],
                    }
                )
    return results
