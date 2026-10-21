# Quant Retention Sandbox

An interactive dashboard for one question: **where does customer retention leak, and what would it take to win customers back profitably?**

It shows revenue concentration, return rates by failure number, reason and plan size, an offer simulator with break-even lift, test-length sizing, and a demo win-back queue.

> **All data here is synthetic.** `generate_data.py` creates it from invented parameters. It is not derived from any real company, customer or export, and the figures say nothing about any real business.

## Run it

```bash
pip install -r requirements.txt
python generate_data.py      # optional, regenerates data/sandbox_accounts.csv
streamlit run app.py
```

## What is in the repo

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `generate_data.py` | Synthetic account-level data generator |
| `SPEC_WINBACK_AUTOMATION.md` | Feature spec for an automated win-back program |
| `scrub_check.py` | Guard that blocks commits containing your private terms, emails or phone numbers |

## The offer maths

Net revenue change per year = failures per month x average fee x 12 x (lift x (1 - discount) - baseline return x discount).
Everyone who would have returned anyway also receives the discount, so the break-even lift is baseline x discount / (1 - discount). Lift is an assumption to be measured in an experiment, not a result.

## Using this with real data

Do not commit real exports. Keep them outside the repo, and only point the app at them locally with permission from the data owner.
