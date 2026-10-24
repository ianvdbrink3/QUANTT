"""Append-only quality evidence; never select a candidate or measure outcomes.

python -m scripts.audit_historical_evidence register|run|verify|replay
Optional XLS reader: xlrd==2.0.2. Source downloads stay in Gitignored storage.
"""
import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import prepare_historical_contracts as h
from scripts.oos_preparation.adapter import stage_immutable

ROOT = h.ROOT
PROTOCOL = ROOT/'research/historical-evidence-protocol.json'
LOCK = ROOT/'research/historical-evidence-lock.json'
OUT = ROOT/'artifacts/historical-evidence'
RAW = ROOT/'data/raw/historical-evidence'
RESULT = ROOT/'research/historical-evidence-audit.json'
REPORT = ROOT/'docs/HISTORICAL_VOLUME_CALENDAR_EVIDENCE.md'
PUBLIC = ROOT/'public/data/historical-evidence-audit.json'
PUBLIC_REPORT = ROOT/'public/reports/HISTORICAL_VOLUME_CALENDAR_EVIDENCE.md'
EXPORT = ROOT/'research/historical-rollover-evidence.csv'
CALENDAR_EXPORT = ROOT/'research/historical-calendar-evidence.csv'


def register():
    if LOCK.exists():
        return verify()
    tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    frozen = {p:h.sha(ROOT/p) for p in tracked if p and (ROOT/p).is_file()}
    inputs = {str(p.relative_to(ROOT)):h.sha(p) for p in h.OUT.glob('*') if p.is_file()}
    h.dump(LOCK, dict(status='AUDIT_ONLY_BEFORE_NEW_COMPUTATION',
        prior_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        protected_files=frozen, private_inputs=inputs, protocol_sha256=h.sha(PROTOCOL),
        new_outcomes_authorized=False))
    return verify()


def verify():
    frozen = json.loads(LOCK.read_text())
    for name,digest in {**frozen['protected_files'],**frozen['private_inputs']}.items():
        if h.sha(ROOT/name) != digest:
            raise ValueError('Pre-audit bytes changed: '+name)
    if h.sha(PROTOCOL) != frozen['protocol_sha256']:
        raise ValueError('Audit protocol changed')
    return dict(all_preexisting_tracked_files_unchanged=len(frozen['protected_files']),
        private_preparation_outputs_unchanged=len(frozen['private_inputs']),
        old_freeze=h.verify(), new_signals_computed=False, holdout_executed=False)


def receipt(filename):
    original = Path('/Users/ianvandenbrink/Downloads')/filename
    target = RAW/filename
    if not h.ignored(target):
        raise ValueError('Audit source must be Gitignored')
    digest = stage_immutable(original,target)
    return target, dict(filename=filename,private_copy=str(target.relative_to(ROOT)),
        sha256=digest,bytes=target.stat().st_size,original_and_copy_identical=True)


def daily_csv(path, contract):
    raw = pd.read_csv(path)
    expected = h.SCHEMA+['Open Int']
    if list(raw.columns) != expected or not path.name.lower().startswith(contract.lower()+'_daily_'):
        raise ValueError('Wrong daily contract/schema')
    parsed = pd.to_datetime(raw.Time,format='%Y-%m-%d',errors='coerce')
    footer = raw[parsed.isna()]
    if len(footer)!=1 or not str(footer.Time.iloc[0]).startswith('Downloaded from Barchart.com as of ') or not footer.drop(columns='Time').isna().all().all():
        raise ValueError('Unexpected daily footer')
    g = raw[parsed.notna()].copy()
    g.index = pd.DatetimeIndex(parsed[parsed.notna()])
    if not g.index.is_unique or not g.index.is_monotonic_increasing or g.empty:
        raise ValueError('Empty/duplicate/unsorted daily source')
    v = pd.to_numeric(g.Volume,errors='raise')
    if not (np.isfinite(v).all() and (v>=0).all() and (v==v.round()).all()):
        raise ValueError('Invalid daily volume')
    return {t.strftime('%Y-%m-%d'):int(value) for t,value in v.items()}


def xls_receipts(protocol):
    import xlrd
    if xlrd.__version__!='2.0.2':
        raise ValueError('Use the pinned xlrd 2.0.2 reader')
    receipts=[]; cells=[]
    for spec in protocol['xls_checks']:
        path,meta=receipt(spec['filename'])
        book=xlrd.open_workbook(str(path))
        sheet=book.sheet_by_name(spec['sheet'])
        if spec['title_contains'] not in str(sheet.cell_value(*spec['title_cell'])):
            raise ValueError('Wrong calendar year/title')
        if sheet.cell_value(*spec['product_cell']) != spec['product_equals']:
            raise ValueError('Wrong product family')
        for check in spec['checks']:
            if sheet.cell_value(*check['header_cell']) != check['action']:
                raise ValueError('Not a trading halt/close column')
            value=sheet.cell_value(*check['cell'])
            minutes=round(float(value)*1440)
            ct=f'{minutes//60:02}:{minutes%60:02}'
            if ct!=check['close_ct']:
                raise ValueError('CME source close differs from protocol')
            # Chicago->NY conversion on the actual date, not a fixed UTC offset.
            ny=pd.Timestamp(f"{check['day']} {ct}",tz='America/Chicago').tz_convert('America/New_York').strftime('%H:%M')
            if ny!=check['close_ny']:
                raise ValueError('Holiday timezone mismatch')
            cells.append(dict(check,
                verified=True,source=protocol['sources'][spec['source']],
                sheet=spec['sheet'],product='Equity Products',source_sha256=meta['sha256']))
        receipts.append(dict(meta,source=protocol['sources'][spec['source']],parser='xlrd 2.0.2'))
    return receipts,cells


def comparison(a,b,day,calendar):
    ix=calendar.grid(day)
    def side(g):
        good=g[g.usable]
        missing=ix.difference(good.index)
        return dict(observed_volume=int(good.volume.sum()),bars=len(good),
            missing=len(missing),unexpected=len(good.index.difference(ix)),
            first_utc=good.index.min().isoformat() if len(good) else None,
            last_utc=good.index.max().isoformat() if len(good) else None,
            missing_ny=[t.tz_convert('America/New_York').isoformat() for t in missing])
    old,new=side(a),side(b)
    endpoint_pass=bool(len(ix) and len(a) and len(b) and
        a.index.min()<=ix.min() and a.index.max()>=ix.max() and
        b.index.min()<=ix.min()+pd.Timedelta(minutes=60) and
        b.index.max()>=ix.max()-pd.Timedelta(minutes=60))
    diff=new['observed_volume']-old['observed_volume']
    return dict(day=day,expected_minutes=len(ix),old=old,new=new,
        endpoint_rule_pass=endpoint_pass,observed_new_minus_old=diff,
        candidate_qualifying=bool(endpoint_pass and diff>0),
        both_grids_complete=bool(len(ix) and not any(s[k] for s in (old,new) for k in ('missing','unexpected'))),
        missing_volume_bound=None)


def roll_audit(full,rolls,daily,calendar):
    records=[]; private=[]
    for r in rolls:
        a=full[(full.contract==r['from'])&full.trade_date.le(r['decision_session'])]
        b=full[(full.contract==r['to'])&full.trade_date.le(r['decision_session'])]
        dates=sorted(set(a.trade_date)&set(b.trade_date))
        rows=[comparison(a[a.trade_date.eq(d)],b[b.trade_date.eq(d)],d,calendar) for d in dates]
        first=next(x['day'] for x in rows if x['candidate_qualifying'])
        if first!=r['decision_session']:
            raise AssertionError('Frozen observed rule not reproduced')
        last=next(x for x in rows if x['day']==first)
        separate=None
        if r['from'] in daily and r['to'] in daily:
            shared=sorted(set(daily[r['from']])&set(daily[r['to']])&set(dates))
            checks=[dict(day=d,old=daily[r['from']][d],new=daily[r['to']][d],
                difference=daily[r['to']][d]-daily[r['from']][d]) for d in shared]
            chosen=next((x for x in checks if x['day']==first),None)
            separate=dict(decision_day=chosen,first_daily_new_greater_in_observed_overlap=
                next((x['day'] for x in checks if x['difference']>0),None),
                same_decision_sign=bool(chosen and chosen['difference']>0),
                comparable_transaction_universe_proven=False,independent_vendor=False,
                audit_only_not_used_to_set_roll=True)
            h.dump(OUT/f"daily-comparison-{r['from']}-{r['to']}.json",checks)
        records.append(dict(old=r['from'],new=r['to'],decision_session=first,
            effective_session=r['effective_session'],observed_rule_reproduced=True,
            overlap_first=dates[0],overlap_days_checked=len(rows),
            earlier_incomplete_comparisons=sum(not x['both_grids_complete'] for x in rows[:-1]),
            earlier_endpoint_rejected=sum(not x['endpoint_rule_pass'] for x in rows[:-1]),
            decision_old_volume=last['old']['observed_volume'],decision_new_volume=last['new']['observed_volume'],
            decision_observed_margin=last['observed_new_minus_old'],
            decision_missing_old=last['old']['missing'],decision_missing_new=last['new']['missing'],
            complete_decision_grid=last['both_grids_complete'],
            before_overlap_dominance_proven=False,earliest_true_exchange_crossover_proven=False,
            official_same_universe_totals_available_before_activation_proven=False,
            daily_crosscheck=separate,status='OBSERVED_RULE_ONLY_NOT_CERTIFIED'))
        private.append(dict(old=r['from'],new=r['to'],comparisons=rows))
    return records,private


class EvidenceCalendar(h.HistoricalCalendar):
    """Isolated source-supported overlay; never mutates the frozen calendar."""
    def __init__(self):
        super().__init__()
        self.registry['closes_ny']['2021-04-02']='09:15'


def context_impact(active,rolls,baseline_daily):
    c=EvidenceCalendar()
    days=[d for d in pd.bdate_range('2018-11-19','2021-12-31').strftime('%Y-%m-%d') if len(c.grid(d))]
    schedule=[h.Activation('NQZ18','2018-11-19')]+[h.Activation(r['to'],r['effective_session']) for r in rolls]
    # Spreads frozen: this is a calendar sensitivity, never an alternate roll run.
    full=pd.read_parquet(h.OUT/'contract-bars.parquet')
    spreads=h.roll_spreads(full[full.usable],schedule)
    state=h.contexts(active,days,c,spreads)
    original={r['day']:r for r in json.loads((h.OUT/'prior-context.json').read_text())}
    changed=[]; flags=[]
    for day in days:
        ctx=state[day][1];old=original.get(day)
        if old:
            differences=[name for name,key in [('atr14_prior','atr'),('PDH','PDH'),('PDL','PDL')]
                if not ((old[name] is None and not np.isfinite(ctx[key])) or
                    (old[name] is not None and old[name]==ctx[key]))]
            if differences:changed.append(dict(day=day,fields=differences))
        flags.append(dict(day=day,atr_ready=bool(np.isfinite(ctx['atr']) and ctx['atr']>0),
            pd_ready=bool(np.isfinite(ctx['PDH']) and np.isfinite(ctx['PDL']))))
    lookup={r['day']:r for r in flags}
    counts={}
    for label,start in [('FULL_2019_2021','2019-01-02'),('REGISTERED_REMAINDER','2019-01-14')]:
        q=[r for r in baseline_daily if start<=r['day']<='2021-12-31']
        counts[label]={m:sum(bool(r['clean_full_RTH'] and lookup[r['day']]['atr_ready'] and
            (lookup[r['day']]['pd_ready'] if m=='COMPRESSED_BREAK5' else
             r['overnight_complete'] if m=='SWEEP_REV_1200' else True)) for r in q)
            for m in ('TOM_RTH','COMPRESSED_BREAK5','SWEEP_REV_1200')}
    # Prefix proof at the first affected cash open: no current/future RTH data.
    cutoff=h.at('2021-04-05','09:30')
    before=h.contexts(active[active.index<cutoff],[d for d in days if d<='2021-04-05'],c,spreads)
    for key in ('atr','PDH','PDL','prior_close'):
        np.testing.assert_equal(before['2021-04-05'][1][key],state['2021-04-05'][1][key])
    return dict(calendar_overlay={'2021-04-02':'09:15 NY, not fully closed'},
        applied_to_frozen_route=False,spreads_and_rollovers_unchanged=True,
        context_changed=changed,technical_day_counts=counts,april5_prefix_test=True,
        no_candidate_selection=True)


def calendar_audit(active,rolls,cells):
    c=h.HistoricalCalendar(); proven={r['day']:r for r in cells}
    days=sorted(h.CLOSED|h.HALF)
    records=[]
    for day in days:
        g=active[active.trade_date.eq(day)]
        exp=c.grid(day);p=proven.get(day)
        normal_clock=g.index[(g.index>=h.at(day,'09:30'))&(g.index<h.at(day,'16:00'))]
        records.append(dict(day=day,cash_closed=day in h.CLOSED,cash_half=day in h.HALF,
            expected_minutes_frozen=len(exp),observed_bars=len(g),observed_rth_bars=len(normal_clock),
            first_bar_ny=g.index.min().tz_convert('America/New_York').isoformat() if len(g) else None,
            last_bar_ny=g.index.max().tz_convert('America/New_York').isoformat() if len(g) else None,
            unexpected_vs_frozen_grid=len(g.index.difference(exp)),
            evidence='CME_XLS_CELLS_VERIFIED' if p else 'CME_MOURNING_NOTICE' if day=='2018-12-05' else 'CASH_CALENDAR_ONLY_FUTURES_HOURS_UNCERTIFIED',
            source=p['source'] if p else h.SOURCES['mourning'] if day=='2018-12-05' else h.SOURCES['cash_calendar'],
            verified_close_ny=p['close_ny'] if p else None,
            frozen_calendar_contradicted=bool(p and day=='2021-04-02')))
    expirations=[]
    for contract,g in active.groupby('contract'):
        day=h.expiry(contract);bad=g[g.index>=h.at(day,'09:30')]
        bad=bad[bad.trade_date.ge(day)]
        expirations.append(dict(contract=contract,nominal_expiry=day,active_bars_at_or_after_expiry_open=len(bad)))
    return records,expirations


def run():
    integrity=verify();p=json.loads(PROTOCOL.read_text());OUT.mkdir(parents=True,exist_ok=True)
    register=json.loads(h.REGISTER.read_text());sources=[];parts=[]
    for item in register['files']:
        for path in (ROOT/item['private_copy'],Path('/Users/ianvandenbrink/Downloads')/item['filename']):
            if h.sha(path)!=item['sha256']:raise ValueError('Source hash changed '+item['filename'])
        frame,_=h.read_source(item);parts.append(frame)
    reconstructed,duplicates=h.reconcile(parts)
    del parts
    daily={}
    for spec in p['daily_checks']:
        path,meta=receipt(spec['filename']);daily[spec['contract']]=daily_csv(path,spec['contract'])
        sources.append(dict(meta,contract=spec['contract'],actual_first=min(daily[spec['contract']]),
            actual_last=max(daily[spec['contract']]),requested_start=spec['requested_start'],
            requested_end=spec['requested_end'],type='VENDOR_DAILY_AUDIT_ONLY',independent=False))
    xls,cells=xls_receipts(p);sources+=xls
    full=pd.read_parquet(h.OUT/'contract-bars.parquet');active=pd.read_parquet(h.OUT/'active-bars.parquet')
    pd.testing.assert_frame_equal(reconstructed,full)
    del reconstructed
    previous=json.loads(h.RESULT.read_text());rolls,detail=roll_audit(full,previous['rollovers'],daily,h.HistoricalCalendar())
    days,expiries=calendar_audit(active,previous['rollovers'],cells)
    baseline_daily=json.loads((h.OUT/'active-day-quality.json').read_text())
    impact=context_impact(active,previous['rollovers'],baseline_daily)
    findings=[r for r in rolls if r['daily_crosscheck'] and not r['daily_crosscheck']['same_decision_sign']]
    result=dict(status='AUDIT_COMPLETE_RELEASE_NOT_APPROVED',date=p['audit_date'],signals_computed=False,
        holdout_executed=False,release_approved=False,integrity=integrity,
        original_sources_hash_verified=len(register['files']),additional_source_receipts=sources,
        raw_to_cached_contract_bars_exact=True,duplicate_quality_rechecked=duplicates,
        audit_code_sha256=h.sha(Path(__file__)),protocol_sha256=h.sha(PROTOCOL),
        volume_rollovers=rolls,calendar_exceptions=days,expiry_checks=expiries,
        independently_certified_rollovers=0,decision_days_with_two_complete_grids=sum(r['complete_decision_grid'] for r in rolls),
        daily_order_disagreements=len(findings),verified_CME_calendar_cells=cells,
        calendar_context_impact=impact,baseline_counts_unchanged=previous['groups'],
        vendor_findings=p['vendor_findings'],sources=p['sources'],
        blockers=['INTRADAY_VS_DAILY_VOLUME_ORDER_DISAGREEMENT','VENDOR_MISSING_MINUTE_SEMANTICS_UNPROVEN',
            'EARLIEST_TRUE_CROSSOVER_NOT_CERTIFIED','FULL_DATE_SPECIFIC_CME_MATRIX_UNCERTIFIED',
            'DOCUMENTED_CALENDAR_OVERLAY_NOT_YET_RELEASED_IN_EXECUTION_ROUTE'],
        separate_not_audited=['license_and_redistribution','independent_tick_fill_evidence','formal_outcome_release'],
        publication='LOCAL_ONLY_NO_PUSH_OR_DEPLOY',raw_data_public=False)
    h.dump(OUT/'all-overlap-session-comparisons.json',detail)
    h.dump(OUT/'context-impact.json',impact)
    h.dump(RESULT,result);h.dump(PUBLIC,result)
    columns=['old','new','decision_session','effective_session','decision_old_volume','decision_new_volume',
        'decision_observed_margin','decision_missing_old','decision_missing_new','earlier_incomplete_comparisons','status']
    with EXPORT.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rolls)
    columns=['day','cash_closed','cash_half','expected_minutes_frozen','observed_bars','observed_rth_bars',
        'first_bar_ny','last_bar_ny','verified_close_ny','evidence','source','frozen_calendar_contradicted']
    with CALENDAR_EXPORT.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(days)
    text=report(result);REPORT.write_text(text);PUBLIC_REPORT.write_text(text)
    verify()
    return dict(status=result['status'],volume_rollovers=len(rolls),daily_order_disagreements=len(findings),
        calendar_context_impact=impact,integrity=integrity)


def report(r):
    lines=['# Volume- en kalenderbewijsaudit — historische NQ-reeks','',r['status'],'',
        '23 oktober 2026. Alleen bronkwaliteit, kalender en vooraf bekende indicatorcontext. Geen signalen, trades, vervolgrendement of P&L op 2019–2021 berekend. Geen regels, bestaande rapporten, bronbars of rolloverdatums gewijzigd.','',
        '## Besluit','',
        'De audit is uitgevoerd, maar definitieve vrijgave is NIET verantwoord. Een echte volumedefinitie-tegenspraak en een aantoonbare kalenderfout zijn gevonden. Het keuringshek blijft gesloten; technische beschikbaarheid is geen onafhankelijke bevestiging.','',
        '## 1. Volume: dezelfde contracten, verschillende transactieverzamelingen','',
        'De hulptekst van de ingelogde Barchart-CSV-pagina bevestigt dat intraday bepaalde transactietypen uitsluit die wel in dagvolume kunnen voorkomen. Uitgeschakelde Total Volume and Open Interest levert contractvolume, geen totaal over alle expiraties. Dit bevestigt NIET dat een ontbrekende minuut nul transacties had. CME-bulletins onderscheiden eveneens Globex- en pit/block-volume; een willekeurig dagtotaal is geen uitwisselbare controle.','',
        '| Beslissessie | Contractpaar | Minuutvolume oud / nieuw | Minuutmarge nieuw−oud | Dagvolume oud / nieuw | Dagmarge | Zelfde rangorde? |','|---|---|---:|---:|---:|---:|---|']
    for z in r['volume_rollovers']:
        d=z['daily_crosscheck']
        if d and d['decision_day']:
            q=d['decision_day'];lines.append(f"| {z['decision_session']} | {z['old']} → {z['new']} | {z['decision_old_volume']:,} / {z['decision_new_volume']:,} | {z['decision_observed_margin']:+,} | {q['old']:,} / {q['new']:,} | {q['difference']:+,} | {d['same_decision_sign']} |")
    lines += ['',
        '14 juni 2019 is dus NIET door de aparte dagbron bevestigd. Dit bewijst niet dat de minuutbestanden corrupt zijn; de filterdefinitie verschilt. Dagvolume wordt niet achteraf als vervangende rolloverregel ingevoerd. De finale publicatietijd van dagtotalen vóór de volgende activering is evenmin bewezen. CME meldt bovendien dat het eerste bulletin pas de volgende werkdag rond middernacht CT verschijnt en de finale versie rond 10:00 CT; dat is geen causale invoer voor een eerdere avondactivering.','',
        '### Alle 13 rollovers, inclusief eerdere overlapdagen','',
        '| Van → naar | Beslissessie | Actief vanaf | Minuutmarge | Ontbreekt oud/nieuw | Eerdere onvolledige vergelijkingen |','|---|---|---|---:|---:|---:|']
    for z in r['volume_rollovers']:
        lines.append(f"| {z['old']} → {z['new']} | {z['decision_session']} | {z['effective_session']} | {z['decision_observed_margin']:+,} | {z['decision_missing_old']} / {z['decision_missing_new']} | {z['earlier_incomplete_comparisons']} |")
    lines += ['',
        f"Alle 13 waargenomen beslissingen gereproduceerd vanaf de overlappende brondata t/m hun beslissessie. Alle 105 ruwe CSV’s opnieuw geparseerd en ontdubbeld: exact dezelfde contractbars als de bevroren privé-Parquet. Slechts {r['decision_days_with_two_complete_grids']} beslissessies hebben twee volledige nominale minuutgrids. Ook die zijn geen onafhankelijke certificering van de eerste werkelijke volumeswitch: eerdere vergelijkingen kunnen incompleet zijn en historie vóór de overlap is niet bewezen. Volledige grid ≠ volledige exchange feed. Ontbrekend volume blijft onbekend, zonder bovengrens of nul-imputatie.",'',
        '## 2. Kalender: concrete correctie gevonden','',
        '| Datum | Origineel CME-bewijs | Correcte grens NY | Oude voorstelling |','|---|---|---|---|',
        '| 2019-11-28 | Equity Products, Thanksgiving-rooster, Halt | 13:00 | klopt |',
        '| 2019-11-29 | Equity Products, Thanksgiving-rooster, Close | 13:15 | klopt |',
        '| 2021-04-02 | Equity Products, Good Friday-rooster, Close 08:15 CT | 09:15 | onterecht volledig gesloten |','',
        'Op Goede Vrijdag 2021 zijn 910 actieve vendorbars aanwezig tot 09:14 NY. Het oorspronkelijke CME-bestand bevestigt een korte futuresessie, ondanks gesloten cashmarkt. De eerdere kalender sloeg die dag geheel over. De geïsoleerde, brononderbouwde overlay corrigeert alleen dit gegeven; de bevroren uitvoeringsroute blijft onaangeroerd.','',
        '### Uitsluitend indicator-/eligibility-impact van deze overlay','',
        '| Periode | Model-context | Oude technische dagen | Overlay technische dagen |','|---|---|---:|---:|']
    for group,new in r['calendar_context_impact']['technical_day_counts'].items():
        for model,count in new.items():
            old=r['baseline_counts_unchanged'][group]['technical_by_model'][model]
            lines.append(f'| {group} | {model} | {old} | {count} |')
    changes=r['calendar_context_impact']['context_changed']
    lines += ['',f"Vooraf bekende ATR/PD-context verschilt op {len(changes)} kalenderdagen. Details bevatten alleen datums/veldnamen, geen strategie-uitkomsten. De toekomst-afknipcontrole op 5 april vóór 09:30 slaagt. De vaste contracten en spreads blijven gelijk.",'',
        '### Nog niet bewezen kalenderonderdelen','',
        'Het register beoordeelt elke cashfeestdag/halve dag in de warme en testhistorie apart. Een cashkalender bewijst geen CME-Globex-uren; een clearing- of settlementbericht evenmin. De twee opgehaalde CME-XLS-bestanden bewijzen drie specifieke daggrenzen, niet automatisch alle overige feestdagen in 2018–2021.','',
        'De officiële wijziging verwijdert de dagelijkse 16:15–16:30 NY-pauze vanaf 28 juni 2021. De rouwdag 5 december 2018 is afzonderlijk onderbouwd. De historische NQ-regel is hoofdstuk 359 (niet het grote S&P-contract): expiratie bij de reguliere Nasdaq-open op de vastgestelde derde vrijdag. Er zijn geen actieve bars na de nominale expiratie-open aangetroffen.','',
        'De SEC-werkgroep bevestigt de cash-halts op 9, 12, 16 en 18 maart 2020, maar beschrijft ook vertraging tussen cash-halt en CME-halt. Vanaf 12 oktober 2020 veranderden bovendien limieten en heropeningstijden. Cash-seconden mogen daarom niet zonder afzonderlijk bewijs naar NQ-minuten worden gekopieerd. Ontbrekende NQ-minuten blijven gemarkeerd; de vier haltdagen worden niet synthetisch compleet gemaakt.','',
        '### Datums waarvoor nog volledig futuresurenbewijs ontbreekt','',
        'Dit is geen lijst van ontbrekende CSV’s of bewezen corruptie. De bars kunnen met het voorlopige rooster overeenkomen; een overeenkomst bewijst het officiële rooster niet. Ook nul bars bewijst op zichzelf geen beurssluiting.','',
        '| Datum | Cash gesloten / half | Aanwezige bars | Laatste aanwezige bar NY |','|---|---|---:|---|']
    for z in r['calendar_exceptions']:
        if z['evidence'].endswith('UNCERTIFIED'):
            lines.append(f"| {z['day']} | {'gesloten' if z['cash_closed'] else 'half'} | {z['observed_bars']} | {z['last_bar_ny'] or 'geen'} |")
    lines += ['',
        '## Minimale ontbrekende bewijslast vóór vrijgave','',
        '1. Barchart-definitie van ontbrekende minuten én een controleerbare reconciliatie van het volume-universum rond de switches, minimaal 14 juni 2019 en 16 maart 2020 plus hun eerdere overlapdagen. Voor 2019 is nu een tegengestelde rangorde vastgesteld; een grotere marge is geen oplossing voor een ongedefinieerde meetgrootheid.',
        '2. Ontbrekende gedateerde Equity Products/Globex-roosters 2018–2021 verzamelen of een onderbouwde, vooraf vastgelegde kalenderbeslissing nemen voor iedere context-rakende uitzondering. Het nieuwe uitzonderingenregister noemt de precieze datums.',
        '3. Daarna de kalendercorrectie en expliciete volumedefinitie in een nieuwe vastgelegde voorbereidingsversie verwerken en alleen technische regressie/causaliteit opnieuw testen. Geen P&L gebruiken om tussen volumeregels te kiezen.',
        '4. Los daarvan blijven gebruiksrechten, onafhankelijke tick/fill-validatie en expliciete uitkomstvrijgave aparte voorwaarden. Deze audit keurt geen winstgevend model goed.','',
        '## Borging en reproduceerbaarheid','',
        f"Alle {r['original_sources_hash_verified']} oorspronkelijke CSV-hashes opnieuw geverifieerd. Alle {r['integrity']['all_preexisting_tracked_files_unchanged']} reeds bijgehouden bestanden en {r['integrity']['private_preparation_outputs_unchanged']} private voorbereidingsbestanden byte-identiek. De aanvullende vier dag-CSV’s en twee CME-XLS-bestanden zijn apart privé gekopieerd en gehasht. De spreadsheetwerkwijze bewaart de originele bronnen en behandelt ontbreken niet als nul.",'',
        '`python -m scripts.audit_historical_evidence verify` controleert de freeze; `run` voert alleen deze bewijsaudit uit; `replay` controleert byte-identieke uitvoer. Voor de originele .xls-bronnen is xlrd 2.0.2 nodig; de extra afhankelijkheid staat in requirements-historical-evidence.txt, naast de bestaande onderzoeksomgeving. Geen nieuw signaal- of P&L-commando aanwezig.','',
        'Lokaal opgeslagen: audit-JSON, rollover-CSV, dit rapport en publieke-safe kopieën. Niet gepusht of gedeployed; de bestaande productie blijft ongewijzigd. Geen ruwe arrays of extra vendor-CSV’s in publieke uitvoer.','',
        '## Bronnen','']+[f'- [{key}]({value})' for key,value in r['sources'].items()]
    return '\n'.join(lines)+'\n'


def replay():
    run()
    paths=[RESULT,PUBLIC,REPORT,PUBLIC_REPORT,EXPORT,CALENDAR_EXPORT]+sorted(OUT.glob('*.json'))
    before={str(x.relative_to(ROOT)):h.sha(x) for x in paths}
    run()
    after={str(x.relative_to(ROOT)):h.sha(x) for x in paths}
    if before!=after:raise AssertionError('Audit replay changed bytes')
    value=dict(status='BYTE_IDENTICAL_QUALITY_EVIDENCE_REPLAY',files_sha256=after,integrity=verify(),
        signals_computed=False,holdout_executed=False)
    h.dump(ROOT/'research/historical-evidence-verification.json',value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register','run','verify','replay'])
    action=parser.parse_args().action
    print(json.dumps(globals()[action](),indent=2))
