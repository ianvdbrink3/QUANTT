"""One-command QUANT research pipeline entry point with explicit synthetic provenance."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quantlab.research_pipeline import main
if __name__=='__main__':
    raise SystemExit(main())
