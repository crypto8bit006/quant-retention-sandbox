# Feature Spec: Win-Back Automation

Status: draft for discussion. Data in the reference dashboard is synthetic.

## 1. Problem
Most customers whose first paid plan fails do not buy again. Repeat buyers carry most revenue, so the first failure is the highest-leverage leak. Today every failed customer gets the same experience, whatever their chance of returning.

## 2. Goals
- Raise the share of first-failure customers who buy a new plan within 14 days.
- Spend incentives only where they change behaviour, never on customers who would return anyway.
- Give support a ranked queue so outreach goes to the highest value at risk first.

Non-goals: changing plan rules or pricing; automated discounts without a measured positive net result.

## 3. Segmentation
A return-propensity score from facts known at the moment of failure (failure reason, speed of failure, plan family and size, failure count, competition history, other plans held).

| Tier | P(return) | Play |
|---|---|---|
| A: at risk | below 0.15 | Personal outreach within 48 hours, failure review, conditional retry offer |
| B: uncertain | 0.15 to 0.40 | Education nudge and retry reminder, no discount |
| C: likely back | above 0.40 | No extra contact |

Cut-offs are inputs and should be recalibrated on real data.

## 4. Triggers and flow
1. Failure event received.
2. Score computed, tier assigned, customer added to the queue with value at risk.
3. Tier play executes (task for support, templated message, or none).
4. Outcome logged at 14 days: bought a new plan or not.

## 5. Experiment design
- Population: first and second paid-plan failures.
- Assignment: 50/50 random split into business as usual and treatment, at customer level.
- Primary metric: new paid plan within 14 days.
- Guardrails: incentive cost per extra returning customer, support load, complaint rate.
- Sizing: use the Pilot sizing tab. Two weeks is a signal test, four weeks supports a decision. Break-even lift = baseline x discount / (1 - discount).
- Success: measured lift above break-even for the targeted segment and positive net revenue after incentives.

## 6. Data requirements
| Data | Why |
|---|---|
| Failure events with reason and timestamp | Trigger and score |
| Order timestamps and fees actually paid | Exact timing and true revenue |
| Payout dates and amounts | Payout-to-repurchase analysis, net margin |
| Rule-violation events | Early-warning triggers before a hard failure |
| Support contact history | Link outreach to outcomes |

## 7. Risks
- Observational data shows who returns, not what makes them return. The experiment is what establishes causation.
- Discount training: repeated offers can teach customers to wait for one. Cap frequency.
- Privacy: use pseudonymous IDs in analytics, restrict who can see contact details, and honour deletion requests.

## 8. Rollout
Week 0: instrument events and queue. Weeks 1 to 2: signal pilot. Weeks 3 to 4: extend if signal is positive. Then decide on automation of the tiers that paid back.
