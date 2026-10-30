/** Read-only presentation calculations. No broker, account or local filesystem access. */
/** @param {number} amount @param {number} spread @param {number} slip */
export function publicCostRoutes(amount, spread, slip = 1) {
  if (
    ![amount, spread, slip].every(Number.isFinite) ||
    amount < 1 ||
    amount > 1e6 ||
    spread < 0 ||
    spread > 100 ||
    slip < 0 ||
    slip > 100
  )
    throw new Error("INVALID_COST_INPUT");
  const plans = [
    {
      key: "trading212",
      label: "Trading 212 · EUR-UCITS",
      minimum: 0,
      fraction: 0,
      fixed: 0,
      note: "EUR-notering, fracties en productrecht niet account-specifiek bevestigd.",
    },
    {
      key: "ibkr",
      label: "IBKR · Tiered NL",
      minimum: 1.25,
      fraction: 0.0005,
      fixed: 0,
      note: "Eerste volumetier; externe venuefees niet inbegrepen.",
    },
    {
      key: "degiro",
      label: "DEGIRO · Kernselectie",
      minimum: 0,
      fraction: 0,
      fixed: 1,
      note: "Alleen toepasselijke Kernselectie-notering, zonder FX/extra fees.",
    },
    {
      key: "alpaca",
      label: "Alpaca · Paper",
      minimum: 0,
      fraction: 0,
      fixed: 0,
      note: "Uitsluitend nulcommissie-ondergrens; echte FX/reguleringskosten en toegang onbekend.",
    },
  ];
  return plans.map((p) => {
    const value =
      (20000 * (Math.max(p.minimum, amount * p.fraction) + p.fixed)) / amount +
      spread +
      slip;
    const gates = Object.fromEntries(
      [5, 10].map((gate) => {
        const residual = gate - spread - slip,
          proportional = 20000 * p.fraction;
        let needed = null;
        if (residual >= proportional && residual >= 0) {
          if (residual === 0)
            needed = p.minimum === 0 && p.fixed === 0 ? 1 : null;
          else if (!(residual === proportional && p.fixed > 0)) {
            const a = (20000 * (p.minimum + p.fixed)) / residual;
            const b =
              residual > proportional
                ? (20000 * p.fixed) / (residual - proportional)
                : 0;
            needed = Math.ceil((Math.max(1, a, b) - 1e-9) * 100) / 100;
          }
        }
        const extra = needed === null ? null : Math.max(0, needed - amount);
        return [
          String(gate),
          {
            minimum_eur: p.key === "alpaca" ? null : needed,
            extra_eur: p.key === "alpaca" ? null : extra,
            months:
              p.key === "alpaca" || extra === null
                ? null
                : Math.ceil(extra / 100),
            progress_pct:
              p.key === "alpaca" || needed === null
                ? 0
                : Math.min(100, (amount / needed) * 100),
            mathematical_pass: value <= gate,
            execution_approved: false,
          },
        ];
      }),
    );
    return {
      key: p.key,
      label: p.label,
      roundtrip_bp: p.key === "alpaca" ? null : value,
      lower_bound_bp: value,
      amount_eur: amount,
      spread_bp: spread,
      slippage_bp: slip,
      note: p.note,
      gates,
    };
  });
}

/** @param {Date} now */
export function terminalClockContext(now) {
  /** @param {string} zone */
  const offset = (zone) => {
    const values = Object.fromEntries(
      new Intl.DateTimeFormat("en-GB", {
        timeZone: zone,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hourCycle: "h23",
      })
        .formatToParts(now)
        .map((p) => [p.type, p.value]),
    );
    return (
      (Date.UTC(
        +values.year,
        +values.month - 1,
        +values.day,
        +values.hour,
        +values.minute,
        +values.second,
      ) -
        Math.floor(now.getTime() / 1000) * 1000) /
      3600000
    );
  };
  const ny = offset("America/New_York"),
    nl = offset("Europe/Amsterdam");
  return {
    ny_label: ny === -4 ? "EDT" : "EST",
    nl_label: nl === 2 ? "CEST" : "CET",
    offset_hours: nl - ny,
  };
}
