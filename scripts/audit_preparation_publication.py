"""Audit the exact Git additions and Vercel source list before publishing.

No deployment, Git write, scoring or private-source upload is performed here.
"""
import json
import re
import subprocess
from pathlib import PurePosixPath
from scripts.prepare_historical_contracts import ROOT, verify, dump, sha

PROJECT='prj_2obEIjnqg5YtfDRE8dM53kJFYHnm'
SCOPE='ianvdbrink3s-projects'


def forbidden(name):
    p=PurePosixPath(name)
    return (name.startswith(('data/raw/','data/curated/','artifacts/','private/','research_runs/','.venv/','.git/'))
        or any(z.startswith('.env') or z=='__pycache__' for z in p.parts)
        or p.suffix in ('.parquet','.sqlite','.db','.pem','.key'))


def audit():
    integrity=verify()
    additions=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    additions=[p for p in additions if p]
    allowed=('app/research/','docs/','research/','public/','scripts/','tests/')
    bad=[p for p in additions if not p.startswith(allowed) or forbidden(p)]
    if bad:raise ValueError('Unexpected/private Git additions: '+str(bad))
    secret=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{24}|github_pat_[A-Za-z0-9_]{24}|sk_live_[A-Za-z0-9]{16}')
    secret_files=[];price_arrays=[]
    def scan(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in ('open','high','low','close','volume') and isinstance(v,list) and len(v)>20:return True
                if scan(v):return True
        elif isinstance(value,list):
            return any(scan(v) for v in value)
        return False
    for name in additions:
        text=(ROOT/name).read_text()
        if secret.search(text):secret_files.append(name)
        if name.endswith('.json') and name.startswith(('public/','research/')) and scan(json.loads(text)):
            price_arrays.append(name)
    if secret_files or price_arrays:
        raise ValueError('Possible secrets or new market arrays: '+str(secret_files+price_arrays))
    cmd=['vercel','deploy','--dry','--json','--project',PROJECT,'--scope',SCOPE]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    dry=json.loads(proc.stdout)
    files=dry['files']
    leaked=[f['path'] for f in files if forbidden(f['path'])]
    if leaked:raise ValueError('Private files in Vercel upload: '+str(leaked))
    result=dict(status='GIT_ADDITIONS_AND_VERCEL_UPLOAD_AUDITED',project=PROJECT,scope=SCOPE,
        integrity=integrity,new_git_files=len(additions),new_git_sha256={p:sha(ROOT/p) for p in additions},
        vercel_files=len(files),vercel_bytes=dry['totalSize'],private_uploads=0,detected_secrets=0,
        new_raw_price_arrays=0,files=files,executed_deployment=False,new_outcomes_computed=False)
    dump(ROOT/'artifacts/publication-20261023/source-upload-audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('new_git_sha256','files')},indent=2))
    return result


if __name__=='__main__':audit()
