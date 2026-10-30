#!/bin/zsh
set -e
set +x
umask 077
QUANT_TASK_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd -- "$QUANT_TASK_ROOT"
if [[ ! -t 0 || ! -t 1 ]]; then
  print 'Open dit bestand in Terminal; verborgen invoer vereist een echt terminalvenster.'
  exit 1
fi
print 'QUANT — Trading 212 DEMO lokaal koppelen'
print 'De agent blijft in alleen-lezenstand. Gebruik uitsluitend je DEMO-sleutels.'
print 'Plak eerst je API Key en druk op Enter. Plak daarna je API Secret en druk op Enter.'
print 'Tijdens het invoeren verschijnen geen letters of sterretjes; dat is normaal.'
print 'De sleutels blijven lokaal, buiten GitHub, Vercel en deze chat.'
"$QUANT_TASK_ROOT/.venv/bin/python" -m portfolio_agent.forward setup-demo-secrets
print '\nOpgeslagen. De lokale adviesagent controleert de demo binnen ongeveer een minuut.'
print 'Er worden geen orders geplaatst.'
