"""bidcurve - price-time priority matching plus a deterministic double auction.

``match_orders`` is a small continuous order book: incoming orders cross against
resting orders at the resting price, with price-time priority. ``simulate`` uses
it with seeded buyer/seller agents so a run is reproducible from its seed.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field, replace
from typing import Iterable, Sequence


class MarketError(ValueError):
    """Raised for malformed orders or simulation parameters."""


@dataclass(frozen=True)
class Order:
    order_id: int
    side: str  # buy | sell
    price: int  # integer minor units (cents)
    quantity: int
    agent: str = ""

    def __post_init__(self) -> None:
        if self.side not in {"buy", "sell"}:
            raise MarketError(f"side must be buy or sell, got {self.side!r}")
        if self.price <= 0:
            raise MarketError("price must be positive")
        if self.quantity <= 0:
            raise MarketError("quantity must be positive")


@dataclass(frozen=True)
class Trade:
    price: int
    quantity: int
    buy_order: int
    sell_order: int
    buyer: str
    seller: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Book:
    bids: list[Order] = field(default_factory=list)  # best first
    asks: list[Order] = field(default_factory=list)  # best first
    trades: list[Trade] = field(default_factory=list)

    def _sort(self) -> None:
        self.bids.sort(key=lambda order: (-order.price, order.order_id))
        self.asks.sort(key=lambda order: (order.price, order.order_id))

    def add(self, order: Order) -> None:
        if order.side == "buy":
            self.bids.append(order)
        else:
            self.asks.append(order)
        self._sort()

    def best_bid(self) -> Order | None:
        return self.bids[0] if self.bids else None

    def best_ask(self) -> Order | None:
        return self.asks[0] if self.asks else None


def _join(order_a: Order, order_b: Order, price: int, quantity: int) -> Trade:
    buy, sell = (order_a, order_b) if order_a.side == "buy" else (order_b, order_a)
    return Trade(price, quantity, buy.order_id, sell.order_id, buy.agent, sell.agent)


def match_orders(orders: Iterable[Order], book: Book | None = None) -> Book:
    """Match orders sequentially against the book, price-time priority."""
    book = book if book is not None else Book()
    for order in orders:
        remaining = order.quantity
        while remaining > 0:
            resting = book.best_ask() if order.side == "buy" else book.best_bid()
            if resting is None:
                break
            crosses = (
                resting.price <= order.price if order.side == "buy"
                else resting.price >= order.price
            )
            if not crosses:
                break

            quantity = min(remaining, resting.quantity)
            book.trades.append(_join(order, resting, resting.price, quantity))
            target = book.asks if resting.side == "sell" else book.bids
            if resting.quantity == quantity:
                target.pop(0)
            else:
                target[0] = replace(resting, quantity=resting.quantity - quantity)
            remaining -= quantity

        if remaining > 0:
            book.add(Order(order.order_id, order.side, order.price, remaining, order.agent))
    return book


@dataclass
class Simulation:
    seed: int
    ticks: int
    trades: list[Trade] = field(default_factory=list)
    price_series: list[float] = field(default_factory=list)
    volume: int = 0
    surplus: int = 0

    @property
    def average_price(self) -> float:
        if not self.trades or self.volume == 0:
            return 0.0
        return round(sum(t.price * t.quantity for t in self.trades) / self.volume, 2)

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "ticks": self.ticks,
            "trade_count": len(self.trades),
            "volume": self.volume,
            "average_price": self.average_price,
            "surplus": self.surplus,
            "price_series": self.price_series,
            "trades": [trade.to_dict() for trade in self.trades],
        }


def simulate(
    seed: int = 7,
    ticks: int = 20,
    buyers: int = 6,
    sellers: int = 6,
    value_low: int = 9000,
    value_high: int = 11000,
    margin: int = 150,
) -> Simulation:
    """Run a seeded double auction where each agent has a fixed private value."""
    if ticks <= 0 or buyers <= 0 or sellers <= 0:
        raise MarketError("ticks, buyers and sellers must be positive")
    if value_low >= value_high:
        raise MarketError("value_low must be below value_high")

    rng = random.Random(seed)
    buyer_values = {f"b{i}": rng.randint(value_low, value_high) for i in range(buyers)}
    seller_costs = {f"s{i}": rng.randint(value_low, value_high) for i in range(sellers)}

    book = Book()
    result = Simulation(seed=seed, ticks=ticks)
    next_id = 1

    for tick in range(1, ticks + 1):
        tick_trades_before = len(book.trades)
        batch: list[Order] = []
        for agent, value in buyer_values.items():
            bid = max(1, value - rng.randint(0, margin))
            batch.append(Order(next_id, "buy", bid, rng.randint(1, 3), agent))
            next_id += 1
        for agent, cost in seller_costs.items():
            ask = cost + rng.randint(0, margin)
            batch.append(Order(next_id, "sell", ask, rng.randint(1, 3), agent))
            next_id += 1

        match_orders(batch, book)
        new_trades = book.trades[tick_trades_before:]
        for trade in new_trades:
            result.trades.append(trade)
            result.volume += trade.quantity
            result.surplus += trade.quantity * (buyer_values[trade.buyer] - seller_costs[trade.seller])
        if new_trades:
            tick_volume = sum(t.quantity for t in new_trades)
            result.price_series.append(round(sum(t.price * t.quantity for t in new_trades) / tick_volume, 2))

    return result


def load_orders(path: str) -> list[Order]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = data.get("orders", [])
    return [
        Order(int(item["order_id"]), str(item["side"]), int(item["price"]),
              int(item["quantity"]), str(item.get("agent", "")))
        for item in data
    ]


def render_book(book: Book) -> str:
    lines = ["bidcurve order book", "=" * 46]
    lines.append(f"trades: {len(book.trades)}")
    for trade in book.trades:
        lines.append(
            f"  {trade.quantity} @ {trade.price}  {trade.buyer} <- {trade.seller} "
            f"(orders {trade.buy_order}/{trade.sell_order})"
        )
    best_bid, best_ask = book.best_bid(), book.best_ask()
    lines.append(f"best bid: {best_bid.price if best_bid else '-'}")
    lines.append(f"best ask: {best_ask.price if best_ask else '-'}")
    lines.append(f"resting: {len(book.bids)} bid(s), {len(book.asks)} ask(s)")
    return "\n".join(lines)


def render_simulation(result: Simulation) -> str:
    lines = ["bidcurve simulation", "=" * 46]
    lines.append(f"seed={result.seed} ticks={result.ticks}")
    lines.append(f"trades={len(result.trades)} volume={result.volume} avg_price={result.average_price}")
    lines.append(f"total surplus={result.surplus}")
    if result.price_series:
        lines.append("price series: " + ", ".join(str(price) for price in result.price_series))
    return "\n".join(lines)


def parse_seq(text: str) -> list[Order]:
    """Parse ``buy:105:3,sell:100:5`` shorthand used by demos and tests."""
    orders: list[Order] = []
    for index, chunk in enumerate(text.split(","), start=1):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) != 3:
            raise MarketError(f"expected side:price:quantity, got {chunk!r}")
        side, price, quantity = parts
        orders.append(Order(index, side.strip(), int(price), int(quantity)))
    return orders
