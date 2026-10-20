"""Outcome-blind data preparation. No signal or performance function is called here."""
from pathlib import Path
import hashlib
import json
import shutil
import pandas as pd
from . import barchart, engine

REPO = Path(__file__).resolve().parents[2]
START, END = '2025-04-18', '2025-09-30'
CLOSES = {'2025-04-18': None, '2025-05-26': '13:00',
          '2025-06-19': '13:00', '2025-07-03': '13:15',
          '2025-07-04': '13:00', '2025-09-01': '13:00'}
BASE_GRID = engine.expected_grid


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def grid(day):
    """Civil NY session date, as in frozen engine; NOT CME clearing TradeDate."""
    if pd.Timestamp(day).weekday() >= 5:
        return pd.DatetimeIndex([], tz='UTC')
    result = BASE_GRID(day)
    if day in CLOSES:
        close = CLOSES[day]
        return result[:0] if close is None else result[result < engine.time_at(day, close)]
    return result


def load_all(raw_dir, sources):
    contracts, audits = [], []
    for contract in ['NQH25', 'NQM25', 'NQU25', 'NQZ25']:
        parts = []
        for item in sources:
            if item['contract'] != contract:
                continue
            path = raw_dir/item['filename']
            if sha(path) != item['sha256']:
                raise ValueError('Raw SHA256 mismatch: '+item['filename'])
            part, _ = barchart.load(path)
            parts.append(part)
        bars = pd.concat(parts)
        duplicates = bars[bars.index.duplicated(False)]
        if duplicates.groupby(level=0)[barchart.FIELDS].nunique().gt(1).any().any():
            raise ValueError('Conflicting overlapping OHLCV: '+contract)
        before = len(bars)
        bars = bars[~bars.index.duplicated()].sort_index()
        bars['contract'] = contract
        bars['trade_date'] = barchart.trade_dates(bars.index).strftime('%Y-%m-%d')
        # An export ending at calendar midnight includes a partial NEXT session.
        # Never feed October 1 into September inference/history.
        bars = bars[bars.trade_date.between('2024-12-30', END)]
        audits.append({'contract': contract, 'raw_rows': before,
                       'unique_retained_bars': len(bars),
                       'duplicate_rows': before-len(pd.concat(parts).index.unique())})
        contracts.append(bars)
    return pd.concat(contracts).sort_index(), audits


def rollovers(full):
    totals = full.groupby(['contract','trade_date']).volume.sum()
    decisions = []
    for old, new in [('NQM25','NQU25'), ('NQU25','NQZ25')]:
        oldg, newg = full[full.contract.eq(old)], full[full.contract.eq(new)]
        shared = sorted(set(oldg.trade_date) & set(newg.trade_date))
        found = None
        for day in shared:
            # Compare full-session observed trade volume, never price outcomes.
            # Incomplete source start/end sessions cannot decide a switch.
            exp = grid(day)
            if not len(exp):
                continue
            og, ng = oldg[oldg.trade_date.eq(day)], newg[newg.trade_date.eq(day)]
            if og.index.min() > exp.min() or og.index.max() < exp.max():
                continue
            if ng.index.min() > exp.min()+pd.Timedelta(minutes=60) or ng.index.max() < exp.max()-pd.Timedelta(minutes=60):
                continue
            a, b = int(totals[old,day]), int(totals[new,day])
            if b <= a:
                continue
            future = sorted(d for d in set(newg.trade_date) if d > day and len(grid(d)))
            if not future:
                raise ValueError('No next session for volume switch')
            effective = future[0]
            prev = (pd.Timestamp(effective)-pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            found = {'from':old, 'to':new, 'decision_session':day,
                     'old_volume':a,'new_volume':b,'effective_session':effective,
                     'effective_utc':engine.time_at(prev,'18:00').isoformat()}
            break
        if found is None:
            raise ValueError('No objective volume switch for '+new)
        decisions.append(found)
    return decisions


def select(frame, decisions):
    june, sept = [x['effective_session'] for x in decisions]
    return ((frame.contract.eq('NQH25') & frame.trade_date.le('2025-03-18')) |
            (frame.contract.eq('NQM25') & frame.trade_date.between('2025-03-19', june, inclusive='left')) |
            (frame.contract.eq('NQU25') & frame.trade_date.between(june, sept, inclusive='left')) |
            (frame.contract.eq('NQZ25') & frame.trade_date.ge(sept))) & frame.trade_date.le(END)


def stage(downloads):
    """Only explicit user-provided filenames; original release sources retained."""
    target = REPO/'data/raw'
    original = json.loads((REPO/'research/reproduction-manifest.json').read_text())
    sources = [{k:x[k] for k in ['filename','sha256','contract']} for x in original['sources']]
    for contract, count in [('NQM25',8), ('NQU25',9), ('NQZ25',2)]:
        for n in range(1,count+1):
            suffix = '' if n==1 else '-'+str(n)
            name = f'{contract.lower()}_intraday-1min_historical-data-10-20-2026{suffix}.csv'
            src, dst = downloads/name, target/name
            if dst.exists() and sha(dst)!=sha(src):
                raise ValueError('Refusing to replace different private raw file: '+name)
            if not dst.exists():
                shutil.copy2(src,dst)
            sources.append({'filename':name,'sha256':sha(dst),'contract':contract})
    full, audits = load_all(target, sources)
    decisions = rollovers(full)
    import datetime
    manifest = {
        'schema_version':1, 'registered_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'phase':'DATA_AND_PROTOCOL_LOCKED_BEFORE_SIGNALS', 'start':START,'end':END,
        'sources':sources,'frozen_engine_sha256':sha(REPO/'scripts/reproduce_research/engine.py'),
        'baseline_manifest_sha256':sha(REPO/'research/reproduction-manifest.json'),
        'primary_strategy':'B_ORB15','primary_quality_view':'all',
        'reference_strategies':['A_London_sweep','B_ORB5','C_VWAP_extreme'],
        'pass_rule':{'minimum_eligible_days':20,'net_points_gt':0,'profit_factor_gt':1,
                     'two_sided_block_bootstrap_p_lt':0.05,'mean_daily_ci_low_gt':0},
        'inference':'Frozen 2000 circular 5-eligible-day block bootstrap, seed 20261020, two-sided centered p; zero-trade eligible days included. Combined results descriptive only.',
        'roll_rule':'Irreversible first incoming > outgoing completed civil-session observed volume; switch next available session at 18:00 NY. Same boundary-completeness checks in holdout_data.py. No intra-session roll.',
        'volume_timing_caveat':'Minute-derived prior-session totals assumed knowable before next 18:00 NY open; no vendor publication-vintage evidence. Not official total-volume/open-interest certification.',
        'calendar':CLOSES,
        'calendar_sources':[
            'https://www.cmegroup.com/trading-hours.html',
            'https://hedgingmarkets.com/wp-content/uploads/2025/02/CME-Good-Friday-2025-Holiday-Schedule.xlsx',
            'https://iqhelp.dtn.com/juneteenth-2025-holiday-exchange-schedule-2/',
            'https://iqhelp.dtn.com/fourth-of-july-service-hours-2025/',
            'https://iqhelp.dtn.com/labor-day-holiday-schedule-2025/',
            'https://help.oneuptrader.com/article/521-us-memorial-holiday-trading-schedule-2025'],
        'calendar_evidence_limit':'Historical CME webpage currently serves 2026 schedules. Historical hours reconstructed from contemporaneous vendor/broker schedules and checked against bars; not a retrieved signed CME 2025 calendar. Civil session dates retained, not clearing TradeDate.',
        'warmup':'Same-contract only, all available prior raw history. No ATR substitution or history transferred across contract. New U/Z may remain ineligible until 14 valid prior RTH true ranges.',
        'holdout_integrity':'No strategy PnL inspected before this protocol. Raw prices/volumes previously inspected for quality; not a prospective preregistration or independent third-party blind study.',
        'cost_rt_usd':24.5,'contract_audits':audits,'rollovers':decisions}
    path = REPO/'research/holdout-protocol.json'
    if path.exists():
        raise ValueError('Protocol already exists; never silently re-register a seen holdout')
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'protocol_sha256':sha(path),'rollovers':decisions,'sources':len(sources)},indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--downloads',type=Path,required=True)
    stage(parser.parse_args().downloads)
