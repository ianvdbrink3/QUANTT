"""Generate Release 0.8 static reference JSON from the real Python pipeline."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quantlab.release08 import main
if __name__=='__main__': raise SystemExit(main())
