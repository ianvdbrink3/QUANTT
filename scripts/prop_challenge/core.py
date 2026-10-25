"""Causal account simulation. No profit-dependent trade selection or era bridging."""
from dataclasses import dataclass, asdict
from itertools import combinations, product
import math
import numpy as np

OPEN, PASS, FLOOR_OBSERVED, FLOOR_BOUND, INACTIVE, UNKNOWN = range(6)
LABELS = ('OPEN', 'PASSED', 'FAILED_OBSERVED_FLOOR', 'FAILED_OHLC_FLOOR_BOUND',
          'FAILED_INACTIVITY_CONSERVATIVE', 'UNRESOLVED_SOURCE_PATH')
HORIZONS = (21, 42, 63)
NIGHTS = ('NONE', 'S1_STOP050', 'S2_NO_STOP', 'S2_STOP050', 'S2_STOP075')
MORNINGS = ('NONE', 'J0830', 'JBULL0930', 'J1M_TIME')
LATE = ('PULLBACK', 'ICT1', 'SB_AM', 'SB_PM')


@dataclass(frozen=True)
class Profile:
    name: str
    kind: str
    value: float
    overnight_cap: int = 3
    intraday_cap: int = 10


def profiles():
    return ([Profile(f'FIXED_{q}', 'FIXED', q) for q in (1, 2, 3)] +
            [Profile(f'RISK_{v}', 'RISK', v) for v in (200, 300, 400)] +
            [Profile(f'CUSHION_{v}', 'CUSHION', v) for v in (200, 300, 400)])


def universe():
    subsets = [x for n in range(5) for x in combinations(LATE, n)]
    result = []
    for night, morning, late in product(NIGHTS, MORNINGS, subsets):
        if night == morning == 'NONE' and not late:
            continue
        key = '+'.join([night, morning, *late])
        result.append(dict(id=key, night=night, morning=morning, late=list(late)))
    return result


def admissible(combo, profile):
    # A nonexistent stop cannot provide an exact stop-dollar risk denominator.
    return not (combo['night'] == 'S2_NO_STOP' and profile.kind != 'FIXED')


def size(profile, risk, night, balance, floor, day_profit, consistency, max_micro):
    """Whole MNQ only, decisions use current realized account state.

    A stop is not guaranteed dollar risk: gaps can exceed this budget. Fixed
    quantities are deliberately not 'repaired' when close to an account floor.
    """
    balance, floor, day_profit = np.broadcast_arrays(balance, floor, day_profit)
    if profile.kind == 'FIXED':
        return np.full(balance.shape, min(int(profile.value), max_micro), dtype=np.int16)
    if risk is None or risk <= 0 or not math.isfinite(risk):
        return np.zeros(balance.shape, dtype=np.int16)
    budget = np.full(balance.shape, profile.value, dtype=float)
    if profile.kind == 'CUSHION':
        headroom = balance-floor
        budget *= np.where(headroom < 1500, .5, np.where(balance > 750, 1.5, 1.))
        # No magical clipping of a future winner: reduce NEW orders only.
        cap = consistency*3000
        budget *= np.where(day_profit >= .8*cap, .5, 1.)
        budget = np.where(day_profit >= cap, 0., budget)
        budget = np.minimum(budget, np.maximum(0., headroom-100.))
    per_contract = 2.*risk+3.22
    cap = min(max_micro, profile.overnight_cap if night else profile.intraday_cap)
    return np.minimum(cap, np.floor(budget/per_contract)).astype(np.int16)


def economic_cost(pass_count, failed_count, open_count, unknown_count, fee_sum,
                  reset_price, activation, purchase):
    """Fresh-account retry proxy, not a promised independent geometric process.

    Initial purchase is already in fee_sum for EVERY attempt. A $49 reset
    replaces a $49 fresh purchase: never charge both again for one restart.
    Unknown paths have unknown attempt length, so no firm expected cost.
    """
    if not pass_count or unknown_count:
        return None
    replacement_delta = max(0., reset_price-purchase)*failed_count
    return (fee_sum+replacement_delta)/pass_count+activation


def simulate(dates, candidates, combo, profile, firm, record=False):
    """All starts, same event stream, maximum63 sessions, one account per start.

    Candidates sort by order ACTIVATION, not future fill. A pending limit also
    reserves the account. Each cohort independently sizes/rejects the order.
    A future blocked trade cannot be substituted after observing its outcome.
    """
    n = len(dates)
    b = np.zeros(n); floor = np.full(n, -2000.); peak = np.zeros(n)
    best = np.zeros(n); active_days = np.zeros(n, dtype=np.int16)
    count = np.zeros(n, dtype=np.int16); state = np.zeros(n, dtype=np.int8)
    quantity_sum = np.zeros(n); skipped = np.zeros(n, dtype=np.int16)
    blocked = np.zeros(n, dtype=np.int16); busy = np.full(n, -np.inf)
    elapsed = np.zeros(n, dtype=np.int16)
    calendar = np.asarray(dates, dtype='datetime64[D]').astype(np.int64)
    last_active = calendar.copy()
    outcomes = {h: [] for h in HORIZONS}
    wanted = set(combo['late']) | ({combo['morning']} if combo['morning'] != 'NONE' else set())
    if combo['night'] != 'NONE': wanted.add(combo['night'])
    for i, day in enumerate(dates):
        ix = np.arange(max(0, i-62), i+1)
        alive = ix[state[ix] == OPEN]
        elapsed[alive] = i-alive+1
        start_balance = b[ix].copy()
        traded = np.zeros(len(ix), dtype=bool)
        # Timer is independent of whether a strategy happens to signal today.
        if firm['inactivity']:
            hit = alive[calendar[i]-last_active[alive] >= firm['inactivity']]
            state[hit] = INACTIVE
        for t in candidates.get(day, ()):
            if t['component'] not in wanted: continue
            eligible = (state[ix] == OPEN)
            conflict = eligible & (busy[ix] > t['activation'])
            blocked[ix[conflict]] += 1
            eligible &= ~conflict
            at = ix[eligible]
            if not len(at): continue
            q = size(profile, t['risk'], t['night'], b[at], floor[at],
                     b[at]-start_balance[eligible], firm['consistency'], firm['max_micro'])
            skipped[at[q == 0]] += 1
            at, q = at[q > 0], q[q > 0]
            if not len(at): continue
            busy[at] = t['release']
            if not t['filled']: continue
            count[at] += 1; quantity_sum[at] += q
            traded[at-ix[0]] = True; last_active[at] = calendar[i]
            fee = 3.22*q
            observed = b[at]+2*q*t['observed_min']-fee
            bound = b[at]+2*q*t['adverse_min']-fee
            breached = bound <= floor[at]+1e-9
            state[at[breached]] = np.where(observed[breached] <= floor[at[breached]]+1e-9,
                                         FLOOR_OBSERVED, FLOOR_BOUND)
            b[at[breached]] = floor[at[breached]]
            at, q = at[~breached], q[~breached]
            if t['unknown']:
                state[at] = UNKNOWN
                continue
            b[at] += (2*t['gross']-3.22)*q
        alive = ix[state[ix] == OPEN]
        day_net = b[ix]-start_balance
        best[alive] = np.maximum(best[alive], day_net[alive-ix[0]])
        active_days[ix[traded]] += 1
        peak[alive] = np.maximum(peak[alive], b[alive])
        floor[alive] = np.maximum(floor[alive], np.minimum(firm['lock'], peak[alive]-2000.))
        good = alive[(b[alive] >= 3000.-1e-9) &
                     (best[alive] <= firm['consistency']*b[alive]+1e-9) &
                     (active_days[alive] >= firm['min_days'])]
        state[good] = PASS
        for horizon in HORIZONS:
            j = i-horizon+1
            if j < 0: continue
            # An ended account's elapsed time stops at its first terminal event.
            end_date = calendar[j+int(elapsed[j])-1]
            months = max(1, int(math.ceil(int(elapsed[j])/21)))
            actual_months = int((end_date-calendar[j])//30)+1
            fee = firm['purchase']+(months-1)*firm['renewal']
            actual_fee = firm['purchase']+(actual_months-1)*firm['renewal']
            outcomes[horizon].append((int(state[j]), int(elapsed[j]), int(count[j]), float(b[j]),
                float(fee), float(actual_fee), int(blocked[j]), int(skipped[j]), float(quantity_sum[j]),
                str(day), dates[j]))
    return outcomes


def summarize(rows, firm):
    n = len(rows)
    if not n: return dict(starts=0)
    a = np.asarray([r[:9] for r in rows], dtype=float)
    s = a[:, 0].astype(int); passed = s == PASS
    failures = np.isin(s, [FLOOR_OBSERVED, FLOOR_BOUND, INACTIVE])
    unknown = s == UNKNOWN
    counts = {label: int(np.sum(s == k)) for k, label in enumerate(LABELS)}
    # At most one start every full horizon: diagnostic, not an optimized phase.
    result = dict(starts=n, passed=int(passed.sum()), failed=int(failures.sum()),
        unknown=int(unknown.sum()), unfinished=counts['OPEN'],
        pass_rate=float(passed.mean()), pass_upper_source_unknown=float((passed|unknown).mean()),
        fail_rate=float(failures.mean()), mean_trades=float(a[:,2].mean()),
        mean_days_to_pass=float(a[passed,1].mean()) if passed.any() else None,
        mean_days_to_fail=float(a[failures,1].mean()) if failures.any() else None,
        mean_attempt_fee_USD=float(a[:,4].mean()),
        mean_calendar_billed_fee_USD=float(a[:,5].mean()),
        cost_per_pass_proxy_USD=economic_cost(int(passed.sum()), int(failures.sum()), counts['OPEN'],
            int(unknown.sum()), float(a[:,4].sum()), firm['purchase'], firm['activation'], firm['purchase']),
        cost_per_pass_resolved_paths_USD=(float(a[~unknown,4].sum())/int(passed.sum())+firm['activation']) if passed.any() else None,
        mean_rejected_overlap=float(a[:,6].mean()), mean_rejected_sizing=float(a[:,7].mean()),
        mean_contracts_per_trade=float(a[:,8].sum()/a[:,2].sum()) if a[:,2].sum() else 0.,
        outcomes=counts)
    if firm['id'] == 'TOPSTEP':
        for reset in (49,99):
            result[f'cost_reset{reset}_USD'] = economic_cost(int(passed.sum()),int(failures.sum()),counts['OPEN'],
                int(unknown.sum()),float(a[:,4].sum()),reset,149,49)
    return result
