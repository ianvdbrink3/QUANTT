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
  const route=new URL('../app/api/portfolio-os/route.ts',import.meta.url);
  if(existsSync(route)) assert.ok(readFileSync(route,'utf8').includes("process.env.NODE_ENV === 'production'"));
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
  assert.ok(src.includes('Geen live-orders'));
  assert.ok(src.includes('REPLAY_ONLY'));
  assert.ok(!src.includes('http://127.0.0.1:3013'));
});

test('human growth curve preserves every published scenario endpoint',async()=>{
  const {growthPoints}=await import('../lib/portfolio-friendly.mjs');
  for(const s of read('current').scenarios){
    const rate=s.profile==='Defensief'?.06:s.profile==='Gebalanceerd'?.08:.1;
    const last=growthPoints(1000,+s.monthly_eur,+s.years,rate).at(-1);
    assert.equal(last.contributions,+s.total_contributions_eur);
    assert.ok(Math.abs(last.value- +s.planning_central_eur)<.0051);
  }
});

test('historical chart candidates cannot become invented public fills',async()=>{
  const {executedMarkers,chartPeriod}=await import('../lib/portfolio-friendly.mjs');
  assert.deepEqual(executedMarkers(read('current'),'QQQ'),[]);
  const days=[{day:'2022-06-01'},{day:'2022-12-30'},{day:'2026-10-28'}];
  assert.deepEqual(chartPeriod(days,'all','2022-12-30'),days.slice(0,2));
});

test('public chart defaults to TradingView and never requests the private history',()=>{
  const chart=readFileSync(new URL('../app/portfolio-os/portfolio-chart.tsx',import.meta.url),'utf8');
  assert.match(chart,/useState\(\s*process\.env\.NODE_ENV === "production" \? "live" : "strategy"/);
  assert.ok(chart.includes('De volledige lokale koershistorie wordt niet openbaar meegestuurd.'));
  assert.ok(chart.includes('length: 20')&&chart.includes('length: 200'));
  assert.equal(existsSync(new URL('../public/data/portfolio-os/chart_daily.json',import.meta.url)),false);
});

const benchmark=read('profile-benchmark');
test('historical comparison covers continuous2019-2026 and both crashes; no fabricated S1 results',()=>{
  assert.equal(benchmark.days.length,1967);
  assert.equal(benchmark.first,'2019-01-02'); assert.equal(benchmark.last,'2026-10-28');
  assert.equal(benchmark.days.filter(d=>d.startsWith('2022-')).length,251);
  assert.equal(benchmark.days.filter(d=>d.startsWith('2020-')).length,253);
  for(const [key,curve] of Object.entries(benchmark.curves)){
    assert.equal(curve.length,benchmark.days.length); assert.ok(curve.every(v=>Number.isFinite(v)&&v>0));
    const [currency,cost,monthly,model]=key.split('|');
    const r=benchmark.rows.find(r=>r.currency===currency&&r.RT_bp===+cost&&r.monthly===+monthly&&r.model===model&&r.period==='FULL');
    assert.ok(Math.abs(r.ending-curve.at(-1))<.00001);
    assert.equal(r.contributions,+monthly?10300:1000);
  }
  assert.equal(benchmark.s1.status,'CENSORED_UNKNOWN_S1_PATHS');
  for(const r of Object.values(benchmark.unscored_profiles)){assert.equal(r.ending,null);assert.equal(r.CAGR_pct,null);}
});
test('new primary historical data is byte-locked and contains no source OHLC or ledger',()=>{
  const reg=JSON.parse(readFileSync(new URL('../research/profile-benchmark-register-2026-10-30.json',import.meta.url)));
  const raw=readFileSync(new URL('../public/data/portfolio-os/profile-benchmark.json',import.meta.url));
  assert.equal(reg.public_output_sha256,createHash('sha256').update(raw).digest('hex'));
  assert.equal(reg.independent_reload_byte_identical,true);
  assert.ok(!raw.toString().includes('/Users/')); assert.ok(!raw.toString().includes('filled_qty'));
  assert.ok(!('audit' in benchmark));assert.ok(!('daily_ohlc' in benchmark));
  assert.deepEqual(benchmark.archived_zero_flow_parity_max_error,{balanced:0,defensive:0,offensive:0});
});
test('historical UI has explicit user-set simulator instead of fixed profile forecasts',()=>{
  const src=readFileSync(new URL('../app/portfolio-os/performance-comparison.tsx',import.meta.url),'utf8');
  assert.ok(src.includes('useState(0)'));assert.ok(src.includes('Rekensimulatie'));
  assert.ok(src.includes('qqq_buyhold'));assert.ok(src.includes('S1-reserve in cash'));
  assert.ok(!src.includes('0.06'));assert.ok(!src.includes('0.08'));
  const parent=readFileSync(new URL('../app/portfolio-os/portfolio-os.tsx',import.meta.url),'utf8');
  assert.ok(parent.includes('<PerformanceComparison profile={profile} />'));assert.ok(!parent.includes('function Growth('));
});
