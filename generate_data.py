"""Generate a fully synthetic account-level dataset for the dashboard.

Nothing here is derived from any real company, customer or export. All
parameters are invented, round numbers chosen for demonstration only.
Run:  python generate_data.py  ->  data/sandbox_accounts.csv
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
N_CUSTOMERS = 6000

PLANS = {  # family: (sizes, fees, node, pass probability)
    "Plan_A": ([5000, 10000, 25000, 50000], [60, 100, 200, 350], "Node_Alpha", 0.10),
    "Plan_B": ([10000, 25000, 50000, 100000], [40, 50, 100, 200], "Node_Beta", 0.16),
    "Plan_C": ([5000, 10000, 25000, 100000], [100, 180, 320, 900], "Node_Gamma", 0.35),
}
REASONS = ["Drawdown_Daily", "Drawdown_Max", "Inactivity"]
REASON_P = [0.45, 0.42, 0.13]
RETURN_P = {"Drawdown_Daily": 0.26, "Drawdown_Max": 0.40, "Inactivity": 0.09}
BOOST = {1: 0.0, 2: 0.18, 3: 0.27, 4: 0.33}  # return propensity rises with each failure


def days_to_fail(reason):
    if reason == "Inactivity":
        return int(rng.integers(25, 45))
    return int(min(60, rng.exponential(5) + 1))


rows = []
for c in range(1, N_CUSTOMERS + 1):
    cid = f"U{c:06d}"
    comp = int(rng.random() < 0.14)
    month0 = int(rng.integers(0, 9))
    seq, fno = 0, 0
    while True:
        seq += 1
        fam = rng.choice(list(PLANS), p=[0.35, 0.45, 0.20])
        sizes, fees, node, p_pass = PLANS[fam]
        k = int(rng.choice(len(sizes), p=[0.35, 0.30, 0.20, 0.15]))
        passed = rng.random() < p_pass
        row = dict(customer_id=cid, purchase_seq=seq, plan_family=fam, plan_size=sizes[k],
                   list_fee=fees[k], execution_node=node, competition_history=comp,
                   purchase_month=f"2026-{min(12, month0 + seq):02d}")
        if passed:
            row.update(outcome="Passed", fail_reason="", days_to_fail=np.nan, failure_no=0)
            ret = rng.random() < 0.6
        else:
            fno += 1
            r = str(rng.choice(REASONS, p=REASON_P))
            p = RETURN_P[r] + BOOST.get(fno, 0.4) + (0.10 if comp else 0) + 0.04 * (sizes[k] >= 50000)
            row.update(outcome="Failed", fail_reason=r, days_to_fail=days_to_fail(r), failure_no=fno)
            ret = rng.random() < min(0.92, p)
        row["returned"] = int(ret)
        rows.append(row)
        if not ret or seq >= 25:
            break

df = pd.DataFrame(rows)
df.to_csv("data/sandbox_accounts.csv", index=False)
print(f"{len(df):,} purchases, {df.customer_id.nunique():,} customers")
