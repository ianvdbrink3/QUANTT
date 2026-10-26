"""Register -> source paths -> 252-session uniform risk and ongoing withdrawals."""
import argparse
import gzip
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
from scripts.prop_refinement import __main__ as prior
from scripts.prop_refinement.core import simulate_start as old_start
from scripts.oos_preparation.year import load_registered
from .core import RULES,Profile,MODELS,simulate_start,summarize

ROOT=prior.ROOT
OUT=ROOT/'artifacts/prop-uniform'
LOCK=ROOT/'research/prop-uniform-registration.json'
PATHS=OUT/'source-paths.json.gz'
NEW_MODELS=('S1-Judas-Bull0930','S1-Judas-0830','S2-Judas-STOP050','S2-Judas-STOP075')
SOURCES=dict(prior.SOURCES,
    topstep_callup='https://help.topstep.com/en/articles/13747178-live-funded-account-call-up-and-call-down-process',
    topstep_live='https://help.topstep.com/en/articles/10657969-live-funded-account-parameters',
    builder_live='https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide')
METHOD=dict(date='2026-10-26',status='EXPLORATORY_UNIFORM_RISK_FULL_WINDOW_NOT_INDEPENDENT_VALIDATION',
    universe='Fourfixedmodels:bothS1JudasandS2broadJ0830with.50/.75priorATRstops. Uniform300/350/400USDnominalrisk pertrade,bothpillars,max6MNQfixedbeforeoutcomes. No max8 orotherthresholdsearch. Stopdistanceandquartercontractknownatorder. No newentriesorATR/SMAdefinitions.',
    sizing='q=max(0,min(6,floor(budget/(2*stopPoints+3.22)))); no min1. ALSOskipif1contractactualfeesrisk>1.25budget,orwholepositionactualfeesrisk>1.25budget. CostsTopstep3.22/Builder6.50; henceBuildernominalriskcanslightlyexceedbudgetbutmuststayunder1.25budget. Zeroquantityneverplaces/reservesorder,paysfees,resetsclock,orcountersasa trade. Gapexecutioncanexceednominalriskcap; notstopguarantee.',
    holds='All252sessionsuntilfailure/end, continueafterpayout2. Recordreceivedfirst2,netfirst2,allreceivedcash,netall,andincrementafter2 fromSAMEaccountpath. No changeinwithdrawalpolicy:maximumpermittedatthefirsteligibleEOD,resetcounts/profit,fullgrossdeducted,onlytradershareincome. No retained-equity-as-income,noresets/reactivations. Identicalmonthlyfees; annualfeesnotchargedafterpass.',
    stages='TopstepyearassumesremainXFA;actualcallupisdiscretionary,notknownhistoricallyandcannotbedeclined. BuilderprimaryMAX5simwithdrawals;at5markSIM_LIMIT_REQUIRES_LIVE_RULES, full-yearpointnetunknownbecauseverifiedlive-onboarding/transfer/payoutconstraintsnotmodeled. Preserveknownreceivedcashaslower-observedamount. SeparateBuilderCONTINUED_SIM_COUNTERFACTUAL ignores5limitthrough252 toquantifyrequested6+payouts,NOTanavailablefundedplanorlivemodel. No inventedliveinitialcapital.',
    controls='Ninelegacycontrols:bothS1priorOBSERVED_KEEPALIVE_R300/ON2andS2nostopOBSERVED_KEEPALIVE/ON2,all3routes; verifyall6021original252sessionaccountfieldsbeforeoutcomes withcontinuationOFF. ThencontinuationON forisolatedpayouttruncationcomparison. Newuniformprofilesfirst2snapshotisolatessizingwithoutaddingfuturepayouts.',
    data='Same669overlappingstartwindows,498old+171recent,252cashdays,nonewperiod. ReusefullyobservedriskpathsforS1/Judas;reconstructexistingfrozenS2STOP050/075fromsamequartercontractsourcebars. Knownexistingentry/exit/priorATRstopparity. Missingminutesarenotprovedquiet;alloutcomesconditionalonobservedbars. No2021--2024bridge.',
    maintenance='Retainprevioussyntheticcash-noonkeepalive,6NYcalendardays/weekendaware,1MNQzero gross3.22cost. No automaticrealordersorclaimedfirmapproval. Baselineactualfees/slippageandDLL/MLLrulesunchanged; live-implementationstatusunconfirmed.',
    inference='Puredevelopmentcontrolonconsumedhistory,allprofilesreported,bothperiodsandcombined. No p-valueorindependentprofitabilityclaim fromoverlappingaccountstarts;nochoosingbudgetbytestoutcome. Passdaymediansconditionalonpass,changingcohortcannotproveper-accountspeedup.',
    preservation='Allpriortrackedbytespreserved. Newmodule/registration/report/aggregate anddashboardonly. SourceOHLCandaccountledgersstayGitignored. Deterministicdoubleaccountreplay. No brokeraccount purchases,transactionsorexternalmessages.')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')


def cases():
    rows=[]
    for r in RULES:
        for model in NEW_MODELS:
            for budget in (300.,350.,400.):
                rows.append((r,model,Profile(f'UNIFORM_{int(budget)}',True,True,uniform_budget=budget,continue_after_two=True)))
                if r.payout_path=='BUILDER':
                    rows.append((r,model,Profile(f'UNIFORM_{int(budget)}_CONTINUED_SIM_COUNTERFACTUAL',True,True,
                        uniform_budget=budget,continue_after_two=True,ignore_builder_stage_limit=True)))
        for model in ('S1-Judas-Bull0930','S1-Judas-0830','S2-Judas'):
            rows.append((r,model,Profile('LEGACY_SIZING_CONTINUE_AFTER_TWO',True,True,
                 judas_budget=300. if model.startswith('S1') else None,continue_after_two=True)))
    return rows


def registration():
    prior.registration()
    for n,d in json.loads((ROOT/'research/prop-refinement-verification.json').read_text())['files'].items():
        assert sha(ROOT/n)==d,n
    protected=[*sorted((ROOT/'scripts/prop_refinement').glob('*.py')),
       ROOT/'docs/PROP_ACCOUNT_REFINEMENT_REPORT_2026-10-26.md',
       ROOT/'public/data/prop-refinement/summary.json',ROOT/'research/prop-refinement-verification.json']
    code=sorted((ROOT/'scripts/prop_uniform').glob('*.py'))
    obj=dict(method=METHOD,sources=SOURCES,cases=[dict(firm=r.name,model=m,profile=asdict(p)) for r,m,p in cases()],
       protected={str(p.relative_to(ROOT)):sha(p) for p in protected},code_sha256={str(p.relative_to(ROOT)):sha(p) for p in code})
    if LOCK.exists():
        if json.loads(LOCK.read_text())!=obj:raise ValueError('Uniform protocol changed')
    else:dump(LOCK,obj)
    return obj


def paths():
    registration()
    src=json.loads(gzip.decompress(prior.PATHS.read_bytes()))
    raw=json.loads((ROOT/'artifacts/prop-challenge/run1/candidates.json').read_text())
    h=prior.baseline.prior.prior.h
    manifest=json.loads(h.REGISTER.read_text())
    for item in manifest['files']:assert sha(ROOT/item['private_copy'])==item['sha256']
    old=pd.read_parquet(h.OUT/'contract-bars.parquet')
    recent,reg,proof=load_registered(ROOT)
    full={'2019_2021':{c:g.sort_index() for c,g in old.groupby('contract')},
          '2024_2026':{c:g.sort_index() for c,g in recent.groupby('contract')}}
    count=gaps=0
    for era,days in raw.items():
        for day,trades in days.items():
            for t in trades:
                if t['component'] not in ('S2_STOP050','S2_STOP075'):continue
                enriched=prior.observed_records(t,full[era][t['contract']])
                enriched['entry_ny_day']=pd.Timestamp(t['entry_time']).tz_convert('America/New_York').strftime('%Y-%m-%d')
                assert enriched['risk']>0 and not enriched['unknown']
                if not t['unknown']:assert enriched['records'][-1][2]==t['adverse_min']
                src[era][day].append(enriched);count+=1;gaps+=t['unknown']
    for ds in src.values():
        for ts in ds.values():ts.sort(key=lambda t:(t['activation'],t['priority'],t['component']))
    OUT.mkdir(parents=True,exist_ok=True)
    PATHS.write_bytes(gzip.compress(json.dumps(src,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    dump(OUT/'source-verification.json',dict(path_sha256=sha(PATHS),prior_path_sha256=sha(prior.PATHS),
        stopped_S2_trades=count,stopped_S2_gapped_paths=gaps,old_source_hashes=len(manifest['files']),
        historical_cache_sha256=sha(h.OUT/'contract-bars.parquet'),recent_raw_reconstruction=proof,
        frozen_stopped_S2_prices_and_stops_reused=True))
    print(json.dumps(dict(status='UNIFORM_SOURCE_PATHS_READY',stopped_S2_trades=count)))


def parity():
    data=json.loads(gzip.decompress(prior.PATHS.read_bytes()))
    days=json.loads((ROOT/'artifacts/prop-challenge/run1/cash-calendar.json').read_text())
    old=json.loads(gzip.decompress((prior.OUT/'run1/accounts.json.gz').read_bytes()))
    count=0;rules={r.name:r for r in RULES}
    for a in old:
        target='OBSERVED_KEEPALIVE_R300' if a['model'].startswith('S1') else 'OBSERVED_KEEPALIVE'
        if a['horizon']!='252_SESSIONS' or a['overnight_MNQ']!=2 or a['profile']!=target:continue
        ds=days[a['era']];start=ds.index(a['start_day'])
        p=Profile(target,True,True,judas_budget=300. if a['model'].startswith('S1') else None)
        new=simulate_start(ds,data[a['era']],a['model'],2,rules[a['firm']],start,start+252,p)
        for k,v in a.items():
            if k in new:assert new[k]==v,(a['firm'],a['start_day'],k)
        count+=1
    assert count==6021
    dump(OUT/'parity.json',dict(status='EXACT_6021_PRIOR_ACCOUNT_PATHS',accounts=count))


def run_once(index):
    registration()
    assert sha(PATHS)==json.loads((OUT/'source-verification.json').read_text())['path_sha256']
    inputs=json.loads(gzip.decompress(PATHS.read_bytes()))
    calendar=json.loads((ROOT/'artifacts/prop-challenge/run1/cash-calendar.json').read_text())
    rows=[];accounts=[]
    for rule,model,p in cases():
        combined=[]
        for era,ds in calendar.items():
            part=[]
            for start in range(len(ds)-251):
                a=simulate_start(ds,inputs[era],model,2,rule,start,start+252,p)
                a.update(era=era,firm=rule.name,model=model,profile=p.name,budget_USD=p.uniform_budget)
                part.append(a)
            accounts.extend(part);combined.extend(part)
            rows.append(dict(era=era,firm=rule.name,model=model,profile=p.name,budget_USD=p.uniform_budget,**summarize(part)))
        rows.append(dict(era='COMBINED',firm=rule.name,model=model,profile=p.name,budget_USD=p.uniform_budget,**summarize(combined)))
        print(f'run{index} {rule.name} {model} {p.name}',flush=True)
    out=OUT/f'run{index}';out.mkdir(parents=True,exist_ok=True)
    dump(out/'summary.json',rows)
    (out/'accounts.json.gz').write_bytes(gzip.compress(json.dumps(accounts,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0))
    prior.baseline.write_csv(out/'summary.csv',[{k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows])
    return rows


def report(rows):
    text='''# Uniform dollar-risico en doorlopende payouts — 26 oktober 2026

Status: ONTWIKKELINGSCONTROLE, GEEN ONAFHANKELIJK GEVALIDEERD PROP-MODEL.

Alle669starts met252cashsessies:498oud (2019–2021),171recent (feitelijkvanafjanuari2025).
Drie vaste budgets $300/$350/$400 en één vooraf gekozen plafond van6MNQ voor beide
pijlers. S1 behoudt de .50ATR-stop; S2 krijgt afzonderlijk de bestaande .50/.75ATR
stopvarianten. De gewone regels/signalen blijven intact. Max8 is niet extra gezocht.

## Risico en kasstromen

Aantalcontracten=max(0,min(6,floor(budget/(2*stopafstand+$3,22)))). Geen minimum1.
Als de formule0oplevert wordt geen order geplaatst, geen fee gerekend, geen timer
gereset en geen tijdslot gereserveerd. Ook bij actual-fees-risico>1,25budget wordt
overgeslagen. Topstepnormaal3,22/MNQ,Builder6,50/MNQ: de laatste kan iets bovenbudget
liggen doordat de gevraagde size-formule3,22gebruikt, maar nooit boven1,25budget.
Dit begrenst nominaal stoprisico; gaps kunnen een stop-fill verslechteren.

De bestaande synthetische keep-alive blijft: nul bruto,3,22kosten,flatopcash-noon,
zesNYkalenderdagen met vervroeging voor weekend/feestdag. Geen bewezen één-seconde
fill of expliciete firmacceptatie. Geobserveerde bars bewijzen geen stille ontbrekende
minuten. Huidige2026accountregels worden retrospectief toegepast op NQalsMNQproxy.

Vanafdezelfdeaccountpath worden zowel de eerste2payouts als alle latere payouts
geteld. Na payout2 blijven alle saldo-/vloer-/consistentie-/fee-regels gelden.
Netto=ontvangen aandeel na winstdeling minus aankoop,abonnementen en activatie.
Geen onopgenomen equity als inkomen,geen retries,geen belasting/FX/API/transferkosten.
TweeMNQbetekent$4perpunt: $3.000targetvraagt750puntenvóórkosten, niet1.500punten.

## Volledig jaar versus eerste twee payouts

Elke rij is gemiddeld per ALLE gestarte accounts, inclusief niet-geslaagde starts.
Payoutaantallen en mediane passtijd zijn geen onafhankelijke replicaties. De oude
controle stopt niet meer bij2, zodat het effect van de eerdere truncatie apart staat.

| Firm | Model | Budget/profiel | Periode | Starts | Pass % | Mediane dagen tot pass | Netto $ eerste2 | Netto $ jaar | Extra cash na2 | Gem. payouts | Max. payouts | Live-overgang onbekend |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''
    for r in rows:
        net=r['mean_net_full_window_USD'];d=r['median_eval_cash_sessions_if_passed']
        text+=(f"| {r['firm']} | {r['model']} | {r['profile']} | {r['era']} | {r['starts']} "
          f"| {100*r['evaluation_pass_rate']:.2f} | {'—' if d is None else f'{d:.1f}'} "
          f"| {r['mean_net_first_two_USD']:.2f} | {'ONBEKEND' if net is None else f'{net:.2f}'} "
          f"| {r['mean_additional_cash_after_second_USD']:.2f} | {r['mean_payouts']:.2f} "
          f"| {r['max_payouts']} | {r['live_transition_unmodeled']} |\n")
    text+='''
## Grenzen aan de jaarprojectie

Topstep kan een XFA op discretionaire beoordeling naar Live overzetten; er is geen
vast payoutaantal. De jaarprojectie veronderstelt daarom dat XFAregels blijven
gelden; dit is geen voorspelling van een echte Live-callup of daaropvolgende cash.

Builder staat maximaal5Sim-payouts toe, daarna gelden andereLive-regels. De
hoofdvariant stopt die bekende Sim-fase na5 en markeert de ontbrekende verdere
levenscyclus. Jaar-netto staat danONBEKEND; reeds ontvangen cash wordt behouden.
CONTINUED_SIM_COUNTERFACTUAL toont daarnaast de volledige252dagen alsof dezelfde
Simregels mochten doorlopen. Dit kwantificeert6+payouts, maar is geen koopbaar
account of geverifieerdeLive-simulatie. GeenLive-startkapitaal of transferbedrag
verzonnen. Alle vorige rapporten blijven byte-identiek naast deze uitbreiding.

Nominale risico's,0-size-skips,payoutkansen en staten staan volledig in deCSV/JSON.
Reproduceren: python -m scripts.prop_uniform register,paths,run,verify. Eerst6021
bestaandeaccountpaths exact gereproduceerd, daarna dubbele byte-identiekeaccountreplay.
Private bronnen/prijsrecords/accountledgers blijvenGitignored. Dezelfde669starts
zijn hergebruikte ontwikkelingsdata,geen onafhankelijke validatie of causaliteitsbewijs.

## Officiële bronnen

'''
    for k,url in SOURCES.items():text+=f'- [{k}]({url})\n'
    return text


def run():
    parity();rows=run_once(1);run_once(2)
    for name in ('summary.json','summary.csv','accounts.json.gz'):
        assert sha(OUT/'run1'/name)==sha(OUT/'run2'/name)
    dest=ROOT/'public/data/prop-uniform'
    dump(dest/'summary.json',dict(method=METHOD,sources=SOURCES,rows=rows))
    (dest/'summary.csv').write_bytes((OUT/'run1/summary.csv').read_bytes())
    text=report(rows)
    (ROOT/'docs/PROP_UNIFORM_RISK_FULL_YEAR_2026-10-26.md').write_text(text)
    (ROOT/'public/reports/PROP_UNIFORM_RISK_FULL_YEAR_2026-10-26.md').write_text(text)
    files=[LOCK,PATHS,OUT/'source-verification.json',OUT/'parity.json',*(OUT/'run1'/n for n in ('summary.json','summary.csv','accounts.json.gz')),
       dest/'summary.json',dest/'summary.csv',ROOT/'docs/PROP_UNIFORM_RISK_FULL_YEAR_2026-10-26.md',ROOT/'public/reports/PROP_UNIFORM_RISK_FULL_YEAR_2026-10-26.md']
    dump(ROOT/'research/prop-uniform-verification.json',dict(status='DOUBLE_REPLAY_IDENTICAL',files={str(p.relative_to(ROOT)):sha(p) for p in files}))
    print(json.dumps(dict(status='UNIFORM_RESEARCH_COMPLETE',rows=len(rows))))


def verify():
    registration()
    for n,d in json.loads((ROOT/'research/prop-uniform-verification.json').read_text())['files'].items():assert sha(ROOT/n)==d,n
    print('UNIFORM_RESEARCH_VERIFIED')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('register','paths','run','verify'))
    a=p.parse_args().action;globals()[{'register':'registration'}.get(a,a)]()
