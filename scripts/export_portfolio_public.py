"""Export allowlisted historical research summaries, never raw market bars or ledgers."""
import argparse,hashlib,json,subprocess
from pathlib import Path

DATASETS=('current','60d_recent','60d_complete','60d_daily')

def export(source_root,output):
    output.mkdir(parents=True,exist_ok=True)
    manifest={}
    for dataset in DATASETS:
        result=subprocess.run([str(source_root/'.venv/bin/python'),'-m','portfolio_agent.os_api','--dataset',dataset],cwd=source_root,capture_output=True,text=True,check=True)
        s=json.loads(result.stdout)
        body={k:s[k] for k in ['mode','live_locked','policy_hash','active_profile','market_asof','market_status','generated_at','clocks','regime','s1','profiles','scenarios','costs','dataset','datasets']}
        body['public_summary']=True
        body['telemetry']={asset:{k:v for k,v in values.items() if k!='source_sha256'} for asset,values in s['telemetry'].items()}
        body['replay']={k:s['replay'][k] for k in ['first','last','days','execution_timing','orders','fills','missing_minute_quote_days']}
        a=s['audit']
        body['sleeve_balances']={}
        for sleeve in ['core','trend','s1','cash']:
            cash=sum(float(w['cash']) for w in a['wallets'] if w['sleeve']==sleeve)
            held=sum(float(p['qty'])*s['telemetry'][p['key']]['close'] for p in a['positions'] if p['sleeve']==sleeve)
            claims=sum(float(p['amount']) for p in a['settlements']+a['dividends'] if p['sleeve']==sleeve)
            body['sleeve_balances'][sleeve]=cash+held+claims
        days=[]
        for d in a['days']:
            day={k:d[k] for k in ['day','nav_reference','unit_nav','drawdown','fills','has_data_skip','has_cost_block']}
            day['advisor']={'state':d['advisor']['state']}
            day['decisions']=(['MISSING_EXACT_0931_ANCHOR'] if d['has_data_skip'] else [])+(['FRICTION_GATE'] if d['has_cost_block'] else [])
            days.append(day)
        intents=[{k:i[k] for k in ['id','day','key','sleeve','side','status','reason','policy_hash']} for i in a['intents']]
        body['audit']={'days':days,'intents':intents,'meta':{'policy_hash':a['meta']['policy_hash']},'wallets':[],'positions':[],'settlements':[],'dividends':[],
                       'database':{'status':'PUBLIC_RESEARCH_SNAPSHOT','modified_at':s['generated_at']}}
        body['briefs']=[{'day':d['day'],'markdown':f"# QUANT onderzoeksdagbrief — {d['day']}\n\nHISTORISCHE REPLAY — GEEN LIVEFEED OF BROKERBEWIJS\n\nRegime: {d['advisor']['state']}\nNAV-referentie: {float(d['nav_reference']):.2f}\nUnit-NAV: {float(d['unit_nav']):.6f}\nDrawdown: {float(d['drawdown'])*100:.2f}%\nUitgevoerde shadow-fills: {d['fills']}\nAnkerstatus: {'ONTBREEKT — GEEN VERVANGENDE FILL' if d['has_data_skip'] else 'BESCHIKBAAR'}\nFrictieblok: {'JA' if d['has_cost_block'] else 'NEE'}\n\nFX=1 referentie-eenheden; geen echte EUR-performance.\nSynthetische spreads; geen bewezen brokerfills.\nOpenbare samenvatting; volledige dagbrief en orderledger blijven lokaal.\n"} for d in days]
        body['database_checked_at']=s['generated_at']
        body['publication']={'mode':'PUBLIC_HISTORICAL_SUMMARY','contains_raw_bars':False,'contains_raw_ledger':False,'broker_connection':False}
        encoded=(json.dumps(body,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
        filename=f'{dataset}.json';(output/filename).write_bytes(encoded)
        manifest[filename]={'sha256':hashlib.sha256(encoded).hexdigest(),'days':len(days),'asof':s['market_asof']}
    (output/'manifest.json').write_text(json.dumps({'schema':1,'files':manifest,'raw_sources_included':False},indent=2)+'\n')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('public/data/portfolio-os'))
    args=p.parse_args();print(json.dumps(export(args.source_root.resolve(),args.output),indent=2))
