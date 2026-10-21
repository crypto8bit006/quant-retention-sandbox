"""Quant Retention Sandbox: a retention and offer-economics dashboard.

Runs on synthetic data only (see generate_data.py). Start with:
    streamlit run app.py
"""
from math import sqrt

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Quant Retention Sandbox", layout="wide")


@st.cache_data
def load(path="data/sandbox_accounts.csv"):
    return pd.read_csv(path)


df = load()
fams = sorted(df.plan_family.unique())
pick = st.sidebar.multiselect("Plan family", fams, default=fams)
df = df[df.plan_family.isin(pick)]
st.sidebar.caption("Synthetic data. No real customers, company or revenue.")

st.title("Quant Retention Sandbox")
st.caption("Where does retention leak, what does an offer really cost, and how long does a test need to run?")

cust = df.groupby("customer_id").agg(purchases=("purchase_seq", "count"), revenue=("list_fee", "sum"))
cust["repeat"] = cust.purchases >= 2
first_fail = df[df.failure_no == 1]
ret_first = first_fail.returned.mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Customers", f"{len(cust):,}")
k2.metric("Buy more than once", f"{cust.repeat.mean():.0%}")
k3.metric("Revenue from repeat buyers", f"{cust.loc[cust.repeat, 'revenue'].sum() / cust.revenue.sum():.0%}")
k4.metric("Buy again after 1st failure", f"{ret_first:.0%}")

t1, t2, t3, t4, t5 = st.tabs(["Revenue concentration", "Where it leaks", "Offer simulator", "Pilot sizing", "Watchlist demo"])

with t1:
    bins = pd.cut(cust.purchases, [0, 1, 2, 3, 4, 9, 999], labels=["1", "2", "3", "4", "5-9", "10+"])
    g = cust.groupby(bins, observed=False).agg(customers=("purchases", "size"), revenue=("revenue", "sum"))
    g["% of customers"] = g.customers / g.customers.sum() * 100
    g["% of revenue"] = g.revenue / g.revenue.sum() * 100
    st.subheader("Share of customers and revenue by number of purchases")
    st.bar_chart(g[["% of customers", "% of revenue"]])
    st.dataframe(g.round(1), use_container_width=True)

with t2:
    a, b = st.columns(2)
    with a:
        st.subheader("Buy again, by failure number")
        r = df[df.failure_no.between(1, 4)].groupby("failure_no").returned.mean() * 100
        r.index = [f"Failure {i}" for i in r.index]
        st.bar_chart(r.rename("% who buy again"))
    with b:
        st.subheader("First failure: by reason")
        r2 = first_fail.groupby("fail_reason").returned.agg(["mean", "size"])
        r2["mean"] *= 100
        st.bar_chart(r2["mean"].rename("% who buy again"))
        st.dataframe(r2.rename(columns={"mean": "% buy again", "size": "first failures"}).round(1), use_container_width=True)
    st.subheader("First failure: by plan size")
    r3 = first_fail.groupby(["plan_family", "plan_size"]).returned.mean().mul(100).unstack(0)
    st.line_chart(r3)

with t3:
    st.subheader("Does an offer pay back?")
    c1, c2, c3 = st.columns(3)
    lift = c1.slider("Assumed lift in return rate (points)", 0.0, 10.0, 3.0, 0.5) / 100
    disc = c2.slider("Offer discount (%)", 0, 30, 15) / 100
    months = c3.number_input("Months of data covered", 1, 24, 9)
    fee = df.list_fee.mean()
    segs = {
        "All first failures": first_fail,
        "Quiet churners (inactivity)": first_fail[first_fail.fail_reason == "Inactivity"],
        "Fast failers (2 days or less)": first_fail[first_fail.days_to_fail <= 2],
        "Large plans ($50K or more)": first_fail[first_fail.plan_size >= 50000],
    }
    out = []
    for name, s in segs.items():
        if len(s) == 0:
            continue
        f, base = len(s) / months, s.returned.mean()
        be = base * disc / (1 - disc)
        net = 12 * f * fee * (lift * (1 - disc) - base * disc)
        out.append({"Segment": name, "Failures / month": round(f), "Baseline return": f"{base:.1%}",
                    "Break-even lift (pts)": round(be * 100, 1), "Net / year (USD)": round(net),
                    "Verdict": "Pays back" if net > 0 else "Loses money"})
    st.dataframe(pd.DataFrame(out), use_container_width=True, hide_index=True)
    st.caption("Net = failures x average fee x (lift x (1 - discount) - baseline x discount). Everyone who would "
               "have returned anyway also gets the discount. Lift is an assumption the pilot should measure.")

with t4:
    st.subheader("How long to prove it?")
    d1, d2 = st.columns(2)
    base14 = d1.slider("Baseline 14-day return rate", 0.05, 0.40, 0.15, 0.01)
    weekly = d2.number_input("Eligible first failures per week", 20, 5000, max(20, round(len(first_fail) / (months * 4.33))))
    z = 1.959964 + 0.841621  # 5% two-sided significance, 80% power
    rows = [{"Weeks": w, "Per arm": round(weekly * w / 2),
             "Smallest detectable lift (pts)": round(100 * z * sqrt(2 * base14 * (1 - base14) / (weekly * w / 2)), 1)}
            for w in range(1, 9)]
    st.line_chart(pd.DataFrame(rows).set_index("Weeks")["Smallest detectable lift (pts)"])
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with t5:
    st.subheader("Win-back queue (demo scoring)")
    st.caption("A transparent rule score, not a trained model. Replace with your own propensity model.")
    last = df.sort_values("purchase_seq").groupby("customer_id").tail(1)
    q = last[(last.outcome == "Failed") & (last.returned == 0)].copy()
    q["score"] = (0.40 * (q.fail_reason == "Drawdown_Max") + 0.25 * (q.fail_reason == "Drawdown_Daily")
                  + 0.10 * q.competition_history + 0.04 * (q.plan_size >= 50000) + 0.05 * q.failure_no.clip(upper=4))
    q["tier"] = pd.cut(q.score, [-1, 0.15, 0.40, 9], labels=["A: at risk", "B: uncertain", "C: likely back"])
    q["value_at_risk"] = (1 - q.score.clip(upper=0.9)) * q.list_fee
    st.dataframe(q.sort_values("value_at_risk", ascending=False)[["customer_id", "plan_family", "plan_size", "fail_reason",
                 "failure_no", "score", "tier", "value_at_risk"]].head(200).round(2), use_container_width=True, hide_index=True)
