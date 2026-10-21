import data from '../../../public/data/research-oos-year-readiness.json';

const n = (v: number) => v.toLocaleString('nl-NL');

export default function DataCollectionUpdate() {
  return <section id="data-collection" className="nq-section" aria-labelledby="collection-title">
    <p className="nq-eyebrow">VOORBEREIDING JAAR-HOLDOUT · 21 OKTOBER 2026 · NIET GESCOORD</p>
    <h2 id="collection-title">Jaarreeks geregistreerd. Vrijgave voor scoring staat uit.</h2>
    <p className="nq-lead">1 oktober 2025–30 september 2026. Alle {data.source_files} bronbestanden zijn privé op SHA-256 vastgelegd, naast {data.warmup_source_files} historische opwarmbestanden. Alleen datakwaliteit, vooraf beschikbare ATR-/volumehistorie en technische eligibility zijn berekend. Geen toekomstige VWAP-signalen, entries, trades of P&amp;L.</p>
    <div className="nq-grid">
      <article className="nq-card"><h3>{n(data.scheduled_sessions)} geplande sessies</h3><p>{n(data.active_unique_bars)} unieke actieve bars. Geen ontbrekende volledige sessies, conflicterende overlaps of onverwachte actieve minuten. Kerst en Nieuwjaar zijn gesloten civiele dagen, geen datagaten.</p></article>
      <article className="nq-card"><h3>{data.regular_full_clean_days} schone normale dagen</h3><p>{data.calendar_adjusted_clean_days} kalenderconform complete dagen inclusief vroege sluitingen. {data.quality_flagged_days} dagen met ontbrekende minuten. {data.documented_outage_minutes} minuten toegeschreven aan de gedocumenteerde storing, daarnaast {data.unresolved_missing_minutes} onverklaarde minuten. Niets geïmputeerd.</p></article>
      <article className="nq-card"><h3>{data.technical_eligible_days.B_ORB15} technisch eligible dagen</h3><p>Alle vier modellen delen dezelfde datums. Eligible betekent complete verplichte vensters en voldoende voorafgaande ATR-/volumehistorie, niet dat er een signaal of winst is. De primaire all-view kan een dag met een gat ná 12:00 wel toelaten.</p></article>
    </div>
    <h3>Technische eligibility per model</h3>
    <ul><li>ORB 15m · enige primaire hypothese: {data.technical_eligible_days.B_ORB15} dagen</li><li>ORB 5m · referentie: {data.technical_eligible_days.B_ORB5} dagen</li><li>London Sweep · referentie: {data.technical_eligible_days.A_London_sweep} dagen</li><li>VWAP Extreme · referentie: {data.technical_eligible_days.C_VWAP_extreme} dagen</li></ul>
    <h3>Volume-rollovers vóór signalen vastgelegd</h3>
    <ul>{data.rollovers.map(roll => <li key={roll.to}>{roll.from} naar {roll.to}: volumebesluit {roll.decision_session}, eerste actieve handelsdag {roll.effective_session}. Activering om 18:00 New York op de voorafgaande kalenderdag.</li>)}</ul>
    <p className="nq-note">Alle rolloverbesluiten blijven gelijk na verwijdering van latere data. Op het volumebesluit van 16 maart ontbreekt één minuut in het uitgaande contract. De bevroren grensvoorwaarden blijven ongewijzigd; dit zijn waargenomen leveranciersvolumes, geen gecertificeerde CME-totalen.</p>
    <p className="nq-warning">Stap 4 is geblokkeerd. De enige beschikbare signaalroute weigert datums na 30 september 2025. Het oude onderzoek is volledig gereproduceerd op historische data; de 73 bevroren bestanden blijven byte-identiek. De vaste jaarperiode, regels en $24,50 roundtripkosten zijn niet aangepast.</p>
    <details className="nq-details"><summary>Beperkingen en uitgesloten dagen</summary>
      <p>Kalenderuren zijn gereconstrueerd uit productspecifieke broker-/leveranciersschema’s, niet uit een ondertekend historisch CME-minuutcertificaat. De US-DST-overgangen op 2 november 2025 en 8 maart 2026 zijn getest. Leveranciersrechten en publicatievintages zijn niet onafhankelijk gecertificeerd. Ruwe marktdata en individuele transacties blijven privé.</p>
      <p>De lokale controle vond geen trade-ledger op de nieuwe periode. Onvolledige logs kunnen absoluut eerder niet-gebruik niet bewijzen. Dit blijft onderdeel van het expliciete vrijgavebesluit.</p>
      <p>Niet eligible voor alle modellen: {data.ineligible_dates.B_ORB15.join(', ')}. Good Friday sluit vóór 12:00 en voldoet niet aan het ongewijzigde ochtendvenster. Een storing wordt niet weggepoetst uit dat venster.</p>
    </details>
    <p><a href="/data/research-oos-year-readiness.md" download>Volledig kwaliteits- en vrijgaverapport</a>{' · '}<a href="/data/research-oos-year-readiness.json" download>Kwaliteit en eligibility (JSON)</a>{' · '}<a href="/data/research-oos-year-sources.json" download>Bronregister en hashes</a>{' · '}<a href="/data/research-oos-year-calendar.json" download>Productkalender</a>{' · '}<a href="/data/research-oos-year-preregistration.json" download>Preregistratie-pakket</a></p>
    <p className="nq-note">De oudere voorbereidingsblokken hieronder zijn historische momentopnamen; deze jaarcontrole vervangt hun toenmalige dekkingsstatus. Baseline v0.9 en vNext159 blijven ongewijzigd.</p>
  </section>;
}
