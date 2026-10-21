"""Planning approximations from CONSUMED pre-Oct2025 ledgers only, no backtest."""
import hashlib
import math

import numpy as np
import pandas as pd
from scipy.stats import norm

TRADE_SHA = 'dfe1a19f2452e130fa298ea522ec90ea9ea4dccdd7a7c4b9c45988227ea23d6a'
ELIGIBILITY_SHA = '24ee41ea92413dd71be529dd266a10c8777b713df39f4e23da52ef6d7df1e64e'


def normal_power(n, effect, sigma):
    z = norm.ppf(.975)
    delta = effect*math.sqrt(n)/sigma
    return float(norm.cdf(-z-delta) + norm.sf(z-delta))


def plan(root):
    paths = [root/'artifacts/volume-path-vnext/trades.csv', root/'artifacts/volume-path-vnext/eligibility.csv']
    for path, expected in zip(paths, [TRADE_SHA, ELIGIBILITY_SHA]):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Consumed-input hash mismatch: '+path.name)
        # Check dates BEFORE requesting any PnL column.
        dates = pd.read_csv(path, usecols=['trade_date']).trade_date
        if not dates.between('2024-12-30','2025-09-30').all():
            raise ValueError('Future data prohibited for planning')
    e = pd.read_csv(paths[1], usecols=['strategy','trade_date','eligible'])
    dates = sorted(e.loc[e.strategy.eq('B_ORB15') & e.eligible, 'trade_date'])
    t = pd.read_csv(paths[0], usecols=['strategy','trade_date','net_points'])
    t = t[t.strategy.eq('B_ORB15')]
    x = t.groupby('trade_date').net_points.sum().reindex(dates, fill_value=0).to_numpy()
    if len(x) != 159:
        raise ValueError('Consumed 159-day reference required')
    sd = float(np.std(x, ddof=1))
    centered = x-x.mean()
    # Bartlett/Newey-West diagnostic with FIXED 4 lags (5-session block scale).
    long_var = float(centered@centered/len(x))
    for lag in range(1,5):
        long_var += 2*(1-lag/5)*float(centered[lag:]@centered[:-lag]/len(x))
    hac_sd = math.sqrt(max(0,long_var))
    scenarios = []
    zsum = float(norm.ppf(.975)+norm.ppf(.8))
    # Assumptions fixed before reading ledgers, not fitted thresholds or exits.
    for dependence in [1.,1.5,2.]:
        sigma = sd*math.sqrt(dependence)
        for effect in [2.5,5.,10.,20.]:
            scenarios.append({'variance_inflation':dependence, 'assumed_net_points_per_eligible_day':effect,
                              'approx_days_for_80pct_power':math.ceil((zsum*sigma/effect)**2),
                              'approx_power_52_days':normal_power(52,effect,sigma),
                              'approx_power_200_days':normal_power(200,effect,sigma),
                              'approx_power_240_days':normal_power(240,effect,sigma)})
    return {'classification':'PLANNING_ONLY_CONSUMED_DATA_NORMAL_APPROXIMATION_NOT_OOS_RESULTS',
            'input_sha256':{'trades':TRADE_SHA,'eligibility':ELIGIBILITY_SHA},
            'historical_eligible_days':159, 'daily_sd_points':sd, 'fixed_lag4_HAC_sd_points':hac_sd,
            'alpha_two_sided':.05, 'target_power':.8, 'scenarios':scenarios,
            'limitations':'Not power of the frozen bootstrap + PF + CI joint rule. Normal approximation with historical noise and hypothetical constant effect; serial dependence, tails and regime shifts may worsen calibration. HAC is a noisy descriptive diagnostic, not a fitted planning choice. No future returns read, no required sample-size change, no optional stopping rule, no guarantee one year suffices.'}
