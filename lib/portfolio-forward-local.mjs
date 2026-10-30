import { readFile } from 'node:fs/promises';
import path from 'node:path';

export function validateForwardRequest(url, origin, production) {
  const target=new URL(url);
  if(production || !['localhost','127.0.0.1','[::1]'].includes(target.hostname)) throw Error('LOCAL_ONLY');
  if(origin && new URL(origin).origin!==target.origin) throw Error('ORIGIN_REJECTED');
  if(target.search) throw Error('NO_QUERY_PARAMETERS');
}

export function forwardView(body,now=new Date()) {
  if(body.schema!==1 || body.live_locked!==true) throw Error('FORWARD_STATE_INVALID');
  const age=(now.getTime()-Date.parse(body.checked_at))/1000;
  if(!Number.isFinite(age)) throw Error('FORWARD_TIMESTAMP_INVALID');
  // Explicit allowlist. No broker balances, account numbers, payloads or credentials.
  const pick=(value,keys)=>Object.fromEntries(keys.map(k=>[k,value?.[k]]));
  return {schema:1,kind:'LOCAL_FORWARD_STATUS',live_locked:true,mode:body.mode,
    checked_at:body.checked_at,market:pick(body.market,['status','source_day','expected_day','independent_check']),
    broker:pick(body.broker,['connected','status','orders_enabled','bindings','execution_status']),
    orders:pick(body.orders,['total','working','unknown','filled']),
    halt:body.halt,trial:{qualified_sessions:body.trial.qualified_sessions,required_sessions:20,status:body.trial.status},
    readiness:body.readiness?{...pick(body.readiness,['status','ready_to_start','blocker_codes']),checks:body.readiness.checks.map(c=>pick(c,['code','passed','message']))}:undefined,
    product_review:body.product_review?.map(p=>pick(p,['ticker','isin','role','currency','legal_structure','issuer','catalog_identity_verified','account_currency_matches','next_execution_at_ny','next_execution_market_open','historical_execution_parity_verified','backtest_performance_inherited','status'])),
    heartbeat:{age_seconds:Math.max(0,Math.floor(age)),status:age>=0&&age<=180?'RECENT':'NOT_RECENT'},
    blocker:body.blocker,profiles:Object.fromEntries(['defensive','balanced','offensive'].filter(p=>body.profiles?.[p]).map(p=>[p,pick(body.profiles[p],['state','state_code','core_weight','trend_weight','signal_day'])])),alert_count:body.alert_count};
}

export async function loadForwardState() {
  const file=path.join(process.cwd(),'artifacts/portfolio_agent/forward/status.json');
  return forwardView(JSON.parse(await readFile(file,'utf8')));
}
