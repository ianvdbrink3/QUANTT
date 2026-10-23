"""One fixed audit of original ToM on consumed data, not a new holdout."""
import argparse
import csv
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.causal_map.__main__ import load_inputs
from scripts.edge_marathon.data import basic_frame, older_closes, quality_and_state, verify_source_register
from scripts.edge_marathon.features import calendar_context
from scripts.edge_marathon.stats import holm
from scripts.oos_preparation.adapter import at, combine, load_csv, sha

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'research/month-turn-audit-protocol.json'
LOCK = ROOT / 'research/month-turn-audit-lock.json'
RESULT = ROOT / 'research/month-turn-audit-results.json'
PUBLIC = ROOT / 'public/data/month-turn-audit.json'
REPORT = ROOT / 'docs/MONTH_TURN_AUDIT.md'
OUT = ROOT / 'artifacts/month-turn-audit'


def dump(path, obj, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x' if exclusive else 'w') as handle:
        handle.write(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def register():
    if LOCK.exists():
        verify()
        return
    if PROTOCOL.exists():
        raise ValueError('Partial registration exists; do not replace')
    protocol = dict(
        id='ORIGINAL-TOM-BENCHMARK-RISK-AUDIT-20261022',
        status='EXPLORATORY_AUDIT_OF_ALREADY_CONSUMED_DATA_NOT_INDEPENDENT_VALIDATION',
        model='Original TOM_RTH only: last cash session of month and first3 cash sessions; long09:30open to15:59close. '
              'Main2024Dec30/31 remain non-ToM as in the original incomplete-month exclusion. No new filters or sizing.',
        samples=['DISCOVERY', 'CONTINUOUS_2022_2024_UNVERIFIED'],
        benchmark='Same-clock long on ALL complete eligible sessions and on the complementary non-ToM sessions. '
                  'Compare means per exposed day, not unequal-exposure cumulative profits. All-session benchmark includes ToM and is not an independent control.',
        volatility='Descriptive common sample with finite prior ATR14>0. Compare (gross_points-1.225)/prior_ATR14. '
                   'Do not remove missing-ATR trades from the original model. No full-sample volatility thresholds or sizing rule.',
        inference=dict(method='Moving block bootstrap of2 consecutive calendar MONTH clusters,10000 replications, fixed seeds20261022101/102. '
                              'Resample whole months, use ratios of pooled event sums/counts; never equal-weight daily or event-rich month means. '
                              'Percentile95% intervals. Approximate two-sided null-centered bootstrap p=(1+count(abs(diff*-diff)>=abs(diff)))/(B+1). '
                              'Weak dependence/stationarity and few-month limitations, not exact randomization inference.',
                       tests='Exactly4 new exploratory contrasts: ToM minus non-ToM in raw net points and net points/priorATR for each of2 separate sources; Holm4. '
                             'Other means, paths, delays, quarters and cost cases descriptive only. Previous25/125 families unchanged.',
                       decision='No formal promotion. Exploratory support only if all4 adjusted contrasts are positive and p<.05; otherwise INSUFFICIENT_EVIDENCE_NO_PROMOTION. '
                                'This is an audit label, not a new preregistration or live authorization.'),
        risk=['closed-trade drawdown from initial0', 'minute-close marked equity drawdown with fullRT cost deducted at entry',
              'worst day, MAE/MFE, top3 contribution and removal, leave-one-day/quarter-out; no post-hoc exclusions become trading filters'],
        execution=dict(entry_delays_minutes=[0, 1, 5], exit='Same fixed15:59close proxy, no exit timing search',
                       roundtrip_cost_usd=[24.5, 34.5, 44.5], points=[1.225, 1.725, 2.225],
                       warning='1/2 extra ticks PER LEG on top of fixed baseline. No BBO/queue/latency evidence; exact open/close fills not certified.'),
        source_check='Existing NQH24 pilot against generic on all complete common sessions2024Jan22-Feb16. '
                     'Fixed old timestamp normalization only, no shift search. Same-date agreement is not sample independence.',
        source_register_sha256=sha(ROOT/'artifacts/edge-marathon/source-register.json'),
        unchanged=['all prior files', 'baseline v0.9', 'vNext freeze', 'afternoon candidate v2', 'original ToM ledger'],
        restrictions='No unseen history, independent holdout, purchases, downloads, account changes, orders, Git push or external deployment.',
        public_output='Aggregates, quarters, sensitivity and report only. No raw OHLCV, daily/trade arrays, absolute source paths or protected-file manifest.',
        references=['https://docs.lib.purdue.edu/ciberwp/43/', 'https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf'],
    )
    dump(PROTOCOL, protocol, exclusive=True)
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    protected = {n:sha(ROOT/n) for n in names if n and (ROOT/n).is_file()}
    evidence = [ROOT/'artifacts/edge-marathon/discovery.json', ROOT/'artifacts/edge-marathon/historical.json',
                ROOT/'artifacts/edge-marathon/discovery-trades.csv',
                ROOT/'artifacts/edge-marathon/continuous_2022_2024_unverified-trades.csv',
                ROOT/'artifacts/raw-market/quality.json', ROOT/'artifacts/edge-marathon/source-register.json']
    dump(LOCK, dict(protocol_sha256=sha(PROTOCOL), protected_files=protected,
                    prior_private_evidence={str(p.relative_to(ROOT)):sha(p) for p in evidence}), exclusive=True)
    print('Locked original ToM audit; preserved', len(protected), 'existing files.', flush=True)


def verify():
    lock = json.loads(LOCK.read_text())
    if sha(PROTOCOL) != lock['protocol_sha256']:
        raise ValueError('Audit protocol changed')
    for name, expected in {**lock['protected_files'], **lock['prior_private_evidence']}.items():
        if sha(ROOT/name) != expected:
            raise ValueError('Prior or locked file changed: ' + name)
    return lock


def day_record(day, prices, context, sample, delay=0):
    if delay not in (0, 1, 5):
        raise ValueError('Unregistered entry delay')
    arrays = [np.asarray(prices[k], float) for k in ('open', 'high', 'low', 'close')]
    if any(len(a) != 390 or not np.isfinite(a).all() for a in arrays):
        raise ValueError('Full unchanged390-minute session required')
    op, hi, lo, cl = arrays
    entry = float(op[delay]); gross = float(cl[-1]-entry)
    is_tom = calendar_context(day)['tom']
    if sample == 'DISCOVERY' and day < '2025-01-01':
        is_tom = False
    atr = float(context.get('atr', np.nan))
    return dict(day=day, month=day[:7], quarter=str(pd.Period(day, freq='Q')),
                tom=bool(is_tom), entry_delay=delay, gross_points=gross, net_points=gross-1.225,
                prior_atr=atr if np.isfinite(atr) and atr > 0 else None,
                mfe_points=float(max(0, np.max(hi[delay:])-entry)),
                mae_points=float(max(0, entry-np.min(lo[delay:]))))


def curve_drawdown(values):
    equity = np.r_[0., np.cumsum(values)]
    return float((np.maximum.accumulate(equity)-equity).max())


def describe(values):
    values = np.asarray(values, float)
    if not len(values):
        return None
    return dict(zip(['p10', 'p25', 'median', 'p75', 'p90', 'p95', 'max'],
                    map(float, np.quantile(values, [.1, .25, .5, .75, .9, .95, 1]))))


def summary(rows, cost=1.225):
    if not rows:
        return dict(days=0, net_points=0., net_dollars=0., mean_net=None, median_net=None, winrate=None,
                    profit_factor=None, closed_trade_drawdown=None)
    values = np.asarray([r['gross_points']-cost for r in rows]); losses = -values[values < 0].sum()
    return dict(days=len(rows), gross_points=float(sum(r['gross_points'] for r in rows)),
                net_points=float(values.sum()), net_dollars=float(values.sum()*20),
                mean_net=float(values.mean()), median_net=float(np.median(values)),
                winrate=float((values > 0).mean()),
                profit_factor=float(values[values > 0].sum()/losses) if losses else None,
                closed_trade_drawdown=curve_drawdown(values), worst_day=float(values.min()),
                worst_day_date=rows[int(np.argmin(values))]['day'])


def month_contrast(rows, normalized=False, seed=20261022101, reps=10000):
    """Pooled means,2-month MBB. No resampling of trades as independent days."""
    months = sorted({r['month'] for r in rows})
    sums = np.zeros((len(months), 2)); counts = np.zeros_like(sums)
    lookup = {m:i for i, m in enumerate(months)}
    for row in rows:
        if normalized and row['prior_atr'] is None:
            continue
        group = 0 if row['tom'] else 1
        value = row['net_points']/row['prior_atr'] if normalized else row['net_points']
        i = lookup[row['month']]; sums[i, group] += value; counts[i, group] += 1
    totals = counts.sum(axis=0)
    if min(totals) == 0 or len(months) < 4:
        raise ValueError('Insufficient months or complementary observations')
    means = sums.sum(axis=0)/totals; diff = float(means[0]-means[1])
    rng = np.random.default_rng(seed); samples = []; n = len(months)
    for offset in range(0, reps, 250):
        starts = rng.integers(0, n-1, size=(min(250, reps-offset), int(np.ceil(n/2))))
        indexes = (starts[:, :, None] + np.arange(2)[None, None, :]).reshape(len(starts), -1)[:, :n]
        numerator = sums[indexes].sum(axis=1); denominator = counts[indexes].sum(axis=1)
        valid = (denominator > 0).all(axis=1)
        samples.extend((numerator[valid]/denominator[valid]).tolist())
    samples = np.asarray(samples)
    delta = samples[:, 0]-samples[:, 1]
    p = (1+int((np.abs(delta-diff) >= abs(diff)-1e-12).sum()))/(len(delta)+1)
    # The all-day mean is descriptive; the two comparison intervals are pooled within groups.
    return dict(unit='net_points_per_prior_ATR' if normalized else 'net_NQ_points',
                months=len(months), tom_days=int(totals[0]), non_tom_days=int(totals[1]),
                tom_mean=float(means[0]), non_tom_mean=float(means[1]), difference=diff,
                tom_ci95=list(map(float, np.quantile(samples[:, 0], [.025, .975]))),
                non_tom_ci95=list(map(float, np.quantile(samples[:, 1], [.025, .975]))),
                difference_ci95=list(map(float, np.quantile(delta, [.025, .975]))),
                p_raw=float(p), bootstrap_valid_replications=len(delta),
                method='Fixed2-consecutive-month moving block bootstrap, pooled sums/counts,10000 draws; approximate null-centered p.',
                limitation='Exploratory nominal intervals, weak dependence and stationarity assumed, few months; not independent confirmation. '
                           'Holm4 corrects only this fixed audit family, not the full accumulated research selection history.')


def risk(rows, state):
    values = np.asarray([r['net_points'] for r in rows]); net = float(values.sum())
    top = sorted(rows, key=lambda r:r['net_points'], reverse=True)[:3]
    positives = [r for r in top if r['net_points'] > 0]
    removed = {r['day'] for r in top}
    remaining = [r for r in rows if r['day'] not in removed]
    quarters = sorted({r['quarter'] for r in rows})
    loq = []
    for quarter in quarters:
        kept = [r for r in rows if r['quarter'] != quarter]
        loq.append(dict(omitted=quarter, **summary(kept)))
    mark = [0.]; realized = 0.
    for row in rows:
        prices = state[row['day']][0]
        path = realized + np.asarray(prices['close']) - prices['open'][0] - 1.225
        mark.append(realized-1.225)  # FullRT friction at entry, explicitly conservative allocation.
        mark.extend(path.tolist())
        realized += row['net_points']
    mark = np.asarray(mark)
    return dict(top3_net_points=float(sum(r['net_points'] for r in positives)),
                top3_share_of_total_net=float(sum(r['net_points'] for r in positives)/net) if net > 0 else None,
                top3_dates=[r['day'] for r in top], without_top3=summary(remaining),
                leave_one_day_out_mean=[float(((net-values)/(len(rows)-1)).min()),
                                        float(((net-values)/(len(rows)-1)).max())],
                leave_one_quarter_out=loq,
                minute_close_equity_drawdown=float((np.maximum.accumulate(mark)-mark).max()),
                mark_to_market_assumption='Minute-close marks plus full24.50RT deduction at entry. '
                                          'Not tick-equity or a guaranteed worst intrabar drawdown; closed-trade DD reported separately.',
                mae=describe([r['mae_points'] for r in rows]), mfe=describe([r['mfe_points'] for r in rows]),
                net_distribution=describe(values),
                capital_limit='No account size, margin schedule, risk budget or tick fills; cannot declare capital suitability.')


def replay_check(rows, sample):
    filename = 'discovery-trades.csv' if sample == 'DISCOVERY' else 'continuous_2022_2024_unverified-trades.csv'
    with (ROOT/'artifacts/edge-marathon'/filename).open() as handle:
        prior = {r['day']:r for r in csv.DictReader(handle) if r['model'] == 'TOM_RTH'}
    actual = {r['day']:r for r in rows if r['tom']}
    if set(actual) != set(prior):
        raise ValueError('Original ToM selected-day membership changed')
    for day, row in actual.items():
        for field in ('gross_points', 'net_points', 'mae_points', 'mfe_points'):
            if abs(row[field]-float(prior[day][field])) > 1e-8:
                raise ValueError(f'Original ToM replay mismatch: {day} {field}')
    return dict(status='ORIGINAL_TOM_REPRODUCED_FROM_SOURCE_BARS', trades=len(actual), compared_fields=4,
                net_points=float(sum(r['net_points'] for r in actual.values())))


def audit_sample(state, included, sample, seed):
    rows = [day_record(day, *state[day], sample) for day in included]
    tom = [r for r in rows if r['tom']]; non = [r for r in rows if not r['tom']]
    shared = [r for r in rows if r['prior_atr'] is not None]
    raw = month_contrast(rows, seed=seed)
    normalized = month_contrast(rows, normalized=True, seed=seed+100)
    quarters = []
    for quarter in sorted({r['quarter'] for r in rows}):
        a = [r for r in tom if r['quarter'] == quarter]; b = [r for r in non if r['quarter'] == quarter]
        sa, sb = summary(a), summary(b)
        quarters.append(dict(quarter=quarter, tom=sa, non_tom=sb,
                             difference=None if not a or not b else sa['mean_net']-sb['mean_net']))
    sensitivity = []
    for delay in (0, 1, 5):
        delayed = [day_record(r['day'], *state[r['day']], sample, delay=delay) for r in tom]
        for cost in (1.225, 1.725, 2.225):
            sensitivity.append(dict(entry_delay_minutes=delay, roundtrip_cost_usd=cost*20, **summary(delayed, cost)))
    atr_groups = {}
    for name, group in [('tom', [r for r in shared if r['tom']]), ('non_tom', [r for r in shared if not r['tom']])]:
        atr_groups[name] = dict(days=len(group), mean_prior_atr=float(np.mean([r['prior_atr'] for r in group])),
                                median_prior_atr=float(np.median([r['prior_atr'] for r in group])),
                                mean_net_points=float(np.mean([r['net_points'] for r in group])),
                                mean_net_per_atr=float(np.mean([r['net_points']/r['prior_atr'] for r in group])))
    result = dict(source=sample, period=[included[0], included[-1]], complete_days=len(rows),
                  replay=replay_check(rows, sample), tom=summary(tom), non_tom=summary(non), all_rth_long=summary(rows),
                  all_benchmark_excess_per_tom_day=summary(tom)['mean_net']-summary(rows)['mean_net'],
                  raw_contrast=raw, normalized_contrast=normalized,
                  normalization=dict(common_sample_days=len(shared), tom_missing_atr=len(tom)-atr_groups['tom']['days'],
                                     non_tom_missing_atr=len(non)-atr_groups['non_tom']['days'], groups=atr_groups,
                                     original_model_exclusions_changed=False,
                                     interpretation='PriorATR normalization is a descriptive common-sample risk-unit comparison, not a sized trading model or causal identification.'),
                  risk=risk(tom, state), quarters=quarters, execution_sensitivity=sensitivity,
                  source_status='REGISTERED_CONTRACT_CHAIN_ALREADY_CONSUMED' if sample == 'DISCOVERY' else 'OLDER_CONTINUOUS_CONTRACT_CHAIN_AND_VINTAGE_UNVERIFIED')
    dump(OUT/(sample.lower()+'-daily.json'), rows)
    return result


def source_parity(records):
    generic_record = next(r for r in records if r['filename'] == 'Dataset_NQ_1min_2022_2025.csv')
    generic = basic_frame(generic_record['paths'][0], 'GENERIC')
    contract_records = [r for r in records if r['filename'].lower().startswith('nqh24_intraday-1min_')]
    contract = combine([load_csv(r['paths'][0], 'NQH24') for r in contract_records], '2024-01-22', '2024-02-16')
    checked = []
    for day in pd.bdate_range('2024-01-22', '2024-02-16').strftime('%Y-%m-%d'):
        grid = pd.date_range(at(day, '09:30'), at(day, '16:00'), freq='min', inclusive='left')
        if len(grid.difference(generic.index)) or len(grid.difference(contract.index)):
            continue
        a = float(generic.at[grid[-1], 'close']-generic.at[grid[0], 'open'])
        b = float(contract.at[grid[-1], 'close']-contract.at[grid[0], 'open'])
        checked.append(dict(day=day, tom=calendar_context(day)['tom'], difference=a-b))
    differences = np.asarray([r['difference'] for r in checked])
    tom = [r for r in checked if r['tom']]
    return dict(status='LIMITED_SAME_DATE_RTH_ANCHOR_COMPARISON_NOT_INDEPENDENT_VALIDATION',
                period=['2024-01-22', '2024-02-16'], complete_common_days=len(checked),
                exact_rth_movement_fraction=float(np.isclose(differences, 0, atol=1e-8).mean()),
                median_abs_difference_points=float(np.median(abs(differences))),
                maximum_abs_difference_points=float(abs(differences).max()),
                mean_difference_points=float(differences.mean()),
                tom_common_days=len(tom), tom_total_difference_points=float(sum(r['difference'] for r in tom)),
                earlier_two_minute_exception_points=15.5,
                limit='19 pilot sessions cannot certify493 older sessions, full historical roll provenance or timestamp vintage. '
                      'Prior two-minute discrepancy remains documented; no old data or negative evidence discarded.')


def load_samples():
    state, _, included, _, _, _, _ = load_inputs()
    yield 'DISCOVERY', state, included
    record = next(r for r in verify_source_register()['records'] if r['filename'] == 'Dataset_NQ_1min_2022_2025.csv')
    generic = basic_frame(record['paths'][0], 'GENERIC')
    generic = generic[generic.trade_date.lt('2024-12-30')]
    state, _, included, quality = quality_and_state(generic, 'CONTINUOUS_2022_2024_UNVERIFIED',
                                                   older_closes(generic.trade_date.min(), generic.trade_date.max()))
    if state is None or len(included) != 493:
        raise ValueError('Older consumed sample changed')
    yield 'CONTINUOUS_2022_2024_UNVERIFIED', state, included


def report(data):
    lines = ['# Audit oorspronkelijke maandwisselregel', '',
             '## Oordeel', '', data['verdict_text'], '',
             'Alle cijfers zijn aanvullend verkennend onderzoek op reeds gebruikte gegevens. Geen nieuwe holdout of gevalideerd winstmodel. '
             'De oorspronkelijke regels, v0.9/vNext en de 15:00-v2-specificatie blijven ongewijzigd.', '',
             '## Regel en benchmark', '',
             'Long op de laatste cashhandelsdag en eerste drie cashhandelsdagen van de maand, van de09:30-open tot de15:59-closebar. '
             'De twee december2024-startdagen blijven volgens de bestaande onvolledige-maandregel buiten ToM, maar tellen wel mee in de long-benchmark. '
             'Eén NQ-contract, $20 per punt, $24,50 roundtrip =1,225punt. Geen stops, targets of nieuwe filters.', '',
             'Alleen de bestaande complete sessies tellen mee. Een volledige sessie is een technische evaluatie-eis, geen op voorhand bekende handelsfilter. '
             'Datakwaliteit blijft een beperking van de simulatie.', '',
             'De dagelijkse long-benchmark bevat ook maandwisseldagen. De complementaire niet-ToM-groep is de zuivere beschrijvende kalendervergelijking. '
             'Vergelijk opbrengst per blootgestelde dag: de totale winst van81 tegen435 posities is geen gelijk-exposurevergelijking.', '',
             '## Hoofdvergelijking', '',
             '| Bron | Groep | Dagen | Netto totaal pt | Gemiddeld netto pt/dag | Mediaan | Win% | PF | Gesloten-trade DD pt |',
             '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for source, s in data['samples'].items():
        label = 'Ontdekking' if source == 'DISCOVERY' else 'Oudere onbevestigde bron'
        for group, title in [('tom', 'Maandwissel'), ('non_tom', 'Andere dagen'), ('all_rth_long', 'Alle dagen long')]:
            r = s[group]
            lines.append(f'| {label} | {title} | {r["days"]} | {r["net_points"]:.3f} | {r["mean_net"]:.3f} | '
                         f'{r["median_net"]:.3f} | {100*r["winrate"]:.1f} | {r["profit_factor"]:.3f} | {r["closed_trade_drawdown"]:.3f} |')
    lines += ['', '## Benchmarkmeerwaarde en onzekerheid', '',
              'Vooraf vastgelegde2-maands moving-blockbootstrap,10.000 herhalingen, gehele maanden als clusters en gepoolde sommen/aantallen. '
              'Geen gelijke weging van daggemiddelden of maanden met verschillende aantallen trades. '
              'Exact vier aanvullende verkennende contrasten; Holm4. Intervallen zijn nominaal95%, niet simultaan. '
              'De p-waarden zijn benaderende nulgecentreerde bootstrapwaarden, geen exacte randomisatietoets. '
              'Zwakke afhankelijkheid/stationariteit en beperkte aantallen maanden begrenzen de geldigheid. '
              'Deze correctie wist de eerdere modelselectie en25/125-toetsenfamilies niet uit.', '',
              '| Bron | Eenheid | ToM N / andere N | Gem. ToM | Gem. andere | Verschil | 95%-interval verschil | Ruwe p | Holm4 p |',
              '|---|---|---:|---:|---:|---:|---|---:|---:|']
    for source, s in data['samples'].items():
        label = 'Ontdekking' if source == 'DISCOVERY' else 'Oudere bron'
        for field in ('raw_contrast', 'normalized_contrast'):
            r = s[field]; ci = r['difference_ci95']; unit = 'Netto pt' if field == 'raw_contrast' else 'Netto pt / voorafATR'
            lines.append(f'| {label} | {unit} | {r["tom_days"]} / {r["non_tom_days"]} | {r["tom_mean"]:.5f} | '
                         f'{r["non_tom_mean"]:.5f} | {r["difference"]:.5f} | [{ci[0]:.5f}; {ci[1]:.5f}] | '
                         f'{r["p_raw"]:.5f} | {r["p_holm4"]:.5f} |')
    lines += ['', 'De vaste frictie is voor elke long-dag gelijk en valt daardoor uit het ruwe verschil tussen groepsgemiddelden weg. '
              'Zij blijft wel volledig in elk modelresultaat verwerkt. Een positief gemiddeld ToM-resultaat is niet automatisch een significante kalenderpremie.', '',
              '## Volatiliteitsvergelijking zonder toekomstige informatie', '']
    for source, s in data['samples'].items():
        n = s['normalization']; a, b = n['groups']['tom'], n['groups']['non_tom']
        lines += [f'### {source}', '',
                  f'Gemeenschappelijke steekproef met vooraf bekendeATR14: {n["common_sample_days"]} dagen; '
                  f'{a["days"]} ToM en {b["days"]} andere dagen. '
                  f'OntbrekendeATR: {n["tom_missing_atr"]} ToM en {n["non_tom_missing_atr"]} andere dagen. '
                  'Deze dagen blijven gewoon in het oorspronkelijke modelresultaat staan.', '',
                  f'Gemiddelde voorafATR: ToM {a["mean_prior_atr"]:.2f}pt, andere dagen {b["mean_prior_atr"]:.2f}pt. '
                  f'Op precies die gemeenschappelijke steekproef: gemiddelde netto ToM {a["mean_net_points"]:.3f}pt, '
                  f'andere dagen {b["mean_net_points"]:.3f}pt.', '']
    lines += ['ATR-normalisatie is een aanvullende beschrijvende vergelijking, geen positiegrootteregel of causale identificatie. '
              'Regime, prijsniveau en andere kalenderkenmerken kunnen nog verschillen. Er is geen volatiliteitsgrens geoptimaliseerd.', '',
              '## Concentratie, drawdown en excursies', '',
              '| Bron | Top3 aandeel netto | Netto zonder top3 pt | Gesloten DD pt | Minuut-close DD pt | Slechtste dag pt | MAE mediaan / P95 / max pt |',
              '|---|---:|---:|---:|---:|---:|---|']
    for source, s in data['samples'].items():
        r = s['risk']; m = r['mae']
        lines.append(f'| {source} | {100*r["top3_share_of_total_net"]:.1f}% | {r["without_top3"]["net_points"]:.3f} | '
                     f'{s["tom"]["closed_trade_drawdown"]:.3f} | {r["minute_close_equity_drawdown"]:.3f} | '
                     f'{s["tom"]["worst_day"]:.3f} | {m["median"]:.2f} / {m["p95"]:.2f} / {m["max"]:.2f} |')
    lines += ['', 'Minuut-close-drawdown gebruikt de waargenomen minuutcloses en rekent de volledige roundtripfrictie bij entry. '
              'Dit is geen tick-drawdown en geen gegarandeerde intrabar-worst-case. '
              'MAE wordt gemeten vanaf de entry tot het vastgelegde einde, niet vanaf een achteraf gekozen stop. '
              'Vermenigvuldig punten met$20 voor éénNQ. Zonder rekeninggrootte, marginhistorie en risicobudget volgt hieruit geen oordeel dat het kapitaalrisico aanvaardbaar is.', '']
    for source, s in data['samples'].items():
        r = s['risk']; loq = r['leave_one_quarter_out']; means = [v['mean_net'] for v in loq]
        lines += [f'### Weglaatcontroles {source}', '',
                  f'Top3-datums: {", ".join(r["top3_dates"])}. '
                  f'Leave-one-day-out gemiddeld netto: [{r["leave_one_day_out_mean"][0]:.3f}; {r["leave_one_day_out_mean"][1]:.3f}]pt. '
                  f'Leave-one-quarter-out gemiddeld netto: [{min(means):.3f}; {max(means):.3f}]pt. '
                  f'MFE mediaan/P95: {r["mfe"]["median"]:.2f}/{r["mfe"]["p95"]:.2f}pt.', '',
                  '| Weggelaten kwartaal | Overige trades | Netto totaal pt | Gemiddeld netto pt |', '|---|---:|---:|---:|']
        for row in loq:
            lines.append(f'| {row["omitted"]} | {row["days"]} | {row["net_points"]:.3f} | {row["mean_net"]:.3f} |')
    lines += ['', 'Deze weglaatcontroles zijn stresstests. Geen enkele datum of kwartaal wordt op basis hiervan uit toekomstige handelsregels verwijderd.', '',
              '## Kosten en vaste entryvertragingen', '',
              'Hetzelfde vooraf vastgelegde ToM-cohort, entry op09:30/09:31/09:35-open en steeds dezelfde15:59-closeproxy. '
              'Geen gekozen winnaar onder de negen scenario’s. Kosten34,50/44,50USD betekenen1/2 extraNQ-ticks per leg BOVENOP de vaste24,50USD.', '',
              '| Bron | Entryvertraging min | RT kosten USD | Trades | Netto pt | Gem. netto pt | PF | Gesloten DD pt |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
    for source, s in data['samples'].items():
        for r in s['execution_sensitivity']:
            lines.append(f'| {source} | {r["entry_delay_minutes"]} | {r["roundtrip_cost_usd"]:.2f} | {r["days"]} | '
                         f'{r["net_points"]:.3f} | {r["mean_net"]:.3f} | {r["profit_factor"]:.3f} | {r["closed_trade_drawdown"]:.3f} |')
    lines += ['', 'Minuutopens en closes zijn meetankers, geen bewijs van uitvoerbare beursfills. '
              'Geen bid/ask-, queue-, orderlatency- of publicatievintagebewijs. '
              'De vaste kalenderselectie is vóór entry bekend, maar de latere technische volledigheid van een dag is dat niet.', '',
              '## Kwartalen', '',
              '| Bron | Kwartaal | ToM N | ToM netto pt | ToM gem. | Andere N | Andere gem. | Verschil gem. |',
              '|---|---|---:|---:|---:|---:|---:|---:|']
    for source, s in data['samples'].items():
        for r in s['quarters']:
            a, b = r['tom'], r['non_tom']; diff = 'n.v.t.' if r['difference'] is None else f'{r["difference"]:.3f}'
            am = 'n.v.t.' if a['mean_net'] is None else f'{a["mean_net"]:.3f}'
            bm = 'n.v.t.' if b['mean_net'] is None else f'{b["mean_net"]:.3f}'
            lines.append(f'| {source} | {r["quarter"]} | {a["days"]} | {a["net_points"]:.3f} | {am} | {b["days"]} | {bm} | {diff} |')
    p = data['source_parity']
    lines += ['', '## Bronvergelijking', '',
              f'BestaandeNQH24-pilot tegen de generieke reeks: {p["complete_common_days"]} volledige gemeenschappelijkeRTH-dagen. '
              f'RTH-open/closebeweging exact gelijk: {100*p["exact_rth_movement_fraction"]:.1f}%. '
              f'Mediane absolute afwijking {p["median_abs_difference_points"]:.3f}pt, maximum {p["maximum_abs_difference_points"]:.3f}pt. '
              f'Op {p["tom_common_days"]} ToM-dagen samen bedraagt generic minus contract {p["tom_total_difference_points"]:.3f}pt. '
              'Dit certificeert niet de hele oudere keten. De eerdere15,5pt-afwijking op het twee-minutenanker van31januari blijft staan.', '',
              'De493 oudere dagen zijn een afzonderlijke gevoeligheidsbron, geen onafhankelijke validatie. '
              'Geen pooling van vendors, geen tijdverschuivingszoektocht, geen wijziging van bronbytes of rollregels.', '',
              '## Reproductie en beperkingen', '',
              f'Beide oorspronkelijke ToM-ledgers zijn exact op geselecteerde datums, bruto/netto enMFE/MAE gereproduceerd. '
              f'{data["protected_files"]} bestaande bestanden worden opSHA-256 bewaakt. '
              'Nieuwe analyses zijn apart opgeslagen; geen oude rapporten overschreven. '
              'De eindverificatie staat inresearch/month-turn-audit-verification.json. '
              'Publieke exports bevatten alleen afgeleide aggregaten; dagelijkse ledgers en brondata blijven privé. '
              'Er is geen aankoop, download, live order, Git-push of Vercel-publicatie uitgevoerd.', '',
              'Het doel is benchmarkmeerwaarde beoordelen, niet achteraf een winstmodel claimen. '
              'Een publicatie over dagelijkse aandelenrendementen bij maandwissel bewijst geenNQ-RTH-edge of institutionele oorzaak: '
              '[McConnell en Xu](https://docs.lib.purdue.edu/ciberwp/43/). '
              'Herhaald selecteren op dezelfde historie blijft gevoelig voor '
              '[backtestoverfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).', '']
    return '\n'.join(lines)


def run():
    lock = verify(); records = verify_source_register()['records']; samples = {}
    for i, (name, state, included) in enumerate(load_samples()):
        samples[name] = audit_sample(state, included, name, 20261022101+i)
        print('Original ToM replay:', name, samples[name]['replay'], flush=True)
    tests = [s[field] for s in samples.values() for field in ('raw_contrast', 'normalized_contrast')]
    adjusted = holm([r['p_raw'] for r in tests])
    for row, p in zip(tests, adjusted):
        row['p_holm4'] = p
    supported = all(r['difference'] > 0 and r['p_holm4'] < .05 for r in tests)
    result = dict(status='EXPLORATORY_SUPPORT_REQUIRES_INDEPENDENT_TEST' if supported else 'INSUFFICIENT_EVIDENCE_NO_PROMOTION',
                  verdict_text='De oorspronkelijke maandwisselregel blijft netto positief in beide gebruikte bronnen. '
                               + ('Alle vier vaste benchmarkcontrasten krijgen verkennende steun; onafhankelijke bevestiging en uitvoeringsbewijs ontbreken.' if supported else
                                  'De vaste audit levert geen consistente, voor alle vier contrasten gecorrigeerde bevestiging van extra kalendermeerwaarde. '
                                  'Niet promoveren tot bewezen winstmodel. Geen filters toevoegen op basis van deze uitslag.'),
                  protocol_sha256=sha(PROTOCOL), protected_files=len(lock['protected_files']), samples=samples,
                  source_parity=source_parity(records),
                  multiplicity=dict(new_contrasts=4, method='Holm4 exploratory', previous_families_unchanged=True),
                  independent_validation=False, new_candidate_preregistration=False,
                  public_privacy='Aggregate-only; no daily/trade prices, raw arrays or absolute private paths.',
                  dashboard_route='/research/month-turn-audit', external_publication=False)
    verify()
    dump(RESULT, result); dump(PUBLIC, result)
    text = report(result); REPORT.write_text(text)
    (ROOT/'public/reports/MONTH_TURN_AUDIT.md').write_text(text)
    print(result['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['register', 'run', 'verify'])
    args = parser.parse_args()
    {'register':register, 'run':run, 'verify':verify}[args.action]()
