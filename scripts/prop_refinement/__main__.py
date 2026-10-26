"""Append-only refinement: register, paths, run, verify, publish aggregates.

Observed bars and cost-only maintenance are explicitly conditional scenarios.
"""
import argparse
import csv
import gzip
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from scripts.prop_lifecycle import __main__ as baseline
from scripts.prop_lifecycle.core import simulate_start as original_start
from scripts.oos_preparation.year import load_registered
from .core import RULES,MODELS,profiles,simulate_start,summarize

ROOT=baseline.ROOT
OUT=ROOT/'artifacts/prop-refinement'
LOCK=ROOT/'research/prop-refinement-registration.json'
PATHS=OUT/'observed-source-paths.json.gz'
SOURCES=dict(baseline.SOURCES,
    mffu_fair_play='https://help.myfundedfutures.com/en/articles/8444599-fair-play-and-prohibited-trading-practices',
    topstep_scaling='https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan',
    topstep_news='https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility')
METHOD=dict(date='2026-10-26',status='CONDITIONAL_DEVELOPMENT_SENSITIVITIES_NOT_PROP_APPROVAL',
    preservation='All previous744frozenfiles PLUS full strictlifecyclecode/reports/publicexports/registration and private replay hashes unchanged. New copied core; default configuration must match ALL originalperstart outputs before newscenarios. No oldsignalparameter or strategyfills changed.',
    windows='Same669overlapping252cash-sessionstarts (498old,171recent), no era bridge. Additionalall1171starts toowneraend forcompleteness. Stop atsecondpayout,failureorhorizon. Per-era andcombined, allstartsdenominators, no newindependentvalidationclaim. No p-values on retrospectiveprofileselection.',
    paths='STRICTriskpath stopsatfirstmissingminute andkeepsbounds. OBSERVED_BARS walks ALL actuallyobserved sourceOHLCuntilthe samefrozen tradeexit, retaining gapcounts. No forwardfill, no assumption missingminutes areprovenquiet, no reconstructionofunseenstop/floorhits; therefore numericalpass/payout/EV areCONDITIONAL,not actualtruepercentages. Sourceendpoint,contractandfrozenpriceparity verified. Existing kernels not rerun or repaired.',
    maintenance='Requested synthetic1MNQroundtrip, zero grosspricechange and3.22USDtotalcost, once6NYcalendar days inactivity. Cash12:00NY slot; ifnextknowncashnoon ispastday6 bringforward tocurrentnoon (weekends/holidays). Onlywhenflat,no normalfilltoday,no pendingorderatnoon,noDLLpause. Countsactualtrade/day,inactivityreset; NEVER150winningday. Costreducesbalanceandcycleprofit,cantriggerfloor. Firstbeforetimerexpiry. Syntheticone-secondfill andvendoracceptanceNOTverified; runasassumption,not realorders or automaticbotcode. AdditionalBuilder6.50maintenancecostsensitivity forhybridprofiles.',
    sizing='OvernightFIXED1/2MNQ. Judas eitherfixedsamequantityORrequestedbudget250/300USD:floor(budget/(2*initialstopPoints+3.22)), min1,max6. Originalcausalstopknownatorder,no futurePnL. Normaltradecost remainsTopstep3.22,Builder6.50. Minimum1 canexceedbudget; actualfeescanalsobreachbudget. Countandreport both, no falsehardriskcap. No wholeaccountfloorclippingriskrepair. SixMNQbelowordinaryXFA20microstartcap andBuilder40;Judasentries09:45--10:29 andmaintenance12avoidcurrentlistedTier1windows08:25--08:35,13:55--14:05,14:25--14:35. Historicalunlistedtemporaryrestrictionsnotcertified.',
    isolation='Comparestrictfixed/noKA; observedfixed/noKA; observedfixed/KA; observedhybrid250/KA; observedhybrid300/KA. S2onlyfirstthree. BothTopstepXFApathsandBuilder. BuilderadditionalKA6.50hybrids. No profit-chosenprofilechanges. Samefees/payoutpolicyasbaseline; maintenanceprice3.22explicitlydiffersfromBuildernormal6.50 andisnotabrokerquote.',
    output='Fullaggregates, per-era tables, netreceivedcashminusactualmodeledfees andactivation; retainedequitynotincome. Private accountledgers/observedriskarrays stayGitignored. Deterministicdoubleaccountreplaybyteparity. PublicbaselineANDrefinementreports,codeanddashboardaftertests/build; explicituserauthorizationforGitHubmainandVercelquanttproduction. No account purchases orbrokerorders.')


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')


def registration():
    baseline.registration()
    proof=json.loads((ROOT/'research/prop-lifecycle-verification.json').read_text())
    for name,digest in proof['files'].items():
        assert sha(ROOT/name)==digest,name
    files=[*sorted((ROOT/'scripts/prop_lifecycle').glob('*.py')),
           ROOT/'docs/PROP_ACCOUNT_LIFECYCLE_REPORT_2026-10-26.md',
           ROOT/'docs/PROP_ACCOUNT_LIFECYCLE_FINDINGS_2026-10-26.md',
           ROOT/'public/data/prop-lifecycle/summary.json',
           ROOT/'public/data/prop-lifecycle/summary.csv',
           ROOT/'research/prop-lifecycle-registration.json',
           ROOT/'research/prop-lifecycle-verification.json']
    code=sorted((ROOT/'scripts/prop_refinement').glob('*.py'))
    obj=dict(method=METHOD,sources=SOURCES,profiles=[asdict(p) for p in profiles()],
             rules=[asdict(r) for r in RULES],models=MODELS,
             protected={str(p.relative_to(ROOT)):sha(p) for p in files},
             code_sha256={str(p.relative_to(ROOT)):sha(p) for p in code})
    obj=json.loads(json.dumps(obj))
    if LOCK.exists():
        if json.loads(LOCK.read_text())!=obj: raise ValueError('Refinement registration changed')
    else: dump(LOCK,obj)
    return obj


def observed_records(t,frame):
    """Full observed ONLY, without the strict missing-minute cutoff."""
    start,end=pd.Timestamp(t['entry_time']),pd.Timestamp(t['exit_time'])
    rows=frame.loc[start:end]
    assert rows.index.is_unique and rows.contract.nunique()==1
    assert start in rows.index and end in rows.index
    assert float(rows.loc[start,'open'])==t['entry']
    stop=t['entry']-t['risk'] if t['risk'] is not None else None
    exit_open=t['reason']!='STOP'
    records=[[baseline.prior.minute(start),0.,0.]]
    minimum=0.
    for ts,r in rows.iterrows():
        opening=float(r.open)-t['entry']
        if ts==end and exit_open:
            assert opening==t['gross']
            adverse=opening
        else:
            adverse=float(r.low)-t['entry']
            if ts==end and stop is not None:
                adverse=max(adverse,stop-t['entry'])
            if ts==end:
                adverse=min(adverse,t['gross'])
        adverse=min(opening,adverse)
        if adverse<minimum:
            minimum=adverse
            records.append([baseline.prior.minute(ts),opening,adverse])
    return dict(t,records=records,negative_record_lows=[-r[2] for r in records],
                unknown=False,source_gap_retained=t['unknown'],observed_bars=len(rows))


def paths():
    registration()
    strict=json.loads(gzip.decompress(baseline.PATHS.read_bytes()))
    h=baseline.prior.prior.h
    register=json.loads(h.REGISTER.read_text())
    for item in register['files']:
        assert sha(ROOT/item['private_copy'])==item['sha256'],item['filename']
    # This exact cache was reconciled against raw CSVs in the published baseline;
    # keep its new hash and independently match every no-gap path below.
    old=pd.read_parquet(h.OUT/'contract-bars.parquet')
    recent,manifest,proof=load_registered(ROOT)
    full={'2019_2021':{c:g.sort_index() for c,g in old.groupby('contract')},
          '2024_2026':{c:g.sort_index() for c,g in recent.groupby('contract')}}
    observed={}
    same=changed=gaps=0
    for era,days in strict.items():
        observed[era]={}
        for day,trades in days.items():
            rows=[]
            for t in trades:
                if t['filled'] and t.get('night'):
                    t2=observed_records(t,full[era][t['contract']])
                    gaps+=t['unknown']
                    if not t['unknown']:
                        assert t2['records']==t['records'],(era,day,t['component'])
                        same+=1
                    else: changed+=t2['records']!=t['records']
                    rows.append(t2)
                else:
                    if t['filled']:
                        ny=pd.Timestamp(t['entry_time']).tz_convert('America/New_York')
                        minute=ny.hour*60+ny.minute
                        assert 585<=minute<=629 # only frozen Judas signals, before noon
                    rows.append(t)
            observed[era][day]=rows
    OUT.mkdir(parents=True,exist_ok=True)
    PATHS.write_bytes(gzip.compress(json.dumps(observed,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    dump(OUT/'source-verification.json',dict(path_sha256=sha(PATHS),strict_paths_sha256=sha(baseline.PATHS),
        historical_raw_files_hashed=len(register['files']),historical_cache_sha256=sha(h.OUT/'contract-bars.parquet'),
        historical_cache_origin='Previously raw-reconciled published baseline cache; no new signal generation',
        recent_source_files=len(manifest['sources'])+len(manifest['warmup_sources']),recent_reconstruction=proof,
        no_gap_night_paths_identical=same,gapped_night_paths=gaps,gapped_records_extended=changed))
    print(json.dumps(dict(status='OBSERVED_SOURCE_PATHS_READY',no_gap_identical=same,gapped=gaps,extended=changed)))


def parity():
    """Every original start, not a sample or only a matching aggregate."""
    from scripts.prop_lifecycle.core import simulate_start as old
    strict=json.loads(gzip.decompress(baseline.PATHS.read_bytes()))
    calendar=json.loads((ROOT/'artifacts/prop-challenge/run1/cash-calendar.json').read_text())
    original=json.loads(gzip.decompress((baseline.OUT/'run1/accounts.json.gz').read_bytes()))
    checks=0
    rules={r.name:r for r in RULES}
    for a in original:
        if a['firm'] not in rules: continue
        ds=calendar[a['era']];start=ds.index(a['start_day'])
        stop=None if a['horizon']=='ERA_END' else start+252
        actual=simulate_start(ds,strict[a['era']],a['model'],a['MNQ'],rules[a['firm']],start,stop)
        for key in actual:
            if key in a: assert actual[key]==a[key],(a['firm'],a['start_day'],key)
        checks+=1
    dump(OUT/'baseline-parity.json',dict(status='EXACT_ALL_FROZEN_ACCOUNT_FIELDS',account_paths=checks))
    print('Baseline account parity',checks)


def applicable(profile,model,rules):
    if model=='S2-Judas' and profile.judas_budget is not None:return False
    if 'KA650' in profile.name and rules.name!='MFFU_BUILDER':return False
    return True


def run_once(index):
    registration()
    assert sha(PATHS)==json.loads((OUT/'source-verification.json').read_text())['path_sha256']
    inputs={False:json.loads(gzip.decompress(baseline.PATHS.read_bytes())),
            True:json.loads(gzip.decompress(PATHS.read_bytes()))}
    calendar=json.loads((ROOT/'artifacts/prop-challenge/run1/cash-calendar.json').read_text())
    rows=[];accounts=[]
    for rule in RULES:
        for model in MODELS:
            for profile in profiles():
                if not applicable(profile,model,rule):continue
                for q in (1,2):
                    for horizon in ('252_SESSIONS','ERA_END'):
                        allrows=[]
                        for era,ds in calendar.items():
                            n=max(0,len(ds)-251) if horizon=='252_SESSIONS' else len(ds)
                            part=[]
                            for start in range(n):
                                a=simulate_start(ds,inputs[profile.observed_bars][era],model,q,rule,start,
                                                 start+252 if horizon=='252_SESSIONS' else None,profile)
                                a.update(era=era,firm=rule.name,model=model,overnight_MNQ=q,
                                         profile=profile.name,horizon=horizon)
                                part.append(a)
                            accounts.extend(part);allrows.extend(part)
                            rows.append(dict(era=era,firm=rule.name,model=model,overnight_MNQ=q,
                                             profile=profile.name,horizon=horizon,**summarize(part)))
                        rows.append(dict(era='COMBINED',firm=rule.name,model=model,overnight_MNQ=q,
                                         profile=profile.name,horizon=horizon,**summarize(allrows)))
                    print(f'run{index} {rule.name} {model} {profile.name} ON{q}',flush=True)
    target=OUT/f'run{index}';target.mkdir(parents=True,exist_ok=True)
    dump(target/'summary.json',rows)
    (target/'accounts.json.gz').write_bytes(gzip.compress(json.dumps(accounts,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    baseline.write_csv(target/'summary.csv',[{k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows])
    return rows


def report(rows):
    text='''# Prop-account levenscyclus — gerichte verfijning, 26 oktober 2026

Status: CONDITIONELE ONTWIKKELINGSSCENARIO'S, GEEN GOEDGEKEURD LIVE-MODEL.
De strikte eerdere rapporten en grenzen blijven byte-identiek beschikbaar.

## Vooraf vastgelegde vergelijking

1. FROZEN_STRICT: oorspronkelijke bronbevriezing, vaste 1/2 MNQ, geen keep-alive.
2. OBSERVED_BARS: alle daadwerkelijk geobserveerde OHLC tijdens dezelfde bestaande
   trades; geen bevriezing op een ontbrekende minuut, geen forward-fill.
3. OBSERVED_KEEPALIVE: voorgaande plus één synthetische 1-MNQ nul-bruto roundtrip
   met $3,22 kosten na zes NY-kalenderdagen, vervroegd vóór weekend/feestdag waar
   nodig. Uitvoering om 12:00 op een cashdag, uitsluitend flat en zonder werkende
   order of dagelijkse soft-pause. Een normale trade reset de timer al.
4. R250/R300: dezelfde onderhoudsregel, maar Judas-size floor(budget /
   (stopafstand × $2 + $3,22)), minimaal1/maximaal6MNQ. Overnight blijft1/2MNQ.
   KA650 is een extra Builder-kostenscenario van $6,50 per onderhoudstrade.

Dit is géén meting van het werkelijke pass-percentage: voor ontbrekende minuten is
niet bewezen dat er geen transacties waren of dat een floor/stop niet geraakt werd.
Een één-seconde marktfill met exact nul bruto rendement is evenmin zichtbaar in
1-minuut OHLC. Keep-alive-acceptatie is niet expliciet bevestigd door de firms;
het kostenmodel is een onderzoeksaanname, geen brokerintegratie of regelvrijgave.

Alle starts op dezelfde252cashsessies (498oud+171recent), én elke1171start tot
eigen era-einde. Geen onafhankelijke steekproeven door overlappende starts. Fees,
funded-reset naar nul, payout-consistency, winstdeling, floor na opname en de twee
payouts zijn gelijk aan de bevroren simulator. Geen nieuwe trading-signalen.

## Alle scenario's — gecombineerd, 669 starts met gelijke jaarfollow-up

Payout-percentages hebben alle starts als noemer, niet alleen geslaagde evaluaties.
Tijd tot pass is conditioneel op de bekende passes; geen wachttijdvoorspelling voor
alle accounts. ON is de vaste overnight-size; Judas kan onder hybride sizing meer
contracten gebruiken. Netto dollars = ontvangen payouts na winstdeling minus aankoop,
abonnementen en activatie tot tweede payout of horizon/falen. Onopgenomen equity
is geen cash. Niet de totale levensduur-EV; geen belasting/FX/API/transferkosten.

| Firm/payout-route | Model | Profiel | ON | Pass % | Mediane cashdagen tot pass | Payout1 % | Payout2 % | Netto $/start | Onbekend % | Gem. keep-alives |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        if r['era']!='COMBINED' or r['horizon']!='252_SESSIONS':continue
        n=r['mean_net_cash_per_start_USD'];d=r['median_eval_cash_sessions_if_passed']
        text+=(f"| {r['firm']} | {r['model']} | {r['profile']} | {r['overnight_MNQ']} "
               f"| {100*r['evaluation_pass_rate']:.2f} | {'—' if d is None else f'{d:.1f}'} "
               f"| {100*r['payout1_all_starts']:.2f} | {100*r['payout2_all_starts']:.2f} "
               f"| {'ONBEKEND' if n is None else f'{n:.2f}'} | {100*r['unknown_rate']:.2f} "
               f"| {r['mean_keep_alive_roundtrips']:.2f} |\n")
    text+='''
## Hybride profielen — beide historische perioden afzonderlijk

De minimum-1-clamp kan een $250/$300-budget overschrijden. Ook de $3,22 in de
size-formule kan de werkelijke gebruikte $6,50 Builder-kosten onderschatten.
Tellingen hieronder zijn account-executies over overlappende starts, geen unieke
trades. Grootste stoprisico is een nominale stopafstand+frictie, geen garantie bij gaps.

| Firm | Model | Profiel | ON | Periode | Pass % | Payout1 % | Payout2 % | Netto $/start | Budgetoverschrijdingen | Grootste nominaal Judas-stoprisico $ |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        if r['era']=='COMBINED' or r['horizon']!='252_SESSIONS' or r['profile'] not in ('OBSERVED_KEEPALIVE_R250','OBSERVED_KEEPALIVE_R300'):continue
        n=r['mean_net_cash_per_start_USD']
        text+=(f"| {r['firm']} | {r['model']} | {r['profile']} | {r['overnight_MNQ']} | {r['era']} "
               f"| {100*r['evaluation_pass_rate']:.2f} | {100*r['payout1_all_starts']:.2f} "
               f"| {100*r['payout2_all_starts']:.2f} | {'ONBEKEND' if n is None else f'{n:.2f}'} "
               f"| {r['judas_budget_overruns']} | {r['max_initial_judas_risk_USD']:.2f} |\n")
    text+='''
## Controles en gebruik

De exacte oorspronkelijke accountvelden worden voor alle33.120oorspronkelijke
accountpaden van de drie officiële routes opnieuw vergeleken. Daarna twee nieuwe
deterministische replays met byte-identieke accountledgers en aggregaten. De private
bronnen, prijsrecords en accountledgers worden niet gepubliceerd. Regels en bronhashes
staan in research/prop-refinement-registration.json en het verificatiebewijs.

Nieuw dashboard: /research/prop-refinement; bevroren lifecycle: /research/prop-lifecycle.
Reproduceer: python -m scripts.prop_refinement register, paths, run, verify.
Alle selecties en profielen blijven ontwikkelingsonderzoek op reeds bekeken data.
Een hoger scenarioresultaat bewijst geen causaliteit van een edge of prop-goedkeuring.

## Officiële bronnen, geraadpleegd 26 oktober 2026

'''
    for name,url in SOURCES.items():text+=f'- [{name}]({url})\n'
    return text


def run():
    parity()
    rows=run_once(1);run_once(2)
    for name in ('summary.json','summary.csv','accounts.json.gz'):
        assert sha(OUT/'run1'/name)==sha(OUT/'run2'/name),name
    dest=ROOT/'public/data/prop-refinement'
    dump(dest/'summary.json',dict(method=METHOD,sources=SOURCES,profiles=[asdict(p) for p in profiles()],rows=rows))
    (dest/'summary.csv').write_bytes((OUT/'run1/summary.csv').read_bytes())
    text=report(rows)
    (ROOT/'docs/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md').write_text(text)
    (ROOT/'public/reports/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md').write_text(text)
    files=[LOCK,PATHS,OUT/'source-verification.json',OUT/'baseline-parity.json',
           *(OUT/'run1'/n for n in ('summary.json','summary.csv','accounts.json.gz')),
           dest/'summary.json',dest/'summary.csv',ROOT/'docs/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md',
           ROOT/'public/reports/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md']
    dump(ROOT/'research/prop-refinement-verification.json',dict(status='BYTE_IDENTICAL_TWO_REFINEMENT_REPLAYS',
         files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(dict(status='REFINEMENT_COMPLETE',summary_rows=len(rows))))


def verify():
    registration()
    for name,digest in json.loads((ROOT/'research/prop-refinement-verification.json').read_text())['files'].items():
        assert sha(ROOT/name)==digest,name
    print('REFINEMENT_AND_FROZEN_LIFECYCLE_VERIFIED')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('register','paths','run','verify'))
    a=p.parse_args().action
    globals()[{'register':'registration'}.get(a,a)]()
