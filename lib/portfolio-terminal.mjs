/** @typedef {import('./portfolio-os-types').OSState} OSState */
/** @param {number|string|null|undefined} value @param {number} digits */
export function terminalNumber(value, digits = 2) {
  if (value == null || !Number.isFinite(Number(value))) return "—";
  return new Intl.NumberFormat("nl-NL", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value));
}
/** @param {import('./portfolio-os-types').Day[]} days @param {string} query @param {string} filter */
export function terminalDays(days, query, filter) {
  const needle = query.toLocaleLowerCase("nl-NL");
  return days
    .filter(
      (day) =>
        `${day.day} ${day.advisor.state} ${JSON.stringify(day.decisions)}`
          .toLocaleLowerCase("nl-NL")
          .includes(needle) &&
        (filter === "all" ||
          (filter === "fills" && day.fills > 0) ||
          (filter === "cost" && day.has_cost_block) ||
          (filter === "data" && day.has_data_skip)),
    )
    .slice()
    .reverse();
}
/** @param {string} key @param {boolean} typing @param {boolean} modified */
export function terminalShortcut(key, typing, modified) {
  return !typing && !modified && /^[1-4]$/.test(key) ? Number(key) : null;
}
/** @param {OSState} state @param {import('./portfolio-os-types').Profile} profile */
export function terminalSleeves(state, profile) {
  const latest = state.audit.days.at(-1),
    nav = Number(latest?.nav_reference ?? 0),
    reserve = Math.max(10, nav * 0.01);
  const preview = profile !== state.active_profile;
  return ["core", "trend", "s1", "cash"].map((sleeve, i) => {
    const cash = Number(
      state.audit.wallets.find((w) => w.sleeve === sleeve)?.cash ?? 0,
    );
    const held = state.audit.positions
      .filter((p) => p.sleeve === sleeve)
      .reduce(
        (sum, p) =>
          sum +
          Number(p.qty) *
            (state.telemetry[/** @type {'QQQ'|'TQQQ'} */ (p.key)]?.close ?? 0),
        0,
      );
    const claims = [...state.audit.settlements, ...state.audit.dividends]
      .filter((p) => p.sleeve === sleeve)
      .reduce((sum, p) => sum + Number(p.amount), 0);
    const weight = state.profiles[profile].weights[i];
    return {
      sleeve,
      weight,
      cash,
      held,
      claims,
      preview,
      value: preview
        ? Math.max(0, nav - reserve) * weight + (i === 3 ? reserve : 0)
        : state.public_summary
          ? (state.sleeve_balances?.[sleeve] ?? 0)
          : cash + held + claims,
    };
  });
}
/** @param {import('./portfolio-os-types').Cost[]} costs @param {string} gate */
export function terminalCostRows(costs, gate) {
  return costs.map((c) => ({
    ...c,
    gate: c.gates[gate],
    fee_eur:
      c.roundtrip_bp == null
        ? null
        : (Math.max(0, c.roundtrip_bp - c.spread_bp - c.slippage_bp) *
            c.amount_eur) /
          10000,
    math_status:
      c.roundtrip_bp == null
        ? "UNKNOWN"
        : c.gates[gate].mathematical_pass
          ? "MATH_PASS"
          : "COST_FAIL",
  }));
}
