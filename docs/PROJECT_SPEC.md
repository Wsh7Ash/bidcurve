# PROJECT_SPEC — bidcurve

- **Name:** bidcurve
- **Category:** simulation
- **Target user:** students, interviewers and engineers learning market
  microstructure
- **Problem:** matching rules are easy to state and hard to see; spread, partial
  fills and price improvement stay abstract
- **Solution:** a deterministic limit order book plus a seeded double-auction
  simulation with a trade tape and price series
- **Core workflow:** match orders or simulate agents → inspect tape/summary
- **Must-have features:** price-time priority, partial fills, resting-price
  execution, seeded agents, volume/average/surplus, text/JSON
- **Nice-to-have features:** cancels, market orders, fee models, pro-rata
- **Stack:** Python 3.10+ standard library
- **Test strategy:** exact trade sequences for priority/partial cases,
  determinism by seed, surplus non-negativity, validation, CLI codes
- **Demo/result strategy:** `bidcurve demo`, `examples/orders.json`, simulation JSON
- **Safety considerations:** educational model only; no exchange connectivity, no
  real money, no trading advice
- **Definition of done:** tests pass, install works, demo recorded, docs accurate
