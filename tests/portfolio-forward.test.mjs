import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {forwardView,validateForwardRequest} from '../lib/portfolio-forward-local.mjs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');

test('forward route rejects production, remote origins, remote hosts and queries',()=>{
  validateForwardRequest('http://127.0.0.1:3013/api/portfolio-forward',null,false);
  for(const args of [
    ['http://127.0.0.1:3013/api/portfolio-forward',null,true],
    ['https://quantt-eight.vercel.app/api/portfolio-forward',null,false],
    ['http://127.0.0.1:3013/api/portfolio-forward','https://evil.example',false],
    ['http://127.0.0.1:3013/api/portfolio-forward?path=secret',null,false],
  ]) assert.throws(()=>validateForwardRequest(...args));
  const route=read('app/api/portfolio-forward/route.ts');
  assert.ok(route.includes('process.env.NODE_ENV === "production"'));
  assert.ok(!/export async function (POST|PUT|DELETE)/.test(route));
});

test('local forward status is an allowlist and heartbeat cannot hide stale service',()=>{
  const raw={schema:1,live_locked:true,mode:'ADVICE_ONLY',checked_at:'2026-10-30T18:00:00Z',market:{status:'CURRENT',secret:'FORBIDDEN'},
    broker:{connected:false,status:'PENDING',account_id:'FORBIDDEN'},orders:{total:0,quantity:'FORBIDDEN'},
    trial:{qualified_sessions:0},profiles:{defensive:{state:'PULLBACK',raw_key:'FORBIDDEN'}},credentials:'FORBIDDEN'};
  assert.ok(!JSON.stringify(forwardView(raw,new Date('2026-10-30T18:00:20Z'))).includes('FORBIDDEN'));
  assert.equal(forwardView(raw,new Date('2026-10-30T18:00:20Z')).heartbeat.status,'RECENT');
  assert.equal(forwardView(raw,new Date('2026-10-30T19:00:00Z')).heartbeat.status,'NOT_RECENT');
  assert.equal(forwardView(raw,new Date('2026-10-30T17:00:00Z')).heartbeat.status,'NOT_RECENT');
  assert.throws(()=>forwardView({...raw,live_locked:false}));
});

test('published account verification cannot imply permission for orders or a completed trial',()=>{
  const data=JSON.parse(read('public/data/portfolio-os/agent-readiness.json'));
  assert.equal(data.kind,'PUBLIC_SETUP_SNAPSHOT_NOT_A_LIVE_MAC_CONNECTION');
  assert.equal(data.live_locked,true);assert.equal(data.orders_enabled,false);
  assert.equal(typeof data.demo_account_verified,'boolean');assert.equal(data.forward_trial.qualified_sessions,0);
  if(data.demo_account_verified) assert.equal(data.broker_status,'DEMO_READ_VERIFIED_AT_PUBLICATION');
  assert.equal(data.readiness.ready_to_start,false);
  assert.ok(data.readiness.blocker_codes.includes('PRODUCT_BINDINGS'));
  assert.ok(data.readiness.blocker_codes.includes('EXECUTION_QUOTES'));
  assert.equal(data.steps.length,6);
  for(const forbidden of ['QUANT_T212_DEMO_KEY','account_id','limitPrice','/Users/','walletImpact']) assert.ok(!JSON.stringify(data).includes(forbidden));
  const ui=read('app/portfolio-os/agent-control.tsx');
  assert.ok(ui.includes('geen live verbinding met je Mac'));
  assert.ok(ui.includes('Alleen echte, volledige demo-observatiedagen tellen'));
  assert.ok(ui.includes('/reports/LOCAL_AGENT_EXECUTION_GUIDE_2026-10-30.md'));
  assert.ok(!ui.includes('method: "POST"'));
});

test('new public checks expose no private broker or history payloads',()=>{
  const data=JSON.parse(read('public/data/portfolio-os/agent-readiness.json'));
  assert.ok(data.readiness.checks.length>=8);
  assert.ok(data.product_review.length>=3);
  assert.ok(data.product_review.every(p=>p.backtest_performance_inherited===false));
  assert.ok(data.product_review.some(p=>p.legal_structure.includes('DEBT_ETP')));
  for(const forbidden of ['availableToTrade','totalValue','dateTime','reservedForOrders','demo-credentials','cash_baseline','broker_id','Authorization']) assert.ok(!JSON.stringify(data).includes(forbidden));
});
