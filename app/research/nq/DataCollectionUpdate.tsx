import data from '../../../public/data/research-december-overlap.json';

const n = (v: number) => v.toLocaleString('nl-NL');

export default function DataCollectionUpdate() {
  return <section id="data-collection" className="nq-section" aria-labelledby="collection-title">
    <p className="nq-eyebrow">21 OKTOBER 2026 · ALLEEN DATA EN VOLUME · HOLDOUT NIET GESCOORD</p>
    <h2 id="collection-title">December-overlap gecontroleerd. Bulkroute voorbereid.</h2>
    <p className="nq-lead">Vier nieuwe Barchart-bestanden zijn lokaal geregistreerd. De bestaande volumeregel schakelt van NQZ25 naar NQH26 vanaf handelsdag 16 december 2025. Er zijn geen toekomstige signalen, features of handelsresultaten berekend.</p>
    <div className="nq-grid">
      <article className="nq-card"><h3>15 volledige actieve sessies</h3><p>{n(data.active_unique_bars)} unieke bars over 1–19 december. {data.active_missing_minutes} ontbrekende actieve minuten en {data.conflicting_overlaps} conflicterende overlaps. Dit is datadekking, geen berekend aantal strategie-eligible dagen.</p></article>
      <article className="nq-card"><h3>Volume-switch vóór activering</h3><p>Crossover op 15 december, activering op 15 december 18:00 New York. Alleen vooraf beschikbare gezamenlijke close voor de spread. Geen aanpassing van Baseline v0.9 of vNext159.</p></article>
      <article className="nq-card"><h3>Bulkraming: $9,51 voor vijf jaar NQ</h3><p>De openbare Databento-calculator toont NQ OHLCV-1m, 30 september 2021–30 september 2026, circa 145,9 MB en geen abonnement. Dit is een raming zonder aangenomen tegoed. Exacte aanvraagprijs, dekking en rechten nog bevestigen. Niets gekocht.</p></article>
    </div>
    <p className="nq-warning">De volledige toekomstige jaarperiode blijft onvolledig en niet gescoord. Kalenderuren na 19 december, bronrechten en de overige 2026-contracten moeten nog worden gecontroleerd. Een eventuele leverancierswissel vereist eerst een vergelijking op reeds verbruikte 2025-data.</p>
    <p className="nq-note">Eén verkeerd gedateerde, afgekapt gedownloade NQH26-export is uitgesloten en niet gestaged. Het eerdere voorbereidingsblok hieronder blijft als historische momentopname behouden; de toen geblokkeerde browsersessie is inmiddels hersteld.</p>
    <p><a href="/data/research-data-route.md" download>Uitgebreid besluit en bulkplan (Markdown)</a>{' · '}<a href="/data/research-december-overlap.json" download>Geaggregeerde audit en bronhashes (JSON)</a></p>
  </section>;
}
