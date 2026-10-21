import freeze from '../../../public/data/research-freeze.json';

export default function FrozenResearch() {
  return <section id="frozen-vnext" className="nq-section" aria-labelledby="frozen-title">
    <p className="nq-eyebrow">ONDERZOEKSSTAND BEVROREN · 21 OKTOBER 2026</p>
    <h2 id="frozen-title">vNext · {freeze.eligible_days} gedeelde dagen</h2>
    <p className="nq-note">Doorlopende point-in-time ATR- en volumehistorie, de post-entry pad-analyse en stabiliteitsaudit liggen vast naast Baseline v0.9. {freeze.historical_tests} bestaande tests behouden, {freeze.release_tests} tests inclusief vier nieuwe integriteitscontroles. {freeze.integrity_files} bestanden worden op SHA-256 bewaakt. Geen gevalideerde edge.</p>
    <p className="nq-warning">December 2024–september 2025 wordt niet verder aangepast. De volgende test staat nog uit: 1 oktober 2025–30 september 2026, alleen na controle van volledigheid en eerder strategiegebruik. ORB15 is de enige primaire hypothese; referenties blijven beschrijvend.</p>
    <details className="nq-details"><summary>Vaste regels en beoordelingscriteria</summary>
      <p>Alleen bekende roll-spreads voor multi-dag indicatoren; uitvoering op onverschoven actieve contractprijzen. Volumereferentie: mediaan van maximaal 20 eerdere observaties van dezelfde NY-minuut, minimum 10. Geen nieuwe filters of exits. $24,50 kosten per roundtrip.</p>
      <p>Op de volledige onafhankelijke testperiode: minstens 20 eligible dagen, netto &gt; 0, profit factor &gt; 1, tweezijdige block-bootstrap p &lt; 0,05 én ondergrens 95%-interval van het daggemiddelde &gt; 0. Dezelfde numerieke criteria als eerder; 20 is geen garantie van voldoende statistische power. Geen tussentijdse resultaatselectie.</p>
      <p>De toekomstige datum-/contractadapter is nog niet uitgevoerd of gebouwd in deze freeze-release. De bestaande historische reproductie blijft intact. De download bevat alle exacte grenzen en beslisregels.</p>
    </details>
    <h3>Aanwezige vervolgdata · alleen geïnventariseerd</h3>
    <p className="nq-note">{freeze.inventory.files_scanned} NQ-CSV’s bekeken op timestamps en hashes, zonder nieuwe backtest. In Downloads staan NQZ25-exports tot 12 december 2025. Individuele H26/M26/U26 en Z26-overlap ontbreken. Andere continue reeksen zijn geen gevalideerde vervanging. De oktober-2026-sample valt buiten het vaste testvenster.</p>
    <a href="/data/research-freeze.json" download>Download bevroren protocol en bestandsinventaris</a>{' · '}
    <a href="/data/research-freeze.md" download>Lees de bevroren onderzoeksstand</a>{' · '}
    <a href="/data/research-data-inventory.md" download>Lees wat aanwezig is en nog ontbreekt</a>
  </section>;
}
