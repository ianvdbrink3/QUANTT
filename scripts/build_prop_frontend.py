"""Clean committed frontend release, including the new research hub redirect."""
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path
from scripts.build_operational_frontend import allowed as baseline_allowed

ROOT=Path(__file__).resolve().parents[1]


def allowed(name):
    return name=='proxy.ts' or baseline_allowed(name)


def build():
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    files=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT).decode().splitlines()
    files=[n for n in files if allowed(n)]
    required={'app/research/prop-firm/page.tsx','public/data/prop-firm.json','public/reports/PROP_FIRM_AND_AUTOMATION_GUIDE.md','proxy.ts'}
    if not required<=set(files):raise ValueError('Prop release has not been committed')
    stage=Path(tempfile.mkdtemp(prefix='quantt-prop-',dir='/private/tmp'))
    archive=subprocess.check_output(['git','archive','--format=tar','HEAD','--',*files],cwd=ROOT)
    hashes={}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            if member.isdir():continue
            if not member.isfile() or not allowed(member.name):raise ValueError('Unsafe release member '+member.name)
            payload=tar.extractfile(member).read();target=stage/member.name
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
            hashes[member.name]=hashlib.sha256(payload).hexdigest()
    if set(hashes)!=set(files):raise ValueError('Incomplete extraction')
    receipt=dict(status='COMMITTED_FRONTEND_ONLY',commit=commit,stage=str(stage),files_sha256=hashes,private_data_included=False,
                 source_tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT).decode().strip())
    out=ROOT/'artifacts/prop-publication';out.mkdir(parents=True,exist_ok=True)
    (out/'stage-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return dict(stage=str(stage),commit=commit,frontend_files=len(hashes),private_data_included=False)


if __name__=='__main__':print(json.dumps(build(),indent=2))
