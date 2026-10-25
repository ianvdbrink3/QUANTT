"""python -m scripts.prop_challenge register|replay|verify|publish."""
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path
import numpy as np
from . import core as c
from . import data as d

ROOT=d.ROOT;OUT=ROOT/'artifacts/prop-challenge'
LOCK=ROOT/'research/prop-challenge-registration.json'
RESULT=ROOT/'research/prop-challenge-results.json'
PROOF=ROOT/'research/prop-challenge-verification.json'
FIRMS=[dict(id='TOPSTEP',consistency=.55,min_days=2,lock=0.,max_micro=50,inactivity=None,
            purchase=49.,renewal=49.,activation=149.),
       dict(id='MFFU_EOD',consistency=.30,min_days=4,lock=100.,max_micro=30,inactivity=7,
            purchase=225.,renewal=0.,activation=0.)]
SOURCES={
 'topstep_parameters':'https://help.topstep.com/en/articles/8284197-trading-combine-parameters',
 'topstep_floor':'https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit',
 'topstep_consistency':'https://help.topstep.com/en/articles/8284208-consistency-at-topstep',
 'topstep_subscription':'https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions',
 'topstep_pricing':'https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions',
 'topstep_risk_adjustments':'https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility',
 'mffu_parameters':'https://help.myfundedfutures.com/en/articles/16158363-rapid-eod-50k-a-comprehensive-look',
 'mffu_eval':'https://help.myfundedfutures.com/en/articles/11802636-traders-evaluation-simplified',
 'mffu_prices':'https://myfundedfutures.com/',
 'mffu_hours':'https://help.myfundedfutures.com/en/articles/9558251-permitted-times-to-trade',
}
OUTCOME_DTYPE=np.dtype([('state','u1'),('elapsed','u1'),('trades','<u2'),('net','<f8'),
                       ('fee','<f4'),('calendar_fee','<f4'),('blocked','<u2'),('skipped','<u2'),('quantity','<u2')])
METHOD=dict(status='EXPLORATORY_ROLLING_ACCOUNT_RESEARCH_NOT_INDEPENDENT_VALIDATION',date='2026-10-25',
 baseline='2d4b795de9547951ab2ed755b4d4dfa08fb37255',
 sample='All1171 cash dates in two eras, with pre-existing ATR/SMA warmup. Every start with a full21/42/63session followup for that horizon. No2021--2024 bridge, no flat missingyears, no same-date multiple minis/micros. Different horizon denominators and omitted right-edge starts explicit.',
 universe='319 combinations:5night choices includingnone x4morning choices includingnone x16subsets of4late components minusempty. Nine sizing profiles. No-stop night cannot be assigned finite exact-stop dollar risk:384 inadmissible cells reported,2487valid combination/sizing cells. No forced12--30 tradequota or extra signals.',
 selection='Only existing kernels. Published TRADE_THROUGH results select SB_AM/PM by maximum minimum-era dailyATRSharpe among variants positiveATR inboth eras; ties minimum-era ATR then name. Chosen AM5m bullCONT2R, PM1m bothCONT2R. ICT1 fixed1m bothON3R. Original pullback firstsignal restricted to>=10:15, as are first ICT1/AM orders; no search for a later signal after exclusion. Three Judas specs exact, no newMSS.',
 overlap='One account position or pending limit at a time. Order activation sorts first, then prioritynight,Judas,ICT1,SBAM,pullback,SBPM. Busy until confirmedexit minute+1 for intrabar exit, or exactopen exit. No early flatten at10:15, no using later fill/PnL to choose an earlier candidate. Sizing rejection doesnot reserve order slot. Unfilled placedlimits do reserve it. No netting across sleeves.',
 execution='Frozen causal strict1tick trade-through entry and stop-first unresolvedSL/TP. Night exact18:00 andnext09:30 samepreknown contract, .50/.75priorATR stops rounded towardentry. .75andbroad.50 are NEW research overlays. No gapfill clipping. No tickcertificate at18:00:05, no MNQquote/queueproof; historicalNQproxy includes pre-MNQlaunch data.',
 sizing='FIXED1/2/3. RISK200/300/400=floor(budget/(2USD*actualstoppts+3.22)), max3night/max10intraday, firmcapapplied. Budgetsmallerthan1MNQ=>skip. CUSHIONsamebase:headroom<1500=>0.5x, else realizednet>750=>1.5x. New-orderbudget halves at80% ofconsistency*3000dailyprofit;zero at100%. Cushionbudget<=headroom-100. No retroactive winnerclipping, no sizedtargetoptimization; actualgapriskunbounded.',
 floor='Startnet0,floor-2000; MLL tested through heldbar adverseOHLC and observedopen/close separately. Conservative possiblebreach counted separately from observed. Ratchet onlyEOD to max(previous,min(lock,peakEOD-2000)), lockTopstep0/MFFU100. EODpassafterallclosedtrades, net>=3000, bestday<=consistency*net, minimumactivecashdays2/4. No DLL unlessspecified, no invented ceilinglossfill.',
 gaps='Missing scheduled holdingminute beforeactualexit creates UNRESOLVED_SOURCE_PATH, never retroactive signalfilter or zero-filled survival. Knownpricebreach strictly beforegap may terminate first. Unknown remains inall-start denominator. Primarypasslower=knownpasses/N; sourceupper=(knownpasses+unknown)/N. Conditionalresolvedcost labeled; no unconditionalcostclaim withunknownpaths.',
 firms='Current2026 TopstepTC50K55%/EOD2000 and MFFURapidEOD50K30%/EOD2000,min4,7calendarday inactivity. Inactivity conservative day-level clock from activation/lastactualfill, no keepalive; exactvendoractivationtimestampunknown. These tests do not certify allrisk/newsrestrictions or futurefundedpayouts. Defaultmax10MNQ can exceed temporaryTopstep3micro newswindowcap; withoutverifiedhistoricaleventcalendar allrankingsremain conditional.',
 costs='3.22USD/MNQroundtrip once peractualfill, charged atentry; fixed1.22fee+assumed2slippage notcurrentMFFUquote. MainTopstep49initial+49per21sessionextension,149activationperpass. Calendar30dayrebilling sensitivity uses realdates separately. MFFUEOD225listpriceonce,norenewal,noactivation;promos/VATexcluded. Topstepreset49 REPLACES49freshentry,neverdoublecharged;99reset isuserstressnotofficial50Kprice. Costproxy=sumattemptfees/passes+activation assumes restartafterhorizon and empiricalretry mix; overlapping starts are not independent renewaltrials. Unknownpaths=>unconditionalcostnull.',
 ranking='Sort eligible min(era21passrate)>=10% separately from allcells; this transparent researchscreen isnot evidence of healthyfutureodds. Mainrankingmin-era pass thencombinedpass thenfee; costrankingseparate. Costeligible requires resolvedunconditionalcost inboth eras. Showallrows,including failures,unknowns,lowvolume andzeros. Nonoverlapping-phase0 starts reported as dependencecheck; no binomialCI/confirmatoryp on overlappingstartwindows.',
 publication='Two fresh source reconstructions, deterministicprivatecandidates/outcomes andpublicaggregate byteparity. All744 priortrackedfiles byteidentical; localuncommittedbot notsilentlypublished. Publiconlyaggregates, fullrankingCSV, methodologyandinteractivepage. No brokerorders,noaccountcreation,nopurchases.')


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')


def protected():
    # Local bot reference is not necessary for other machines: use committed git.
    return {n:digest(ROOT/n) for n in subprocess.check_output(['git','ls-files'],cwd=ROOT).decode().splitlines()
            if (ROOT/n).is_file() and not n.startswith(('scripts/prop_challenge/','tests/test_prop_challenge'))
            and n not in ('research/prop-challenge-registration.json','research/prop-challenge-results.json','research/prop-challenge-verification.json')
            and not n.startswith(('public/data/prop-challenge/','public/reports/PROP_CHALLENGE','docs/PROP_CHALLENGE','app/research/prop-challenge/','app/research/prop-firm/layout.tsx','scripts/publish_prop_challenge'))}


def register():
    if LOCK.exists():return verify()
    d.prior.verify()
    dump(LOCK,dict(method=METHOD,firms=FIRMS,sources=SOURCES,protected=protected(),
                  profiles=[asdict(p) for p in c.profiles()],universe=c.universe(),specs=d.SPECS))
    return dict(status='METHOD_AND_FINITE_UNIVERSE_LOCKED',combinations=len(c.universe()),valid_cells=sum(c.admissible(m,p) for m in c.universe() for p in c.profiles()))


def verify():
    x=json.loads(LOCK.read_text())
    code_lock=ROOT/'research/prop-challenge-code-lock.json'
    if code_lock.exists():
        for name,sha in json.loads(code_lock.read_text())['files'].items():
            assert digest(ROOT/name)==sha, 'Research code changed '+name
    assert x['method']==METHOD and x['firms']==FIRMS
    assert x['specs']==d.SPECS and x['profiles']==[asdict(p) for p in c.profiles()]
    assert x['universe']==c.universe()
    for name,sha in x['protected'].items():
        assert digest(ROOT/name)==sha, 'Frozen file changed '+name
    if PROOF.exists():
        for name,sha in json.loads(PROOF.read_text())['files'].items():
            assert digest(ROOT/name)==sha, 'Output changed '+name
    return dict(status='FROZEN_REFERENCES_VERIFIED',protected_files=len(x['protected']))


def combine(eras,firm):
    result={k:sum(e[k] for e in eras) for k in ('starts','passed','failed','unknown','unfinished')}
    n=result['starts']
    result.update(pass_rate=result['passed']/n,fail_rate=result['failed']/n,
                  pass_upper_source_unknown=(result['passed']+result['unknown'])/n,
                  mean_trades=sum(e['mean_trades']*e['starts'] for e in eras)/n)
    for what,key in [('passed','mean_days_to_pass'),('failed','mean_days_to_fail')]:
        total=result[what]
        result[key]=sum((e[key] or 0)*e[what] for e in eras)/total if total else None
    fees=sum(e['mean_attempt_fee_USD']*e['starts'] for e in eras)
    result['cost_per_pass_proxy_USD']=c.economic_cost(result['passed'],result['failed'],result['unfinished'],result['unknown'],fees,firm['purchase'],firm['activation'],firm['purchase'])
    result['cost_per_pass_resolved_paths_USD']=None
    return result


def one_run(folder):
    verify();folder.mkdir(parents=True,exist_ok=True)
    cash,candidates,source=d.build()
    dump(folder/'candidates.json',candidates)
    dump(folder/'source-verification.json',source)
    print('Raw reconstruction and strict kernel parity complete',flush=True)
    results=[];excluded=[]
    dump(folder/'cash-calendar.json',cash)
    raw=(folder/'rolling-outcomes.bin.gz').open('wb')
    ledgers=gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0,compresslevel=7)
    ledgers.write(b'QUANT_CHALLENGE_V1\n')
    for j,combo in enumerate(c.universe()):
        for profile in c.profiles():
            if not c.admissible(combo,profile):
                excluded.append(dict(combination=combo['id'],profile=profile.name,reason='NO_FINITE_STOP_FOR_STOP_DOLLAR_SIZING'));continue
            for firm in FIRMS:
                per_era={}
                for era,dates in cash.items():
                    outcomes=c.simulate(dates,candidates[era],combo,profile,firm)
                    per_era[era]={}
                    for horizon,rows in outcomes.items():
                        stats=c.summarize(rows,firm)
                        sparse=rows[::horizon]
                        stats.update(nonoverlap_starts=len(sparse),nonoverlap_pass_rate=sum(r[0]==c.PASS for r in sparse)/len(sparse),
                                     omitted_right_edge_starts=horizon-1)
                        per_era[era][horizon]=stats
                        header=[combo['id'],profile.name,firm['id'],era,horizon,len(rows)]
                        ledgers.write(json.dumps(header,separators=(',',':')).encode()+b'\n')
                        compact=np.array([tuple(row[:9]) for row in rows],dtype=OUTCOME_DTYPE)
                        ledgers.write(compact.tobytes())
                for horizon in c.HORIZONS:
                    eras={era:values[horizon] for era,values in per_era.items()}
                    total=combine(list(eras.values()),firm)
                    minimum=min(e['pass_rate'] for e in eras.values())
                    results.append(dict(combination=combo['id'],night=combo['night'],morning=combo['morning'],late=combo['late'],
                        sizing=profile.name,firm=firm['id'],horizon=horizon,eras=eras,combined=total,
                        min_era_pass_rate=minimum,healthy_both_eras_screen=minimum>=.10,
                        cost_eligible=all(e['cost_per_pass_proxy_USD'] is not None for e in eras.values())))
        if j%20==0: print(f'Rolling simulation {j+1}/{len(c.universe())} combinations',flush=True)
    ledgers.close();raw.close()
    result=dict(status=METHOD['status'],method=METHOD,firms=FIRMS,sources=SOURCES,
        universe=dict(combinations=len(c.universe()),profiles=len(c.profiles()),valid_cells=2487,excluded_cells=len(excluded),ranking_rows=len(results)),
        calendar={era:dict(sessions=len(ds),start=ds[0],end=ds[-1],windows={str(h):len(ds)-h+1 for h in c.HORIZONS}) for era,ds in cash.items()},
        source_summary={k:v for k,v in source.items() if k!='source_verification'},results=results,
        excluded=excluded,freeze_protected=len(json.loads(LOCK.read_text())['protected']))
    dump(folder/'summary.json',result)
    write_csv(folder/'ranking.csv',results)
    (folder/'report.md').write_text(report(result))
    verify()
    return result


def ranking(rows):
    return sorted(rows,key=lambda r:(-int(r['healthy_both_eras_screen']),-r['min_era_pass_rate'],
        -r['combined']['pass_rate'],r['combined']['cost_per_pass_proxy_USD'] or float('inf'),r['combination'],r['sizing']))


def write_csv(path,results):
    cols=['firm','horizon','combination','sizing','healthy_both_eras_screen','min_era_pass_rate','cost_eligible']
    measures=['starts','passed','failed','unknown','unfinished','pass_rate','pass_upper_source_unknown','fail_rate','mean_trades',
        'mean_days_to_pass','mean_days_to_fail','cost_per_pass_proxy_USD','cost_per_pass_resolved_paths_USD']
    fields=cols+[f'{era}_{key}' for era in ('2019_2021','2024_2026','COMBINED') for key in measures]
    with Path(path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in ranking(results):
            out={k:r[k] for k in cols}
            for era in ('2019_2021','2024_2026','COMBINED'):
                v=r['combined'] if era=='COMBINED' else r['eras'][era]
                out.update({f'{era}_{k}':v.get(k) for k in measures})
            w.writerow(out)


def report(x):
    lines=['# Rolling prop-challenge simulator','',METHOD['status'],'',
      'Exploratieve selectie op reeds gebruikte ontwikkelingsdata. Rolling vensters overlappen; percentages zijn historische frequenties, geen onafhankelijke slagingskans. Geen orders, aankopen of funded-certificering.','',
      '## Vast universum en noemers','',json.dumps(x['universe'],ensure_ascii=False),'',json.dumps(x['calendar'],ensure_ascii=False),'',
      'Alle volledige 21/42/63-sessievensters binnen elk echt tijdperk; nooit over de datakloof heen. De 21-sessiebenadering is niet exact 30 kalenderdagen. Private uitkomsten blijven lokaal.','',
      '## Ranglijst per firma en horizon','']
    fmt=lambda v: 'onbeslist' if v is None else f'{v:.2f}'
    for firm in FIRMS:
        for horizon in c.HORIZONS:
            rows=[r for r in x['results'] if r['firm']==firm['id'] and r['horizon']==horizon]
            leaders=ranking(rows)[:10]
            lines += [f"### {firm['id']} · {horizon} sessies",'',
              '| Combinatie | Sizing | Pass oud % | Pass recent % | Pass samen % | Fail % | Bron onbeslist % | Trades/poging | Kosten/pass $ |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|']
            for r in leaders:
                s=r['combined'];a=r['eras']['2019_2021'];b=r['eras']['2024_2026']
                lines.append(f"| {r['combination']} | {r['sizing']} | {100*a['pass_rate']:.2f} | {100*b['pass_rate']:.2f} | {100*s['pass_rate']:.2f} | {100*s['fail_rate']:.2f} | {100*s['unknown']/s['starts']:.2f} | {s['mean_trades']:.2f} | {fmt(s['cost_per_pass_proxy_USD'])} |")
            healthy=sum(r['healthy_both_eras_screen'] for r in rows)
            costs=sorted([r for r in rows if r['healthy_both_eras_screen'] and r['cost_eligible']],key=lambda r:r['combined']['cost_per_pass_proxy_USD'])
            lines += ['',f'{healthy}/{len(rows)} cellen halen de vooraf genoteerde beschrijvende 10%-grens in beide tijdperken. Dit is geen validatielabel.',
                ('Laagste onvoorwaardelijke kostenproxy onder die grens: '+costs[0]['combination']+' / '+costs[0]['sizing']+' / $'+fmt(costs[0]['combined']['cost_per_pass_proxy_USD'])) if costs else 'Geen combinatie met zowel die tweeperiodegrens als een volledig opgeloste kostenproxy.','']
    lines += ['## Bron- en uitvoeringskwaliteit','',json.dumps(x['source_summary'],ensure_ascii=False,indent=2),'',
      '## Kosteninterpretatie','',
      'Topstep: $49 per begonnen 21-sessieblok plus $149 activatie per geslaagde poging. Apart worden echte kalenderdatums en 30-dagen-rebilling berekend. Reset $49 vervangt heraanschaf $49; geen dubbeltelling. $99 is uitsluitend een gevraagde stressaanname, niet de officiële 50K-resetprijs.',
      'MFFU: Rapid EOD 50K, $225 eenmalige lijstprijs, geen maandverlenging en $0 activatie. Promotieprijzen en belasting niet verwerkt. $3,22 roundtrip is daar een gestandaardiseerde kostenaanname, geen bevestigde MFFU-quote.',
      'Kosten/pass = totale kosten van alle pogingen / geslaagde pogingen + activatie. Dit is een empirische herstartproxy; bij een horizonlimiet worden onvoltooide pogingen als beëindigd verondersteld. Het is geen exacte optimale resetplanning of onafhankelijke verwachtingswaarde. Bij onbesliste bronpaden blijft de onvoorwaardelijke kostenproxy leeg. De resolved-path proxy mag niet als ranglijstredding worden gebruikt.',
      '', '## Grenzen van de conclusie','',
      'Een model dat veel trades neemt is niet automatisch beter. Een losse voor-10:15 Judas-entry kan tot15:55 bezet blijven en blokkeert late pijlers. De nieuwe gestapelde modellen en sizingregels zijn niet out-of-sample getoetst. Selecteren op de hoogste rolling passrate is extra data-mining; geen promotion naar gevalideerd.',
      '1-minuut OHLC bewijst geen queuefills of tickvolgorde. De adverse bar-bound kan een verliesvloer conservatief raken die met bekende open/closeprijzen niet aantoonbaar geraakt is. Onbekende nachtminuten veroorzaken een apart onbeslist resultaat. NQ-prijzen zijn een MNQ-proxy; een deel van2019 ligt vóór MNQ-introductie.',
      'Topstep kan tijdelijk microcontractlimieten verlagen; een geverifieerde volledige historische nieuwskalender ontbreekt voor deze actuele2026regels. Daarom zijn accountpercentages conditioneel aan het gesimuleerde regelprofiel en geen volledige prop-compliance. MFFU-inactiviteit gebruikt een conservatieve kalenderdagdiagnose; exacte activatietijd is onbekend.',
      '', '## Exacte vastgelegde methode','']+[f'- **{k}**: {v}' for k,v in METHOD.items()]
    lines+=['','## Officiële bronnen','']+[f'- [{k}]({url})' for k,url in SOURCES.items()]
    return '\n'.join(lines)+'\n'


def replay():
    register()
    first=one_run(OUT/'run1')
    print('Run1 complete; second independent raw-source reconstruction',flush=True)
    one_run(OUT/'run2')
    files=['summary.json','candidates.json','cash-calendar.json','source-verification.json','rolling-outcomes.bin.gz','ranking.csv','report.md']
    assert all(digest(OUT/'run1'/n)==digest(OUT/'run2'/n) for n in files),'Independent reconstruction mismatch'
    dump(RESULT,first)
    target=ROOT/'docs/PROP_CHALLENGE_ROLLING_REPORT.md';target.write_bytes((OUT/'run1/report.md').read_bytes())
    paths=[RESULT,target]+[OUT/run/name for run in ('run1','run2') for name in files]
    dump(PROOF,dict(status='BYTE_IDENTICAL_DOUBLE_RAW_RECONSTRUCTION',files={str(p.relative_to(ROOT)):digest(p) for p in paths},
        frozen=verify(),private_outcomes_published=False))
    return dict(status='COMPLETE',rows=len(first['results']),protected=first['freeze_protected'])


def publish():
    verify();x=json.loads(RESULT.read_text())
    out=ROOT/'public/data/prop-challenge';out.mkdir(parents=True,exist_ok=True)
    # Compact columnar aggregate ranking, no per-start dates or trade arrays.
    columns=['combination','sizing','healthy','cost_eligible','pass','fail','unknown','unfinished','starts','trades','days_pass','days_fail','cost',
             'old_pass','new_pass','old_cost','new_cost','old_starts','new_starts','old_sparse_pass','new_sparse_pass','upper_pass']
    for firm in FIRMS:
        for horizon in c.HORIZONS:
            table=[]
            for r in ranking([r for r in x['results'] if r['firm']==firm['id'] and r['horizon']==horizon]):
                s=r['combined'];a=r['eras']['2019_2021'];b=r['eras']['2024_2026']
                table.append([r['combination'],r['sizing'],r['healthy_both_eras_screen'],r['cost_eligible'],s['pass_rate'],s['fail_rate'],
                    s['unknown']/s['starts'],s['unfinished']/s['starts'],s['starts'],s['mean_trades'],s['mean_days_to_pass'],s['mean_days_to_fail'],s['cost_per_pass_proxy_USD'],
                    a['pass_rate'],b['pass_rate'],a['cost_per_pass_proxy_USD'],b['cost_per_pass_proxy_USD'],a['starts'],b['starts'],
                    a['nonoverlap_pass_rate'],b['nonoverlap_pass_rate'],s['pass_upper_source_unknown']])
            dump(out/f'{firm["id"].lower()}-{horizon}.json',dict(columns=columns,rows=table))
    dump(out/'register.json',{k:x[k] for k in ('status','method','firms','sources','universe','calendar','source_summary','freeze_protected')})
    dest=ROOT/'public/reports'
    (dest/'PROP_CHALLENGE_ROLLING_REPORT.md').write_bytes((ROOT/'docs/PROP_CHALLENGE_ROLLING_REPORT.md').read_bytes())
    (dest/'PROP_CHALLENGE_FULL_RANKING.csv').write_bytes((OUT/'run1/ranking.csv').read_bytes())
    dump(ROOT/'research/prop-challenge-publication.json',dict(status='PUBLIC_AGGREGATES_ONLY',
        files={str(p.relative_to(ROOT)):digest(p) for p in list(out.glob('*.json'))+[dest/'PROP_CHALLENGE_ROLLING_REPORT.md',dest/'PROP_CHALLENGE_FULL_RANKING.csv']},private_data_included=False))
    return dict(status='PUBLISHED_LOCAL_AGGREGATES',tables=6)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['register','replay','verify','publish'])
    print(json.dumps(globals()[p.parse_args().action](),indent=2))
