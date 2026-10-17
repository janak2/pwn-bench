"""Run the BountyBench Native harness: WhiteRabbit on BountyBench's exploit lane.

    uv run bountybench_run.py --list            # list the exploit tasks
    uv run bountybench_run.py --dry-run lunary:0 # show the command without running
    uv run bountybench_run.py lunary:0           # run one task (needs Docker + endpoint)
    uv run bountybench_run.py --all              # run every exploit task

Set PWNBENCH_BASE_URL and PWNBENCH_API_KEY in .env (the SGLang pod and its API key).
Run setup_bountybench.sh first to vendor BountyBench.
"""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from src.bountybench import (
    VENDOR,
    build_command,
    list_exploit_tasks,
    run_task,
)

load_dotenv()

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("tasks", nargs="*", help="tasks to run, as repo:bounty (e.g. lunary:0)")
parser.add_argument("--list", action="store_true", help="list exploit tasks and exit")
parser.add_argument("--all", action="store_true", help="run every exploit task")
parser.add_argument("--dry-run", action="store_true", help="print the command(s) without running")
parser.add_argument("--phase-iterations", type=int, default=5, help="max agent iterations per task")
args = parser.parse_args()

if not VENDOR.exists():
    raise SystemExit("vendor/bountybench not found. Run ./setup_bountybench.sh first.")

available = list_exploit_tasks()
by_name = {t.name: t for t in available}

if args.list:
    print(f"{len(available)} exploit tasks:")
    for t in available:
        print(f"  {t.name}")
    raise SystemExit(0)

if args.all:
    selected = available
else:
    try:
        selected = [by_name[name] for name in args.tasks]
    except KeyError as e:
        raise SystemExit(f"Unknown task {e.args[0]!r}. Use --list to see available tasks.")
if not selected:
    raise SystemExit("No tasks selected. Pass repo:bounty, --all, or --list.")

if args.dry_run:
    for t in selected:
        print(f"# {t.name} (cwd={VENDOR})")
        print(f"OPENAI_BASE_URL=$PWNBENCH_BASE_URL OPENAI_API_KEY=*** {' '.join(build_command(t, args.phase_iterations))}")
    raise SystemExit(0)

base_url = os.environ.get("PWNBENCH_BASE_URL")
api_key = os.environ.get("PWNBENCH_API_KEY")
if not base_url or not api_key:
    raise SystemExit("Set PWNBENCH_BASE_URL and PWNBENCH_API_KEY in .env.")

runs_dir = Path("runs")
results = []
for t in selected:
    print(f"[run] {t.name} ...")
    result = run_task(t, base_url, api_key, args.phase_iterations, runs_dir)
    print(f"[run] {t.name}: {'PASS' if result['solved'] else 'FAIL'} (exit {result['exit_code']})")
    results.append(result)

Path("results.json").write_text(json.dumps(results, indent=2))
solved = sum(r["solved"] for r in results)
print(f"\n{solved}/{len(results)} solved. Logs in runs/, summary in results.json.")
