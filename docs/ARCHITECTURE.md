# Architecture

## Matching

```text
incoming order
      │
      ▼
best opposite resting order ──crosses?── no ──► rest in book
      │ yes
      ▼
trade at RESTING price, quantity = min(remaining, resting)
      │
      ├─ resting fully filled → remove it
      └─ resting partial      → replace with reduced quantity
      │
      └─ loop until remaining is 0 or prices no longer cross
```

Bids sort by `(-price, order_id)`, asks by `(price, order_id)`, so the first
element is always the best price and the earliest order at that price.

## Why resting-price execution

Executing at the resting order's price is the common "price improvement for the
aggressor" convention: a buyer willing to pay 105 who hits a 100 ask pays 100.
The alternative (midpoint or aggressor price) is a policy choice; this one is
simple and testable.

## Simulation

Each agent gets one fixed private value from the seeded RNG (buyers) or cost
(sellers). Every tick, each agent submits a shaded order, then the batch is
matched against the persistent book. This produces a trade tape, a per-tick
volume-weighted price series, total volume and realised surplus
`(buyer_value − seller_cost) × quantity`.

Because trades require a crossing, `surplus` cannot be negative.

## Determinism

One `random.Random(seed)` drives agent values, shading and sizes in a fixed
order. Two runs with the same seed and parameters produce identical dicts, which
the tests assert.

## Errors

`MarketError` covers bad sides, non-positive prices/quantities, impossible
simulation parameters and malformed shorthand; the CLI maps it to exit code 2.
