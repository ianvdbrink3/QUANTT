"""Verify complete fixed-plan receipt without parsing numerical market data."""
import json
import subprocess
from collections import defaultdict
from scripts.intake_historical_first_six import ROOT,DOWNLOADS,sha


def run():
    sources=['research/afternoon-historical-intake-batch01.json',
             'research/afternoon-historical-intake-batch02-final.json',
             'research/afternoon-historical-intake-batch03.json']
    records=[r for name in sources for r in json.loads((ROOT/name).read_text())['files']]
    plan_path=ROOT/'research/afternoon-historical-download-plan.json'
    plan=json.loads(plan_path.read_text())['rows'];by_sequence=defaultdict(list)
    for record in records:
        by_sequence[record['sequence']].append(record)
        if sha(DOWNLOADS/record['filename'])!=record['sha256']:raise ValueError('Source hash mismatch')
        if sha(ROOT/record['private_copy'])!=record['sha256']:raise ValueError('Private hash mismatch')
        if subprocess.run(['git','check-ignore','-q',record['private_copy']],cwd=ROOT).returncode:
            raise ValueError('Raw file not Gitignored')
        request=next(r for r in plan if r['sequence']==record['sequence'])
        if record['contract']!=request['contract']:raise ValueError('Contract mismatch')
        if record['numeric_ohlcv_parsed']:raise ValueError('Outcome intake boundary violated')
        if record['metadata_issue_counts']:raise ValueError('Metadata warning requires review')
    expected={r['sequence'] for r in plan}
    if set(by_sequence)!=expected or len(expected)!=103:raise ValueError('Fixed plan incomplete')
    groups=defaultdict(list)
    for request in plan:groups[request['contract']].append(request['sequence'])
    register=dict(status='ALL_103_FIXED_PLAN_BLOCKS_RECEIVED_METADATA_VERIFIED_NOT_DATASET_VALIDATED',
        date='2026-10-23',plan_sha256=sha(plan_path),received_unique_blocks=len(by_sequence),
        physical_files=len(records),duplicate_download_aliases=len(records)-len(by_sequence),pending=0,
        contract_count=len(groups),contract_blocks=dict(groups),
        source_bars_including_contract_overlaps_and_duplicate_downloads=sum(r['parsed_bars'] for r in records),
        metadata_flagged_files=0,all_download_hashes_verified=True,all_private_hashes_verified=True,
        all_private_files_gitignored=True,numeric_OHLCV_read=False,signals_computed=False,holdout_executed=False,
        paid=False,subscription_changed=False,external_publication=False,
        receipt_register_sha256={name:sha(ROOT/name) for name in sources},files=records)
    output=ROOT/'research/historical-2019-2021-complete-source-register.json'
    output.write_text(json.dumps(register,indent=2,allow_nan=False)+'\n')
    lines=['# Historische contractreeks: ontvangst compleet','',
        '23 oktober2026. **Alle103vaste planblokken zijn ontvangen. Er ontbreken geen downloads meer.**',
        '',f"Er staan {len(records)} fysieke CSV-bestanden in de ontvangstregisters:103unieke planblokken en{len(records)-103}reeds bekende dubbele downloads. Die dubbele bestanden blijven bewaard, maar tellen niet opnieuw mee. Tijdens de hervatte ronde zijn de72destijds resterende blokken ontvangen.",'',
        '| Contract | Unieke planblokken |','|---|---:|']
    for contract,blocks in groups.items():lines.append(f'| {contract} | {len(blocks)} |')
    lines+=['','## Gecontroleerd','',
        '- SHA-256 van alle oorspronkelijke Downloads-bestanden vergeleken met hun geregistreerde hashes.',
        '- Alle privé-kopieën byte-identiek en perbestand op Gitignore gecontroleerd.',
        '- Alle103bloknummers uit de oorspronkelijke downloadlijst aanwezig. Contract, bronbereik, schema, footer, volgorde, dubbele labels en de20.000-recordgrens metadata-only gecontroleerd. Geen metadatawaarschuwingen.',
        f"- {register['source_bars_including_contract_overlaps_and_duplicate_downloads']:,} bronbars inclusief contractoverlap en dubbele downloads. Dit is nadrukkelijk niet het aantal unieke minuten van één actieve reeks.",
        '- Geen aankoop, account, abonnementswijziging, Git-push of Vercel-uitrol.',
        '', '## Nog niet vastgesteld','',
        'Een complete ontvangst is geen volledige datakwaliteits- of importgoedkeuring. Numerieke prijzen/volumes, alle RTH-minuten, CMEfeestdagen/haltes, definitieve volume-rollovers, causaliteit van opwarming en licentiegeschiktheid moeten nog afzonderlijk worden beoordeeld. Nieuwe2019–2021-prijzen zijn tijdens deze intake niet numeriek geanalyseerd. Geen signalen, rendementen of onafhankelijke backtest berekend.',
        '', '## Lokale opslag en reproduceerbaarheid','',
        'Originelen blijven in Downloads. De privé-kopieën staan in data/raw/historical-replication-2019-2021/. Het volledige bronregister met hashes staat in research/historical-2019-2021-complete-source-register.json. De eerdere batchregisters en oorspronkelijke downloadlijst blijven behouden.',
        '', 'De spreadsheetvaardigheid is alleen gebruikt voor herleidbare bronregistratie en structuurcontrole; geen bron-CSV herschreven, prijzen aangevuld of onderzoeksuitkomsten berekend.', '']
    (ROOT/'docs/NQ_HISTORICAL_COMPLETE_RECEIPT_2026-10-23.md').write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in register.items() if k not in ('files','contract_blocks','receipt_register_sha256')},indent=2))
    return register


if __name__=='__main__':run()
