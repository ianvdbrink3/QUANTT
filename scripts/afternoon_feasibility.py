"""Planning calibration only. Never test observed discovery means or new data."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import nct, t

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/afternoon-feasibility'
PROTOCOL = ROOT / 'research/afternoon-feasibility-protocol.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def holm_positive(p, mean):
    """Two parallel two-sided tests; either own positive rejection suffices."""
    order = np.argsort(p, axis=1, kind='stable')
    ranked = np.take_along_axis(p, order, axis=1)
    adjusted = np.maximum.accumulate(ranked * np.array([2., 1.]), axis=1).clip(0, 1)
    unranked = np.empty_like(adjusted)
    np.put_along_axis(unranked, order, adjusted, axis=1)
    return (unranked < .05) & (mean > 0)


def hac_batch(values, mask):
    """values: batch x scheduled day x horizon, zero on unselected days."""
    n = mask.sum(axis=1)
    if np.any(n < 2):
        raise ValueError('Insufficient synthetic selected days')
    means = values.sum(axis=1) / n[:, None]
    scores = (values - mask[:, :, None] * means[:, None, :]) / n[:, None, None]
    meat = np.sum(scores * scores, axis=1)
    for lag in range(1, 6):
        meat += 2 * (1 - lag / 6) * np.sum(scores[:, lag:] * scores[:, :-lag], axis=1)
    se = np.sqrt(np.maximum(0, meat) * (n / (n - 1))[:, None])
    return means, se, n


def power_n(n, delta, sigma):
    critical = t.ppf(1 - .025 / 2, n - 1)
    nc = delta * np.sqrt(n) / sigma
    # Positive support requires a positive statistic; negative rejection is not success.
    return float(nct.sf(critical, n - 1, nc))


def required_n(delta, sigma):
    lo, hi = 2, 4
    while power_n(hi, delta, sigma) < .8:
        hi *= 2
        if hi > 10000000:
            raise ValueError('Unbounded planning size')
    while lo < hi:
        mid = (lo + hi) // 2
        if power_n(mid, delta, sigma) >= .8:
            hi = mid
        else:
            lo = mid + 1
    return lo


def circular_indices(rng, reps, length, original, block=20):
    starts = rng.integers(original, size=(reps, (length + block - 1) // block))
    return ((starts[:, :, None] + np.arange(block)) % original).reshape(reps, -1)[:, :length]


def wilson(n, total):
    p = n / total
    z = 1.959963984540054
    center = (p + z*z/(2*total)) / (1+z*z/total)
    half = z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/(1+z*z/total)
    return [float(center-half), float(center+half)]


def original_calibration():
    from scripts.register_afternoon_candidate_v2 import verify as verify_candidate
    from scripts.afternoon_falsification import verify as verify_falsification
    verify_candidate()
    verify_falsification()
    quality = json.loads((ROOT / 'artifacts/raw-market/quality.json').read_text())
    calendar = [r['day'] for r in quality]
    trans = pd.read_csv(ROOT / 'artifacts/afternoon-falsification/transitions.csv')
    selected = set(trans.loc[trans.at1430.eq('UP'), 'day'])
    assert len(calendar) == 454 and len(selected) == 162
    assert all(next(x for x in quality if x['day'] == day)['included'] for day in selected)
    frame = pd.read_csv(ROOT / 'artifacts/afternoon-falsification/measurements.csv', float_precision='round_trip')
    old = frame[frame.scheme.eq('fixed') & frame.group.eq('UP') & frame.clock.eq('15:00') & frame.part.eq('FULL')].set_index('day')
    assert set(old.index) == selected
    prior = json.loads((ROOT / 'research/holdout-protocol.json').read_text())
    year = json.loads((ROOT / 'research/oos-year-rollovers.json').read_text())
    schedule = [('2024-12-30', 'NQH25'), ('2025-03-19', 'NQM25')]
    schedule += [(r['effective_session'], r['to']) for r in prior['rollovers'] + year['rollovers']]
    sources = json.loads((ROOT / 'research/oos-year-sources.json').read_text())
    paths = {}
    for item in sources['sources'] + sources['warmup_sources']:
        paths[ROOT / item['relative_private_path']] = (item['contract'], item['sha256'])
    observed = {}
    for path, (contract, digest) in paths.items():
        if sha(path) != digest:
            raise ValueError('Registered source changed: ' + path.name)
        with path.open(newline='') as stream:
            for row in csv.DictReader(stream):
                stamp = row['Time']
                # Source Chicago and NY share DST dates; RTH NY15:00 = Chicago14:00.
                if stamp[-5:] not in ('14:00', '14:01', '14:14') or stamp[:10] not in selected:
                    continue
                day = stamp[:10]
                active = next(c for effective, c in reversed(schedule) if effective <= day)
                if contract != active:
                    continue
                key = (day, stamp[-5:])
                value = (float(row['Open']), float(row['Latest']))
                if key in observed and observed[key] != value:
                    raise ValueError('Conflicting original anchors')
                observed[key] = value
    returns = []
    ordered = sorted(selected)
    for day in ordered:
        start = observed[day, '14:00'][0]
        full = observed[day, '14:14'][1] - start
        assert abs(full - (old.loc[day, 'points'] - old.loc[day, 'gap_before'])) < 1e-9
        returns.append([observed[day, '14:01'][1] - start, full])
    x = np.array(returns)
    residuals = x - x.mean(axis=0)  # Do not publish or test the original means.
    positions = {day: i for i, day in enumerate(calendar)}
    mask = np.zeros(len(calendar), dtype=bool)
    values = np.zeros((len(calendar), 2))
    for day, residual in zip(ordered, residuals):
        mask[positions[day]] = True
        values[positions[day]] = residual
    return calendar, quality, selected, mask, values, residuals, len(paths)


def simulate(mask, values, protocol):
    rows = []
    zero_rows = []
    reps = protocol['replications']
    effects = protocol['effects_net_points']
    scenarios = [(d, 0) for d in effects] + [(0, d) for d in effects] + [(d, d) for d in effects]
    for length in protocol['scheduled_sessions']:
        rng = np.random.default_rng(protocol['seed'] + length)
        counts = np.zeros((len(scenarios), 3), dtype=int)
        zero = 0
        zero_any_rejection = 0
        selections = []
        for offset in range(0, reps, 50):
            batch = min(50, reps - offset)
            ix = circular_indices(rng, batch, length, len(mask))
            mean, se, n = hac_batch(values[ix], mask[ix])
            selections.extend(n.tolist())
            for j, delta in enumerate(scenarios + [(0, 0)]):
                shifted = mean + np.array(delta)
                p = 2 * t.sf(np.abs(shifted / np.maximum(se, 1e-15)), n[:, None] - 1)
                supported = holm_positive(p, shifted)
                if j == len(scenarios):
                    zero += np.any(supported, axis=1).sum()
                    zero_any_rejection += np.any(holm_positive(p, np.ones_like(shifted)), axis=1).sum()
                else:
                    counts[j] += [supported[:, 0].sum(), supported[:, 1].sum(), np.any(supported, axis=1).sum()]
        for delta, count in zip(scenarios, counts):
            p = count[2] / reps
            rows.append(dict(scheduled_sessions=length, years_assuming250=length / 250,
                net_effect_2m=delta[0], net_effect_15m=delta[1],
                mean_selected_days=float(np.mean(selections)), p025_selected_days=float(np.quantile(selections, .025)),
                p975_selected_days=float(np.quantile(selections, .975)),
                power_2m=float(count[0] / reps), power_15m=float(count[1] / reps),
                family_positive_power=float(p), monte_carlo_se=float(np.sqrt(p * (1 - p) / reps))))
        zero_rows.append(dict(scheduled_sessions=length, positive_family_false_support=float(zero / reps),
            any_sign_family_rejection=float(zero_any_rejection / reps),
            any_sign_mc_se=float(np.sqrt((zero_any_rejection/reps)*(1-zero_any_rejection/reps)/reps)),
            mc_se=float(np.sqrt((zero / reps) * (1 - zero / reps) / reps))))
        print(f'Planning simulation: {length} scheduled sessions complete', flush=True)
    return rows, zero_rows


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = json.loads(PROTOCOL.read_text())
    calendar, quality, selected, mask, values, residuals, source_count = original_calibration()
    n = int(mask.sum())
    _, se, _ = hac_batch(values[None], mask[None])
    effective = se[0] * np.sqrt(n)
    iid = residuals.std(axis=0, ddof=1)
    rho = float(np.corrcoef(residuals.T)[0, 1])
    rng = np.random.default_rng(protocol['seed'])
    ix = circular_indices(rng, 5000, len(mask), len(mask))
    frequency_ci = np.quantile(mask[ix].mean(axis=1), [.025, .975]).tolist()
    rate = float(mask.mean())
    approximation = []
    for h, sigma in zip((2, 15), effective):
        for delta in protocol['effects_net_points']:
            for multiplier in (1., 1.25, 1.5):
                count = required_n(delta, float(sigma * multiplier))
                approximation.append(dict(horizon_minutes=h, net_effect_points=delta, sigma_multiplier=multiplier,
                    selected_days_for80=count, scheduled_sessions_expected=float(count / rate),
                    years_at250=float(count / rate / 250),
                    years_frequency_interval=[float(count / frequency_ci[1] / 250), float(count / frequency_ci[0] / 250)],
                    positive_power_at_n=power_n(count, delta, float(sigma * multiplier))))
    quarters = []
    for quarter in sorted({str(pd.Period(day, freq='Q')) for day in calendar}):
        days = [day for day in calendar if str(pd.Period(day, freq='Q')) == quarter]
        included = sum(r['included'] for r in quality if r['day'] in days)
        count = len(selected.intersection(days))
        quarters.append(dict(quarter=quarter, scheduled=len(days), complete=included, selected=count,
            rate_scheduled=count / len(days), rate_complete=count / included if included else None))
    simulations, zeros = simulate(mask, values, protocol)
    correlation = dict(paired_outcome_correlation=rho)
    for h, j in ((2, 0), (15, 1)):
        correlation[str(h)] = dict(iid_sigma_points=float(iid[j]), hac5_equivalent_sigma_points=float(effective[j]),
            hac5_to_iid_variance_ratio=float((effective[j] / iid[j]) ** 2),
            calendar_score_autocorrelations=[float(np.corrcoef(values[lag:, j], values[:-lag, j])[0, 1]) for lag in range(1, 6)])
    result = dict(status='FEASIBILITY_ONLY_INDEPENDENT_TEST_NOT_RELEASED', candidate_changed=False,
        observed_mean_tested=False, new_strategy_runs=0, independent_outcomes_read=False,
        scheduled_sessions=len(calendar), complete_RTH_days=sum(q['included'] for q in quality), selected_days=n,
        selection_rate_scheduled=rate, selection_rate_complete=n / 435,
        selection_wilson_iid_ci95=wilson(n, len(calendar)),
        selection_block20_ci95=frequency_ci, selected_per250_expected=250 * rate,
        selected_per250_frequency_interval=[250 * x for x in frequency_ci],
        calibration=correlation, quarters=quarters, approximation=approximation,
        joint_Holm2_simulations=simulations, zero_calibration=zeros,
        method=protocol, source_files_checked=source_count,
        hashes={str(p.relative_to(ROOT)): sha(p) for p in [PROTOCOL, Path(__file__),
            ROOT / 'research/afternoon-candidate-v2.json', ROOT / 'artifacts/afternoon-falsification/measurements.csv',
            ROOT / 'artifacts/afternoon-falsification/transitions.csv', ROOT / 'artifacts/raw-market/quality.json']})
    dump(ROOT / 'research/afternoon-feasibility-results.json', result)
    dump(OUT / 'summary.json', result)
    report(result)


def report(r):
    lines = ['# Haalbaarheid onafhankelijke 15:00-toets', '', '22 oktober 2026. Planning, geen nieuwe backtest of onafhankelijke toets. V2 en alle eerdere rapporten blijven ongewijzigd.', '',
        '## Vrijgavebesluit', '',
        '**Nog niet vrijgeven.** De steekproefgetallen hieronder zijn indicatieve planning, geen gecertificeerde minimumomvang. Naast de nog niet bewezen gratis dataroute toont de nulkalibratie dat de bevroren tweezijdige HAC(5)/t-meetlat in dit empirische blokmodel niet overal de nominale 5% familieverwerpingen haalt. Holm corrigeert multipliciteit maar herstelt geen verkeerd gekalibreerde ruwe p-waarden. De kandidaat of meetlat is niet aangepast; een aparte kalibratiebeoordeling hoort vóór een toekomstige toetsvrijgave.', '',
        '## Steekproef en aannamen', '',
        f"De vaste 14:30 UP-groep telt {r['selected_days']} dagen: {100*r['selection_rate_complete']:.2f}% van 435 complete RTH-dagen en {100*r['selection_rate_scheduled']:.2f}% van 454 geplande sessies. Niet de dynamische 167-dagengroep.",
        f"Bij de planningsaanname van 250 geplande sessies/jaar: gemiddeld {r['selected_per250_expected']:.1f} geselecteerde dagen/jaar. Blokbootstrapband voor de frequentie: {r['selected_per250_frequency_interval'][0]:.1f}–{r['selected_per250_frequency_interval'][1]:.1f}. Dit is een interval voor geschatte frequentie, geen voorspellingsinterval of kalendergarantie. De historische frequentie omvat ook initiële ATR-opwarming en afgekeurde sessies; de toekomstige proef warmt vooraf op. De Wilson-iid-band staat als beschrijvende gevoeligheid in JSON, niet als afhankelijkheidsrobuust alternatief.", '',
        'Alle ontdekkingsgemiddelden zijn vóór simulatie verwijderd. +2/+4/+6 zijn hypothetische NETTO punten na de bestaande 1,225 punten frictie. Geen van deze scenario’s is gekozen als formele minimaal relevante edge. Alleen reeds verbruikte bronankers op bestaande cohortdagen zijn voor variantie gebruikt; geen signalen of uitslagtoets op het ontdekkingsgemiddelde.', '',
        '| Horizon | SD iid pt | HAC(5)-equivalent pt | HAC/iid variantie |', '|---|---:|---:|---:|']
    for h in (2, 15):
        c = r['calibration'][str(h)]
        lines.append(f"| {h}m | {c['iid_sigma_points']:.2f} | {c['hac5_equivalent_sigma_points']:.2f} | {c['hac5_to_iid_variance_ratio']:.3f} |")
    lines += ['', f"Gepaarde correlatie beide horizons: {r['calibration']['paired_outcome_correlation']:.3f}. Kalender-score-autocorrelaties lag 1–5 staan in de JSON. HAC(5) en de indicatornul op niet-geselecteerde dagen volgen v2.", '',
        '## Benodigde geselecteerde dagen voor 80% positieve ondersteuning', '',
        'Noncentral-t-planningsbenadering met tweezijdige alpha 0,025 per horizon. Dit is de strenge eerste Holm-drempel: een voldoende route voor die horizon, niet de exacte gezamenlijke familiesucceskans. HAC-equivalente SD wordt voor toekomstige N constant verondersteld. Jaaromrekening is een verwachting op de totale kalenderfrequentie.', '',
        '| Netto effect pt | 2m: dagen | 2m: jaren | 15m: dagen | 15m: jaren |', '|---|---:|---:|---:|---:|']
    for delta in (2, 4, 6):
        a = [x for x in r['approximation'] if x['net_effect_points'] == delta and x['sigma_multiplier'] == 1]
        lines.append(f"| +{delta} | {a[0]['selected_days_for80']} | {a[0]['years_at250']:.2f} | {a[1]['selected_days_for80']} | {a[1]['years_at250']:.2f} |")
    lines += ['', 'Jaarbandbreedte door onzekerheid in selectiefrequentie alleen (niet door variantie/regime/onbekende edge):', '',
        '| Effect pt | 2m jarenband | 15m jarenband |', '|---|---:|---:|']
    for delta in (2, 4, 6):
        a = [x for x in r['approximation'] if x['net_effect_points'] == delta and x['sigma_multiplier'] == 1]
        band = lambda row: f"{row['years_frequency_interval'][0]:.2f}–{row['years_frequency_interval'][1]:.2f}"
        lines.append(f'| +{delta} | {band(a[0])} | {band(a[1])} |')
    lines += ['', '### Hogere toekomstige spreiding', '', '| Horizon | Effect pt | SD-factor | Benodigde dagen | Jaren |', '|---|---:|---:|---:|---:|']
    for x in r['approximation']:
        if x['sigma_multiplier'] > 1:
            lines.append(f"| {x['horizon_minutes']}m | +{x['net_effect_points']} | {x['sigma_multiplier']} | {x['selected_days_for80']} | {x['years_at250']:.2f} |")
    lines += ['', '## Gezamenlijke Holm2-power', '',
        '5.000 simulaties per vaste kalenderlengte; circulaire blokken van 20 geplande sessies. Gepaarde gecentreerde residuen én selectie/kwaliteit blijven samen. Beide gemiddelden en HAC(5)-SE worden per synthetisch panel opnieuw berekend. Twee tweezijdige p-waarden, exacte Holm2-step-down en positief eigen gemiddelde. Geen inhoudelijke horizon-gate. Een effect op slechts één horizon en een effect op beide worden apart getoond.', '',
        '| Geplande sessies | Verwachte geselecteerd | Effect 2m | Effect 15m | Positief familiesucces % | MC-SE procentpunt |', '|---|---:|---:|---:|---:|---:|']
    for x in r['joint_Holm2_simulations']:
        lines.append(f"| {x['scheduled_sessions']} | {x['mean_selected_days']:.1f} | {x['net_effect_2m']} | {x['net_effect_15m']} | {100*x['family_positive_power']:.2f} | {100*x['monte_carlo_se']:.2f} |")
    lines += ['', '### Nulkalibratie', '', '| Sessies | Onterecht positief familiesucces % | Holm-verwerping enige richting % | MC-SE positief procentpunt |', '|---|---:|---:|---:|']
    for x in r['zero_calibration']:
        lines.append(f"| {x['scheduled_sessions']} | {100*x['positive_family_false_support']:.2f} | {100*x['any_sign_family_rejection']:.2f} | {100*x['mc_se']:.2f} |")
    lines += ['',
        f"**Kalibratiewaarschuwing:** tweezijdige Holm-verwerping in enige richting varieert in dit nulmodel van {100*min(x['any_sign_family_rejection'] for x in r['zero_calibration']):.2f}% tot {100*max(x['any_sign_family_rejection'] for x in r['zero_calibration']):.2f}% in plaats van nominale 5%. Positief familiesucces varieert afzonderlijk van {100*min(x['positive_family_false_support'] for x in r['zero_calibration']):.2f}% tot {100*max(x['positive_family_false_support'] for x in r['zero_calibration']):.2f}%. Negatieve verwerpingen zijn geen positieve kandidaatondersteuning, maar vallen wel onder de tweezijdige FWER-afspraak. Monte-Carlo-SE van alle verwerpingen staat in de JSON. Dit blokmodel is geen universele marktwaarheid; de afwijking is reden voor kalibratieonderzoek, niet bewijs dat de geobserveerde markt-asymmetrie afwezig is. Powerpercentages worden daarom niet als gegarandeerde toetskwaliteit gebruikt.", '',
        '## Selectiefrequentie per kwartaal', '', '| Kwartaal | Gepland | Compleet | Geselecteerd | % gepland |', '|---|---:|---:|---:|---:|']
    for q in r['quarters']:
        lines.append(f"| {q['quarter']} | {q['scheduled']} | {q['complete']} | {q['selected']} | {100*q['rate_scheduled']:.2f} |")
    lines += ['', '2024Q4 is slechts een gedeeltelijk kwartaal. Geen kwartaal is verwijderd of gebruikt om een filter te maken.', '',
        '## Besluit en beperkingen', '',
        'Een klein netto-effect vraagt aanzienlijk meer informatie dan een groot effect. Een kort forwardtraject is geen gegarandeerde bevestiging; zonder uitkomstgestuurd verlengen moet onvoldoende informatie herkenbaar blijven. De steekproefomvang voor een definitieve toets is nog NIET vastgelegd.', '',
        'De berekeningen zijn gevoelig voor slechts 162 geselecteerde ontdekkingsdagen, historische selectie van de kandidaat, regimeverandering, staarten, datakwaliteit en blocklengte. De cirkelverbinding en herhaling van een kort verleden kunnen toekomstige crises niet reconstrueren. De SD-sensitiviteiten zijn scenario’s, geen betrouwbaarheidsgrenzen. Geen tick-/bid-ask-/latencybewijs of echte fillvalidatie. +2/+4/+6 punten betreffen het ongewijzigde kostenmodel, niet gegarandeerde uitvoerbaarheid.', '',
        '## Reproductie en bronnen', '',
        '`python -m scripts.afternoon_feasibility` schrijft uitsluitend nieuwe planningsoutputs; geen bestaande rapporten of bronbestanden. Seed, protocol, hashes en alle scenario’s staan in `research/afternoon-feasibility-results.json`. De bronankers zijn niet openbaar geëxporteerd.', '',
        '- [SciPy noncentral-t documentatie](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html).',
        '- [Holm (1979), oorspronkelijke procedure](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf).', '']
    (ROOT / 'docs/AFTERNOON_VALIDATION_FEASIBILITY.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    run()
