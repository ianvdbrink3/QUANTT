"""Extract only committed frontend files to a clean, private-data-free release."""
import argparse
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
TOP={'app','components','lib','public'}
CONFIG={'package.json','package-lock.json','next-env.d.ts','next.config.ts',
        'postcss.config.mjs','tsconfig.json','vercel.json','.vercelignore',
        'research/historical-calendar-v2-verification.json'}


def allowed(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts:return False
    if not (p.parts[0] in TOP or name in CONFIG):return False
    if any(part in {'.git','.env','.venv','raw','private','artifacts','research_runs','node_modules'} for part in p.parts):return False
    if p.name.startswith('.env') or p.suffix in {'.parquet','.gz','.zip','.sqlite','.db'}:return False
    if '_intraday-' in p.name or p.name.startswith(('Dataset_NQ_','NQ_in_')):return False
    if p.suffix=='.csv' and not name.startswith(('public/reports/','public/data/')):return False
    return True


def build():
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    files=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT).decode().splitlines()
    files=[n for n in files if allowed(n)]
    if 'app/research/operational/page.tsx' not in files or 'public/reports/OPERATIONAL_TRADING_PLAYBOOK.md' not in files:
        raise ValueError('Operational release has not been committed')
    stage=Path(tempfile.mkdtemp(prefix='quantt-operational-',dir='/private/tmp'))
    archive=subprocess.check_output(['git','archive','--format=tar','HEAD','--',*files],cwd=ROOT)
    hashes={}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            if member.isdir():continue
            if not member.isfile() or not allowed(member.name):raise ValueError('Unsafe release member: '+member.name)
            payload=tar.extractfile(member).read()
            target=stage/member.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
            hashes[member.name]=hashlib.sha256(payload).hexdigest()
    if set(hashes)!=set(files):raise ValueError('Incomplete frontend extraction')
    receipt=dict(status='COMMITTED_FRONTEND_ONLY',commit=commit,stage=str(stage),files_sha256=hashes,
                 private_data_included=False,source_tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT).decode().strip())
    out=ROOT/'artifacts/operational-publication';out.mkdir(parents=True,exist_ok=True)
    (out/'stage-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return dict(stage=str(stage),commit=commit,frontend_files=len(hashes),private_data_included=False)


if __name__=='__main__':print(json.dumps(build(),indent=2))
