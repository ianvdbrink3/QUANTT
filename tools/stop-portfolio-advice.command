#!/bin/zsh
set -e
QUANT_TASK_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd -- "$QUANT_TASK_ROOT"
exec "$QUANT_TASK_ROOT/.venv/bin/python" -m portfolio_agent.forward service-stop
