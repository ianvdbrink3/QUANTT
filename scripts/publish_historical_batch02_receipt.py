"""Publish aggregate receipt, not prices, new outcomes or private paths."""
import json
from collections import defaultdict
from scripts.survivor_portfolio import ROOT,dump,verify
from scripts.oos_preparation.adapter import sha


def run():
    path=ROOT/'research/afternoon-historical-intake-batch02-final.json'
    receipt=json.loads(path.read_text());groups=defaultdict(list)
    for r in receipt['files']:groups[r['contract']].append(r)
    public=dict(status='DOWNLOADS_PARTIAL_BROWSER_WINDOW_UNAVAILABLE_NOT_DAILY_LIMIT',
        new_unique_blocks=receipt['new_unique_blocks'],new_physical_files=receipt['new_physical_files'],
        duplicate_download_aliases=receipt['duplicate_download_aliases'],total_received=receipt['total_plan_blocks_received'],
        total_plan_blocks=103,remaining=receipt['pending_plan_blocks'],metadata_flagged_files=receipt['metadata_flagged_files'],
        numeric_OHLCV_read=False,new_outcomes=False,paid=False,external_publication=False,
        last_observed_quota=dict(used=36,limit=250,final_verified=False),
        next_requests=[dict(contract=r['contract'],sequence=r['sequence'],start=r['start_mmddyyyy'],end=r['end_mmddyyyy']) for r in receipt['remaining'][:3]])
    dump(ROOT/'public/data/three-survivors-intake.json',public)
    lines=['# Historische intake batch02 — gedeeltelijk ontvangen','',
        f"22oktober2026: {receipt['new_unique_blocks']} nieuwe unieke planblokken ontvangen; met de eerdere6 staat de teller op {receipt['total_plan_blocks_received']}/103. Nog{receipt['pending_plan_blocks']}blokken ontbreken. {receipt['new_physical_files']}nieuwe fysieke bestanden, waaronder{receipt['duplicate_download_aliases']}expliciet geregistreerde dubbele downloads. Niets verwijderd of stilzwijgend dubbel meegeteld.",'',
        '## Onderbreking','',
        'Safari wisselde eerst van tab/venster tijdens bediening. De gebruiker gaf daarna aan Safari vrij te laten. Latere bedieningspogingen eindigden met een wijzigingsmelding en geen beschikbaar native venster. Browserinventaris: Safari draait nog, maar geen bedienbaar venster. Daarom geen verdere klikken of downloadclaims. Laatst daadwerkelijk zichtbare teller36van250; dit is niet de gecontroleerde eindstand en geen bereikte daglimiet. Geen aankoop, account, verlenging, abonnement, CAPTCHA-oplossing of veiligheidsomzeiling.','',
        '## Ontvangen unieke blokken','',
        '| Contract | Unieke planblokken | Fysieke bestanden | Minuutbars incl. dubbele downloads |','|---|---|---:|---:|']
    for contract,rows in sorted(groups.items()):
        lines.append(f"| {contract} | {', '.join(map(str,sorted({r['sequence'] for r in rows})))} | {len(rows)} | {sum(r['parsed_bars'] for r in rows)} |")
    lines+=['','## Eerstvolgende ontbrekende blokken','', '| # | Contract | Start MM/DD/YYYY | Einde MM/DD/YYYY |','|---:|---|---|---|']
    for r in receipt['remaining'][:8]:lines.append(f"| {r['sequence']} | {r['contract']} | {r['start_mmddyyyy']} | {r['end_mmddyyyy']} |")
    lines+=['','## SHA-256 en privacy','',
        'Elk origineel blijft in Downloads. Byte-identieke kopieën zijn perbestand op Gitignore gecontroleerd en staan privé onder data/raw/historical-replication-2019-2021. Volledige metadata en hashes: research/afternoon-historical-intake-batch02-final.json. Twee herhaalde blokken blijven als aliases geregistreerd; hun afzonderlijke bytes en footers zijn behouden. De eerste zes, de oude downloadlijst en vensterregistratie blijven byte-identiek.','',
        f"Er zijn {receipt['metadata_flagged_files']} bestanden met metadatawaarschuwingen. Dit is GEEN certificaat van hoge datakwaliteit: numerieke OHLCV, alle RTH-minuten, officiële CMEkalender/halts, volume-rollovers en licentiegeschiktheid zijn nog niet beoordeeld. Geen nieuwe prijzen numeriek gelezen, cohort of signaal gemaakt, rendement berekend of holdout vrijgegeven. Dit onderscheid volgt uit de spreadsheetvaardigheid: structuurcontrole is geen financieel resultaatonderzoek.",'',
        f"Register-SHA256: {sha(path)}",'']
    text='\n'.join(lines)
    for out in (ROOT/'docs/NQ_HISTORICAL_INTAKE_BATCH02.md',ROOT/'public/reports/NQ_HISTORICAL_INTAKE_BATCH02.md'):out.write_text(text)
    verify();print(json.dumps(public,indent=2))


if __name__=='__main__':run()
