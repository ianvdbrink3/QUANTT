"""Descriptive diagnostics only. Does not modify or rerun strategy selection."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
import pandas as pd
from . import engine, holdout, holdout_data as data

REPO = data.REPO


def stats(values):
    a = pd.Series(values,dtype=float).dropna()
    return {'n':len(a),'mean':float(a.mean()) if len(a) else None,
            'median':float(a.median()) if len(a) else None,
            'p25':float(a.quantile(.25)) if len(a) else None,
            'p75':float(a.quantile(.75)) if len(a) else None}


def trade_diagnostics(master, trades):
    rows = []
    for r in trades.itertuples():
        day = master[master.trade_date.eq(r.trade_date)]
        entry,signal = pd.Timestamp(r.entry_utc),pd.Timestamp(r.signal_utc)
        hi,lo = float(day.at[signal,'orb15_high']),float(day.at[signal,'orb15_low'])
        atr = float(day.at[signal,'atr14_prior'])
        row = {'trade_date':r.trade_date,'contract':r.contract,'direction':r.direction,
               'net_points':r.net_points,'atr14_prior':atr,
               'mfe_exit_bar_bound':r.mfe_bar_bound_points,
               'mae_exit_bar_bound':r.mae_bar_bound_points,
               'mfe_exit_bar_bound_atr':r.mfe_bar_bound_points/atr,
               'mae_exit_bar_bound_atr':r.mae_bar_bound_points/atr,
               'entry_open_inside_range':bool(lo<=r.entry_price<=hi)}
        for n in [1,5,15]:
            end = entry+pd.Timedelta(minutes=n)
            w = engine.window(day,entry,end)
            complete = engine.complete(w,entry,end)
            # A fixed post-entry descriptive path, regardless of actual earlier SL/TP.
            row[f'return_inside_{n}m'] = bool(w.close.between(lo,hi,inclusive='both').any()) if complete else None
            if n==15:
                row['forward15_complete'] = complete
                row['forward15_mfe'] = (max(0,float(w.high.max())-r.entry_price) if r.direction==1 else max(0,r.entry_price-float(w.low.min()))) if complete else None
                row['forward15_mae'] = (max(0,r.entry_price-float(w.low.min())) if r.direction==1 else max(0,float(w.high.max())-r.entry_price)) if complete else None
        rows.append(row)
    return pd.DataFrame(rows)


def period_summary(daily,eligibility,trades,diagnostics,start,end):
    e = eligibility[eligibility.strategy.eq('B_ORB15') & eligibility.eligible & eligibility.trade_date.between(start,end)]
    dates = sorted(e.trade_date.unique())
    d = daily[daily.trade_date.isin(dates)]
    t = trades[trades.strategy.eq('B_ORB15') & trades.trade_date.isin(dates)]
    x = diagnostics[diagnostics.trade_date.isin(dates)]
    sides = {}
    for label,side in [('long',1),('short',-1)]:
        st = t[t.direction.eq(side)]
        losses = -st.loc[st.net_points.lt(0),'net_points'].sum()
        sides[label] = {'trades':len(st),'net_points':float(st.net_points.sum()),
                        'mean_net_points':float(st.net_points.mean()) if len(st) else None,
                        'win_rate':float(st.net_points.gt(0).mean()) if len(st) else None,
                        'profit_factor':float(st.loc[st.net_points.gt(0),'net_points'].sum()/losses) if losses>0 else None}
    returns = {}
    for n in [1,5,15]:
        a = x[f'return_inside_{n}m'].dropna()
        returns[str(n)] = {'trades_with_complete_window':len(a),'returned_inside':int(a.sum()),
                           'fraction':float(a.mean()) if len(a) else None}
    return {'period':[start,end],'eligible_days':len(d),'trades':len(t),
            'orb15_points':stats(d.orb15_range_points),'orb15_pct_prior_atr':stats(d.orb15_range_pct_atr),
            'prior_rth_atr14_points':stats(d.atr14_prior),
            'actual_same_day_rth_range_points':stats(d.rth_high-d.rth_low),
            'long_short':sides,'mfe_exit_bar_bound_points':stats(x.mfe_exit_bar_bound),
            'mae_exit_bar_bound_points':stats(x.mae_exit_bar_bound),
            'mfe_exit_bar_bound_atr':stats(x.mfe_exit_bar_bound_atr),
            'mae_exit_bar_bound_atr':stats(x.mae_exit_bar_bound_atr),
            'forward15_mfe_points':stats(x.forward15_mfe),'forward15_mae_points':stats(x.forward15_mae),
            'return_inside_range_after_entry':returns,
            'entry_open_inside_range':int(x.entry_open_inside_range.sum())}


def warmup_audit(full,decisions):
    rows = []
    for contract,g in full.groupby('contract'):
        previous_complete = False
        previous_close = np.nan
        valid_tr = []
        for day,bars in g.groupby('trade_date',sort=True):
            w = engine.window(bars,engine.time_at(day,'09:30'),engine.time_at(day,'16:00'))
            complete = engine.complete(w,engine.time_at(day,'09:30'),engine.time_at(day,'16:00'))
            row = {'contract':contract,'trade_date':day,'rth_bars':len(w),
                   'rth_complete':complete,'prior_valid_tr_count':len(valid_tr),
                   'prior_atr14':float(np.mean(valid_tr[-14:])) if len(valid_tr)>=14 else None}
            tr = max(float(w.high.max()-w.low.min()),abs(float(w.high.max())-previous_close),abs(float(w.low.min())-previous_close)) if complete and previous_complete else None
            row['valid_tr_today'] = tr is not None
            rows.append(row)
            if tr is not None:
                valid_tr.append(tr)
            previous_complete = complete
            previous_close = float(w.close.iloc[-1]) if complete else np.nan
    audit = pd.DataFrame(rows)
    summary = []
    for roll in decisions:
        c,date = roll['to'],roll['effective_session']
        g = audit[audit.contract.eq(c)].sort_values('trade_date')
        pre = g[g.trade_date.lt(date)]
        day = g[g.trade_date.eq(date)].iloc[0]
        ready = g[g.prior_atr14.notna()]
        active_unready = g[g.trade_date.ge(date)&g.prior_atr14.isna()]
        summary.append({'contract':c,'roll_session':date,'raw_first_session':g.trade_date.min(),
                        'pre_roll_sessions':len(pre),'pre_roll_complete_rth':int(pre.rth_complete.sum()),
                        'pre_roll_valid_tr':int(pre.valid_tr_today.sum()),
                        'valid_prior_tr_at_roll':int(day.prior_valid_tr_count),
                        'atr_ready_at_roll':bool(pd.notna(day.prior_atr14)),
                        'first_atr_ready_session':ready.trade_date.min() if len(ready) else None,
                        'active_sessions_without_atr_in_available_data':len(active_unready),
                        'last_available_prior_tr_count':int(g.prior_valid_tr_count.iloc[-1]),
                        'zero_lost_sessions_possible_under_frozen_rules':bool(pd.notna(day.prior_atr14))})
    return audit,summary


def markdown(result):
    a,b = result['in_sample'],result['out_of_sample']
    fmt = lambda x: 'n.v.t.' if x is None else f'{x:.2f}'
    lines = ['# ORB 15m post-mortem en contracteigen ATR-opwarming','',
             'Beschrijvend onderzoek op inmiddels bekeken data. Geen parameteroptimalisatie, nieuwe edgeclaim of wijziging aan de bevroren 0.9-engine/holdout.','',
             '## Vergelijking van de vooraf bestaande eligible sessies','',
             '| Maatstaf | In-sample: 42 eligible dagen | Holdout: 81 eligible dagen |','|---|---:|---:|']
    for label,key in [('Gemiddelde ORB15, punten','orb15_points'),('Gemiddelde ORB15 / eerdere ATR, %','orb15_pct_prior_atr'),('Gemiddelde eerdere 14-RTH ATR, punten','prior_rth_atr14_points'),('Gemiddelde gerealiseerde RTH-range die dag, punten','actual_same_day_rth_range_points'),('Gemiddelde MFE tot exitbar, bovengrens in punten','mfe_exit_bar_bound_points'),('Gemiddelde MAE tot exitbar, bovengrens in punten','mae_exit_bar_bound_points'),('Gemiddelde MFE / ATR, exitbar-bovengrens','mfe_exit_bar_bound_atr'),('Gemiddelde MAE / ATR, exitbar-bovengrens','mae_exit_bar_bound_atr'),('Gemiddelde MFE eerste vaste 15 minuten, punten','forward15_mfe_points'),('Gemiddelde MAE eerste vaste 15 minuten, punten','forward15_mae_points')]:
        lines.append(f"| {label} | {fmt(a[key]['mean'])} (n={a[key]['n']}) | {fmt(b[key]['mean'])} (n={b[key]['n']}) |")
    lines += ['', 'De openingsrange was in absolute punten kleiner en de eerdere RTH-ATR lager. De openingsrange als percentage van die ATR bleef vrijwel gelijk. De winst kwam in-sample volledig uit shorts; in de holdout werden juist shorts verlieslatend. De snelle terugkeer in de ORB-range nam niet toe. Dit onderbouwt geen verhaal dat meer snelle failed breakouts het verlies veroorzaakten.', '',
              'ATR is de ongewijzigde SMA van de laatste 14 geldige RTH true ranges, uitsluitend vóór de onderzochte dag en van hetzelfde contract. De gerealiseerde dagrange is een aparte achterafmeting, geen signaalinput. ORB/ATR-statistiek betreft alle eligible dagen; MFE/MAE betreft alleen de werkelijk geselecteerde trades.','',
              '## Long versus short','', '| Periode/richting | Trades | Netto punten | Gemiddelde/trade | Winrate | PF |','|---|---:|---:|---:|---:|---:|']
    for label,p in [('In-sample',a),('Holdout',b)]:
        for side,s in p['long_short'].items():
            lines += [f"| {label} {side} | {s['trades']} | {fmt(s['net_points'])} | {fmt(s['mean_net_points'])} | {fmt(100*s['win_rate'])}% | {fmt(s['profit_factor'])} |"]
    lines += ['', '## Failed breakout: definitie vóór deze beschrijvende telling','',
              'Een terugkeer betekent ten minste één voltooide minuutclose binnen de oorspronkelijke 09:30–09:45 ORB-range, inclusief de grenzen. De klok start bij de echte entry (minuut na het signaal). Primair betekent direct: binnen de eerste 5 minuten. Ook 1 en 15 minuten worden getoond, niet gebruikt om een parameter te kiezen. Dit zijn vaste post-entryvensters, onafhankelijk van een eerdere SL/TP-exit; dus geen handelssignaal of claim dat de positie bij terugkeer nog open was.','',
              '| Venster | In-sample | Holdout |','|---|---:|---:|']
    for n in ['1','5','15']:
        x,y = a['return_inside_range_after_entry'][n],b['return_inside_range_after_entry'][n]
        lines += [f"| {n} minuten | {x['returned_inside']}/{x['trades_with_complete_window']} ({fmt(100*x['fraction'])}%) | {y['returned_inside']}/{y['trades_with_complete_window']} ({fmt(100*y['fraction'])}%) |"]
    lines += ['', f"Bij de entry-open al binnen de range: {a['entry_open_inside_range']} in-sample en {b['entry_open_inside_range']} holdout.",
              'MFE/MAE tot exit gebruikt de oorspronkelijke bar-bounds: de high/low van de exitminuut kan na de exit zijn ontstaan. De vaste 15-minutenpaden zijn marktbeschrijving na entry, geen alternatief doorgerekend exitmodel. Uit minuutbars is de exacte intrabarvolgorde niet afleidbaar.','',
              '## ATR-rolloverdiagnose','',
              '**De engine warmt het niet-actieve contract al op vóór de selectie van het actieve contract.** `build_features(full)` draait per contract over alle beschikbare bronbars; pas daarna wordt de rolloverselectie toegepast. Er is geen bewuste reset op de rollover. De beperking is de kwaliteit en lengte van de contracteigen RTH-historie.','',
              '| Inkomend contract | Overlapdagen vóór roll | Volledige RTH vóór roll | Geldige TR vóór roll | Eerste ATR-ready dag | Actieve dagen zonder ATR² |','|---|---:|---:|---:|---|---:|']
    for r in result['warmup']:
        lines += [f"| {r['contract']} | {r['pre_roll_sessions']} | {r['pre_roll_complete_rth']} | {r['pre_roll_valid_tr']} | {r['first_atr_ready_session'] or 'niet bereikt t/m 30 september'} | {r['active_sessions_without_atr_in_available_data']} |"]
    lines += ['', '² Alleen de datums waarop dit contract actief is binnen de beschikbare onderzoeksperiode, niet een voorspelling voor latere dagen.',
              'Voor een geldige true range moeten zowel de huidige als de voorafgaande geobserveerde sessie een volledige RTH hebben. Een dun verhandeld contract met veel minuten zonder bar mist daardoor meer dan alleen kalenderdagen. Feestdagen en een enkele ontbrekende RTH-minuut kunnen de 14 geldige observaties verder spreiden.','',
              '## Volgende engine-generatie: ontwerp, niet retrospectief toegepast','',
              '1. Bewaar een contracteigen as-of-featurestaat, ook voor niet-actieve contracten. Sleutel: contract, RTH-definitie, kwaliteitsbeleid, bronhash en laatste voltooide sessie. Nooit een doorlopende back-adjusted reeks als ATR-bron gebruiken.',
              '2. Voer vóór iedere roll een readiness-gate uit: >=14 geldige eerdere TR-observaties, controle op vorige close en afzonderlijk voldoende same-clock volumehistorie en complete overnight-prefix. Niet alleen ATR bepaalt eligibility.',
              '3. Bestaande overlap hergebruiken is al ondersteund en geeft met deze bestanden geen nulverlies. Verzamel voor volgende studies voldoende eerdere contracteigen historie vóór de roll. Onder de strikte volledige-minuutregel is doorgaans minstens 15 volledige RTH-sessies nodig; feestdagen/gaten kunnen meer geschiedenis vereisen.',
              '4. Alternatief uitsluitend voor een nieuwe, vooraf vastgelegde engine: betrouwbare contracteigen RTH-dagaggregaten met exact dezelfde 09:30–16:00 NY-definitie en aantoonbare as-of-beschikbaarheid, of expliciete vendorbevestiging dat ontbrekende minuten echt geen transacties betekenen. Niet stilzwijgend lege minuten forward-fillen of ontbrekende bars als bewezen nulhandel behandelen.',
              '5. Nul ATR-uitval bij roll is alleen mogelijk als die gate vooraf slaagt. Geen garantie met de huidige ruwe bestanden; geen features van het uitgaande contract lenen. De bevroren HOLDOUT_FAILED-uitkomst blijft intact.','',
              '## Interpretatiegrenzen','',
              'Dit vergelijkt geselecteerde eligible dagen en trades, niet alle kalenderdagen. De septembercontract-warmup veroorzaakt selectieve dekking. Verschillen in volatiliteit of failed-breakoutpercentages zijn beschrijvende samenhang, geen aangetoonde oorzaak van verlies. Er is geen parameter of richting gewijzigd en geen nieuwe strategie geselecteerd.','',
              'Reproduceren: eerst `npm run verify:holdout`, daarna `npm run diagnose:orb15`. Bron- en inputhashes staan in de publieke diagnose-export; ruwe bars en uitvoeringsprijzen blijven privé.']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--holdout-run',type=Path)
    args = parser.parse_args(argv)
    evidence = json.loads((REPO/'research/holdout-verification-evidence.json').read_text())
    runs = [args.holdout_run] if args.holdout_run else sorted((REPO/'artifacts').glob('holdout-*'),key=lambda p:p.stat().st_mtime,reverse=True)
    run = next((p for p in runs if p and (p/'verification-report.json').exists() and json.loads((p/'verification-report.json').read_text()).get('status')=='PASS'),None)
    if run is None:
        raise ValueError('Run npm run verify:holdout first')
    for name,digest in evidence['private_output_sha256'].items():
        if data.sha(run/name)!=digest:
            raise ValueError('Verified holdout input changed: '+name)
    protocol = json.loads((REPO/'research/holdout-protocol.json').read_text())
    holdout.preflight(REPO/'data/raw',protocol)
    master = pd.read_parquet(run/'master.parquet').set_index('timestamp_utc')
    master.index = pd.to_datetime(master.index,utc=True)
    daily = pd.read_csv(run/'session-quality.csv')
    eligibility = pd.read_csv(run/'eligibility.csv')
    trades = pd.read_csv(run/'trades.csv')
    full,_ = data.load_all(REPO/'data/raw',protocol['sources'])
    selected = full[data.select(full,protocol['rollovers'])].sort_index()
    # Parquet is private, not a trusted cache: reconcile every raw price/volume.
    columns = [*data.barchart.FIELDS,'contract','trade_date']
    pd.testing.assert_frame_equal(master[columns],selected[columns],check_dtype=False,check_names=False)
    for r in trades[trades.strategy.eq('B_ORB15')].itertuples():
        feature = daily[daily.trade_date.eq(r.trade_date)].iloc[0]
        at = master.loc[pd.Timestamp(r.signal_utc)]
        assert np.isclose(at.orb15_high,feature.orb15_high)
        assert np.isclose(at.orb15_low,feature.orb15_low)
        assert np.isclose(at.atr14_prior,feature.atr14_prior)
    diagnostics = trade_diagnostics(master,trades[trades.strategy.eq('B_ORB15')])
    a = period_summary(daily,eligibility,trades,diagnostics,'2024-12-30','2025-04-17')
    b = period_summary(daily,eligibility,trades,diagnostics,data.START,data.END)
    assert (a['eligible_days'],b['eligible_days'],a['trades'],b['trades'])==(42,81,37,76)
    audit,warmup = warmup_audit(full,protocol['rollovers'])
    for r in warmup:
        end = next((x['effective_session'] for x in protocol['rollovers'] if x['from']==r['contract']),data.END)
        z = audit[audit.contract.eq(r['contract']) & audit.trade_date.ge(r['roll_session']) & audit.trade_date.lt(end if end!=data.END else '2025-10-01')]
        r['active_sessions_without_atr_in_available_data'] = int(z.prior_atr14.isna().sum())
    # Independent same-contract ATR audit must match all selected frozen feature values.
    merged = daily.merge(audit,on=['contract','trade_date'],validate='one_to_one')
    assert np.allclose(merged.atr14_prior,merged.prior_atr14,equal_nan=True)
    result = {'schema_version':1,'classification':'DESCRIPTIVE_POST_HOC_NOT_NEW_HOLDOUT',
              'frozen_engine_unchanged':True,'frozen_holdout_status':'HOLDOUT_FAILED',
              'input_sha256':evidence['private_output_sha256'],
              'source_sha256':[s['sha256'] for s in protocol['sources']],
              'in_sample':a,'out_of_sample':b,'warmup':warmup,
              'definitions':{'direct_failed_breakout':'At least one minute CLOSE inside original ORB15 within first 5 post-entry bars, inclusive boundaries; fixed diagnostic path, may occur after simulated exit',
                             'mfe_mae':'Exit-minute OHLC extrema are bounds, not exact intrabar excursions; separate fixed 15m diagnostic ignores actual exit',
                             'atr':'Frozen SMA14 prior same-contract valid RTH TR; no transfer, no parameter optimization'}}
    out = REPO/'artifacts/postmortem'
    out.mkdir(exist_ok=True)
    diagnostics.to_csv(out/'trade-diagnostics.csv',index=False)
    audit.to_csv(out/'all-contract-warmup.csv',index=False)
    holdout.write(REPO/'public/data/research-postmortem.json',result)
    (REPO/'docs/ORB15_POSTMORTEM_AND_ATR_ARCHITECTURE.md').write_text(markdown(result))
    print(json.dumps(engine.clean(result),indent=2,allow_nan=False))


if __name__=='__main__':
    main()
