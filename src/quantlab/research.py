"""Descriptive statistics and fixed, causal research screens; no edge claims."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from quantlab.data import aggregate, contiguous_returns


def block_inference(values, seed=20250319, samples=2000, block=5):
    """Circular moving-block bootstrap in trading-day order, two-sided null test."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 20:
        return {'ci_low': None, 'ci_high': None, 'p_value': None, 'block_days': block}
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(x), size=(samples, int(np.ceil(len(x) / block))))
    indices = ((starts[..., None] + np.arange(block)) % len(x)).reshape(samples, -1)[:, :len(x)]
    means = x[indices].mean(axis=1)
    low, high = np.quantile(means, [.025, .975])
    centered = means - x.mean()
    p = (1 + (np.abs(centered) >= abs(x.mean())).sum()) / (samples + 1)
    return {'ci_low': float(low), 'ci_high': float(high), 'p_value': float(p), 'block_days': block}


def benjamini_hochberg(p_values):
    p = np.array([1 if x is None else x for x in p_values], dtype=float)
    order = np.argsort(p)
    adjusted = np.minimum.accumulate((p[order] * len(p) / np.arange(1, len(p) + 1))[::-1])[::-1]
    out = np.empty(len(p))
    out[order] = np.minimum(1, adjusted)
    return out.tolist()


def autocorrelation(r, lag, minutes=1, absolute=False):
    x = r.abs() if absolute else r
    t = r.index.to_series()
    valid = (t - t.shift(lag)).eq(pd.Timedelta(minutes=lag * minutes))
    # For log returns every underlying return must be valid, including inside a lag.
    valid &= r.notna().rolling(lag + 1).sum().eq(lag + 1)
    return float(x[valid].corr(x.shift(lag)[valid])) if valid.sum() > 10 else None


def describe(frame, session_config):
    r = contiguous_returns(frame)
    profiles = {}
    for zone in ['UTC', 'America/New_York']:
        f = pd.DataFrame({'hour': frame.index.tz_convert(zone).hour, 'return_bps': r * 10000,
                          'range_points': frame.high - frame.low, 'activity': frame.volume})
        grouped = f.groupby('hour').agg(bars=('range_points', 'size'), mean_return_bps=('return_bps', 'mean'),
            volatility_bps=('return_bps', 'std'), mean_range_points=('range_points', 'mean'),
            mean_activity=('activity', 'mean'))
        profiles[zone] = grouped.reset_index().to_dict('records')
    sessions = []
    for spec in session_config['sessions']:
        local = frame.index.tz_convert(spec['timezone'])
        clock = local.strftime('%H:%M')
        start, end = spec['start'], spec['end']
        mask = ((clock >= start) & (clock < end)) if start < end else ((clock >= start) | (clock < end))
        selected = frame.loc[mask]
        returns = r.loc[mask].dropna()
        sessions.append({**spec, 'bars': len(selected), 'days': int(pd.Index(local[mask].date).nunique()),
                         'mean_return_bps': returns.mean()*10000, 'volatility_bps': returns.std()*10000,
                         'mean_range_points': (selected.high-selected.low).mean(),
                         'mean_activity': selected.volume.mean()})
    distributions = []
    acf = []
    for minutes, rule in [(1, '1min'), (5, '5min'), (15, '15min'), (60, '1h')]:
        bars = aggregate(frame, rule)
        # Require complete bars both sides and exact elapsed time; never forward fill.
        complete = bars.minute_count.eq(minutes)
        rr = contiguous_returns(bars, minutes).where(complete & complete.shift(fill_value=False)).dropna()
        if rr.empty:
            continue
        bps = rr.to_numpy()*10000
        # Display central 99%; explicitly disclose excluded tails and retain quantiles.
        limits = np.quantile(bps, [.005, .995])
        counts, edges = np.histogram(bps, bins=50, range=tuple(limits))
        distributions.append({'timeframe': rule, 'n': len(rr), 'mean_bps': bps.mean(), 'std_bps': bps.std(ddof=1),
            'skewness': stats.skew(bps, bias=False), 'excess_kurtosis': stats.kurtosis(bps, bias=False),
            'tail_3sigma_fraction': float((np.abs(bps-bps.mean()) > 3*bps.std()).mean()),
            'q01_bps': np.quantile(bps, .01), 'q99_bps': np.quantile(bps, .99),
            'histogram_tail_count': int(len(bps)-counts.sum()),
            'histogram': [{'return_bps': (edges[i]+edges[i+1])/2, 'count': int(c)} for i,c in enumerate(counts)]})
    for lag in range(1, 31):
        acf.append({'lag': lag, 'return_acf': autocorrelation(r, lag), 'absolute_return_acf': autocorrelation(r, lag, absolute=True)})
    daily_rv = r.groupby(frame.index.date).std().dropna()*10000
    prior = daily_rv.shift(1)
    threshold = prior.expanding(min_periods=20).median()
    regimes = [{'date': str(d), 'prior_day_volatility_bps': float(prior.loc[d]),
                'regime': 'high' if prior.loc[d] > threshold.loc[d] else 'low'}
               for d in prior.index if pd.notna(prior.loc[d]) and pd.notna(threshold.loc[d])]
    return {'hourly': profiles, 'sessions': sessions, 'distributions': distributions, 'autocorrelation': acf,
            'regimes': regimes, 'regime_rule': 'Previous UTC day volatility vs expanding median of prior days; 20-day warmup',
            'method': 'Log close returns; exact elapsed-time masks; full M1 coverage required for multi-minute distribution bars.'}


def hypothesis_trades(frame, hypothesis):
    """Entry at the next known open; final close in a complete, fixed horizon."""
    local = frame.index.tz_convert(hypothesis['timezone'])
    entries = frame.index[local.strftime('%H:%M') == hypothesis['entry']]
    horizon = hypothesis['horizon_minutes']
    trades = []
    for entry in entries:
        exit_time = entry + pd.Timedelta(minutes=horizon - 1)
        window = frame.loc[entry:exit_time]
        if len(window) != horizon or window.index[-1] != exit_time:
            continue
        direction = 1
        if hypothesis['direction'] == 'reverse_prior_hour':
            prior = frame.loc[entry-pd.Timedelta(hours=1):entry-pd.Timedelta(minutes=1)]
            if len(prior) != 60:
                continue
            change = prior.close.iloc[-1] - prior.open.iloc[0]
            if change == 0:
                continue
            direction = -int(np.sign(change))
        opening = float(window.open.iloc[0])
        gross = direction * (window.close.iloc[-1]-opening)
        trades.append({'entry': entry.isoformat(), 'date': str(entry.tz_convert(hypothesis['timezone']).date()),
                       'entry_price': opening, 'direction': direction, 'gross_points': float(gross),
                       'gross_bps': float(gross/opening*10000)})
    return pd.DataFrame(trades)


def metrics(trades, costs):
    if trades.empty:
        return {'trades': 0, 'days': 0, 'status': 'REQUIRES_MORE_DATA'}
    x = trades.gross_points - costs
    bps = x / trades.entry_price * 10000
    equity = np.r_[0, x.cumsum().to_numpy()]
    dd = equity - np.maximum.accumulate(equity)
    gains, losses = x[x>0].sum(), -x[x<0].sum()
    sd = bps.std(ddof=1)
    return {'trades': len(x), 'days': int(trades.date.nunique()), 'net_points': float(x.sum()),
        'mean_net_points': float(x.mean()), 'mean_net_bps': float(bps.mean()), 'win_rate': float((x>0).mean()),
        'sharpe_daily_trade': float(bps.mean()/sd*np.sqrt(252)) if sd > 0 else None,
        'max_drawdown_points': float(max(0, -dd.min())), 'profit_factor': float(gains/losses) if losses > 0 else None,
        **block_inference(x)}


def evaluate(frame, hypotheses, costs, data_version, config_version):
    results = []
    for spec in hypotheses['hypotheses']:
        trades = hypothesis_trades(frame, spec)
        scenarios = {name: c['spread_points']+2*c['slippage_per_side_points']+c['commission_round_trip_points']
                     for name, c in costs.items()}
        n = len(trades)
        a, b = int(n*.6), int(n*.8)
        base = metrics(trades, scenarios['base'])
        splits = {name: metrics(t, scenarios['base']) for name, t in [
            ('discovery', trades.iloc[:a]), ('validation', trades.iloc[a:b]), ('holdout', trades.iloc[b:]) ]}
        for name, t in [('discovery',trades.iloc[:a]),('validation',trades.iloc[a:b]),('holdout',trades.iloc[b:])]:
            splits[name]['start'] = t.date.iloc[0] if len(t) else None
            splits[name]['end'] = t.date.iloc[-1] if len(t) else None
        yearly = {str(year): metrics(t, scenarios['base']) for year,t in trades.groupby(trades.date.str[:4])} if n else {}
        result = {**spec, 'data_version': data_version, 'config_version': config_version, 'metrics': base,
            'splits': splits, 'yearly': yearly,
            'cost_scenarios': {name: {'round_trip_points': cost, **metrics(trades, cost)} for name,cost in scenarios.items()},
            'status': 'SCREENED' if n >= 100 else 'REQUIRES_MORE_DATA',
            'baseline': 'Zero net points; one fixed, non-overlapping intraday trade per available day',
            'limitations': 'Descriptive fixed screens. Costs are scenarios; no ASK quotes, broker fills, execution validation or independent replication. Holdout opened once; no tuning allowed on these results.',
            'equity': [{'date': d, 'net_points': float(v)} for d,v in zip(trades.date, (trades.gross_points-scenarios['base']).cumsum())] if n else []}
        results.append(result)
    adjusted = benjamini_hochberg([r['metrics'].get('p_value') for r in results])
    for result,q in zip(results,adjusted):
        result['q_value'] = q
        result['significant_fdr_005'] = q < .05
        result['run_id'] = hashlib.sha256(f"{result['id']}:{data_version}:{config_version}:v1".encode()).hexdigest()[:20]
    return results


def append_registry(path: Path, results, timestamp):
    existing = {json.loads(line)['run_id'] for line in path.read_text().splitlines() if line} if path.exists() else set()
    with path.open('a') as handle:
        for result in results:
            if result['run_id'] not in existing:
                row = {k:v for k,v in result.items() if k != 'equity'}
                row['created_at_utc'] = timestamp
                handle.write(json.dumps(row, allow_nan=False) + '\n')
