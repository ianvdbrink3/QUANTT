"""Read PRIVATE compact ledgers. Never used or shipped by the public site."""
import gzip
import json
import numpy as np
from .__main__ import OUTCOME_DTYPE


def read(path):
    with gzip.open(path,'rb') as f:
        if f.readline()!=b'QUANT_CHALLENGE_V1\n':raise ValueError('Unknown outcome format')
        while True:
            line=f.readline()
            if not line:return
            header=json.loads(line)
            count=header[-1]
            payload=f.read(count*OUTCOME_DTYPE.itemsize)
            if len(payload)!=count*OUTCOME_DTYPE.itemsize:raise ValueError('Truncated outcome ledger')
            yield header,np.frombuffer(payload,dtype=OUTCOME_DTYPE).copy()
