"""Append-only technical review. Any signal replay is restricted to OLD discovery.

Never imports or scores historical2019-2021 prices through a candidate selector.
"""
import csv
import json
import numpy as np
import pandas as pd
from scripts import prepare_historical_contracts as h


def old_discovery_parity():
    from scripts.causal_map.__main__ import load_inputs
    from scripts.edge_marathon.core import select,fill
    from scripts.edge_marathon.features import calendar_context
    state,days,included,_,active,old_calendar,rolls=load_inputs()
    # Hard guard before selector/fill imports can ever receive a price array.
    if len(included)!=435 or any(not '2024-12-30'<=d<='2026-09-30' for d in days):
        raise PermissionError('Only the435 already-consumed discovery days may be replayed')
    class Router:
        def grid(self,day):
            return h.HistoricalCalendar().grid(day) if '2018-11-19'<=day<='2021-12-31' else old_calendar.grid(day)
    active=active.copy();active['usable']=True
    reconstructed=h.contexts(active,days,Router(),rolls)
    expected={(r['day'],r['model']):r for r in csv.DictReader((h.ROOT/'artifacts/edge-marathon/discovery-trades.csv').open())
        if r['model'] in ('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')}
    seen=set();counts={m:0 for m in ('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')}
    keys=('atr','PDH','PDL','prior_close','ONH','ONL','on_open','on_close')
    for day in included:
        old_prices,old_ctx=state[day];prices,ctx=reconstructed[day]
        for key in old_prices:
            np.testing.assert_array_equal(prices[key],old_prices[key])
        for key in keys:
            np.testing.assert_equal(ctx[key],old_ctx[key])
        assert h.cash_context(day)==calendar_context(day)
        ctx=dict(ctx,**h.cash_context(day))
        if day<'2025-01-01':ctx['tom']=False  # frozen incomplete-first-month rule
        for event in select(prices,ctx):
            if event['model'] not in counts:continue
            trade=fill(event,prices,ctx);key=(day,event['model']);old=expected.get(key)
            if old is None:raise AssertionError('Unexpected old-discovery trade')
            for field in ('decision','entry','end','direction','entry_price','exit_price','gross_points','net_points','mfe_points','mae_points'):
                if float(trade[field])!=float(old[field]):raise AssertionError('Old discovery parity changed '+field)
            counts[event['model']]+=1;seen.add(key)
    if seen!=set(expected):raise AssertionError('Missing old-discovery trades')
    return dict(status='EXACT_OLD_DISCOVERY_PARITY_ONLY',days=435,trade_counts=counts,
        compared_fields=list(keys),new_2019_2021_signals_computed=False,
        note='Adapter regression on already consumed2024Dec-2026Sep only, not independent confirmation.')


def review():
    integrity=h.verify()
    result=json.loads(h.RESULT.read_text())
    full=pd.read_parquet(h.OUT/'contract-bars.parquet')
    active=pd.read_parquet(h.OUT/'active-bars.parquet')
    daily=json.loads((h.OUT/'active-day-quality.json').read_text())
    prior={r['day']:r for r in json.loads((h.OUT/'prior-context.json').read_text())}
    c=h.HistoricalCalendar();prefix=[];coverage=[]
    schedule=[h.Activation('NQZ18','2018-11-19')]+[h.Activation(r['to'],r['effective_session']) for r in result['rollovers']]
    for r in result['rollovers']:
        day=r['effective_session'];cut=h.at(day,'09:30')
        schedule_asof=[s for s in schedule if s.session<=day]
        f=full[(full.index<cut)&full.usable]
        selected=h.select_active(f,schedule_asof)
        rolls=h.roll_spreads(f,schedule_asof)
        dates=[d['day'] for d in daily if d['day']<=day]
        ctx=h.contexts(selected,dates,c,rolls)[day][1]
        for a,b in [('atr','atr14_prior'),('PDH','PDH'),('PDL','PDL'),('ONH','ONH'),('ONL','ONL')]:
            expected=prior[day][b]
            np.testing.assert_equal(ctx[a],np.nan if expected is None else expected)
        prefix.append(dict(day=day,passed=True,current_RTH_absent_from_prefix=True,
            prior_ATR14_ready=bool(np.isfinite(ctx['atr'])),new_contract=r['to']))
        evidence=[]
        for contract in (r['from'],r['to']):
            g=full[(full.contract==contract)&(full.trade_date==r['decision_session'])]
            missing=c.grid(r['decision_session']).difference(g[g.usable].index)
            evidence.append(dict(contract=contract,missing=len(missing),
                missing_ny=[t.tz_convert('America/New_York').isoformat() for t in missing]))
        coverage.append(dict(old=r['from'],new=r['to'],decision_session=r['decision_session'],
            effective_session=day,observed_new_minus_old_volume=r['new_volume']-r['old_volume'],
            old_extra_unobserved_volume_needed_to_reverse_observed_order=r['new_volume']-r['old_volume']+1,
            missing=evidence,
            interpretation='Threshold is an algebraic sensitivity, NOT a bound on missing volume or proof of true crossover. No missing minute assigned zero volume.'))
    bad=[r for r in daily if '2019-01-02'<=r['day']<='2021-12-31' and r['normal_cash_session'] and not r['clean_full_RTH']]
    anomalies=[dict(day=r['day'],contract=r['contract'],missing_RTH=r['missing_rth_clocks'],
        boundary_0929_missing=not r['boundary_0929'],
        classification='MISSING_0929_BOUNDARY_ONLY' if r['rth_missing']==0 else r['gap_classification']) for r in bad]
    old_parity=old_discovery_parity()
    out=dict(status='TECHNICAL_REVIEW_NOT_OUTCOME_RELEASE',signals_on_registered_remainder=False,holdout_executed=False,
        integrity=integrity,old_discovery_parity=old_parity,actual_roll_open_prefix_tests=prefix,
        source_session_volume_review=coverage,active_anomalies=anomalies,
        root_report_note='2020-03-13 has390RTH bars but lacks09:29. Root COMPLETE labels its RTH-only gap classification, not full eligibility. This supplement explicitly corrects the presentation, not any exclusion or count.',
        remaining_blockers=[b for b in result['blockers'] if b!='NEW_FULL_WINDOW_ROUTE_OUTCOME_PARITY_NOT_EXECUTED'],
        not_proven=['complete CME date-specific holiday/halts','true volume in missing vendor minutes','license permissions','independent timestamps/tick fills'],
        no_price_imputation=True,external_publication=False)
    h.dump(h.ROOT/'research/historical-preparation-review.json',out)
    public={k:v for k,v in out.items() if k!='source_session_volume_review'}
    # Missing timestamp audit is metadata, but keep its long arrays private.
    h.dump(h.OUT/'roll-volume-review.json',coverage)
    h.dump(h.ROOT/'public/data/historical-preparation-review.json',public)
    lines=['# Aanvullende technische beoordeling 2019–2021','',out['status'],'',
        'Geen signalen of resultaten op de geregistreerde2019–2021-restperiode. De enige signaalreplay hieronder betreft de reeds verbruikte435 ontdekkingsdagen, uitsluitend als regressiecontrole.','',
        f"Oude ontdekkingsreeks: exact435 dagen, alle8 contextvelden, OHLCV-arrays en de oorspronkelijke {sum(old_parity['trade_counts'].values())} trades exact gereproduceerd ({old_parity['trade_counts']}). Geen nieuwe P&L-tabellen gepubliceerd.",'',
        'Alle13 echte rollover-openingen opnieuw berekend met de actuele RTH volledig afgeknipt op09:30. De vooraf bekende ATR, PDH/PDL en nachtankers blijven gelijk. Alle13 hebben ATR14 beschikbaar op dag1 van het nieuwe contract. De eerste overgang is17december2018, gelijk aan de legacy-fragmentroute.','',
        '## De tien uitgesloten normale cashdagen','', '| Datum | Contract | Ontbrekende RTH-minuten NY | 09:29 ontbreekt |','|---|---|---|---|']
    for r in anomalies:lines.append(f"| {r['day']} | {r['contract']} | {', '.join(r['missing_RTH']) or 'geen'} | {r['boundary_0929_missing']} |")
    lines += ['',out['root_report_note'],'','## Volume-overgangen: resterende onzekerheid','',
        '3van13 beslissessies hebben beide contracten volledig op de gereconstrueerde minuutgrid. De overige10 hebben ontbrekende interne minuten. Veel daarvan liggen in de dunne nacht. Geen ontbrekende minuut is als nulvolume ingevuld. De verwachte grid is geen bewijs dat er in elke minuut werkelijk transacties hadden moeten zijn.','',
        'De kleinste waargenomen volumemarge is2.055contracten op14juni2019 (switch17juni). De oude NQM19 mist01:32NY en het nieuwe NQU19 mist9 nachtminuten. Zonder onafhankelijke totalen/no-trade-definitie is de tekenvastheid van de werkelijke volumevergelijking niet bewezen. Op16maart2020 ontbreken776/804minuten tegenover de normalegrid, deels in een limit-/haltregime. Het register bevat beide feitelijke aantallen zonder ze als bewezen broncorruptie aan te merken.','',
        '## Wat nu nog nodig is, zonder strategie-uitkomsten te openen','',
        '- Datum-specifieke historische NQ-futuresuren en limit-/haltvensters onderbouwen waar ze de voorafgaande indicatorhistorie of rolloverbeslissing raken. Cash- en CME-kalender niet verwarren.',
        '- Vendorbetekenis van ontbrekende volume-minuten of onafhankelijke dagtotalen voor de beslissessies vaststellen. Vooral14juni2019 en16maart2020. Geen rolloverdatum aanpassen op P&L.',
        '- Licentie/gebruik en eventuele distributierechten blijven afzonderlijk onbevestigd. De Barchartvoorwaarden waren via de documentopvraag niet leesbaar door een verificatiescherm. Geen omzeiling geprobeerd.',
        '- Daarna de nieuwe runner/codeversie definitief vastleggen en afzonderlijk de uitkomsttoets vrijgeven. Nog geen120 gescoorde waarnemingen claimen: dit rapport telt technische dagen, geen signalen of trades.','',
        'Geen aankoop, nieuwe account, externe upload, Git-push of productie-uitrol. Ruwe data blijft privé.','']
    text='\n'.join(lines)
    (h.ROOT/'docs/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md').write_text(text)
    (h.ROOT/'public/reports/HISTORICAL_2019_2021_TECHNICAL_REVIEW.md').write_text(text)
    h.verify()
    print(json.dumps(dict(status=out['status'],old_discovery_parity=old_parity,
        actual_prefix_tests=len(prefix),remaining_blockers=out['remaining_blockers']),indent=2))
    return out


if __name__=='__main__':review()
