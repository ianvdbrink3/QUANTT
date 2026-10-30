"""Pure intentions; no broker, network or LLM discretion."""
from decimal import Decimal
import pandas as pd
from .regime import classify,sleeve_targets,WEIGHTS


def advise(qqq_close,qqq_features,tqqq_close,tqqq_features,profile,healthy=True):
    state=classify(qqq_close,qqq_features,healthy)
    own_tqqq=bool(pd.notna(tqqq_features['SMA200']) and tqqq_close>tqqq_features['SMA200'])
    targets=sleeve_targets(state,own_tqqq,pd.notna(qqq_features['HIGH_VOL']))
    w=WEIGHTS[profile]
    return dict(state=state.name,state_code=state.value,
        core_weight=str(Decimal(str(w[0]))*Decimal(str(targets[0]))),
        trend_weight=str(Decimal(str(w[1]))*Decimal(str(targets[1]))),
        s1_signal=bool(qqq_features['S1']) and state.value==2,
        s1_execution='BLOCKED_UNVERIFIED_EXTENDED_PROTECTION_AND_NL_ROUTE',s2_execution='DISABLED',
        distance_sma200_pct=float(100*(qqq_close/qqq_features['SMA200']-1)) if pd.notna(qqq_features['SMA200']) else None)
