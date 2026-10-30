"""Local owner-only demo secret file or explicit process environment. Never exported."""
from pathlib import Path
import json
import os
import stat
from .common import atomic


def read_credentials(root):
    key=os.environ.get('QUANT_T212_DEMO_KEY','');secret=os.environ.get('QUANT_T212_DEMO_SECRET','')
    if key and secret:return key,secret
    p=Path(root)/'demo-credentials.json'
    if not p.exists():return '',''
    if p.is_symlink() or p.stat().st_uid!=os.getuid() or stat.S_IMODE(p.stat().st_mode)!=0o600 or p.stat().st_size>8192:
        raise ValueError('DEMO_SECRET_FILE_PERMISSIONS_INVALID')
    body=json.loads(p.read_text())
    if set(body)!={'key','secret'} or not all(isinstance(v,str) and v and '\n' not in v for v in body.values()):raise ValueError('DEMO_SECRET_SCHEMA_INVALID')
    return body['key'],body['secret']


def setup(root):
    import getpass
    key=getpass.getpass('Trading 212 DEMO API key (verborgen): ')
    secret=getpass.getpass('Trading 212 DEMO API secret (verborgen): ')
    if not key or not secret:raise ValueError('EMPTY_DEMO_CREDENTIALS')
    atomic(Path(root)/'demo-credentials.json',dict(key=key,secret=secret))
    return dict(status='SAVED_LOCALLY_OWNER_ONLY',orders_enabled=False)
