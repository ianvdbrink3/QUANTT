"""Raw-only replay of the outcome-blind registered Level 3 protocol."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import tempfile
import numpy as np
import pandas as pd
from . import engine, holdout_data as data
from .cli import compare, trade_ledger_sha256

REPO = data.REPO
STRATEGIES = ['A_London_sweep','B_ORB5','B_ORB15','C_VWAP_extreme']


def write(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(engine.clean(obj),indent=2,allow_nan=False)+'\n')


def preflight(raw_dir, protocol):
    if not __debug__:
        raise ValueError('Python -O disables required assertions')
    if data.sha(REPO/'scripts/reproduce_research/engine.py') != protocol['frozen_engine_sha256']:
        raise ValueError('Frozen strategy engine changed')
    if data.sha(REPO/'research/reproduction-manifest.json') != protocol['baseline_manifest_sha256']:
        raise ValueError('Original reference manifest changed')
    if protocol['calendar'] != data.CLOSES or protocol['cost_rt_usd'] != engine.COST*20:
        raise ValueError('Calendar or cost drift')
    for item in protocol['sources']:
        name = item['filename']
        if Path(name).name != name:
            raise ValueError('Unsafe source name')
        if data.sha(raw_dir/name) != item['sha256']:
            raise ValueError('Raw SHA256 mismatch: '+name)


def extra_metrics(trades, dates):
    trades = trades.sort_values(['entry_utc','trade_date'])
    result = engine.metrics(trades,dates)
    daily = trades.groupby('trade_date').net_points.sum().reindex(dates,fill_value=0)
    best3 = float(trades.net_points.nlargest(3).sum())
    result.update(max_drawdown_usd=result['max_drawdown_points']*20,
                  drawdown_definition='Realized closed-trade equity including initial zero; NOT intratrade mark-to-market drawdown',
                  worst_day=str(daily.idxmin()) if len(daily) else None,
                  worst_day_points=float(daily.min()) if len(daily) else None,
                  worst_day_usd=float(daily.min()*20) if len(daily) else None,
                  best3_net_points=best3,
                  best3_share_net_profit_pct=100*best3/result['net_points'] if result['net_points']>0 else None,
                  net_points_without_best3=result['net_points']-best3,
                  ci_definition='95% interval for mean net points per eligible session, including no-trade zero sessions',
                  total_net_ci_low=result['ci_low']*len(dates) if result['ci_low'] is not None else None,
                  total_net_ci_high=result['ci_high']*len(dates) if result['ci_high'] is not None else None)
    return result


def summarize(trades, eligibility, daily, start, end):
    out = {}
    for strategy in STRATEGIES:
        e = eligibility[eligibility.strategy.eq(strategy) & eligibility.trade_date.between(start,end) & eligibility.eligible]
        t = trades[trades.strategy.eq(strategy) & trades.trade_date.between(start,end)]
        views = {}
        for view in ['all','clean']:
            ve = e if view=='all' else e[e.data_quality_flag.eq('ok')]
            dates = sorted(ve.trade_date.unique())
            vt = t[t.trade_date.isin(dates)]
            views[view] = extra_metrics(vt,dates)
        out[strategy] = views
    return out


def verdict(metrics, protocol):
    r = protocol['pass_rule']
    checks = {
        'sample_size':metrics['eligible_days']>=r['minimum_eligible_days'],
        'net_profit':metrics['net_points']>r['net_points_gt'],
        'profit_factor':metrics['profit_factor'] is not None and metrics['profit_factor']>r['profit_factor_gt'],
        'positive_95pct_lower_bound':metrics['ci_low'] is not None and metrics['ci_low']>r['mean_daily_ci_low_gt'],
        'significant_primary_test':metrics['p_value'] is not None and metrics['p_value']<r['two_sided_block_bootstrap_p_lt']}
    return ('HOLDOUT_PASSED' if all(checks.values()) else 'HOLDOUT_FAILED'), checks


def verify_trades(master, trades):
    for r in trades.itertuples():
        g = master[(master.contract.eq(r.contract)) & master.trade_date.eq(r.trade_date)]
        entry, signal, exitbar = map(pd.Timestamp,[r.entry_utc,r.signal_utc,r.exit_bar_utc])
        assert entry == signal+pd.Timedelta(minutes=1)
        assert entry in g.index and exitbar in g.index
        assert entry < engine.time_at(r.trade_date,'12:00') and exitbar < engine.time_at(r.trade_date,'12:00')
        assert r.entry_price == g.at[entry,'open']
        assert math.isclose(r.net_points,r.direction*(r.exit_price-r.entry_price)-1.225,abs_tol=1e-9)
        assert math.isclose(r.net_usd,20*r.net_points,abs_tol=1e-9)
        assert (r.contract,r.trade_date) == (g.contract.iloc[0],g.trade_date.iloc[0])
        replay = engine.simulate(g,signal,r.direction,.25*float(g.atr14_prior.iloc[0]),
                                  .5*float(g.atr14_prior.iloc[0]) if r.strategy!='C_VWAP_extreme' else None,
                                  target=float(g.at[signal,'vwap_close']) if r.strategy=='C_VWAP_extreme' else None)
        assert replay is not None
        for key in ['entry_price','exit_price','stop','target','gross_points','net_points','exit_reason','both_hit_bar']:
            assert replay[key] == getattr(r,key), (r.trade_date,key)
    assert not trades.duplicated(['strategy','trade_date']).any()


def report(summary):
    m = summary['holdout']['B_ORB15']['all']
    c = summary['combined']['B_ORB15']['all']
    q = summary['quality']
    fmt = lambda v: 'niet beschikbaar' if v is None else f'{v:,.3f}'
    lines = ['# Niveau 3 — ORB 15m holdout-validatie', '',
             'Periode: 18 april–30 september 2025. Alleen ORB 15m is de primaire hypothese. De overige drie schermen zijn referenties.', '',
             '## Eindoordeel', '', f"**{summary['status']}**. Dit is een historische vaste-regels-vervolgtest, geen prospectieve registratie of garantie voor live rendement.", '',
             '| Maatstaf | Holdout | Gecombineerd dec 2024–sep 2025 |', '|---|---:|---:|']
    for label,key in [('Eligible sessies','eligible_days'),('Trades','trades'),('Netto NQ-punten','net_points'),('Netto USD, één NQ','net_usd'),('Winrate (fractie)','win_rate'),('Profit factor','profit_factor'),('Maximale gerealiseerde drawdown, punten','max_drawdown_points'),('Maximale gerealiseerde drawdown, USD','max_drawdown_usd'),('Grootste verliesdag, punten','worst_day_points'),('Beste 3 / netto winst (%)','best3_share_net_profit_pct'),('Netto zonder beste 3, punten','net_points_without_best3'),('95% CI ondergrens gemiddelde eligible dag','ci_low'),('95% CI bovengrens gemiddelde eligible dag','ci_high'),('Tweezijdige bootstrap p','p_value')]:
        lines.append(f'| {label} | {fmt(m[key])} | {fmt(c[key])} |')
    lines += ['',f"Grootste verliesdag holdout: {m['worst_day']}. Drawdown is closed-trade equity, niet intratrade mark-to-market.", '',
              '## Datadekking', '',
              f"{q['scheduled_open_sessions']} geplande open civil-sessiondagen; {q['observed_sessions']} met bars; {q['eligible_orb15']} eligible ORB15; {q['clean_eligible_orb15']} in de clean-sensitiviteit.",
              f"{q['missing_minutes']} ontbrekende minuten in geselecteerde sessies na kalendercorrectie. Feestdagen worden als special_session gemarkeerd, niet automatisch als corrupt.",
              'De primaire all-view vereist een volledige VWAP-prefix tot 12:00 en onveranderde ATR-/volumewarmup. Een gat na 12:00 kan in all-view blijven, maar niet in clean-view.',
              'Good Friday 18 april is gesloten. De kalender gebruikt NY civil-sessiondagen zoals de bevroren engine, niet CME clearing TradeDate. Juli 4 kan daardoor apart van de officiële clearingdatum voorkomen.', '',
              '## Rollover vooraf vastgelegd', '']
    for r in summary['rollovers']:
        lines += [f"- {r['from']} → {r['to']}: beslissing {r['decision_session']}, volumes {r['old_volume']} versus {r['new_volume']}; ingang {r['effective_session']} ({r['effective_utc']})."]
    lines += ['', 'Vergelijking: eerste inkomende volume-overwicht in een afgesloten sessie; overstap volgende sessie. Geen strategie-uitkomsten gebruikt. Vorige sessievolume wordt vóór de volgende opening bekend verondersteld, niet vendor-vintage geverifieerd.', '',
              '## Warmup en uitval per contract', '', '| Contract | Sessies | ATR-ready | ORB15 eligible |', '|---|---:|---:|---:|']
    for r in q['by_contract']:
        lines += [f"| {r['contract']} | {r['sessions']} | {r['atr_ready']} | {r['eligible']} |"]
    lines += ['', 'Geen ATR of historische volumereferentie tussen contracten overgedragen. Dunne pre-rollcontracten leveren onvoldoende volledige RTH-historie, vooral voor NQZ25. Niet-eligible dagen hebben geen backtestresultaat. Een volledig verzamelde kalenderperiode is dus geen volledig verhandelde holdout.', '',
              '## Statistiek en kosten', '',
              'Exact bevroren engine: 2 ticks slippage per kant plus $4,50 RT commissie = $24,50 = 1,225 NQ-punten. Signaal na voltooide bar, entry volgende minuutopen, stop vóór target bij beide geraakt, alle posities vóór 12:00 NY gesloten. Geen contractoverstap met open positie.',
              '2000 circular moving-block bootstrapreplicaties, blokken van 5 eligible dagen, seed 20261020. CI is voor gemiddelde dag-PnL inclusief nullen op eligible dagen zonder trade. P-waarde tweezijdig rond gecentreerde nulverdeling. Kalendergaten tussen eligible dagen zijn niet gevuld met fictieve trades.',
              'Enige primaire hypothese: ORB15, all-view. Geen multipliciteitscorrectie voor die ene primaire holdouttest. Referenties en clean-view zijn sensitiviteiten. Gecombineerde statistiek hergebruikt de ontdekkingsperiode en is geen onafhankelijke bevestiging.',
              'Passregel vooraf: >=20 eligible dagen, positieve nettowinst, PF>1, CI-ondergrens>0 en p<0,05. Concentratierisico wordt gerapporteerd, geen achteraf toegevoegde passdrempel.', '',
              '## Reproduceerbaarheid en beperkingen', '',
              f"Oorspronkelijke ORB15-ledger exact gereproduceerd: {summary['baseline_reproduced']}. Frozen engine SHA-256: `{summary['frozen_engine_sha256']}`.",
              'Alle 30 bron-CSV-hashes staan in research/holdout-protocol.json. Ruwe bars, trades en Parquet blijven in genegeerde lokale mappen. Publiek alleen aggregaten en bron-/codehashes.',
              'Historische CME-kalenderpagina toont inmiddels 2026. De historische sluitingen zijn gereconstrueerd uit onderstaande contemporaine data-aanbieder-/brokerschema’s en vergeleken met de bars; geen afzonderlijk gecertificeerd CME-2025-kalenderbestand. Geen toestemming tot herdistributie van ruwe Barchart-data verondersteld.', '',
              'De blinde volgorde is lokaal in Git vastgelegd vóór de eerste signaalrun. De data waren vooraf op kwaliteit bekeken; dit is geen extern geregistreerde of onafhankelijk uitgevoerde studie. Na deze test is deze holdout verbruikt. Niet optimaliseren en dezelfde periode opnieuw als holdout presenteren.', '', 'Kalenderbronnen:', '']
    lines += ['- '+url for url in summary['calendar_sources']]
    lines += ['', '## Referentieschermen (niet promoten op basis van deze run)', '', '| Scherm | Trades | Netto punten | PF | p |', '|---|---:|---:|---:|---:|']
    for strategy in STRATEGIES:
        r = summary['holdout'][strategy]['all']
        lines += [f"| {strategy} | {r['trades']} | {fmt(r['net_points'])} | {fmt(r['profit_factor'])} | {fmt(r['p_value'])} |"]
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir',type=Path,default=REPO/'data/raw')
    parser.add_argument('--record-first-run',action='store_true',help='Create first result reference once; never overwrite a seen reference')
    args = parser.parse_args(argv)
    protocol = json.loads((REPO/'research/holdout-protocol.json').read_text())
    reference_path = REPO/'research/holdout-reference.json'
    if args.record_first_run and reference_path.exists():
        raise ValueError('First-run reference already exists')
    if not args.record_first_run and not reference_path.exists():
        raise ValueError('Published first-run reference missing')
    preflight(args.raw_dir,protocol)
    work = Path(tempfile.mkdtemp(prefix='holdout-',dir=REPO/'artifacts'))
    result = {'status':'FAILED'}
    try:
        print('1/5 SHA256 preflight; recompute source-only volume rolls',flush=True)
        full, audits = data.load_all(args.raw_dir,protocol['sources'])
        decisions = data.rollovers(full)
        compare(protocol['rollovers'],decisions)
        # Persist outcome-blind stage evidence BEFORE features or signals.
        write(work/'data-stage.json',{'protocol_sha256':data.sha(REPO/'research/holdout-protocol.json'),
                                     'rollovers':decisions,'audits':audits})
        print('2/5 Frozen features per contract/session, historical calendar override only',flush=True)
        original_grid = engine.expected_grid
        engine.expected_grid = data.grid
        try:
            enriched,daily,snapshots,gaps = engine.build_features(full)
        finally:
            engine.expected_grid = original_grid
        master = enriched[data.select(enriched,decisions)].sort_index()
        daily = daily[data.select(daily,decisions)].sort_values('trade_date').reset_index(drop=True)
        snapshots = snapshots[data.select(snapshots,decisions)]
        gaps = gaps[data.select(gaps,decisions)]
        # Calendar labels are quality metadata, no change to frozen eligibility.
        special = master.trade_date.isin(data.CLOSES)
        master.loc[special,'data_quality_flag'] = master.loc[special,'data_quality_flag'].map(lambda x:'special_session' if x=='ok' else 'special_session;'+x)
        daily.loc[daily.trade_date.isin(data.CLOSES),'data_quality_flag'] = daily.loc[daily.trade_date.isin(data.CLOSES),'data_quality_flag'].map(lambda x:'special_session' if x=='ok' else 'special_session;'+x)
        assert master.index.is_unique and master.index.is_monotonic_increasing
        assert master.groupby('trade_date').contract.nunique().max()==1
        for _,g in master.groupby(['contract','trade_date']):
            assert pd.isna(g.return_1m.iloc[0])
        print('3/5 Frozen four hypothesis screens (ORB15 only primary)',flush=True)
        trades, eligibility = engine.hypotheses(master)
        verify_trades(master,trades)
        # Full original ledger, not merely its headline count or PnL.
        baseline = trades[trades.trade_date.le('2025-04-17')].copy()
        baseline_dates = sorted(master.loc[master.trade_date.le('2025-04-17'),'trade_date'].unique())
        halfmap = {d:'first' if i<len(baseline_dates)//2 else 'second' for i,d in enumerate(baseline_dates)}
        baseline['half'] = baseline.trade_date.map(halfmap)
        old_manifest = json.loads((REPO/'research/reproduction-manifest.json').read_text())
        # Match serialization of the original published CSV ledger.
        baseline.to_csv(work/'baseline-trades.csv',index=False)
        ledger = trade_ledger_sha256(pd.read_csv(work/'baseline-trades.csv').to_dict('records'))
        assert ledger == old_manifest['expected']['orb15_trade_ledger_sha256'], ledger
        holdout = summarize(trades,eligibility,daily,data.START,data.END)
        combined = summarize(trades,eligibility,daily,'2024-12-30',data.END)
        status, checks = verdict(holdout['B_ORB15']['all'],protocol)
        hd = daily[daily.trade_date.between(data.START,data.END)]
        he = eligibility[eligibility.strategy.eq('B_ORB15') & eligibility.trade_date.between(data.START,data.END)]
        scheduled = [d.strftime('%Y-%m-%d') for d in pd.bdate_range(data.START,data.END) if len(data.grid(d.strftime('%Y-%m-%d')))]
        coverage = []
        for contract,g in hd.groupby('contract'):
            dates = set(g.trade_date)
            coverage.append({'contract':contract,'sessions':len(g),'atr_ready':int(g.atr14_prior.notna().sum()),
                             'eligible':int(he[he.trade_date.isin(dates)].eligible.sum())})
        quality = {'scheduled_open_sessions':len(scheduled),'closed_sessions':['2025-04-18'],
                   'observed_sessions':len(hd),'absent_open_sessions':sorted(set(scheduled)-set(hd.trade_date)),
                   'eligible_orb15':holdout['B_ORB15']['all']['eligible_days'],
                   'clean_eligible_orb15':holdout['B_ORB15']['clean']['eligible_days'],
                   'missing_minutes':int(hd.missing_minutes.sum()),'by_contract':coverage,
                   'selected_holdout_bars':int(master.trade_date.between(data.START,data.END).sum()),
                   'daily':hd[['contract','trade_date','data_quality_flag','missing_minutes','atr_history_count']].to_dict('records')}
        code_files = ['engine.py','barchart.py','holdout_data.py','holdout.py','cli.py']
        summary = {'schema_version':1,'status':status,'promotion_checks':checks,
                   'period':{'start':data.START,'end':data.END},'primary_strategy':'B_ORB15',
                   'cost_rt_usd':24.5,'baseline_reproduced':True,'baseline_orb15_ledger_sha256':ledger,
                   'frozen_engine_sha256':protocol['frozen_engine_sha256'],
                   'code_sha256':{name:data.sha(Path(__file__).parent/name) for name in code_files},
                   'protocol_sha256':data.sha(REPO/'research/holdout-protocol.json'),
                   'source_sha256':[x['sha256'] for x in protocol['sources']],
                   'rollovers':decisions,'calendar_sources':protocol['calendar_sources'],
                   'quality':quality,'holdout':holdout,'combined':combined,
                   'equity':{s:trades[trades.strategy.eq(s)&trades.trade_date.between(data.START,data.END)][['trade_date','net_points','net_usd']].assign(equity_points=lambda x:x.net_points.cumsum()).to_dict('records') for s in STRATEGIES}}
        print('4/5 Reconcile ledger, realized PnL, zero-day bootstrap, result reference',flush=True)
        preflight(args.raw_dir,protocol)
        public = REPO/'public/data/research-holdout.json'
        if args.record_first_run:
            write(reference_path,summary)
            write(public,summary)
            (REPO/'docs/LEVEL3_HOLDOUT_REPORT.md').write_text(report(summary))
        else:
            compare(json.loads(reference_path.read_text()),engine.clean(summary))
            compare(json.loads(public.read_text()),engine.clean(summary))
            if (REPO/'docs/LEVEL3_HOLDOUT_REPORT.md').read_text()!=report(summary):
                raise ValueError('Published report differs from rerun')
        # Detailed proprietary outputs stay private.
        master.reset_index(names='timestamp_utc').to_parquet(work/'master.parquet',index=False)
        trades.to_csv(work/'trades.csv',index=False)
        eligibility.to_csv(work/'eligibility.csv',index=False)
        daily.to_csv(work/'session-quality.csv',index=False)
        snapshots.to_csv(work/'snapshots.csv',index=False)
        gaps.to_csv(work/'missing-minutes.csv',index=False)
        write(work/'summary.json',summary)
        result = {'status':'PASS','hypothesis_status':status,'primary':holdout['B_ORB15']['all'],
                  'protocol_sha256':summary['protocol_sha256'],
                  'reference_sha256':data.sha(reference_path),'baseline_reproduced':True}
        print('5/5 REPRODUCTION PASS; hypothesis '+status,flush=True)
        print(json.dumps(engine.clean(result),indent=2))
        return 0
    except Exception as exc:
        result['error'] = str(exc)
        raise
    finally:
        write(work/'verification-report.json',result)
        print('Private artifacts: '+str(work.relative_to(REPO)),flush=True)


if __name__ == '__main__':
    raise SystemExit(main())
