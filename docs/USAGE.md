# Usage

## Teaching price-time priority

```shell
bidcurve match --orders "sell:100:2,sell:100:3,buy:101:4"
```

The first ask is filled completely, the second partially. Change the order ids
to show that time breaks price ties.

## Checking a book by hand

```shell
bidcurve match examples/orders.json --json
```

The JSON contains the trade tape plus best bid/ask after matching, which is
enough to verify an exercise.

## Comparing seeds

```shell
bidcurve sim --seed 1 --ticks 15
bidcurve sim --seed 2 --ticks 15
```

Different seeds draw different private values, so volume and average price move.
Keep the seed when reporting a result.

## Experimenting with shading

The CLI exposes buyers, sellers and ticks; edit the library call to change
`value_low`, `value_high` and `margin`:

```python
from bidcurve import simulate

result = simulate(seed=4, ticks=30, value_low=800, value_high=1200, margin=300)
print(result.average_price, result.volume, result.surplus)
```

## Reading the summary

- `volume`: total quantity traded.
- `average_price`: volume-weighted across all trades.
- `surplus`: total gains from trade given the agents' private values.
- `price_series`: one volume-weighted price per tick that traded.
