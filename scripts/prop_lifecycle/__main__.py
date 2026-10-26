"""Register -> reconstruct source paths -> simulate/reproduce -> aggregate export.

python -m scripts.prop_lifecycle register|paths|run|verify
"""
import argparse
import csv
import gzip
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
import pandas as pd
from .core import RULES, MODELS, simulate_start, summarize
from scripts.prop_challenge import data as prior
from scripts.prop_challenge.__main__ import verify as frozen_verify

ROOT = prior.ROOT
OUT = ROOT/'artifacts/prop-lifecycle'
LOCK = ROOT/'research/prop-lifecycle-registration.json'
PATHS = OUT/'source-paths.json.gz'
SOURCES = {
    'topstep_pricing':'https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions',
    'topstep_subscription':'https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions',
    'topstep_XFA':'https://help.topstep.com/en/articles/8284215-express-funded-account-parameters',
    'topstep_payout':'https://help.topstep.com/en/articles/8284233-topstep-payout-policy',
    'topstep_floor':'https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit',
    'builder':'https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide',
    'builder_one_time':'https://myfundedfutures.com/',
    'builder_inactivity':'https://help.myfundedfutures.com/en/articles/16596524-inactivity-rule-one-time-payment-model',
    'builder_payout_floor':'https://help.myfundedfutures.com/en/articles/13745661-payout-policy-overview-best-and-fastest-prop-firm-payouts',
    'mffu_open_loss':'https://help.myfundedfutures.com/en/articles/8348565-end-of-day-eod-drawdown-explained',
}
METHOD = dict(date='2026-10-26', status='DEVELOPMENT_POOL_LIFECYCLE_RESEARCH_NOT_VALIDATED_MODEL',
    universe='Exactly S1-Judas-Bull0930,S1-Judas-0830,S2-Judas, fixed1/2MNQ. S1overnight .50ATRstop,S2nostop;18NY exact frozen entries; strict1ticktrade-through Judas. No third intraday candidate, no sizing/stop search.',
    rules='Current2026 rules retrospectively applied. Topstep50K Standard pricing49/30calendar days+149activation, eval55%, fundedStandard5days>=150 OR separately preregisteredConsistency3days40%,90%share; actual50Kcaps2000/3000,minimum125. Builder50Kdefault2000floor,1000DLL,153one-time,zeroactivation,80%share,min500cap2000,2100buffer,2activedays and48hours conservatively2calendar date differences; cycle50%. Buildereval7calendar inactivity per supplementary new-purchasepolicy; funded7. Also named counterfactual ignoreeval7 sensitivity, not an available account certification.',
    cost='Topstep3.22/MNQroundtrip (1.22fees+2assumedslippage); Builder6.50provisionalnotbrokerquote. Fixed quantity1/2, no risk-based resizing. All MNQ executions are proxies on NQbars, including pre-MNQlaunch. Terminal cash excludes retained equity, currencyconversion,VAT,transfers,automationfeesandtaxes.',
    timing='Each cash date starts a separate purchased account from precedingcivil18NY. No prior accruedprofit; no2019--2024era bridge. Actual trading candidates may use alreadyknown earlier signalday. Evalpasses atEOD -> fresh fundedzero nextcashGlobexsession;149charged atpass even ifright-edge. Never trade funded on same cashday. Pendingorders reserve account; activationorder priorityfrozen. No forcedearlyJudasexit forvolumeboost.',
    risk='EOD2000ratchet, fixedfloor throughoutday; intraday unrealizedloss includingentryfriction. OHLCadverse-first bounds, entrybarconservative. Records of newadverseminima stop atfirstmissing scheduledminute. FloorhitBEFOREgap may fail; otherwise gapUNKNOWN. DLL Builder softpause: earliestbarbarrierfill, adverseopenifgapped,otherwise quarterpointgross roundedadverse; existingfee/slippage assumption once, cancelallotherordersforthatcashday. DLL notfailure unlessgappedthroughfloor. Targets/strategyfills unchanged unlessaccountriskforcesexit. No tickcertification.',
    payouts='Request maximum currentlypermitted amount at firsteligible EOD, bothpayouts; no delayed-payout optimization. Assumeinstantapproval/creditandfullgrossdeduction, no reviewtime/transferfee. Topstepremainingequity=halfsubjectcap,floor0afterfirst. Builderretain2100buffer,min500sincecycle,cycleconsistencyresets,floor100afterfirst. Requalify days/profit separately, payoutdaynotnextcycle. Stop aftersecondcreditedpayout: reportednet iscashthroughsecondpayout orhorizon,NOT lifetimeincome. No resets/reactivations/retrycharges, since oneoriginalstartedaccount tracked totermination.',
    inactivity='No artificialkeepalive. Filled trade required (conservative to ambiguous placed-trade wording). Day-level NY calendar expiry beforecandidate/EOD atlastactualfillday+7Builder and+31Topstepfunded; accountactivationclock preceding18day. Weekend/holidaycalendar included. Discretionary may-close treated as closure; no vacationwaiver assumed.',
    endpoints='Every1171cashdate evaluated untilowneraend; all-right-edgecensoringretained. ALSO primaryequal252cashsessionhorizon onlystartswith252futurecashdates (498old+171recent). Counts success/failure/unknown/censored separately. Meanfinite-horizoncashwithknownpaths includes unfinishedaccounts fees/receivedcash,not unrealizedprofit. Unknownpath=>all-startpointmeanNULL; knownaccruedcash and resolved-onlymean explicitlylabelled,not unbiasedexpectation. No binomialCIorindependenceclaim onoverlappingstarts.',
    preservation='Frozen744files and prioroutcomehashes verified. New module/report/aggregates only. Paths and per-start accountledgers private. Two deterministic lifecycle replays on independently loaded verifiedsourcepath file; paths reconstructed once from sourcebars with kernelpriceparity, not falsely claimed as two rawsignalregenerations. No purchases/orders/deployment.')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False,
                               allow_nan=False, separators=(',', ':'))+'\n')


def registration():
    frozen_verify()
    inputs = [ROOT/'artifacts/prop-challenge/run1'/s for s in ('candidates.json','cash-calendar.json')]
    code = [ROOT/'scripts/prop_lifecycle'/s for s in ('__init__.py','core.py','__main__.py')]
    result = dict(method=METHOD, models=MODELS, rules=[asdict(r) for r in RULES],
                  sources=SOURCES, input_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},
                  code_sha256={str(p.relative_to(ROOT)):sha(p) for p in code})
    # JSON roundtrip converts tuples to arrays, allowing exact subsequent equality.
    result = json.loads(json.dumps(result))
    if LOCK.exists():
        if json.loads(LOCK.read_text()) != result:
            raise ValueError('Registered method, inputs or code changed')
    else:
        dump(LOCK,result)
    return result


def record_path(t, frame, calendar, detail):
    """Keep only successively adverse lows: exact barrier crossings, small file."""
    start, finish = pd.Timestamp(t['entry_time']), pd.Timestamp(t['exit_time'])
    rows = frame.loc[start:finish]
    if rows.index.has_duplicates:
        raise ValueError('Mixed-contract/duplicate risk path')
    if start not in rows.index or finish not in rows.index:
        raise ValueError('Frozen exact fill anchor missing')
    side, entry = detail['direction'], t['entry']
    first_day = start.tz_convert('America/New_York').strftime('%Y-%m-%d')
    last_day = finish.tz_convert('America/New_York').strftime('%Y-%m-%d')
    if t['night']:
        expected = []
        # Grid labels the next trading day; a Sunday stop still belongs to
        # Monday's reviewed grid. Match the original scheduled exit cash day.
        for day in pd.bdate_range(first_day, t['day']).strftime('%Y-%m-%d'):
            expected.extend(calendar.grid(day))
        expected = pd.DatetimeIndex(expected, tz='UTC')
    else:
        expected = pd.date_range(start, finish, freq='min')
    expected = expected[(expected >= start)&(expected < finish)]
    missing = expected.difference(rows.index)
    cutoff = missing.min() if len(missing) else None
    records = [[prior.minute(start), 0., 0.]]
    low_record = 0.
    for ts, row in rows.iterrows():
        if cutoff is not None and ts >= cutoff:
            break
        terminal = ts == finish
        opening = side*(float(row.open)-entry) if ts > start or detail['entry_at_open'] else None
        if terminal and detail['exit_at_open']:
            adverse = t['gross']
            opening = t['gross']
        else:
            adverse = side*(float(row.low if side == 1 else row.high)-entry)
            if terminal:
                if detail.get('stop_price') is not None:
                    adverse = max(adverse, side*(detail['stop_price']-entry))
                adverse = min(adverse, t['gross'])
        if opening is not None:
            adverse = min(adverse, opening)
        if adverse < low_record:
            low_record = float(adverse)
            records.append([prior.minute(ts), opening, low_record])
    if cutoff is None and t['gross'] < low_record:
        records.append([prior.minute(finish), t['gross'], t['gross']])
    # Independent consistency check against already-published conservative minima.
    measured = records[-1][2]
    if abs(measured-t['adverse_min']) > 1e-7:
        raise ValueError(('Risk path parity mismatch', t['component'], t['day'], measured,t['adverse_min']))
    return dict(t, records=records, negative_record_lows=[-r[2] for r in records],
                unknown=cutoff is not None, first_missing_utc=None if cutoff is None else str(cutoff),
                entry_ny_day=first_day)


def paths():
    registration()
    data, cash, full, sources = prior.prior.load_inputs()
    old = json.loads((ROOT/'artifacts/prop-challenge/run1/candidates.json').read_text())
    frozen = json.loads((prior.ict.OUT/'run1/orders-and-ledgers.json').read_text())['TRADE_THROUGH']
    details = {(t['block'], t['day'],label):t for label in ('J0830','JBULL0930')
               for t in frozen[prior.SPECS[label]]}
    out = {}
    stats = dict(fills=0, unknown=0, new_low_records=0)
    for era, days in old.items():
        active = data[era]['active']
        out[era] = {}
        for day, trades in days.items():
            use = []
            for t in trades:
                if t['component'] not in ('J0830','JBULL0930','S1_STOP050','S2_NO_STOP'):
                    continue
                if not t['filled']:
                    use.append(t)
                    continue
                if t['night']:
                    detail = dict(direction=1, entry_at_open=True, exit_at_open=t['reason']!='STOP',
                                  stop_price=t['entry']-t['risk'] if t['risk'] else None)
                    frame = full[era][t['contract']]
                else:
                    detail = details[era,day,t['component']]
                    assert abs(detail['entry_price']-t['entry']) < 1e-8
                    assert abs(detail['gross_points']-t['gross']) < 1e-8
                    frame = active
                enriched = record_path(t, frame, data[era]['calendar'], detail)
                assert enriched['unknown'] == t['unknown'], (t['component'],day)
                stats['fills'] += 1
                stats['unknown'] += enriched['unknown']
                stats['new_low_records'] += len(enriched['records'])
                use.append(enriched)
            out[era][day] = use
    payload = json.dumps(out,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    PATHS.parent.mkdir(parents=True,exist_ok=True)
    PATHS.write_bytes(gzip.compress(payload,mtime=0))
    dump(OUT/'path-verification.json',dict(sources=sources,stats=stats,path_sha256=sha(PATHS),
         exact_frozen_entry_exit_and_adverse_minimum_parity=True))
    print(json.dumps(dict(status='SOURCE_PATHS_RECONSTRUCTED',**stats)))


def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run_once(index):
    registration()
    if sha(PATHS) != json.loads((OUT/'path-verification.json').read_text())['path_sha256']:
        raise ValueError('Changed source paths')
    candidates=json.loads(gzip.decompress(PATHS.read_bytes()))
    calendar=json.loads((ROOT/'artifacts/prop-challenge/run1/cash-calendar.json').read_text())
    summaries=[]
    ledgers=[]
    # One explicitly labelled rule sensitivity: no closure for missing eval trades.
    rulesets=(*RULES, replace(RULES[2],name='MFFU_BUILDER_NO_EVAL_INACTIVITY_SENSITIVITY',eval_inactivity=None))
    for rules in rulesets:
        for model in MODELS:
            for quantity in (1,2):
                for horizon in ('ERA_END','252_SESSIONS'):
                    combined=[]
                    for era,dates in calendar.items():
                        n=len(dates) if horizon=='ERA_END' else max(0,len(dates)-251)
                        accounts=[]
                        for start in range(n):
                            a=simulate_start(dates,candidates[era],model,quantity,rules,start,
                                             None if horizon=='ERA_END' else start+252)
                            a.update(era=era,firm=rules.name,model=model,MNQ=quantity,horizon=horizon)
                            accounts.append(a)
                        combined.extend(accounts)
                        ledgers.extend(accounts)
                        summaries.append(dict(era=era,firm=rules.name,model=model,MNQ=quantity,
                                              horizon=horizon,**summarize(accounts)))
                    summaries.append(dict(era='COMBINED',firm=rules.name,model=model,MNQ=quantity,
                                          horizon=horizon,**summarize(combined)))
                    print(f'run{index} {rules.name} {model} {quantity} {horizon}',flush=True)
    target=OUT/f'run{index}'
    target.mkdir(parents=True,exist_ok=True)
    dump(target/'summary.json',summaries)
    body=json.dumps(ledgers,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    (target/'accounts.json.gz').write_bytes(gzip.compress(body,mtime=0))
    flat=[]
    for a in ledgers:
        flat.append({k:v for k,v in a.items() if k not in ('milestones','payouts')}|a['milestones'])
    write_csv(target/'accounts.csv',flat)
    write_csv(target/'summary.csv',[{k:json.dumps(v,sort_keys=True) if isinstance(v,dict) else v for k,v in r.items()}
                                    for r in summaries])
    return summaries


def report(rows):
    text='''# Accountlevenscyclus S1/S2-Judas — 26 oktober 2026

Status: BESCHRIJVEND ONTWIKKELINGSONDERZOEK; GEEN PROP-FIRM-GOEDKEURING.

Uitsluitend drie bestaande modellen op 1 of 2 MNQ, exacte 18:00-entry en twee
bestaande Judas-varianten. Geen derde intraday-motor of nieuwe signaalzoektocht.
Alle 1.171 cashsessies zijn ontwikkelingsdata. Huidige regels worden retrospectief
toegepast op NQ-prijzen als MNQ-proxy. Voor MNQ zijn $3,22 Topstep en voorlopig
$6,50 Builder roundtrip aangenomen, inclusief slippage; geen persoonlijke fillquote.

## Hoofdvergelijking: gelijk venster van 252 cashsessies

Elke accountstart heeft een volledig jaar aan mogelijke follow-up (498 starts in
2019–2021; 171 in het recentere blok). De recente feitelijke reeks begint 27 januari
2025. Geen sprong over ontbrekende jaren. Kolommen payout zijn percentages van ALLE
gestarte accounts. Dezelfde dagen overlappen tussen starts; geen onafhankelijke
herhaalde experimenten en geen confirmatoire p-waarden.

Een account stopt na de tweede payout, een floor-/inactiviteitsbreuk of de horizon.
Actieve accounts zijn gecensureerd, niet mislukt. 'Netto $' is ontvangen cash na
winstdeling minus betaalde abonnementen en activatie, tot dit eindpunt. Dit is geen
verwachting over de resterende levensduur. Achtergebleven simulatie-equity is geen
ontvangen inkomen. UNKNOWN heeft onopgeloste bronminuten: dan is de all-start
puntverwachting niet identificeerbaar en staat er ONBEKEND.

| Firm/payout-route | Model | MNQ | Periode | Starts | Eval gehaald % | Payout1 % | Payout2 % | Unknown % | Actief einde % | Netto $/start |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        if r['horizon']!='252_SESSIONS' or 'SENSITIVITY' in r['firm']:
            continue
        net=r['mean_net_cash_per_start_USD']
        text+=(f"| {r['firm']} | {r['model']} | {r['MNQ']} | {r['era']} | {r['starts']} "
               f"| {100*r['evaluation_pass_rate']:.2f} | {100*r['payout1_all_starts']:.2f} "
               f"| {100*r['payout2_all_starts']:.2f} | {100*r['unknown_rate']:.2f} "
               f"| {100*r['censored']:.2f} | {'ONBEKEND' if net is None else f'{net:.2f}'} |\n")
    text+='''
## Tijd tot evaluatie en funded-doorgang, gecombineerd op 252 sessies

Tijdsduur is uitsluitend gemeten bij bekende geslaagde evaluaties, geen voorspelde
wachttijd voor alle accounts. Buffer is de eerste funded-equity van $2.600, ook
voor Topstep als vergelijkingspunt; Topstep eist deze buffer niet. Een vroege payout
kan plaatsvinden zonder $2.600 te hebben bereikt. Een ontbrekende ratio betekent
dat er geen bekende evaluatiepass was. Funded-percentages hebben ALLE bekende
evaluatiepasses als noemer; unknown en onvoltooid worden niet stilzwijgend verwijderd.

| Firm | Model | MNQ | Passes | Mediane cashdagen tot pass | Gem. kalenderdagen | Gem. betalingen | Buffer/pass % | Payout1/pass % | Payout2/pass % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
'''
    def fmt(x,percent=False):
        return '—' if x is None else f'{x*(100 if percent else 1):.2f}'
    for r in rows:
        if r['horizon']!='252_SESSIONS' or r['era']!='COMBINED' or 'SENSITIVITY' in r['firm']:
            continue
        text+=(f"| {r['firm']} | {r['model']} | {r['MNQ']} | {r['known_evaluation_passes']} "
               f"| {fmt(r['median_eval_cash_sessions_if_passed'])} | {fmt(r['mean_eval_calendar_days_if_passed'])} "
               f"| {fmt(r['mean_eval_monthly_payments_if_passed'])} | {fmt(r['buffer2600_rate_given_pass'],True)} "
               f"| {fmt(r['payout1_rate_given_pass'],True)} | {fmt(r['payout2_rate_given_pass'],True)} |\n")
    text+='''
## Kosten, payout-beleid en beperkingen

- Topstep Standard-prijs: $49 per 30 kalenderdagen zolang evaluatie loopt, $149
  activatie bij pass; geen funded-abonnement. Hoofdroute XFA Standard: vijf dagen
  minstens $150 netto; aparte Consistency-route: drie dagen en 40%. 90% winstdeling,
  50K-caps respectievelijk $2.000/$3.000, minimum $125. Na payout floor nul.
- Builder Default: $153 eenmalig, geen activatie. $2.000 EOD-floor en $1.000 DLL;
  geen eval-consistency. Funded: buffer $2.100 plus minstens $500, twee dagen en
  48 uur, 50% cycle-consistency, 80% winstdeling, maximaal $2.000 per payout.
  Na eerste payout floor $100. De aanvullende inactiviteitsregel omvat bij nieuwe
  aankopen ook de evaluatie. Geen vakantie-ontheffing of geforceerde keep-alive.
- Verzoek het maximum dat op de eerste eligible EOD mag, geen geoptimaliseerd
  uitstel. Approval/credit direct aangenomen. Opnieuw kwalificeren na iedere payout;
  bruto withdrawal volledig uit saldo, alleen aandeel trader als ontvangen cash.
- Eén gestart account, zonder betaalde resets/reactivaties. Netto per start is
  dus inclusief de initiële aankoop, maar geen automatisch retry-budget. Geen
  belastingen, wisselkoers, transferkosten, API- of automatiseringsabonnementen.
- Strategiestops worden niet veranderd. Een DLL liquideert met een causale
  1m-barrier-aanname en pauzeert de dag. Gaps vullen slechter dan de drempel. De
  OHLC-volgorde is conservatief; intrabar-extremen zijn geen tick-fillbewijs.
- Volumeselectie/prijsankers uit de eerdere kernen worden hergebruikt; geen
  stille contractwissel in een positie. Ontbrekende geplande bronminuten worden
  nooit naar nul rendement of overleving vertaald. Accountvloer vóór het eerste
  datagat kan wel een bekende breuk bewijzen.
- Inactiviteit wordt conservatief als sluiting behandeld; officiële tekst noemt
  discretionaire sluiting. NY-kalenderdagen tellen, ook weekend/feestdag. Voor
  Topstep >30 dagen; Builder zeven. Een echte fill vereist, geen kunstmatige orders.

## Gevoeligheid en alle startdatums

`summary.csv` bevat beide perioden en gecombineerd, zowel iedere start tot het eigen
era-einde als het gelijke 252-sessievenster. Daarnaast één expliciet hypothetische
Builder-variant zonder eval-inactiviteitsafsluiting; dit is geen geverifieerd koopbaar
account. Zo wordt het verschil tussen marktverlies en inactiviteit zichtbaar.
De per-start registratie met alle milestones/fees staat privé in artifacts en wordt
niet in het dashboard gepubliceerd. Geen bestaande kernen of rapporten gewijzigd.

Reproduceren: `.venv/bin/python -m scripts.prop_lifecycle register`, vervolgens
`paths`, `run`, `verify`. Eén nieuwe bronpadreconstructie; twee deterministische
accountreplays met byte-identieke uitkomsten, niet twee nieuwe signaalbacktests.

## Bronnen (geraadpleegd 26 oktober 2026)

'''
    for name,url in SOURCES.items():
        text+=f'- [{name}]({url})\n'
    return text


def run():
    rows=run_once(1)
    run_once(2)
    for name in ('accounts.json.gz','accounts.csv','summary.json','summary.csv'):
        assert sha(OUT/'run1'/name)==sha(OUT/'run2'/name), name
    target=ROOT/'public/data/prop-lifecycle'
    dump(target/'summary.json',dict(method=METHOD,rules=[asdict(r) for r in RULES],rows=rows,sources=SOURCES))
    write_csv(target/'summary.csv',[{k:json.dumps(v,sort_keys=True) if isinstance(v,dict) else v for k,v in r.items()}
                                   for r in rows])
    (ROOT/'docs/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md').write_text(report(rows))
    public=ROOT/'public/reports/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md'
    public.write_text(report(rows))
    files=[LOCK,PATHS,OUT/'path-verification.json',*(OUT/'run1'/n for n in ('accounts.json.gz','accounts.csv','summary.json','summary.csv')),
           target/'summary.json',target/'summary.csv',public,ROOT/'docs/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md']
    dump(ROOT/'research/prop-lifecycle-verification.json',dict(status='BYTE_IDENTICAL_TWO_ACCOUNT_REPLAYS',
        files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(dict(status='COMPLETED',summary_rows=len(rows))))


def verify():
    registration()
    proof=json.loads((ROOT/'research/prop-lifecycle-verification.json').read_text())
    for name,digest in proof['files'].items():
        assert sha(ROOT/name)==digest,name
    print(json.dumps(dict(status='LIFECYCLE_VERIFIED',files=len(proof['files']))))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('register','paths','run','verify'))
    action=parser.parse_args().action
    globals()[dict(register='registration').get(action,action)]()
