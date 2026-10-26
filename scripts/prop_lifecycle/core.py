"""One account per start, no retries, no future-dependent candidate substitution."""
from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, datetime
import math
from statistics import mean, median


MODELS = {
    'S1-Judas-Bull0930': ('S1_STOP050', 'JBULL0930'),
    'S1-Judas-0830': ('S1_STOP050', 'J0830'),
    'S2-Judas': ('S2_NO_STOP', 'J0830'),
}


@dataclass(frozen=True)
class Rules:
    name: str
    purchase: float
    renewal: float
    activation: float
    rt_cost: float
    eval_consistency: float | None
    eval_min_days: int
    floor_lock: float
    dll: float | None
    eval_inactivity: int | None
    funded_inactivity: int
    payout_path: str
    share: float
    payout_cap: float
    eval_target: float = 3000.
    drawdown: float = 2000.


RULES = (
    Rules('TOPSTEP_STANDARD', 49., 49., 149., 3.22, .55, 2, 0., None, None, 31,
          'STANDARD', .9, 2000.),
    Rules('TOPSTEP_CONSISTENCY', 49., 49., 149., 3.22, .55, 2, 0., None, None, 31,
          'CONSISTENCY', .9, 3000.),
    Rules('MFFU_BUILDER', 153., 0., 0., 6.50, None, 1, 100., 1000., 7, 7,
          'BUILDER', .8, 2000.),
)


def ordinal(day):
    return date.fromisoformat(day).toordinal()


def entry_day(t):
    # Already calculated from source-aware timestamp, no host timezone dependency.
    return t.get('entry_ny_day', t['day'])


def barrier_fill(t, threshold):
    """First decreasing adverse-record crossing BEFORE the first missing minute.

    Low/high-first is a conservative OHLC convention, not a tick execution claim.
    An observed adverse open beyond the barrier fills at that open, never clipped.
    """
    ix = bisect_left(t['negative_record_lows'], -threshold - 1e-9)
    if ix == len(t['records']):
        return None
    minute, opening, adverse = t['records'][ix]
    return dict(minute=minute, gross=opening if opening is not None and opening <= threshold else threshold,
                observed_open=opening is not None and opening <= threshold)


def payout_request(balance, cycle_net, best, active, winning, previous_payouts, first_fill_day,
                   day, rules):
    if rules.payout_path == 'BUILDER':
        if active < 2 or first_fill_day is None or ordinal(day)-first_fill_day < 2:
            return 0.
        if cycle_net < 500.-1e-8 or best > .5*cycle_net+1e-8:
            return 0.
        available = min(rules.payout_cap, balance-2100., cycle_net)
        return max(0., available) if available >= 500.-1e-8 else 0.
    if rules.payout_path == 'STANDARD':
        ready = winning >= 5 and (previous_payouts == 0 or cycle_net > 0)
    else:
        ready = active >= 3 and cycle_net > 0 and best <= .4*cycle_net+1e-8
    available = min(rules.payout_cap, balance*.5)
    return available if ready and available >= 125.-1e-8 else 0.


def simulate_start(dates, candidates, model, quantity, rules, start, stop=None):
    """Stop after two credited payouts, failure, unknown path or the stated horizon.

    Requests occur at EOD, assumed approved/deducted without review delay. The
    fresh funded account can first trade in the NEXT cash day's Globex/RTH session.
    Cash withdrawals lower account equity; non-withdrawn equity is never income.
    """
    end = len(dates) if stop is None else min(stop, len(dates))
    if quantity not in (1, 2):
        raise ValueError('Only the two preregistered fixed MNQ quantities')
    wanted = set(MODELS[model])
    start_day = dates[start]
    # Account purchase at 18NY the calendar evening before the first cash date.
    purchase_ord = ordinal(start_day)-1
    balance = peak = best = cycle_net = 0.
    floor = -rules.drawdown
    fees = rules.purchase
    months = 1
    phase = 'EVALUATION'
    last_trade = purchase_ord
    first_fill_day = None
    active = winning = 0
    busy = -math.inf
    count = blocked = dll_count = 0
    milestone = dict(eval_pass_day=None, eval_sessions=None, eval_calendar_days=None,
                     eval_monthly_payments=None, buffer2600_day=None, payout1_day=None,
                     payout2_day=None, funded_start_day=None)
    received = withdrawn = 0.
    payouts = []
    state = 'CENSORED_EVALUATION'
    unknown = False
    terminal_day = None
    for i in range(start, end):
        day = dates[i]
        today = ordinal(day)
        if phase == 'FUNDED_PENDING':
            phase = 'FUNDED'
            balance = peak = best = cycle_net = 0.
            floor = -rules.drawdown
            active = winning = 0
            last_trade = today-1
            first_fill_day = None
            busy = -math.inf
            milestone['funded_start_day'] = day
        if phase == 'EVALUATION' and rules.renewal:
            billed = (today-purchase_ord)//30+1
            fees += max(0, billed-months)*rules.renewal
            months = max(months, billed)
        start_balance = balance
        traded = False
        paused = False
        inactivity = rules.eval_inactivity if phase == 'EVALUATION' else rules.funded_inactivity
        for t in candidates.get(day, ()):
            if t['component'] not in wanted:
                continue
            trade_day = ordinal(entry_day(t)) if t['filled'] else today
            if inactivity and trade_day-last_trade >= inactivity:
                state = 'FAILED_INACTIVITY_'+phase
                terminal_day = date.fromordinal(last_trade+inactivity).isoformat()
                break
            if paused or busy > t['activation']:
                blocked += 1
                continue
            # Pending orders reserve the account; future fills do not select orders.
            busy = t['release']
            if not t['filled']:
                continue
            traded = True
            count += 1
            last_trade = trade_day
            if first_fill_day is None:
                first_fill_day = trade_day
            fee = rules.rt_cost*quantity
            scale = 2.*quantity
            dll_level = start_balance-rules.dll if rules.dll else -math.inf
            barrier = max(floor, dll_level)
            hit = barrier_fill(t, (barrier-balance+fee)/scale)
            if hit:
                net_at_hit = balance+hit['gross']*scale-fee
                if barrier == floor or net_at_hit <= floor+1e-8:
                    state = ('FAILED_OBSERVED_OPEN_FLOOR_' if hit['observed_open'] else
                             'FAILED_CONSERVATIVE_OHLC_FLOOR_')+phase
                    terminal_day = day
                    break
                # DLL is a liquidation/pause, not an account failure. Round in the
                # adverse direction to an executable 0.25-point lattice.
                gross = math.floor((hit['gross']+1e-9)/.25)*.25
                balance += gross*scale-fee
                if balance <= floor+1e-8:
                    state = 'FAILED_DLL_GAP_FLOOR_'+phase
                    terminal_day = day
                    break
                dll_count += 1
                paused = True
                continue
            if t['unknown']:
                state = 'UNKNOWN_SOURCE_PATH_'+phase
                unknown = True
                terminal_day = day
                break
            balance += scale*t['gross']-fee
        if terminal_day:
            break
        # A clock can expire on a day with no selected candidate. No keep-alive.
        if inactivity and today-last_trade >= inactivity:
            state = 'FAILED_INACTIVITY_'+phase
            terminal_day = date.fromordinal(last_trade+inactivity).isoformat()
            break
        day_net = balance-start_balance
        cycle_net += day_net
        best = max(best, day_net)
        active += int(traded)
        winning += int(day_net >= 150.-1e-8)
        peak = max(peak, balance)
        floor = max(floor, min(rules.floor_lock, peak-rules.drawdown))
        if phase == 'EVALUATION':
            if (balance >= rules.eval_target-1e-8 and active >= rules.eval_min_days and
                (rules.eval_consistency is None or best <= rules.eval_consistency*balance+1e-8)):
                milestone.update(eval_pass_day=day, eval_sessions=i-start+1,
                                 eval_calendar_days=today-purchase_ord+1,
                                 eval_monthly_payments=months)
                fees += rules.activation
                phase = 'FUNDED_PENDING'
                state = 'CENSORED_FUNDED_PENDING'
        else:
            if balance >= 2600.-1e-8 and milestone['buffer2600_day'] is None:
                milestone['buffer2600_day'] = day
            amount = payout_request(balance, cycle_net, best, active, winning, len(payouts),
                                    first_fill_day, day, rules)
            if amount:
                balance -= amount
                withdrawn += amount
                received += amount*rules.share
                payouts.append(dict(day=day, gross=amount, received=amount*rules.share,
                                    balance_after=balance))
                milestone['payout'+str(len(payouts))+'_day'] = day
                floor = rules.floor_lock
                best = cycle_net = 0.
                active = winning = 0
                first_fill_day = None
                if len(payouts) == 2:
                    state = 'COMPLETED_TWO_PAYOUTS'
                    terminal_day = day
                    break
            state = 'CENSORED_FUNDED'
    stop_day = terminal_day or dates[end-1]
    # A weekend inactivity expiry may precede the next observed cash date.
    # Bill only through the actual eval pass/termination, never that later date.
    eval_stop = milestone['eval_pass_day'] or stop_day
    months = (ordinal(eval_stop)-purchase_ord)//30+1 if rules.renewal else 1
    fees = rules.purchase+(months-1)*rules.renewal+rules.activation*bool(milestone['eval_pass_day'])
    if unknown:
        # Worst fees allowed by the fixed follow-up; no fabricated point EV.
        max_months=(ordinal(dates[end-1])-purchase_ord)//30+1 if rules.renewal else 1
        max_fees=(rules.purchase+(max_months-1)*rules.renewal+rules.activation
                  if not milestone['eval_pass_day'] else fees)
        bounds=[received-max_fees,
                received+(2-len(payouts))*rules.payout_cap*rules.share-fees]
    else:
        bounds=[received-fees,received-fees]
    return dict(start_day=start_day, stop_day=stop_day, state=state, phase=phase,
                observed_cash_sessions=min(end-start, sum(d<=stop_day for d in dates[start:end])),
                elapsed_calendar_days=ordinal(stop_day)-purchase_ord+1,
                fees_USD=fees, monthly_payments=months, credited_payouts=len(payouts),
                received_USD=received, gross_withdrawn_USD=withdrawn,
                cash_net_accrued_USD=received-fees,
                net_cash_through_horizon_USD=None if unknown else received-fees,
                finite_horizon_cash_bounds_USD=bounds,
                remaining_simulated_equity_USD=None if unknown or state.startswith('FAILED') else balance,
                source_unknown=unknown, trades=count, blocked_orders=blocked, DLL_pauses=dll_count,
                milestones=milestone, payouts=payouts)


def summarize(accounts):
    n = len(accounts)
    passed = [a for a in accounts if a['milestones']['eval_pass_day']]
    unknown = [a for a in accounts if a['source_unknown']]
    known = [a for a in accounts if not a['source_unknown']]
    completed = [a for a in accounts if a['credited_payouts'] == 2]
    eval_days = [a['milestones']['eval_sessions'] for a in passed]
    def pct(test):
        return sum(test(a) for a in accounts)/n if n else None
    def conditional(test):
        return sum(test(a) for a in passed)/len(passed) if passed else None
    return dict(starts=n, known_evaluation_passes=len(passed),
                evaluation_pass_rate=pct(lambda a: bool(a['milestones']['eval_pass_day'])),
                median_eval_cash_sessions_if_passed=median(eval_days) if eval_days else None,
                mean_eval_calendar_days_if_passed=mean(a['milestones']['eval_calendar_days'] for a in passed) if passed else None,
                mean_eval_monthly_payments_if_passed=mean(a['milestones']['eval_monthly_payments'] for a in passed) if passed else None,
                buffer2600_rate_given_pass=conditional(lambda a: bool(a['milestones']['buffer2600_day'])),
                payout1_rate_given_pass=conditional(lambda a: a['credited_payouts'] >= 1),
                payout2_rate_given_pass=conditional(lambda a: a['credited_payouts'] >= 2),
                payout1_all_starts=pct(lambda a: a['credited_payouts'] >= 1),
                payout2_all_starts=pct(lambda a: a['credited_payouts'] >= 2),
                failures=pct(lambda a: a['state'].startswith('FAILED')),
                censored=pct(lambda a: a['state'].startswith('CENSORED')),
                unknown_rate=len(unknown)/n if n else None,
                mean_net_cash_per_start_USD=mean(a['cash_net_accrued_USD'] for a in accounts) if not unknown and n else None,
                partial_identification_cash_bounds_USD=[mean(a['finite_horizon_cash_bounds_USD'][j] for a in accounts) for j in (0,1)] if n else None,
                mean_net_cash_resolved_only_USD=mean(a['cash_net_accrued_USD'] for a in known) if known else None,
                mean_net_cash_accrued_until_known_stop_USD=mean(a['cash_net_accrued_USD'] for a in accounts) if n else None,
                mean_fees_accrued_USD=mean(a['fees_USD'] for a in accounts) if n else None,
                mean_received_accrued_USD=mean(a['received_USD'] for a in accounts) if n else None,
                completed_two_payout_accounts=len(completed),
                states={s:sum(a['state']==s for a in accounts) for s in sorted({a['state'] for a in accounts})})
