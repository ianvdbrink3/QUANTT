"""Bounded, durable cash-history pagination; never interpret missing pages as zero."""
from .common import digest,stamp

PATHS={'transactions':'/equity/history/transactions','dividends':'/equity/history/dividends'}


def _items(rows,kind):
    result={};last=None
    for item in rows:
        ref=item.get('reference')
        if not isinstance(ref,str) or not ref:raise ValueError('CASH_HISTORY_REFERENCE_MISSING')
        at=stamp(item['dateTime' if kind=='transactions' else 'paidOn'])
        if last is not None and at>last:raise ValueError('CASH_HISTORY_ORDER_NOT_VERIFIED')
        last=at
        if ref in result and digest(result[ref])!=digest(item):raise ValueError('CASH_HISTORY_REFERENCE_CONFLICT')
        result[ref]=item
    return result


def _cursor(value,path):
    if not value:return None
    if not isinstance(value,str) or not value.startswith('/api/v0'+path+'?'):raise ValueError('CASH_HISTORY_CURSOR_REJECTED')
    from urllib.parse import urlparse,parse_qs
    s=value.removeprefix('/api/v0');p=urlparse(s)
    if p.fragment or '..' in value or set(parse_qs(p.query))-{'limit','cursor'}:raise ValueError('CASH_HISTORY_CURSOR_REJECTED')
    return s


def sync(client,store,kind):
    if kind not in PATHS:raise ValueError('CASH_HISTORY_KIND_INVALID')
    path=PATHS[kind];key='cash_history_scan:'+kind
    state=store.get(key,dict(committed={},pending=None));committed=state['committed'];pending=state.get('pending')
    target=pending['cursor'] if pending else path+'?limit=50'
    body=client.read(target)
    if not isinstance(body,dict) or not isinstance(body.get('items'),list):raise ValueError('CASH_HISTORY_SCHEMA_INVALID')
    page=_items(body['items'],kind);next_=_cursor(body.get('nextPagePath'),path)
    merged=dict(pending['items'] if pending else {})
    for ref,item in page.items():
        for old in (committed.get(ref),merged.get(ref)):
            if old is not None and digest(old)!=digest(item):raise ValueError('CASH_HISTORY_REFERENCE_CONFLICT')
        merged[ref]=item
    # A newest-to-oldest head with an unchanged known tail joins the verified archive.
    # Account cash must still reconcile; this is not a claim of atomic REST snapshots.
    anchor=not pending and bool(page) and list(page)[-1] in committed
    if not next_ or anchor:
        if pending:committed=dict(merged)
        else:committed.update(merged)
        state=dict(committed=committed,pending=None)
        with store.transaction():store.set(key,state)
        return list(committed.values()),True
    seen=pending['seen'] if pending else []
    if next_ in seen or len(seen)>=1000:raise ValueError('CASH_HISTORY_CURSOR_LOOP_OR_LIMIT')
    state['pending']=dict(cursor=next_,seen=seen+[next_],items=merged)
    with store.transaction():store.set(key,state)
    return list(committed.values()),False
