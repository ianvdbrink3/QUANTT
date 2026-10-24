"""Fetch only discovered public historical calendar pages and their attachments.

No authenticated endpoints, market prices, account data or browser automation.
Downloaded bytes are immutable and Gitignored. Classification requires review.
"""
import hashlib
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, quote, unquote
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/raw/historical-calendar-v2'
INDEX='https://www.ampfutures.com/news/topic/trading-info'
EXTRA=['https://www.cannontrading.com/tools/support-resistance-levels/good-friday-2019-holiday-schedule-cme-globex-ice-exchange/']


class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.images=[];self.anchor=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.anchor=[a['href'],'']
        if tag=='img' and a.get('src'):self.images.append(dict(src=a['src'],alt=a.get('alt','')))
    def handle_data(self,data):
        if self.anchor is not None:self.anchor[1]+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.anchor is not None:self.links.append(self.anchor);self.anchor=None


def fetch(url,kind):
    # No guessed URL grids, credentials, retries around security, or substitutions.
    if urlsplit(url).scheme!='https':raise ValueError('HTTPS sources only')
    url=quote(html.unescape(url),safe=':/%?=&+(),@')
    name=hashlib.sha256(url.encode()).hexdigest()[:16]
    suffix=Path(unquote(urlsplit(url).path)).suffix or '.html'
    path=OUT/(name+suffix)
    import subprocess
    if subprocess.run(['git','check-ignore','-q',str(path)],cwd=ROOT).returncode:
        raise ValueError('Source location must remain private')
    try:
        if path.exists():body=path.read_bytes();content_type='CACHED_ORIGINAL'
        else:
            with urlopen(url,timeout=12) as response:
                body=response.read(8_000_001);content_type=response.headers.get('Content-Type','')
            if len(body)>8_000_000:raise ValueError('Source exceeds 8MB bound')
            path.write_bytes(body)
        return dict(url=url,kind=kind,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(body).hexdigest(),
            bytes=len(body),content_type=content_type,status='FETCHED_NOT_YET_CLASSIFIED')
    except Exception as exc:
        return dict(url=url,kind=kind,status='FETCH_FAILED',error=type(exc).__name__+': '+str(exc)[:180])


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    index=fetch(INDEX,'DISCOVERY_INDEX');records=[index]
    if 'path' not in index:raise ValueError('Cannot read discovery index')
    parser=Links();parser.feed((ROOT/index['path']).read_text())
    pages=[]
    for url,title in parser.links:
        if not re.search(r'201[89]|202[01]',title):continue
        if not re.search(r'holiday|thanksgiving|christmas|new year|good friday|presidents|martin luther',title,re.I):continue
        if '2018' in title and not re.search(r'thanksgiving|christmas|new year',title,re.I):continue
        if '/news/' in url:pages.append(urljoin(INDEX,url))
    pages=list(dict.fromkeys(pages+EXTRA))
    with ThreadPoolExecutor(max_workers=4) as pool:
        page_records=list(pool.map(lambda u:fetch(u,'HISTORICAL_ROSTER_PAGE'),pages))
    records+=page_records
    attachments={}
    for r in page_records:
        if 'path' not in r:continue
        source=(ROOT/r['path']).read_text(errors='replace')
        parser=Links();parser.feed(source)
        r['title']=html.unescape((re.search(r'<title[^>]*>(.*?)</title>',source,re.S) or [None,''])[1]).strip()
        for image in parser.images:
            url=urljoin(r['url'],image['src']);description=unquote(url)+' '+image['alt']
            if '<' in url or '>' in url or not re.search(r'\.(png|jpe?g|webp|gif)(\?|$)',url,re.I):continue
            if not re.search(r'201[89]|202[01]',description):continue
            if not re.search(r'holiday|thanksgiving|christmas|good.?friday|schedule',description,re.I):continue
            # Preserve the exact exposed URL; do not invent an original by rewriting it.
            # Some tables are only exposed as publisher-resized images.
            if '/Related-Post/' in url:continue
            if '/hs-fs/' in url and any(unquote(urlsplit(i['src']).path).split('/hubfs/')[-1]==
                    unquote(urlsplit(url).path).split('/hubfs/')[-1] and '/hs-fs/' not in i['src'] for i in parser.images):continue
            item=attachments.setdefault(url,dict(parents=[],alt=image['alt']))
            item['parents'].append(r['url'])
        for url,text in parser.links:
            url=urljoin(r['url'],url)
            if re.search(r'\.(xls|xlsx|pdf)(\?|$)',url,re.I) and re.search(r'holiday|schedule',unquote(url),re.I):
                attachments.setdefault(url,dict(parents=[],alt=text))['parents'].append(r['url'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        attached=list(pool.map(lambda u:fetch(u,'UNREVIEWED_PRESERVED_DOCUMENT'),attachments))
    for requested,r in zip(attachments,attached):r.update(attachments[requested])
    records+=attached
    manifest=dict(date='2026-10-23',sources=records,source_pages=len(page_records),attachments=len(attached),
        automatic_evidence_approval=False,authenticated_requests=False,signals_computed=False)
    # This is a download manifest, not an authored scientific dataset or source edit.
    (OUT/'download-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(pages=len(page_records),attachments=len(attached),
        failed=[r for r in records if r['status']=='FETCH_FAILED'],
        image_files=[dict(path=r['path'],alt=r['alt'],parents=r['parents']) for r in attached if 'path' in r]),indent=2))


if __name__=='__main__':main()
