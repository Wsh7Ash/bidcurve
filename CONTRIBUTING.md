# Contributing

## Setup

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Invariants

- The book is always sorted best-first after any mutation.
- A trade never occurs unless the incoming price crosses the resting price.
- Trades execute at the resting order's price.
- Simulation output is a pure function of `(seed, ticks, buyers, sellers, ranges, margin)`.

## Adding a feature

1. Implement in `Book`/`match_orders`, not in the CLI.
2. Add an exact trade-sequence test and a no-trade case.
3. Document the convention (for example, execution price) in
   `docs/ARCHITECTURE.md`.

## Style

- Standard library only.
- Prices are integers in minor units; never introduce floats into matching.
