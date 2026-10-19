"""Vercel production Release 0.8 smoke test — actual HTTP + Chromium DOM.

Runs in CI without Vercel credentials. Fails if public production route or data
is absent, synthetic provenance is lost, or key selectors fail to hydrate.
"""
from __future__ import annotations
import argparse
import json
import time
import urllib.request
from playwright.sync_api import sync_playwright

def fetch_json(url:str)->dict:
    with urllib.request.urlopen(url,timeout=25) as resp:
        if resp.status!=200: raise AssertionError(f"Expected HTTP 200: {url}")
        return json.loads(resp.read())

def verify(base:str)->None:
    base=base.rstrip('/')
    # Git provider deployment may still be switching aliases: require live
    # Python-generated reference, not the empty bootstrap JSON.
    ref=None
    for attempt in range(24):
        try:
            ref=fetch_json(base+'/data/research08.json')
            if ref.get('classification')=='DETERMINISTIC SYNTHETIC REFERENCE' and len(ref.get('runs',[]))==2:
                break
        except Exception as exc:
            print('Reference pending:',type(exc).__name__,str(exc)[:130],flush=True)
        time.sleep(10)
    else:
        raise AssertionError('Live export absent, incomplete, or still bootstrap placeholder')
    assert ref['edge_validated'] is False
    assert {r['instrument'] for r in ref['runs']}=={'NQ','ES'}
    assert all(r['provenance']=='SYNTHETIC SANDBOX (DETERMINISTIC)' for r in ref['runs'])
    assert all(r['governance']['holdout_sealed'] and not r['governance']['holdout_scored'] for r in ref['runs'])
    assert ref['sources'][0]['market_type']=='index_cfd'
    assert ref['sources'][1]['observed_bars']==0
    print('Production JSON: OK, NQ events',len(ref['runs'][0]['events']),'ES events',len(ref['runs'][1]['events']))
    with sync_playwright() as engine:
        browser=engine.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        response=page.goto(base+'/research',wait_until='networkidle',timeout=60000)
        assert response and response.status==200
        page.get_by_role('heading',name='Research Command Center').wait_for(timeout=30000)
        page.get_by_text('Reference export pending').wait_for(state='detached',timeout=25000)
        assert page.get_by_text('SYNTHETIC SANDBOX (DETERMINISTIC)').count()>=1
        assert page.get_by_text('EMPIRICAL CFD (DUKASCOPY - 1 DAY)').count()>=1
        assert page.get_by_text('CME FUTURES READY (AWAITING INGEST)').count()>=1
        assert page.locator('.r08-chart').count()>=2
        page.get_by_label('Instrument').select_option('ES')
        assert float(page.locator('.r08-tile').first.locator('strong').inner_text().replace(',',''))==next(r['quality']['rows'] for r in ref['runs'] if r['instrument']=='ES')
        page.get_by_label('Event family').select_option('VWAP Mean Reversion')
        page.get_by_label('Forward window').select_option('60')
        page.get_by_label('Costs').select_option('stress')
        page.get_by_label('OHLC fill bounds').select_option('optimistic')
        assert page.get_by_text('HOLDOUT SEALED').count()>=1
        assert not errors, 'Browser JavaScript errors: '+str(errors[:5])
        print('Production Chromium: selectors, charts, provenance and hydration OK')
        browser.close()
    for route in ('/','/quality','/sessions','/experiments'):
        with urllib.request.urlopen(base+route,timeout=25) as resp:
            assert resp.status==200
    print('Production legacy routes: HTTP 200')

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--url',default='https://quantt-eight.vercel.app')
    args=p.parse_args(argv)
    verify(args.url)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
