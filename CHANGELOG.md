# Changelog

## [1.0.0] - 2026-11-15

### Added

- Price-time priority limit order book with partial fills and resting-price
  execution.
- Seeded double-auction simulation with fixed agent values, per-tick price
  series, volume and realised surplus.
- `match`, `sim` and `demo` commands; shorthand `side:price:quantity` parsing.
- pytest suite covering priority, partial fills, determinism and CLI codes.
