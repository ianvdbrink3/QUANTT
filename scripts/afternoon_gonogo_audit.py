"""Second numerical audit, not an external reviewer and not a backtest."""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'research/afternoon-gonogo-audit-protocol.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def matrix_hac(values, mask):
    n = int(mask.sum())
    mean = values.sum(axis=0) / n
    score = (values - mask[:, None]*mean) / n
    distance = np.abs(np.arange(len(mask))[:, None] - np.arange(len(mask))[None, :])
    kernel = np.maximum(0., 1-distance/6)
    cov = score.T @ kernel @ score * n/(n-1)
    return mean, np.sqrt(np.maximum(np.diag(cov), 0)), cov


def estimate(panel, included):
    count = np.count_nonzero(included, axis=1)
    if np.any(count < 2):
        raise ValueError('Insufficient synthetic information')
    avg = np.sum(panel, axis=1) / count[:, None]
    influence = (panel-included[:, :, None]*avg[:, None, :]) / count[:, None, None]
    variance = np.einsum('bdh,bdh->bh', influence, influence)
    for k in range(1, 6):
        variance += ((6-k)/3)*np.einsum('bdh,bdh->bh', influence[:, k:], influence[:, :-k])
    variance *= (count/(count-1))[:, None]
    return avg, np.sqrt(np.maximum(variance, 0)), count


def reject(p):
    # A horizon is first-ranked when its p is the smaller of the pair.
    # The other horizon is rejected only after first-ranked rejection.
    p = np.asarray(p, dtype=float)
    if p.ndim != 2 or p.shape[1] != 2:
        raise ValueError('Exactly two parallel hypotheses required')
    p = np.where(np.isnan(p), 1., p)
    if np.any((p < 0) | (p > 1)):
        raise ValueError('Invalid p-values')
    first = np.minimum(p[:, 0], p[:, 1]) < .025
    both = first & (np.maximum(p[:, 0], p[:, 1]) < .05)
    return np.column_stack([first & ((p[:, 0] <= p[:, 1]) | both),
                            first & ((p[:, 1] <= p[:, 0]) | both)])


def null_panel(rng, model, batch, length, mask, values, sigma, rho):
    if model.startswith('EMPIRICAL'):
        block = 20 if 'BLOCK20' in model else (5 if 'BLOCK5' in model else 1)
        blocks = (length+block-1)//block
        starts = rng.integers(len(mask), size=(batch, blocks))
        indexes = ((starts[:, :, None]+np.arange(block)) % len(mask)).reshape(batch, -1)[:, :length]
        panel, included = values[indexes], mask[indexes]
        if model.endswith('SYMMETRIC'):
            signs = rng.choice([-1., 1.], size=(batch, blocks))
            signs = np.repeat(signs, block, axis=1)[:, :length]
            panel = panel*signs[:, :, None]
        return panel, included
    included = rng.random((batch, length)) < mask.mean()
    if model == 'STUDENT_T5_IID':
        a = rng.standard_t(5, size=(batch, length, 2))*np.sqrt(3/5)
    else:
        a = rng.normal(size=(batch, length, 2))
        if model == 'NEGATIVE_SKEW_IID':
            a = (a+6*(.02-rng.binomial(1, .02, size=a.shape)))/np.sqrt(1+36*.02*.98)
    a[:, :, 1] = rho*a[:, :, 0] + np.sqrt(1-rho*rho)*a[:, :, 1]
    return a*sigma*included[:, :, None], included


def summarize_events(events, reps):
    k = int(np.count_nonzero(events))
    p = k/reps
    z = 1.959963984540054
    center = (p+z*z/(2*reps))/(1+z*z/reps)
    radius = z*np.sqrt(p*(1-p)/reps+z*z/(4*reps*reps))/(1+z*z/reps)
    return dict(count=k, rate=p, mc_ci95=[float(center-radius), float(center+radius)])


def block_variance(values, block=20):
    centered = values-values.mean(axis=0)
    covariance = [np.mean(centered*np.roll(centered, k, axis=0), axis=0) for k in range(block)]
    true = covariance[0].copy()
    estimated = covariance[0].copy()
    for k in range(1, block):
        true += 2*(1-k/block)*covariance[k]
        if k < 6:
            estimated += 2*(1-k/block)*(1-k/6)*covariance[k]
    return dict(block=block, model_long_run_coefficient=true.tolist(),
        expected_population_HAC5_coefficient=estimated.tolist(),
        true_to_HAC5_variance_ratio=(true/estimated).tolist(),
        lag0_to19_circular_covariances=[x.tolist() for x in covariance])


def quote_net(entry_ask, exit_bid, remaining_adverse_points=0., commission_usd=4.5):
    """Bid/ask crossing is already in quotes. Never subtract frozen friction twice."""
    if remaining_adverse_points < 0 or commission_usd < 0:
        raise ValueError('Invalid additional cost')
    return exit_bid-entry_ask-remaining_adverse_points-commission_usd/20


def simulate(protocol, mask, values):
    sigma = values[mask].std(axis=0, ddof=1)
    rho = float(np.corrcoef(values[mask].T)[0, 1])
    rows = []
    partial = []
    reps = protocol['replications']
    for m, model in enumerate(protocol['models']):
        for length in protocol['lengths']:
            rng = np.random.default_rng(protocol['seed']+m*10000+length)
            all_rej = []
            all_sign = []
            all_mean = []
            all_se = []
            all_counts = []
            for off in range(0, reps, 100):
                panel, included = null_panel(rng, model, min(100, reps-off), length, mask, values, sigma, rho)
                mean, se, n = estimate(panel, included)
                all_mean.append(mean); all_se.append(se); all_counts.append(n)
                p = 2*t.sf(np.abs(mean/np.maximum(se, 1e-15)), n[:, None]-1)
                all_rej.append(reject(p)); all_sign.append(mean > 0)
            rejected, positive = np.concatenate(all_rej), np.concatenate(all_sign)
            mean, se, n = np.concatenate(all_mean), np.concatenate(all_se), np.concatenate(all_counts)
            rows.append(dict(model=model, scheduled_sessions=length, repetitions=reps, mean_selected=float(n.mean()),
                any_sign_FWER=summarize_events(rejected.any(axis=1), reps),
                positive_family=summarize_events((rejected & positive).any(axis=1), reps),
                negative_family=summarize_events((rejected & ~positive).any(axis=1), reps),
                empirical_mean_estimator_variance=np.var(mean, axis=0, ddof=1).tolist(),
                mean_estimated_variance=np.mean(se*se, axis=0).tolist(),
                observed_to_estimated_variance=(np.var(mean, axis=0, ddof=1)/np.mean(se*se, axis=0)).tolist()))
            for affected in (0, 1):
                shifted = mean.copy(); shifted[:, affected] += 4
                p = 2*t.sf(np.abs(shifted/np.maximum(se, 1e-15)), n[:, None]-1)
                r = reject(p); null = 1-affected
                partial.append(dict(model=model, scheduled_sessions=length, nonzero_horizon_minutes=[2,15][affected],
                    null_horizon_minutes=[2,15][null],
                    null_any_sign_rejection=summarize_events(r[:, null], reps),
                    null_positive_support=summarize_events(r[:, null] & (shifted[:, null] > 0), reps)))
            print(f'Null audit: {model} {length} complete', flush=True)
    return rows, partial


def run():
    from scripts.afternoon_feasibility import original_calibration, hac_batch
    from scripts.afternoon_specificity import uncertainty
    protocol = json.loads(PROTOCOL.read_text())
    _, _, _, mask, values, _, sources = original_calibration()
    mean, independent_se, covariance = matrix_hac(values, mask)
    _, batch_se, _ = hac_batch(values[None], mask[None])
    n = int(mask.sum())
    scalar = [uncertainty(0., (values[:, h]-mask*mean[h])/n, n, n-1)['se_HAC5'] for h in (0,1)]
    assert np.allclose(independent_se, batch_se[0], rtol=0, atol=1e-12)
    assert np.allclose(independent_se, scalar, rtol=0, atol=1e-12)
    rows, partial = simulate(protocol, mask, values)
    result = dict(status='AUDIT_COMPLETED_INDEPENDENT_TEST_NOT_RELEASED',
        implementation_check=dict(matrix_vs_frozen_scalar_and_vectorized=True, atol=1e-12,
            se_points=independent_se.tolist(), covariance=covariance.tolist(), source_files=sources),
        independence_limit='Second matrix formulation and separate simulator by same assistant, not an external reviewer or independent data validation.',
        null_models=rows, partial_null_models=partial, block20_variance_diagnostic=block_variance(values),
        costs=dict(frozen_points=1.225, assumed_execution_points=1., commission_points=.225,
            commission_usd=4.5, raw_quote_data_present=False,
            quote_net_rule='exit_bid - entry_ask - separately measured adverse costs not in quotes - .225pt commission',
            empirical_execution_verified=False),
        v2_changed=False, new_strategy_runs=0, observed_discovery_mean_tested=False,
        protocol=protocol, hashes={str(p.relative_to(ROOT)):digest(p) for p in [PROTOCOL, Path(__file__), ROOT/'research/afternoon-candidate-v2.json']})
    path = ROOT/'research/afternoon-gonogo-audit-results.json'
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result['block20_variance_diagnostic']['true_to_HAC5_variance_ratio']))


if __name__ == '__main__':
    run()
