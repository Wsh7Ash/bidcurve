# bidcurve

**See what a continuous double auction does, tick by tick — price-time matching
plus a reproducible agent simulation.**

## Why

Order matching is usually described in prose ("best price first, then time") but
the consequences — partial fills, price improvement, where the spread goes — are
easier to understand by running a book. `bidcurve` provides a small, deterministic
matching engine and a seeded double-auction simulation so a lecture, test or
experiment can be replayed exactly.

## Features

- Price-time priority limit order book with partial fills
- Trades execute at the resting order's price
- Seeded buyer/seller agents with fixed private values and shading
- Per-tick price series, volume, average price and realised surplus
- Text or JSON output; explicit order lists or shorthand input

## Example

`bidcurve demo` (order book section, then a seeded simulation):

```text
bidcurve order book
==============================================
trades: 2
  5 @ 100   <-  (orders 2/1)
  2 @ 104   <-  (orders 4/3)
best bid: 105
best ask: -
resting: 1 bid(s), 0 ask(s)

bidcurve simulation
==============================================
seed=11 ticks=8
trades=53 volume=75 avg_price=10418.27
total surplus=47589
price series: 10557.7, 10545.62, 10453.33, 10502.57, ...
```

## Architecture

```text
src/bidcurve/__init__.py  Order/Trade/Book, match_orders, seeded simulate()
src/bidcurve/cli.py       match / sim / demo and exit codes
tests/test_bidcurve.py    priority, partial fills, determinism, CLI
```

The book keeps bids sorted by `(-price, order_id)` and asks by
`(price, order_id)`. Incoming orders walk the opposite side while the prices
cross, producing one trade per resting order touched.

## Requirements

- Python 3.10+
- pytest for tests

## Installation

```shell
git clone https://github.com/Wsh7Ash/bidcurve.git
cd bidcurve
python -m pip install -e .
```

## Quick start

```shell
bidcurve demo
bidcurve match --orders "sell:100:5,buy:110:3"
```

## Usage

```shell
# Explicit orders from a file
bidcurve match examples/orders.json

# JSON trade tape
bidcurve match --orders "sell:100:5,buy:110:5" --json

# Reproducible simulation
bidcurve sim --seed 7 --ticks 20 --buyers 8 --sellers 8 --json
```

Order shorthand is `side:price:quantity`, comma separated. Prices are integers in
minor units (cents), which avoids float equality problems.

Exit codes: `0` success, `2` invalid order, file or parameter.

## Configuration

There is no config file. Simulation parameters are CLI flags; defaults are seed
`7`, 20 ticks, 6 buyers and 6 sellers.

## Testing

```shell
python -m pip install -e . pytest
python -m pytest tests -q
```

## Project structure

```text
bidcurve/
├─ src/bidcurve/        engine + simulation + CLI
├─ tests/               pytest suite
├─ examples/            sample orders
├─ docs/                architecture, usage, spec
├─ results/             generated tapes and series
└─ .github/workflows/   CI
```

## Limitations

- Limit orders only; no market orders, cancels, icebergs or fees.
- Trades print at the resting price, which is one valid exchange convention but
  not the only one.
- The agent model is deliberately simple: fixed private values, uniform shading,
  no learning or strategic adaptation.
- Matching is single-threaded and deterministic; it is a teaching tool, not an
  exchange.

## Roadmap

- Order cancellation and amend
- Market orders and fee models
- Compare price-time with pro-rata allocation

## License

MIT — see `LICENSE`.
