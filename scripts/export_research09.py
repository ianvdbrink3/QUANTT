"""One-command, private-by-default CSV -> Parquet -> observed research export."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quantlab.futures_import import stage_futures_csv
from quantlab.observed_release09 import export_observed, append_registry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="QUANT 0.9 observed futures; never an edge certification")
    parser.add_argument("--csv", action="append", default=[], metavar="NQ=/path/data.csv",
                        help="Instrument-qualified input, repeat for ES/MNQ/MES")
    parser.add_argument("--staged", action="append", default=[], metavar="path.parquet",
                        help="Previously validated Parquet with its .quality.json sidecar")
    parser.add_argument("--source", help="Named vendor/source for --csv (no synthetic/CFD)")
    parser.add_argument("--stage-dir", default="artifacts/observed-stage")
    parser.add_argument("--out", default="artifacts/research09.json")
    parser.add_argument("--registry", default="artifacts/observed-registry.jsonl")
    parser.add_argument("--publication-approved", action="store_true",
                        help="Explicitly approve publishing aggregates/metadata under public/")
    args = parser.parse_args(argv)
    if not args.csv and not args.staged:
        parser.error("Provide --csv or --staged; no synthetic fallback")
    if args.csv and not args.source:
        parser.error("--source is required for CSV input")
    if args.source and not args.csv:
        parser.error("--source only applies to CSV staging")
    paths = [Path(p) for p in args.staged]
    stage_dir = Path(args.stage_dir)
    if args.csv and "public" in stage_dir.parts:
        parser.error("Raw/staged user data cannot be placed under public/")
    for item in args.csv:
        symbol, separator, filename = item.partition("=")
        if not separator or symbol not in {"NQ", "ES", "MNQ", "MES"} or not filename:
            parser.error("CSV must be specified as NQ=/path/file.csv (or ES/MNQ/MES)")
        candidate = stage_dir / (symbol + ".parquet")
        if candidate in paths or candidate.exists():
            parser.error(f"Staging target exists: {candidate}; use a clean directory")
        quality = stage_futures_csv(filename, candidate, instrument=symbol, source=args.source)
        candidate.with_suffix(".quality.json").write_text(
            json.dumps(quality, sort_keys=True, indent=2, default=str) + "\n", encoding="utf-8"
        )
        paths.append(candidate)
    result = export_observed(paths, args.out, publication_approved=args.publication_approved)
    append_registry(result, args.registry)
    print(f"OBSERVED, UNVERIFIED: {result['row_count']} bars; run={result['run_id']}")
    print(f"Research report: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
