import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {publicCostRoutes,terminalClockContext} from '../lib/portfolio-public.mjs';
import {terminalSleeves,terminalDays,terminalShortcut} from '../lib/portfolio-terminal.mjs';

const read=name=>JSON.parse(readFileSync(new URL(`../public/data/portfolio-os/${name}.json`,import.meta.url),'utf8'));
const manifest=read('manifest');

test('published dataset hashes and 60-day coverage are consistent',()=>{
  for(const [name,info] of Object.entries(manifest.files)) {
    const data=readFileSync(new URL(`../public/data/portfolio-os/${name}`,import.meta.url));
    assert.equal(createHash('sha256').update(data).digest('hex'),info.sha256);
    const s=JSON.parse(data);assert.equal(s.audit.days.length,60);assert.equal(s.briefs.length,60);
    assert.equal(s.live_locked,true);assert.equal(s.s1.execution_allowed,false);
    assert.equal(s.policy_hash,s.audit.meta.policy_hash);
  }
  assert.equal(read('60d_complete').replay.missing_minute_quote_days,0);
  assert.equal(read('60d_recent').replay.missing_minute_quote_days,20);
});

test('public exports exclude raw source bars, ledger payloads, identifiers and paths',()=>{
  for(const name of Object.keys(manifest.files)) {
    const s=read(name.slice(0,-5)),raw=JSON.stringify(s);
    for(const forbidden of ['_database','_briefs','reserved_cash','limit_price','filled_qty','shadow-quantt-1000','/Users/','sqlite3','source_sha256']) assert.ok(!raw.includes(forbidden),forbidden);
    for(const k of ['wallets','positions','settlements','dividends']) assert.deepEqual(s.audit[k],[]);
    assert.ok(!('events' in s.audit));assert.ok(!('fills' in s.audit));
    assert.equal(s.public_summary,true);
    for(const i of s.audit.intents) {
      assert.deepEqual(Object.keys(i).sort(),['id','day','key','sleeve','side','status','reason','policy_hash'].sort());
      assert.match(i.id,/^[a-f0-9]{64}$/);
    }
  }
  assert.equal(existsSync(new URL('../app/api/portfolio-os',import.meta.url)),false);
});

test('public cost calculator reproduces frozen conditional rates and permission lock',()=>{
  const rows=Object.fromEntries(publicCostRoutes(100,3).map(r=>[r.key,r]));
  assert.equal(rows.ibkr.roundtrip_bp,254);assert.equal(rows.degiro.roundtrip_bp,204);
  assert.equal(rows.degiro.gates['5'].minimum_eur,20000);
  assert.equal(rows.degiro.gates['10'].minimum_eur,3333.34);
  assert.equal(rows.ibkr.gates['5'].minimum_eur,null);
  assert.equal(rows.alpaca.roundtrip_bp,null);assert.equal(rows.alpaca.gates['5'].minimum_eur,null);
  assert.equal(publicCostRoutes(1000,3).find(r=>r.key==='ibkr').roundtrip_bp,29);
  assert.ok(Object.values(rows).every(r=>Object.values(r.gates).every(g=>g.execution_approved===false)));
});

test('costs are monotonic and reject invalid public scenario inputs',()=>{
  for(const n of [1,100,1000,20000,1e6]) {
    const a=publicCostRoutes(n,3),b=publicCostRoutes(n,4);
    for(let i=0;i<a.length;i++) assert.ok(Math.abs(b[i].lower_bound_bp-a[i].lower_bound_bp-1)<1e-8);
  }
  for(const args of [[0,3],[-1,3],[1e6+1,3],[100,-1],[100,101],[NaN,3],[100,3,Infinity]]) assert.throws(()=>publicCostRoutes(...args));
});

test('live clock labels use current US/EU DST rules instead of snapshot DST',()=>{
  for(const [date,ny,nl,delta] of [['2026-01-15T18:00:00Z','EST','CET',6],['2026-07-15T18:00:00Z','EDT','CEST',6],['2026-03-15T18:00:00Z','EDT','CET',5],['2026-10-30T18:00:00Z','EDT','CET',5]])
    assert.deepEqual(terminalClockContext(new Date(date)),{ny_label:ny,nl_label:nl,offset_hours:delta});
});

test('public sleeve balances and profile previews conserve NAV without policy mutation',()=>{
  const s=read('current'),before=JSON.stringify(s),nav=Number(s.audit.days.at(-1).nav_reference);
  for(const profile of ['defensive','balanced','offensive']) assert.ok(Math.abs(terminalSleeves(s,profile).reduce((sum,r)=>sum+r.value,0)-nav)<1e-6);
  assert.equal(JSON.stringify(s),before);
});

test('audit filters stay linked to date; shortcuts never intercept input',()=>{
  const s=read('60d_recent');
  assert.equal(terminalDays(s.audit.days,'','data').length,20);
  assert.equal(terminalDays(s.audit.days,'','fills').length,8);
  for(const day of terminalDays(s.audit.days,'','fills')) assert.ok(s.briefs.some(b=>b.day===day.day));
  assert.equal(terminalShortcut('3',false,false),3);assert.equal(terminalShortcut('3',true,false),null);
});

test('public UI fetches static summaries in production and keeps historical evidence status',()=>{
  const src=readFileSync(new URL('../app/portfolio-os/portfolio-os.tsx',import.meta.url),'utf8');
  assert.ok(src.includes('process.env.NODE_ENV !== "production"'));
  assert.ok(src.includes('/data/portfolio-os/${dataset}.json'));
  assert.ok(src.includes('PUBLIC_SNAPSHOT / LIVE_LOCKED'));
  assert.ok(src.includes('REPLAY_ONLY'));
  assert.ok(!src.includes('http://127.0.0.1:3013'));
});
