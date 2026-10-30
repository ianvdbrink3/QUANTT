"""Execution quotes are an explicit unresolved dependency, never fabricated NBBO."""
from pathlib import Path
import json
import os
import stat


def read_quotes(root):
    p=Path(root)/'execution-quotes.json'
    if not p.exists():return {}
    if p.is_symlink() or p.stat().st_uid!=os.getuid() or stat.S_IMODE(p.stat().st_mode)!=0o600 or p.stat().st_size>100000:
        raise ValueError('EXECUTION_QUOTE_FILE_PERMISSIONS_INVALID')
    body=json.loads(p.read_text())
    if set(body)!={'schema','quotes'} or body['schema']!=1 or not isinstance(body['quotes'],dict):raise ValueError('QUOTE_PACKET_INVALID')
    for ticker,q in body['quotes'].items():
        required={'ticker','bid','ask','currency','observed_at','provider','source_sha256','synthetic','verified_execution_quote'}
        if not isinstance(q,dict) or set(q)!=required or q['ticker']!=ticker:raise ValueError('QUOTE_PACKET_INVALID')
        if not q['provider'] or not isinstance(q['source_sha256'],str) or len(q['source_sha256'])!=64:raise ValueError('QUOTE_PROVENANCE_MISSING')
        try:int(q['source_sha256'],16)
        except ValueError:raise ValueError('QUOTE_PROVENANCE_MISSING') from None
    return body['quotes']
