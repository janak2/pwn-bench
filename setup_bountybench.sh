#!/usr/bin/env bash
# Vendor the BountyBench Exploit environment and wire it to the WhiteRabbit endpoint.
#
# Clones BountyBench + its bountytasks submodules into vendor/, builds a Python 3.11
# venv (BountyBench requires 3.11), installs its requirements, and applies the
# WhiteRabbit patch so `openai/whiterabbitneo-v3` works against an OPENAI_BASE_URL
# endpoint (our SGLang pod). Safe to re-run.
#
# Requires: git, uv. Running the benchmark additionally requires a Docker daemon.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR="$REPO_ROOT/vendor/bountybench"
PATCH="$REPO_ROOT/patches/bountybench-whiterabbit.patch"
TASKS_PATCH="$REPO_ROOT/patches/bountytasks-gunicorn.patch"
VENV="$VENDOR/.venv311"

if [ ! -d "$VENDOR/.git" ]; then
    echo "[setup] Cloning BountyBench into $VENDOR"
    git clone https://github.com/bountybench/bountybench "$VENDOR"
fi

echo "[setup] Initializing task submodules (this pulls ~25 target systems and can take a while)"
git -C "$VENDOR" submodule update --init --recursive

echo "[setup] Applying WhiteRabbit patch"
# Apply before installing so the trimmed requirements.txt (no crfm-helm) is used.
if git -C "$VENDOR" apply --reverse --check "$PATCH" 2>/dev/null; then
    echo "[setup] Patch already applied; skipping"
else
    git -C "$VENDOR" apply "$PATCH"
    echo "[setup] Patch applied"
fi

echo "[setup] Applying bountytasks patch (resilient pip install for the gunicorn target)"
if git -C "$VENDOR/bountytasks" apply --reverse --check "$TASKS_PATCH" 2>/dev/null; then
    echo "[setup] Tasks patch already applied; skipping"
else
    git -C "$VENDOR/bountytasks" apply "$TASKS_PATCH"
    echo "[setup] Tasks patch applied"
fi

echo "[setup] Building Python 3.11 venv at $VENV"
uv venv --python 3.11 "$VENV"
uv pip install --python "$VENV/bin/python" -r "$VENDOR/requirements.txt"

echo "[setup] Done. Set PWNBENCH_BASE_URL and PWNBENCH_API_KEY in .env, then run: uv run bountybench_run.py --list"
