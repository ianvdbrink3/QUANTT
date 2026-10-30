/** Plain-language presentation only. Frozen signals and accounting remain elsewhere. */
/** @param {number} code */
export function marketCopy(code) {
  if (code === 2)
    return {
      tone: "green",
      title: "Opwaartse trend",
      headline: "De groeitrend is intact.",
      description:
        "De Nasdaq staat boven de 20- en 200-daagse gemiddelden en de beweeglijkheid blijft onder de hoge-volatiliteitsgrens.",
    };
  if (code === 1)
    return {
      tone: "amber",
      title: "Dip binnen de lange trend",
      headline: "Rustig afwachten: de korte trend hapert.",
      description:
        "De koers staat boven de lange veiligheidslijn. De korte trend of de beweeglijkheid geeft wel reden voor voorzichtigheid.",
    };
  if (code === 0)
    return {
      tone: "red",
      title: "Noodrem van het model actief",
      headline: "De lange trend is gebroken.",
      description:
        "De koers staat op of onder de 200-daagse lijn. Het model kiest voor cash; een signaal is nog geen uitgevoerde verkoop.",
    };
  return {
    tone: "red",
    title: "Gegevenscontrole nodig",
    headline: "Nog geen betrouwbaar oordeel.",
    description:
      "Niet alle benodigde gegevens zijn beschikbaar. Nieuwe orders blijven geblokkeerd.",
  };
}
/** @param {string} value */
export function dutchDate(value) {
  return new Intl.DateTimeFormat("nl-NL", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T12:00:00Z`));
}
/** @param {number} start @param {number} monthly @param {number} years @param {number} annual */
export function growthPoints(start, monthly, years, annual) {
  const rate = Math.pow(1 + annual, 1 / 12) - 1;
  return Array.from({ length: years * 12 + 1 }, (_, month) => ({
    month,
    contributions: start + monthly * month,
    value:
      start * Math.pow(1 + rate, month) +
      (rate === 0
        ? monthly * month
        : (monthly * (Math.pow(1 + rate, month) - 1)) / rate),
  }));
}
/** @param {import('./portfolio-chart-types').ChartRow[]} rows @param {string} period @param {string} asof */
export function chartPeriod(rows, period, asof) {
  const available = rows.filter((r) => r.day <= asof);
  if (period === "2022")
    return available.filter(
      (r) => r.day >= "2022-01-01" && r.day <= "2022-12-31",
    );
  if (period === "all") return available;
  const end = new Date(`${asof}T12:00:00Z`);
  end.setUTCMonth(end.getUTCMonth() - (period === "year" ? 12 : 3));
  return available.filter((r) => r.day >= end.toISOString().slice(0, 10));
}
/** @param {import('./portfolio-os-types').OSState} state @param {string} asset */
export function executedMarkers(state, asset) {
  const fills =
    /** @type {Array<{intent_id:string;price:string;id:string}>} */ (
      /** @type {unknown} */ (state.audit.fills ?? [])
    );
  return fills.flatMap((fill) => {
    const intent = state.audit.intents.find(
      (i) => i.id === fill.intent_id && i.key === asset,
    );
    return intent
      ? [
          {
            day: intent.day,
            price: Number(fill.price),
            side: intent.side,
            label: `${intent.side === "BUY" ? "Koop" : "Verkoop"} in simulatie · ${state.replay.execution_timing === "NEXT_DAILY_OPEN" ? "09:30" : "09:31"} NY`,
            id: fill.id,
          },
        ]
      : [];
  });
}
