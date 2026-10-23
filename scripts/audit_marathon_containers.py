"""Metadata-only completeness audit of known non-CSV local data containers."""
import json
import zipfile
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq
from scripts.edge_marathon.runner import ROOT,OUT,safe_dump,verify
from scripts.afternoon_inference_round import sha


def run():
    verify();records=[]
    paths=[ROOT/'data/curated/USATECHIDXUSD-1m.parquet',
           ROOT.parent/'Quantt/data/curated/USATECHIDXUSD-1m.parquet',
           ROOT.parent/'data/overnight_nq/NQ_point_in_time_1min.parquet',
           ROOT.parent/'Quantt/data/raw/histdata/NSXUSD/2024.zip',
           ROOT.parent/'Quantt/data/raw/histdata/NSXUSD/2025.zip']
    for path in paths:
        if not path.exists():continue
        r=dict(path=str(path),filename=path.name,sha256=sha(path),bytes=path.stat().st_size)
        if path.suffix=='.parquet':
            meta=pq.ParquetFile(path);r.update(rows=meta.metadata.num_rows,columns=meta.schema.names)
            if path.name.startswith('NQ_point'):
                dates=pd.read_parquet(path,columns=['trade_date','contract'])
                r.update(first_trade_date=str(dates.trade_date.min()),last_trade_date=str(dates.trade_date.max()),
                         contracts=sorted(dates.contract.unique().tolist()),
                         classification='DERIVED_ALREADY_CONSUMED_NQ_MASTER_NOT_ADDITIONAL_HISTORY')
                if dates.trade_date.astype(str).lt('2024-12-30').any():raise ValueError('Unexpected older derived NQ history, needs explicit audit')
            else:
                r['classification']='DUKASCOPY_INDEX_CFD_NOT_CME_NQ_FUTURES'
        else:
            try:
                with zipfile.ZipFile(path) as z:
                    r['archive_member_names']=[x.filename for x in z.infolist()]
                r['classification']='HISTDATA_NSXUSD_CFD_ARCHIVE_NOT_NQ_CONTRACTS'
            except zipfile.BadZipFile:
                r['classification']='INVALID_ZIP_NOT_IMPORTABLE_NQ_DATA'
        records.append(r)
    result=dict(status='NON_CSV_CONTAINER_METADATA_AUDITED_NO_EXTRA_NQ_HOLDOUT_FOUND',records=records,
        no_archives_extracted=True,no_new_strategy_outcomes=True,
        identity_evidence=['configs/instruments.yaml','src/quantlab/data.py','scripts/build_research.py','scripts/source_probe.py'],
        limitation='Known project data roots plus known container files only, not a claim of searching every file on the entire disk. CFD quote bars are not silently relabeled as NQ futures. The106678bar master duplicates consumed research, not extra holdout dates.')
    safe_dump(OUT/'non-csv-containers.json',result)
    print(result['status'],len(records),'containers',flush=True)
    return result


if __name__=='__main__':run()
