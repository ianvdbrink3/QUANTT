"""Fixed full-history profile comparison. Sources and existing kernels stay immutable.

python -m scripts.profile_benchmark --verify
Public output contains derived portfolio NAV and aggregates, never source OHLC/fills.
"""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import math

import numpy as np
import pandas as pd

from portfolio_agent.signal_engine import features
from portfolio_agent.regime import WEIGHTS, classify, sleeve_targets
from portfolio_agent.calendars import early_close, is_session
from scripts.etf_empirical.data import daily, minutes
from scripts.etf_empirical.core import holding, contribution_dates, minute_path
from scripts.portfolio_agent_study import portfolio as archived_portfolio

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/portfolio_agent/profile-benchmark'
PUBLIC = ROOT / 'public/data/portfolio-os/profile-benchmark.json'
FX = ROOT / 'data/raw/profile-benchmark-2026-10-30/ecb-usd-eur.csv'
MODELS = {
    'defensive_off': 'Voorzichtig · S1 uit',
    'balanced_off': 'Gebalanceerd · S1 uit',
    'offensive': 'Aanvallend · state-machine',
    'qqq_trend200': 'QQQ TREND200',
    'qqq_buyhold': 'Gewoon QQQ Buy & Hold',
    'tqqq_trend200': 'TQQQ TREND200 · extra referentie',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(body):
    return json.dumps(body, allow_nan=False, sort_keys=True, separators=(',', ':')).encode() + b'\n'


def fx_frames(frames):
    """EUR cash; causal lagged ECB conversion reference at open, current at mark.

    ECB fixes are valuation references, not executable quotes. Keep USD indicators.
    Cash remains EUR; no fabricated USD cash yield or currency hedge.
    """
    raw = pd.read_csv(FX)
    rates = raw.set_index('TIME_PERIOD').OBS_VALUE.astype(float).sort_index()
    if not rates.index.is_unique or not np.isfinite(rates).all() or (rates <= 0).any():
        raise ValueError('INVALID_ECB_SERIES')
    days = frames['QQQ'].index
    # Do not use the same-day 16:00 CET publication for an earlier NY opening.
    opening = pd.Series({d: rates.loc[rates.index < d].iloc[-1] for d in days if d >= '2019-01-01'})
    closing = rates.reindex(opening.index, method='ffill')
    converted = {}
    for key, frame in frames.items():
        f = frame.copy()
        common = opening.index
        f.loc[common, 'open'] = frame.loc[common, 'open'] / opening
        f.loc[common, 'close'] = frame.loc[common, 'close'] / closing
        f.loc[common, 'distribution'] = frame.loc[common, 'distribution'] / opening
        converted[key] = f
    return converted


def profile_replay(frames, fs, days, profile, bp, monthly=0):
    """Existing S1_OFF study kernel plus explicit month-end external flows.

    Flow arrives after first trading day's open, waits to next open; next open
    executes paid month rebalance. This avoids backdating a monthly purchase.
    No account circuit-breaker/reset policy is invented for this allocation study.
    """
    weights = np.array(WEIGHTS[profile][:3])
    cash = weights * 990.
    permanent = 10. + WEIGHTS[profile][3] * 990.
    q = np.zeros(2)
    last = paid = 1000.
    fee_total = 0.
    prior_targets = None
    pending_flow = False
    orders = 0
    rets, navs, inlegs, audit = [], [], [], []
    index = list(frames['QQQ'].index)
    previous = {b: a for a, b in zip(index, index[1:])}
    deposits = set(contribution_dates(days))
    for i, d in enumerate(days):
        prev = previous[d]
        op = np.array([frames[s].at[d, 'open'] for s in ('QQQ', 'TQQQ')], float)
        cl = np.array([frames[s].at[d, 'close'] for s in ('QQQ', 'TQQQ')], float)
        cash[:2] += q * np.array([frames[s].at[d, 'distribution'] for s in ('QQQ', 'TQQQ')], float)
        nav_open = permanent + float(cash.sum() + np.dot(q, op))
        # Indicators always use original USD frames/features, including in EUR view.
        state = classify(float(fs['QQQ'].at[prev, '_close']), fs['QQQ'].loc[prev])
        trend = bool(fs['TQQQ'].at[prev, '_close'] > fs['TQQQ'].at[prev, 'SMA200'])
        known = pd.notna(fs['QQQ'].at[prev, 'HIGH_VOL'])
        targets = np.array(sleeve_targets(state, trend, known)[:2])
        month = i == 0 or days[i-1][:7] != d[:7] or pending_flow
        budgets = weights * (nav_open - max(10., .01 * nav_open)) if month else np.r_[cash[:2] + q * op, cash[2]]
        wanted = budgets[:2] * targets / op
        caps = weights[:2] * (nav_open - max(10., .01 * nav_open)) / op
        trim = q > caps + 1e-9
        change = np.ones(2, dtype=bool) if prior_targets is None else targets != prior_targets
        desired = np.where(change | month | trim, np.minimum(wanted, caps), q)
        daily_fee = 0.
        for k in range(2):
            delta = min(0., desired[k] - q[k])
            fee = -delta * op[k] * bp / 20000.
            cash[k] -= delta * op[k] + fee
            q[k] += delta
            daily_fee += fee
            orders += int(delta < -1e-9)
        if month:
            free = permanent + float(cash.sum())
            need = np.maximum(0., budgets - np.r_[q * op, 0.])
            factor = min(1., free / need.sum()) if need.sum() else 0.
            cash = need * factor
            permanent = free - float(cash.sum())
        for k in range(2):
            delta = max(0., desired[k] - q[k])
            delta = min(delta, max(0., cash[k] / (op[k] * (1 + bp / 20000.))))
            fee = delta * op[k] * bp / 20000.
            cash[k] -= delta * op[k] + fee
            q[k] += delta
            daily_fee += fee
            orders += int(delta > 1e-9)
        prior_targets = targets
        if i == len(days)-1:
            for k in range(2):
                fee = q[k] * cl[k] * bp / 20000.
                cash[k] += q[k] * cl[k] - fee
                daily_fee += fee
                orders += int(q[k] > 0)
                q[k] = 0.
        before_flow = permanent + float(cash.sum() + np.dot(q, cl))
        flow = float(monthly) if d in deposits else 0.
        rets.append(before_flow / last - 1)
        permanent += flow
        paid += flow
        pending_flow = bool(flow)
        last = before_flow + flow
        navs.append(last)
        inlegs.append(paid)
        fee_total += daily_fee
        audit.append(dict(day=d,decision_day=prev,state=int(state),targets=targets.tolist(),
                          shares=q.tolist(),cash=cash.tolist(),reserve=permanent,flow=flow,fees=daily_fee))
        if before_flow <= 0 or min(cash) < -1e-7 or permanent < -1e-7:
            raise ValueError('CASH_OR_NAV_INVARIANT')
    return dict(daily_returns=rets,daily_NAV=navs,contributions=inlegs,fees=fee_total,orders=orders,audit=audit)


def statistics(returns, days, ending, contributions, fees=None, orders=None):
    r = np.asarray(returns, float)
    equity = np.r_[1., np.cumprod(1+r)]
    peak = np.maximum.accumulate(equity)
    longest = duration = 0
    recovery_calendar = 0
    start = pd.Timestamp(days[0]).tz_localize('America/New_York') + pd.Timedelta(hours=9.5)
    peak_day = start
    last_peak_index = 0
    episodes = []
    for i, value in enumerate(equity[1:]):
        stamp = pd.Timestamp(days[i]).tz_localize('America/New_York') + pd.Timedelta(hours=16)
        if value >= peak[i+1] - 1e-12:
            if duration:
                episodes.append(dict(sessions=duration,calendar_days=(stamp-peak_day).days,recovered=True))
            peak_day = stamp
            duration = 0
            last_peak_index = i+1
        else:
            duration = i+1-last_peak_index
            longest = max(longest, duration)
            recovery_calendar = max(recovery_calendar, (stamp-peak_day).days)
    if duration:
        episodes.append(dict(sessions=duration,calendar_days=(stamp-peak_day).days,recovered=False))
    elapsed = (pd.Timestamp(days[-1]+' 16:00',tz='America/New_York')-start).total_seconds()/(365.2425*86400)
    sd = r.std(ddof=1) if len(r)>1 else 0.
    return dict(ending=ending,contributions=contributions,profit=ending-contributions,
        CAGR_pct=100*(equity[-1]**(1/elapsed)-1),total_growth_pct=100*(equity[-1]-1),
        max_DD_pct=100*float(np.max(1-equity/peak)),Sharpe=float(np.sqrt(252)*r.mean()/sd) if sd else None,
        max_underwater_sessions=longest,max_underwater_calendar_days=max([recovery_calendar]+[e['calendar_days'] for e in episodes]),
        last_drawdown_unrecovered=bool(duration),fees=fees,orders=orders,sessions=len(days),elapsed_years=elapsed)


def s1_coverage(frames, fs, days, splits):
    # Reload the hashed raw minute CSVs, not an earlier private trade ledger.
    minute_frames, _ = minutes()
    paths = {}
    required = [d for d in days[:-1] if not early_close(d) and bool(fs['QQQ'].at[d,'S1'])
                and classify(float(frames['QQQ'].at[d,'close']),fs['QQQ'].loc[d]).value == 2]
    successors=dict(zip(days,days[1:]))
    for d in required:
        p, _ = minute_path(minute_frames['TQQQ'],d,successors[d],
            {'ATR14':fs['TQQQ'].at[d,'ATR14_pre']},splits['TQQQ'],'LATENCY',True,
            cash_dates=list(frames['QQQ'].index))
        if p is not None: paths[d]=p
    missing = [d for d in required if d not in paths]
    incomplete = [d for d in required if d in paths and not paths[d]['stop_data_complete']]
    def counts(subset):
        return dict(required=len(subset),anchors=sum(d in paths for d in subset),
                    complete_stop_paths=sum(d in paths and paths[d]['stop_data_complete'] for d in subset),
                    missing_anchors=sum(d in missing for d in subset),incomplete_stop_paths=sum(d in incomplete for d in subset))
    return dict(status='CENSORED_UNKNOWN_S1_PATHS',**counts(required),
                crash_2022=counts([d for d in required if d.startswith('2022-')]),
                missing_dates=missing,incomplete_dates=incomplete,
                rule='State2 + S1; TQQQ16:01 -> next09:31; stop0.50 priorATR; max0.5percentNAV risk')


def build():
    lock = ROOT/'research/profile-benchmark-register-2026-10-30.json'
    if lock.exists() and json.loads(lock.read_text())['fx_sha256'] != sha(FX):
        raise ValueError('ECB_SOURCE_BYTES_CHANGED')
    frames, audits, splits = daily()
    fs = {s:features(frames[s]).assign(_close=frames[s].close) for s in ('QQQ','TQQQ')}
    days = list(frames['QQQ'].loc['2019-01-01':].index)
    expected = list(pd.date_range(days[0],days[-1],freq='D').strftime('%Y-%m-%d'))
    assert [d for d in expected if is_session(d)] == days
    eur = fx_frames(frames)
    coverage = s1_coverage(frames,fs,days,splits)
    result = dict(schema=1,status='HISTORICAL_DEVELOPMENT_SIMULATION_NOT_LIVE_OR_INDEPENDENT',
        first=days[0],last=days[-1],days=days,initial=1000,monthly=100,
        method=dict(execution='PREVIOUS_CLOSE_SIGNAL_NEXT_OFFICIAL_DAILY_OPEN_REFERENCE',
            deposits='100 after first cash-session open of each subsequent month; deploy next open; no backdating',
            rebalance='Monthly paid reweighting plus existing daily sleeve cap trims and regime changes;1percent/min10 reserve',
            distributions='Split-adjusted prices; real dividend accrual once on ex-date; economic NAV, not settled payment cash',
            currency='USD reference plus EUR cash using prior-date ECB at open, latest published ECB at close; FX quotes/fees not observed',
            risk='Allocation state-machine study; daily NAV, not intraday DD; no new account circuit-breaker or reset policy',
            benchmark='QQQ/TQQQ TREND200 use own ETF SMA200. Extra TQQQ reference is not a sixth optimized model.',
            costs='2 or10bp roundtrip notional; half per leg; cash interest0; taxes and brokerFXfees excluded'),
        s1=coverage,models=MODELS,curves={},rows=[],sources={s:audits[s]['source_sha256'] for s in ('QQQ','TQQQ')},
        fx_sha256=sha(FX),source_reconciliation={s:audits[s]['adjustment_reconciliation_max_abs_error'] for s in ('QQQ','TQQQ')},
        splits=splits['TQQQ'],unscored_profiles={
            'defensive_s1_on':dict(label='Voorzichtig · S1 aan',weights=WEIGHTS['defensive'],status=coverage['status'],ending=None,CAGR_pct=None,max_DD_pct=None),
            'balanced_s1_on':dict(label='Gebalanceerd · S1 aan',weights=WEIGHTS['balanced'],status=coverage['status'],ending=None,CAGR_pct=None,max_DD_pct=None)})
    for currency, prices in [('USD',frames),('EUR',eur)]:
        for bp in (2,10):
            for monthly in (0,100):
                for model in MODELS:
                    if model in ('defensive_off','balanced_off','offensive'):
                        profile = model.removesuffix('_off')
                        run = profile_replay(prices,fs,days,profile,bp,monthly)
                    else:
                        asset = 'TQQQ' if model.startswith('tqqq') else 'QQQ'
                        rule = 'BUYHOLD' if model.endswith('buyhold') else 'TREND200'
                        f = pd.DataFrame({'TREND200':frames[asset].close>fs[asset].SMA200})
                        old = holding(prices[asset],f,days,rule,bp,monthly)
                        inleg = [1000+monthly*sum(x<=d for x in contribution_dates(days)) for d in days]
                        run = dict(daily_returns=old['daily_returns'],daily_NAV=old['daily_NAV'],contributions=inleg,
                                   fees=old['summary']['total_model_costs'],orders=old['summary']['orders'])
                    key = f'{currency}|{bp}|{monthly}|{model}'
                    result['curves'][key] = [round(v,5) for v in run['daily_NAV']]
                    summary = statistics(run['daily_returns'],days,run['daily_NAV'][-1],run['contributions'][-1],run['fees'],run['orders'])
                    ix = [i for i,d in enumerate(days) if d.startswith('2022-')]
                    year = statistics([run['daily_returns'][i] for i in ix],[days[i] for i in ix],
                        run['daily_NAV'][ix[-1]],run['contributions'][ix[-1]])
                    result['rows'].append(dict(currency=currency,RT_bp=bp,monthly=monthly,model=model,period='FULL',**summary))
                    result['rows'].append(dict(currency=currency,RT_bp=bp,monthly=monthly,model=model,period='2022',**year))
    # Exact zero-flow parity to the old allocation engine on its exact date range.
    old_days=list(frames['QQQ'].loc['2019-01-14':'2026-09-30'].index)
    parity={}
    for profile in WEIGHTS:
        a=archived_portfolio(frames,fs,old_days,profile,2,{},False)['daily_returns']
        b=profile_replay(frames,fs,old_days,profile,2)['daily_returns']
        delta=float(np.max(np.abs(np.array(a)-np.array(b))))
        assert delta<1e-12,(profile,delta)
        parity[profile]=delta
    result['archived_zero_flow_parity_max_error']=parity
    return result


def report(body):
    lines=['# Profielen versus eenvoudige referenties — 30 oktober 2026','',
        f"Doorlopend **{body['first']} t/m {body['last']}**, {len(body['days'])} volledige cashsessies. Ontwikkelingsdata, geen onafhankelijke validatie. Geen parameters gekozen op basis van deze uitkomsten.",
        '', '## Wat werkelijk berekend is','',
        'Dezelfde `features`, `classify`, `sleeve_targets` en gewichten als de bestaande studie. Zonder stortingen reproduceert de nieuwe runner de oude drie S1-uit-profielen op het oude tijdvenster tot <1e-12 per dag. Er is geen nieuw filter of alternatief stopbeleid toegevoegd.',
        '', 'De profielen houden eerst max(10,1% NAV) cash aan. Herweging is betaald op maand-/regimewissels; de bestaande dagelijkse cap-trims blijven aanwezig. Dit is een allocatiebacktest, geen replay van de lokale bot met lotgroottes, 5bp-kostenpoort, settlement, handmatige drawdown-reset of echte brokerquotes.',
        '', 'Vorige afgeronde slotbar bepaalt de volgende officiële opening. Het definitieve huidige slot wordt nooit als instap gebruikt. Eindliquidatie op 28 oktober is een vooraf gekozen onderzoeksgrens. Fractionele stukken, cashrente nul, belasting uitgesloten. Dag-NAV onderschat mogelijk intraday verliezen.',
        '', 'Splits worden niet opnieuw toegepast op reeds split-gecorrigeerde OHLC. Werkelijke dividenden worden eenmaal aan de vorige eigenaar toegekend op ex-date; dat is economische herbelegging, geen bewezen betaaldagcash. TQQQ-prijzen bevatten de fondsfinanciering al.',
        '', 'Maandinleg: januari 2019 is uitsluitend de begininleg. Vanaf februari komt 100 na de opening op de eerste cashdag beschikbaar; aankoop volgt op de eerstvolgende opening, tegen werkelijke historische ETF-koersen. Bij bear-regime blijft de storting cash. Rendement en drawdown worden flow-gecorrigeerd berekend; stortingen zijn geen rendement.',
        '', '## S1 blijft onbekend, geen fictief volledige lijn','',
        f"Vereiste S1-nachten: **{body['s1']['required']}**; exacte ankers: **{body['s1']['anchors']}**; complete geobserveerde stoppaden: **{body['s1']['complete_stop_paths']}**. Ontbrekende ankers {body['s1']['missing_anchors']}; onvolledige stoppaden {body['s1']['incomplete_stop_paths']}. Ook 2022: {body['s1']['crash_2022']}.",
        '', 'Voorzichtig 50/0/25/25 en Gebalanceerd 60/30/10 mét S1 houden daarom status **CENSORED_UNKNOWN_S1_PATHS**: eindvermogen, CAGR, DD en Sharpe onbekend. Geen same-close dagbarinvulling en geen ontbrekende nacht als nulrendement. De getoonde berekenbare profielen zijn expliciet **S1 uit**; die reservering blijft cash.',
        '', '## Valuta en kosten','',
        'Hoofdweergave EUR: cash in euro; ETF-aankoop/verkoop gebruikt de laatst vóór die datum gepubliceerde ECB USD-per-EUR-referentie; dagwaardering gebruikt de actuele beschikbare ECB-fix. Dit is historische FX-referentiewaardering, geen bewezen uitvoerbare wisselkoers. FX-spread/conversiecommissie en belastingen ontbreken. De aparte USD-weergave houdt de oude studies vergelijkbaar; zij mag niet als werkelijk euroresultaat worden gelabeld.',
        '', 'Kosten zijn vaste aannames van 2 en 10 bp RT, naar koop-/verkoopnotional. Werkelijke brokerminimumkosten kunnen hoger zijn. [ECB API](https://data.ecb.europa.eu/help/api/data-examples), [publicatie rond16:00CET](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).',
        '', '## Volledige reeks — zuivere groei zonder bijstorten','']
    for currency in ('EUR','USD'):
        lines += [f'### {currency} · 2 bp RT','', '| Regel | Eindwaarde vanaf1.000 | CAGR% | Groei% | MaxDD% | Sharpe | Langste onderwater sessies / kalenderdagen |', '|---|---:|---:|---:|---:|---:|---:|']
        for r in body['rows']:
            if (r['currency'],r['RT_bp'],r['monthly'],r['period'])==(currency,2,0,'FULL'):
                lines.append(f"| {MODELS[r['model']]} | {r['ending']:.2f} | {r['CAGR_pct']:.3f} | {r['total_growth_pct']:.2f} | {r['max_DD_pct']:.2f} | {r['Sharpe']:.3f} | {r['max_underwater_sessions']} / {r['max_underwater_calendar_days']} |")
    lines += ['', '## Vermogensopbouw —1.000 start +100 per maand, EUR2bp','', '| Regel | Eigen inleg | Eindvermogen | Winst boven inleg |','|---|---:|---:|---:|']
    for r in body['rows']:
        if (r['currency'],r['RT_bp'],r['monthly'],r['period'])==('EUR',2,100,'FULL'):
            lines.append(f"| {MODELS[r['model']]} | {r['contributions']:.2f} | {r['ending']:.2f} | {r['profit']:.2f} |")
    lines += ['', '## 2022 apart — bestaande posities uit2021 blijven bestaan','', 'De jaarcijfers komen uit de doorlopende replay, niet een gunstig herstartmoment in cash. Rendement en DD gebruiken het NAV-slot vóór2022 als start. Het dashboard toont bij2022 de bestaande vermogenslijn; het herstart geen portefeuille.', '', '| Regel | Valuta | RTbp | Rendement2022% | MaxDD2022% | Sharpe2022 |','|---|---|---:|---:|---:|---:|']
    for r in body['rows']:
        if r['period']=='2022' and r['monthly']==0:
            lines.append(f"| {MODELS[r['model']]} | {r['currency']} | {r['RT_bp']} | {r['total_growth_pct']:.2f} | {r['max_DD_pct']:.2f} | {r['Sharpe']:.3f} |")
    lines += ['', '## Meerwaarde — zonder mooipraterij','']
    for c in ('EUR','USD'):
        subset={r['model']:r for r in body['rows'] if (r['currency'],r['RT_bp'],r['monthly'],r['period'])==(c,2,0,'FULL')}
        for model in ('defensive_off','balanced_off','offensive'):
            r=subset[model]
            comparisons=[]
            for ref in ('qqq_buyhold','qqq_trend200','tqqq_trend200'):
                v=subset[ref]
                comparisons.append(f"{MODELS[ref]}: {'hoger' if r['ending']>v['ending'] else 'lager'} eindvermogen ({r['ending']-v['ending']:+.2f}), {'lagere' if r['max_DD_pct']<v['max_DD_pct'] else 'hogere'} DD ({r['max_DD_pct']:.2f}% vs{v['max_DD_pct']:.2f}%)")
            lines.append(f"- **{c} {MODELS[model]}** — "+'; '.join(comparisons)+'.')
    lines += ['', 'De eerder geciteerde19,6%/40,8% komen uit een andere begindatum/einddatum. De nieuwe gelijktijdige referenties hierboven hebben exact dezelfde2019-01-02–2026-10-28-periode. Een lagere DD is geen garantie voor nachtrust; herstelduur en hefboomverliezen blijven relevant.',
        '', 'De complete2/10bp-matrix staat in `research/PROFILE_BENCHMARK_RESULTS_2026-10-30.csv`. Het openbare JSON bevat uitsluitend afgeleide NAV-curves en aggregaten. Bron-OHLC, individuele orders en ledgers blijven lokaal. De oude6/8/10%-scenario’s blijven als bevroren archief bestaan, maar zijn geen actieve onderzoeksuitkomst meer en verdwijnen uit de standaardgrafiek.',
        '', '## Reproductie','', 'Benodigd: Python met numpy, pandas, python-dateutil en requests. Kopieer de onveranderde dagelijkse en minuutbestanden volgens de twee bronregisters onder data/raw; plaats de ECB-CSV op het geregistreerde relatieve pad. Er is geen brokerlogin, private ledger of betaald account nodig.', '', '`python -m scripts.profile_benchmark --verify` laadt opnieuw brondata, controleert hashes en geeft alleen bij byte-identieke uitkomsten vrij. `research/profile-benchmark-register-2026-10-30.json` legt bron-/codehashes en het outputhash vast. De toekomstsimulator is uitsluitend door de gebruiker ingestelde rekenkunde, zonder profielrendementsclaim.']
    return '\n'.join(lines)+'\n'


def run(verify=False):
    OUT.mkdir(parents=True,exist_ok=True)
    body=build()
    first=encode(body)
    if verify:
        second=encode(build())
        assert first==second,'NONDETERMINISTIC_REPRODUCTION'
    PUBLIC.parent.mkdir(parents=True,exist_ok=True)
    PUBLIC.write_bytes(first)
    # Only aggregates/derived NAV public. Original daily/minute bars are unchanged.
    (ROOT/'docs/PROFILE_BENCHMARK_VERDICT_2026-10-30.md').write_text(report(body))
    with (ROOT/'research/PROFILE_BENCHMARK_RESULTS_2026-10-30.csv').open('w') as f:
        fields=list(body['rows'][0]);w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(body['rows'])
    inputs=['scripts/profile_benchmark.py','portfolio_agent/regime.py','portfolio_agent/signal_engine.py',
        'scripts/portfolio_agent_study.py','scripts/etf_empirical/core.py','scripts/etf_empirical/data.py',
        'research/etf-empirical-sources-2026-10-29.json','research/etf-minute-intake-2026-10-29.json']
    register=dict(status=body['status'],source_hashes=body['sources'],fx_sha256=body['fx_sha256'],
        fx_source=dict(path=str(FX.relative_to(ROOT)),url='https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?startPeriod=2018-12-20&endPeriod=2026-10-28&format=csvdata',usage='prior-date publication at entry; current available fix at mark; reference not quote'),
        code_and_register_hashes={p:sha(ROOT/p) for p in inputs},public_output_sha256=hashlib.sha256(first).hexdigest(),
        public_bytes=len(first),independent_reload_byte_identical=verify,period=[body['first'],body['last']],
        obsolete_planning_data='ARCHIVED_NOT_HISTORICAL; no6/8/10profile rate used in new output')
    (ROOT/'research/profile-benchmark-register-2026-10-30.json').write_bytes(encode(register))
    print(json.dumps(dict(output=str(PUBLIC.relative_to(ROOT)),days=len(body['days']),rows=len(body['rows']),
                         bytes=len(first),reproduced=verify,s1=body['s1'],parity=body['archived_zero_flow_parity_max_error']),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true')
    run(parser.parse_args().verify)
