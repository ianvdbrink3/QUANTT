#!/usr/bin/env python3
"""Offline integrity gate for publicly published QUANT historical NQ reports.

Checks snapshots against each other; does not authenticate raw Barchart bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FILES = ("nq-overnight.json", "research09.json")


def check(a: dict, b: dict) -> dict:
    def require(v: bool, message: str):
        if not v:
            raise AssertionError(message)
    require(a.get("schema_version") == "nq-overnight-1", "Invalid overnight schema")
    require(b.get("schema_version") == "0.9", "Invalid 0.9 schema")
    require(a.get("status") == "EXPLORATORY_NO_VALIDATED_EDGE", "Invalid exploratory status")
    require(b.get("status") == "STAGED_UNVERIFIED", "Invalid source status")
    require(a.get("edge_validated") is False and b.get("edge_validated") is False, "No validated edge allowed")
    require(b.get("data_is_synthetic") is False, "Observed is incorrectly synthetic")
    require(a.get("row_count", 0) > 0 and a["row_count"] == b.get("row_count"), "Row count mismatch")
    g = a.get("import_gate", {})
    require(g.get("passed") is True and g.get("synthetic_input") is False, "Import gate incomplete")
    require(g.get("source_authenticated") is False and g.get("calendar_certified") is False,
            "Source or calendar certification unverified")
    require(g.get("run_id") == b.get("run_id"), "Research run mismatch")
    quality = a.get("day_quality", [])
    flags = Counter(day.get("data_quality_flag") for day in quality)
    require(len(quality) == a.get("trade_dates"), "Missing day audit rows")
    require(flags.get("ok") == a.get("clean_days"), "Clean day count mismatch")
    require(sum(v for k,v in flags.items() if k != "ok") == a.get("flagged_days"),
            "Flagged day count mismatch")
    require(sum(int(day.get("missing_minutes", 0)) for day in quality) == a.get("missing_minutes"),
            "In-session missing minutes mismatch")
    require(0 < a.get("eligible_days",0) <= a.get("atr_ready_days",0) <= a.get("trade_dates",0),
            "Eligible day count mismatch")
    require(len(a.get("strategies",[])) == 4 and len(a.get("source_csv_hashes",[])) > 0,
            "Expected original strategy screens with source hashes")
    require(len(a.get("checks",{})) >= 20 and all(a["checks"].values()), "Published checks failed")
    src = b.get("sources",[])
    require(len(src) == 1 and src[0].get("instrument") == "NQ", "Source must be NQ only")
    require(src[0].get("rows") == a["row_count"], "Source row mismatch")
    require(src[0].get("calendar_verified") is False and
            src[0].get("contract_provenance_verified") is False,
            "Unverified source incorrectly claimed certified")
    require(b.get("governance",{}).get("holdout_validated") is False and
            b.get("governance",{}).get("trading_edge_validation_allowed") is False,
            "Holdout/edge claim incorrect")
    for s in a["strategies"]:
        sid=s.get("id","?"); m=s["metrics"]
        require(s.get("edge_validated") is False, sid+" edge validated incorrectly")
        require(s.get("holm_original") >= m.get("p_value"), sid+" invalid adjusted p")
        require(abs(m["net_points"] * 20 - m["net_usd"]) < 0.01, sid+" PnL points mismatch")
        require(abs(sum(x["net_points"] for x in s["splits"].values()) -
                    m["net_points"]) < .01, sid+" half-split mismatch")
        for case, x in s["cost_scenarios"].items():
            require(x["trades"] == m["trades"], sid+" stress trades mismatch")
            require(abs(x["net_points"] * 20 - x["net_usd"]) < .01,
                    sid+" "+case+" USD reconciliation mismatch")
        require(m["ci_low"] is None or m["ci_low"] <= m["ci_high"],
                sid+" invalid confidence interval")
    return {"status":"INTERNALLY_CONSISTENT_NOT_SOURCE_CERTIFIED",
            "rows":a["row_count"],"trade_dates":a["trade_dates"],
            "eligible_days":a["eligible_days"],"strategies":len(a["strategies"]),
            "checks":len(a["checks"]),"edge_validated":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-url",help="Compare committed JSON bytes to live production after deploy")
    args=p.parse_args()
    paths=[ROOT/"public"/"data"/name for name in FILES]
    a,b=[json.loads(f.read_text(encoding="utf-8")) for f in paths]
    print(json.dumps(check(a,b),sort_keys=True))
    if args.base_url:
        for f in paths:
            u=args.base_url.rstrip("/")+"/data/"+f.name
            with urlopen(Request(u,headers={"User-Agent":"QUANT-public-json-parity/0.9"}),timeout=25) as r:
                if r.status != 200:
                    raise AssertionError(f.name+": HTTP "+str(r.status))
                actual=r.read()
            if hashlib.sha256(actual).digest()!=hashlib.sha256(f.read_bytes()).digest():
                raise AssertionError("DRIFT: "+f.name)
            print("BYTE_PARITY_OK",f.name,hashlib.sha256(actual).hexdigest())
    return 0


if __name__=="__main__":
    raise SystemExit(main())
