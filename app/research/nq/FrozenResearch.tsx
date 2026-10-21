import freeze from '../../../public/data/research-freeze.json';
import preparation from '../../../public/data/research-oos-preparation.json';

export default function FrozenResearch() {
  return <section id="frozen-vnext" className="nq-section" aria-labelledby="frozen-title">
    <p className="nq-eyebrow">ONDERZOEKSSTAND BEVROREN · 21 OKTOBER 2026</p>
    <h2 id="frozen-title">vNext · {freeze.eligible_days} gedeelde dagen</h2>
    <p className="nq-note">Doorlopende point-in-time ATR- en volumehistorie, de post-entry pad-analyse en stabiliteitsaudit liggen vast naast Baseline v0.9. {freeze.historical_tests} bestaande tests behouden, {freeze.release_tests} tests inclusief vier nieuwe integriteitscontroles. {freeze.integrity_files} bestanden worden op SHA-256 bewaakt. Geen gevalideerde edge.</p>
    <p className="nq-warning">December 2024–september 2025 wordt niet verder aangepast. De volgende test staat nog uit: 1 oktober 2025–30 september 2026, alleen na controle van volledigheid en eerder strategiegebruik. ORB15 is de enige primaire hypothese; referenties blijven beschrijvend.</p>
    <details className="nq-details"><summary>Vaste regels en beoordelingscriteria</summary>
      <p>Alleen bekende roll-spreads voor multi-dag indicatoren; uitvoering op onverschoven actieve contractprijzen. Volumereferentie: mediaan van maximaal 20 eerdere observaties van dezelfde NY-minuut, minimum 10. Geen nieuwe filters of exits. $24,50 kosten per roundtrip.</p>
      <p>Op de volledige onafhankelijke testperiode: minstens 20 eligible dagen, netto &gt; 0, profit factor &gt; 1, tweezijdige block-bootstrap p &lt; 0,05 én ondergrens 95%-interval van het daggemiddelde &gt; 0. Dezelfde numerieke criteria als eerder; 20 is geen garantie van voldoende statistische power. Geen tussentijdse resultaatselectie.</p>
      <p>Ten tijde van deze freeze-release was de toekomstige datum-/contractadapter nog niet gebouwd. De actuele voorbereidingsstatus staat hierboven. De bestaande historische reproductie blijft intact. De download bevat alle exacte grenzen en beslisregels.</p>
    </details>
    <h3>Historische inventarisatie bij de freeze · inmiddels aangevuld</h3>
    <p className="nq-note">{freeze.inventory.files_scanned} NQ-CSV’s bekeken op timestamps en hashes, zonder nieuwe backtest. In Downloads staan NQZ25-exports tot 12 december 2025. Individuele H26/M26/U26 en Z26-overlap ontbreken. Andere continue reeksen zijn geen gevalideerde vervanging. De oktober-2026-sample valt buiten het vaste testvenster.</p>
    <a href="/data/research-freeze.json" download>Download bevroren protocol en bestandsinventaris</a>{' · '}
    <a href="/data/research-freeze.md" download>Lees de bevroren onderzoeksstand</a>{' · '}
    <a href="/data/research-data-inventory.md" download>Lees wat aanwezig is en nog ontbreekt</a>
    <div id="oos-preparation">
      <h3>Eerste voorbereidingsmomentopname · zie actuele jaarcontrole hierboven</h3>
      <p className="nq-warning">Status: {preparation.status}. Zes bronblokken privé vastgelegd, {preparation.standard_clean_days} schone normale dagen en {preparation.complete_noon_prefix_days} complete ochtend-prefixen. Geen strategie-uitkomsten geopend. H26/M26/U26/Z26, december-rollbewijs en volledige productkalender ontbreken nog; de voorbereiding geeft geen toestemming voor scoring.</p>
      <p className="nq-note">De aparte data-adapter reproduceert alle 30 historische bronbestanden en de juni-/septemberroll zonder strategieën uit te voeren. Onbekende kalenderdatums en conflicterende overlap worden geweigerd. Eerdere kwaliteitsinspectie is geregistreerd; volledige niet-gebruikgarantie is niet bewezen.</p>
      <details className="nq-details"><summary>Powerplanning · alleen oude onderzoeksdata</summary>
        <p>Planning met de reeds verbruikte 159 dagen, niet met toekomstige resultaten. Bij een hypothetische echte netto edge van 10 punten per eligible dag is de normale benadering circa 12% power bij 52 dagen en 38% bij 240 dagen. Voor 20 punten is dit circa 34% en 91%. Dit is geen exacte power van het bevroren gezamenlijke bootstrap-/CI-/PF-criterium en geen reden om de vaste jaarhorizon of regels te wijzigen.</p>
        <p>In deze voorbereiding zijn geen nieuwe signalen of rendementen berekend. Kalenderuitzonderingen en opwarmhistorie worden niet versoepeld om meer trades te krijgen. De bron heeft geen tick-aantallen.</p>
      </details>
      <a href="/data/research-oos-preparation.json" download>Download voorbereiding en poweraannames</a>{' · '}
      <a href="/data/research-oos-preparation.md" download>Lees uitvoering, beperkingen en downloadplan</a>
    </div>
  </section>;
}
