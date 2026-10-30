import argparse
import json
import signal
import threading
from .common import ROOT,config,atomic


def main():
    parser=argparse.ArgumentParser(description='QUANT lokale adviesagent; echte orders zijn onmogelijk.')
    parser.add_argument('command',choices=['once','watch','status','publish-readiness','setup-demo-secrets','service-render','service-install','service-stop'])
    parser.add_argument('--config',default=str(ROOT/'config/portfolio-forward.json'));parser.add_argument('--refresh',action='store_true')
    a=parser.parse_args()
    try:
        if a.command=='watch':
            from .agent import watch
            stop=threading.Event()
            for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,lambda *_:stop.set())
            watch(a.config,stop);return
        if a.command=='once':
            from .agent import tick
            result=tick(a.config,a.refresh)
        elif a.command=='status':
            from .agent import status
            result=status(a.config)
        elif a.command=='publish-readiness':
            from .agent import public_readiness
            result=public_readiness(a.config);atomic(ROOT/'public/data/portfolio-os/agent-readiness.json',result)
        elif a.command=='setup-demo-secrets':
            from .secrets import setup
            result=setup(ROOT/config(a.config)['root'])
        else:
            from .service import render,install,uninstall
            result={'path':str(render(a.config))} if a.command=='service-render' else install(a.config) if a.command=='service-install' else uninstall()
        print(json.dumps(result,indent=2,default=str,allow_nan=False))
    except Exception as e:
        # No requests exception, URL, request header or API secret in CLI output.
        reason=str(e) if isinstance(e,ValueError) and str(e).isupper() and len(str(e))<90 else 'LOCAL_AGENT_COMMAND_FAILED'
        print(json.dumps(dict(status='BLOCKED',reason=reason,live_locked=True)))
        raise SystemExit(1) from None


if __name__=='__main__':main()
