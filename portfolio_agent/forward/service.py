"""Mac launchd service. Only default advice mode can be installed automatically."""
from pathlib import Path
import os
import plistlib
import subprocess
import sys
from .common import ROOT,config

LABEL='com.quantt.portfolio-advice'


def render(path=None):
    c=config(path)
    if c['mode']!='ADVICE_ONLY' or c['demo_orders_enabled']:raise ValueError('ONLY_ADVICE_SERVICE_CAN_BE_INSTALLED')
    root=ROOT/c['root'];root.mkdir(parents=True,exist_ok=True,mode=0o700)
    body=dict(Label=LABEL,ProgramArguments=[str(ROOT/'.venv/bin/python'),'-m','portfolio_agent.forward','watch','--config',str(Path(path or ROOT/'config/portfolio-forward.json').resolve())],
        WorkingDirectory=str(ROOT),RunAtLoad=True,KeepAlive=True,ThrottleInterval=60,ProcessType='Background',
        EnvironmentVariables={'PYTHONUNBUFFERED':'1','PATH':'/usr/bin:/bin:/usr/sbin:/sbin'},
        StandardOutPath=str(root/'service.out.log'),StandardErrorPath=str(root/'service.error.log'))
    output=root/(LABEL+'.plist');output.write_bytes(plistlib.dumps(body));os.chmod(output,0o600)
    return output


def install(path=None):
    if sys.platform!='darwin':raise ValueError('MAC_ONLY_SERVICE')
    src=render(path);target=Path.home()/'Library/LaunchAgents'/src.name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=src.read_bytes():raise ValueError('EXISTING_SERVICE_CONFIG_DIFFERS')
    target.write_bytes(src.read_bytes());os.chmod(target,0o600)
    domain='gui/'+str(os.getuid())
    exists=subprocess.run(['launchctl','print',domain+'/'+LABEL],capture_output=True).returncode==0
    if not exists:subprocess.run(['launchctl','bootstrap',domain,str(target)],check=True,capture_output=True)
    subprocess.run(['launchctl','kickstart',domain+'/'+LABEL],check=True,capture_output=True)
    return dict(status='ADVICE_SERVICE_REGISTERED',label=LABEL,orders_enabled=False,mac_must_be_awake=True)


def uninstall():
    if sys.platform!='darwin':raise ValueError('MAC_ONLY_SERVICE')
    target=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist')
    subprocess.run(['launchctl','bootout','gui/'+str(os.getuid())+'/'+LABEL],capture_output=True)
    # Preserve the plist as a reversible disabled file; never remove user evidence.
    if target.exists():target.rename(target.with_suffix('.plist.disabled'))
    return dict(status='ADVICE_SERVICE_STOPPED')
