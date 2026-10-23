"""Read-only technical quality audit. No cohort, horizon return or strategy call."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.oos_preparation.adapter import Calendar,at,combine,determine_roll,load_csv,sha
from scripts.afternoon_inference_round import dump,verify_lock

ROOT=Path(__file__).resolve().parents[1]
INTAKE=ROOT/'research/afternoon-historical-intake-batch01.json'
SPECIAL={'2018-11-22':'13:00','2018-11-23':'13:15','2018-12-05':'09:30',
         '2018-12-24':'13:15','2018-12-25':None,'2019-01-01':None}
SOURCES={
    'mourning_exchange':'https://www.cmegroup.com/content/dam/cmegroup/notices/ser/2018/12/SER-8289.pdf',
    'expiration_exchange':'https://www.cmegroup.com/market-regulation/files/16-081R_EXHA.pdf',
    'christmas_broker':'https://cdn.tradestation.com/uploads/Christmas-2018.pdf',
    'thanksgiving_broker':'https://www.ampfutures.com/news/thanksgiving-holiday-trading-schedule-2018',
    'thanksgiving_friday_unconfirmed':'13:15NY provisional reconstruction; authoritative date-specific close not recovered. Exclude from eligibility regardless.'}


class HistoricalCalendar(Calendar):
    def grid(self,day,remove_observed_outage=False):
        ix=super().grid(day,remove_observed_outage)
        # Historical equity-index15:15-15:30CT pause. This is outside RTH.
        return ix[(ix<at(day,'16:15')) | (ix>=at(day,'16:30'))]


def expected_rth(day,contract):
    if pd.Timestamp(day).weekday()>=5:return pd.DatetimeIndex([],tz='UTC')
    close=SPECIAL.get(day,'16:00')
    if contract=='NQZ18' and day>='2018-12-21':close='09:30'
    if close is None or close<='09:30':return pd.DatetimeIndex([],tz='UTC')
    return pd.date_range(at(day,'09:30'),at(day,min(close,'16:00')),freq='min',inclusive='left')


def run():
    verify_lock();intake=json.loads(INTAKE.read_text());parts=[];files=[]
    for item in intake['files']:
        path=ROOT/item['private_copy']
        if sha(path)!=item['sha256']:raise ValueError('Intake source changed')
        # Strict checks: schema/footer, ascending unique, finite coherent OHLC,
        # quarter tick, integer positive vendor volume, timezone parsing.
        g=load_csv(path,item['contract']);parts.append(g)
        prices=g[['open','high','low','close']].to_numpy(float)
        files.append(dict(filename=path.name,sha256=sha(path),contract=item['contract'],bars=len(g),
            numeric_schema_tick_ohlc_volume_errors=0,price_min=float(prices.min()),price_max=float(prices.max()),
            volume_min=int(g.volume.min()),volume_max=int(g.volume.max()),volume_sum=int(g.volume.sum()),
            cap_warning=len(g)>=19999,footer_rows=1,ticks_or_quotes_columns=False))
    full=combine(parts,'2018-11-19','2019-01-14')
    calendar=HistoricalCalendar(dict(reviewed_ranges=[['2018-11-19','2019-01-14']],closes_ny=SPECIAL))
    rows=[];warmup={}
    for contract,frame in full.groupby('contract'):
        first=frame.trade_date.min();last=min(frame.trade_date.max(),'2019-01-11')
        previous=None;true_ranges=[];first_ready=None
        for day in pd.bdate_range(first,last).strftime('%Y-%m-%d'):
            g=frame[frame.trade_date.eq(day)]
            expected=expected_rth(day,contract)
            missing=expected.difference(g.index)
            all390=len(expected)==390 and not len(missing)
            expected_session=calendar.grid(day)
            if contract=='NQZ18' and day>='2018-12-21':
                expected_session=expected_session[expected_session<at('2018-12-21','09:30')]
            session_missing=expected_session.difference(g.index)
            unexpected=g.index.difference(expected_session)
            ready=len(true_ranges)>=14
            if all390 and ready and first_ready is None:first_ready=day
            row=dict(contract=contract,day=day,rth_expected=len(expected),rth_observed=len(expected.intersection(g.index)),
                missing_rth=len(missing),missing_rth_clocks=list(missing.tz_convert('America/New_York').strftime('%H:%M')),
                full_390_rth=all390,special_or_expiry=day in SPECIAL or (contract=='NQZ18' and day>='2018-12-21'),
                session_expected=len(expected_session),session_missing=len(session_missing),session_unexpected=len(unexpected),
                overnight_complete=not len(expected_session[expected_session<at(day,'09:30')].difference(g.index)),
                prior_complete_true_ranges=len(true_ranges),atr14_ready_at_open=ready)
            rows.append(row)
            # Quality/readiness only; no cohort, no horizon returns, no PnL.
            if all390:
                rth=g.reindex(expected)
                high=float(rth.high.max());low=float(rth.low.min());close=float(rth.close.iloc[-1])
                if previous is not None:true_ranges.append(max(high-low,abs(high-previous),abs(low-previous)))
                previous=close
            elif len(calendar.grid(day)):
                previous=None
        warmup[contract]=dict(first_full_rth_atr14_ready=first_ready,valid_prior_tr_count_at_end=len(true_ranges),
            jan2=next((r for r in rows if r['contract']==contract and r['day']=='2019-01-02'),None))
    try:
        roll=determine_roll(full,'NQZ18','NQH19',calendar,'2018-12-20')
        truncated=full[full.trade_date.le(roll['decision_session'])]
        if determine_roll(truncated,'NQZ18','NQH19',calendar,roll['decision_session'])!=roll:raise ValueError('Future-dependent roll')
        roll['future_cutoff_verified']=True
        roll['status']='OBSERVED_VOLUME_RULE_WITH_CALENDAR_LIMITATIONS'
    except ValueError as exc:roll=dict(status='DATA_INSUFFICIENT',reason=str(exc))
    vol=[]
    for day in sorted(set(full.trade_date)):
        if not '2018-12-03'<=day<='2018-12-20':continue
        entry={'day':day}
        for contract in ['NQZ18','NQH19']:
            g=full[full.trade_date.eq(day)&full.contract.eq(contract)]
            ix=calendar.grid(day)
            entry[contract]=dict(volume=int(g.volume.sum()),bars=len(g),expected=len(ix),
                missing=len(ix.difference(g.index)),rth_complete=not len(expected_rth(day,contract).difference(g.index)))
        vol.append(entry)
    continuous_readiness={'status':'DATA_INSUFFICIENT'}
    if 'effective_session' in roll:
        from scripts.reproduce_research.continuous import continuous_daily
        from scripts.reproduce_research.next_engine import Activation
        daily,_=continuous_daily(full,[Activation('NQZ18','2018-11-19'),Activation('NQH19',roll['effective_session'])])
        observed=daily[daily.trade_date.between('2019-01-02','2019-01-11')]
        continuous_readiness=dict(status='TECHNICAL_ATR_ONLY_NOT_COHORT_ELIGIBILITY',
            january_full_rth_days=int(observed.rth_complete.sum()),
            january_atr14_ready_full_rth_days=int((observed.rth_complete & observed.atr14_continuous.notna()).sum()),
            per_day=[dict(day=r.trade_date,prior_valid_TR=int(r.valid_prior_TR),rth_complete=bool(r.rth_complete),
                atr14_ready=bool(np.isfinite(r.atr14_continuous))) for r in observed.itertuples()],
            rule='Unmodified point-in-time continuous_daily using Z18 pre-roll history, H19 raw bars after activation; no signal/cohort evaluation')
    summary={c:dict(full_rth_days=sum(r['full_390_rth'] for r in rows if r['contract']==c),
        incomplete_standard_rth=[dict(day=r['day'],missing=r['missing_rth']) for r in rows if r['contract']==c and r['rth_expected']==390 and r['missing_rth']],
        special_sessions=[dict(day=r['day'],expected=r['rth_expected'],observed=r['rth_observed']) for r in rows if r['contract']==c and r['special_or_expiry']]) for c in ['NQZ18','NQH19']}
    out=dict(status='TECHNICAL_BATCH_AUDITED_NOT_FULL_HISTORICAL_RELEASE',source_bars=sum(len(g) for g in parts),
        unique_contract_bars=len(full),overlap_removed=sum(len(g) for g in parts)-len(full),files=files,
        contracts=summary,readiness=warmup,continuous_atr_readiness=continuous_readiness,rollover=roll,volume_evidence=vol,day_quality=rows,sources=SOURCES,
        calendar_status='EXCHANGE_MOURNING_AND_EXPIRY_PLUS_BROKER_HOLIDAYS_NOV23_CLOSE_UNCERTIFIED',
        source_timezone='America/Chicago assumed existing vendor convention; NY=Chicago+1hour here, UTC offset NY-5. No DST transition occurs in these six files.',
        signal_or_horizon_returns_computed=False,new_historical_outcomes_released=False,
        limitation='No forward filling. Missing vendor minutes may be no trades rather than corruption; inactive-contract thinness is not high-quality complete RTH. Filename identifies contract, no embedded exchange instrument ID. No BBO/ticks/fill proof. License remains unverified, no raw publication.')
    dump(ROOT/'research/historical-batch01-quality.json',out)
    lines=['# Kwaliteit eerste zes historische NQ-bestanden','',out['status'],'',
        f"**{out['source_bars']:,} bronbars**. Alle zes slagen voor schema, footer, unieke oplopende timestamps, eindige OHLCV, coherente OHLC, 0,25-punt tick-grid en positief geheel vendorvolume. Geen afkapping op de 20.000-recordgrens. Originele hashes zijn gecontroleerd; bronbytes niet gewijzigd. Dit maakt de reeks nog niet volledig of model-eligible.",'',
        '| Contract | Volledige 390-min RTH-dagen | Standaarddagen met ontbrekende RTH-minuten | Eerste ATR14-readiness |',
        '|---|---:|---:|---|']
    for c,s in summary.items():lines.append(f"| {c} | {s['full_rth_days']} | {len(s['incomplete_standard_rth'])} | {warmup[c]['first_full_rth_atr14_ready']} |")
    lines += ['', '## Kalender en contractovergang','',
        '- 5 december 2018: CME bevestigt halt om 08:30 Chicago /09:30 New York. Geen RTH verwachten. NQZ18 eindigt op 21 december om08:30 Chicago: verenigbaar met expiratie aan de cash open, geen kunstmatige verlenging naar16:00.',
        '- Thanksgiving 22 november13:00NY is broker-ondersteund; 23 november13:15NY blijft een voorlopige kalenderreconstructie. Christmas Eve13:15NY en Christmas Day gesloten zijn door TradeStation gedocumenteerd. New Year gesloten is kalenderreconstructie. Deze uitzonderingen worden niet als gewone corrupte390-minuten-sessies bestempeld en niet trade-eligible verklaard.',
        '- Volledige sessiedekking buiten RTH gebruikt ook de historische16:15–16:30NY-pauze als reconstructie. De volledige kalender is niet als exchange-gecertificeerd vrijgegeven. Per dag staan zowel RTH- als nachtsessie-gaten in JSON.','',
        'Volumeregel op voltooide gezamenlijke sessies, activatie volgende sessie en laatste gemeenschappelijke RTH-close vóór activatie:','',
        '```json',json.dumps(roll,indent=2),'```','',
        '### Doorlopende ATR in plaats van contract-only opwarming','',
        f"De contract-only telling hierboven is niet de vNext-vereiste. Met de ongewijzigde point-in-time continuous-module en Z18-historie zijn **{continuous_readiness.get('january_atr14_ready_full_rth_days',0)} van {continuous_readiness.get('january_full_rth_days',0)}** aanwezige volledige RTH-dagen van2–11januari al ATR14-ready. Beide tellingen staan apart in JSON. Geen UP-cohort of vrijgegeven eindtoets.",'',
        '## Ontbrekende standaard-RTH-minuten','']
    for c,s in summary.items():
        lines.append(c+': '+(', '.join(f"{r['day']} ({r['missing']})" for r in s['incomplete_standard_rth']) or 'geen'))
    lines += ['', '## Grenzen van dit oordeel','',
        'De beperkte batch stopt met volledige H19-RTH op11 januari2019; zondag13januariavond is geen volledige volgende handelsdag. Contract-only ATR reset de prior-close na een onvolledige/korte sessie, niet na een volledig gesloten dag. De aparte continuous-telling draagt vooraf bekende, causale Panama-historie mee, nooit onverschoven contractprijsverschillen. Readiness en volumetelling zijn technische checks, geen 15:00-cohort of kandidaatuitkomsten. Geen onafhankelijke toets vrijgegeven.','',
        'Timestamps zijn Chicago→UTC→New York geconverteerd. Er is in deze batch geen DST-overgang geobserveerd; tests van IANA-overgangen zijn geen empirische certificering. Volume is het volume van deze bron, niet onafhankelijk tegen CME-totalen gevalideerd. Geen Tick/BBO-kolommen of licentiegoedkeuring aanwezig. De spreadsheet-richtlijnen zijn toegepast voor bronbehoud en expliciete ontbrekende waarden; er is geen bron-CSV herschreven.','', '## Bronverwijzingen','']
    for k,v in SOURCES.items():lines.append(f'- {k}: {v}')
    (ROOT/'docs/HISTORICAL_BATCH01_QUALITY.md').write_text('\n'.join(lines)+'\n')
    verify_lock();print(json.dumps(dict(status=out['status'],contracts=summary,readiness=warmup,rollover=roll),indent=2),flush=True)


if __name__=='__main__':run()
