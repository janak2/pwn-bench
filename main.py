"""Evaluate agentic harnesses x LLMs on the same CTF tasks.

    uv run main.py [config.yaml]
"""
import argparse
import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.runner import run_matrix

load_dotenv()

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("config", nargs="?", default="config.yaml", help="matrix config")
# Expand ${VARS} from the environment before parsing, so secrets live in .env.
config = yaml.safe_load(os.path.expandvars(Path(parser.parse_args().config).read_text()))

results = run_matrix(config)
Path("results.json").write_text(json.dumps(results, indent=2))

print(f"\n{'RESULT':6}  {'model':20} {'harness':14} {'task':14} {'steps':>5}  submitted")
for r in results:
    status = "PASS" if r["solved"] else "FAIL"
    print(f"{status:6}  {r['model']:20} {r['harness']:14} {r['task']:14} {r['steps']:>5}  {r['submitted']}")

solved = sum(r["solved"] for r in results)
print(f"\n{solved}/{len(results)} solved. Transcripts in runs/, summary in results.json.")
