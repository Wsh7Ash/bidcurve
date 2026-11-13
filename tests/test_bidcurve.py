import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from bidcurve import (
    MarketError,
    Order,
    load_orders,
    match_orders,
    parse_seq,
    render_book,
    simulate,
)
from bidcurve.cli import main


def test_simple_cross_trades_at_resting_price():
    book = match_orders(parse_seq("sell:100:5,buy:110:5"))
    assert len(book.trades) == 1
    trade = book.trades[0]
    assert (trade.price, trade.quantity) == (100, 5)
    assert book.bids == [] and book.asks == []


def test_price_time_priority_and_partial_fills():
    orders = [
        Order(1, "sell", 100, 2),
        Order(2, "sell", 100, 3),
        Order(3, "buy", 101, 4),
    ]
    book = match_orders(orders)
    assert [(t.price, t.quantity, t.sell_order) for t in book.trades] == [
        (100, 2, 1),
        (100, 2, 2),
    ]
    assert book.asks[0].order_id == 2 and book.asks[0].quantity == 1


def test_non_crossing_orders_rest():
    book = match_orders(parse_seq("buy:99:5,sell:101:5"))
    assert book.trades == []
    assert book.best_bid().price == 99
    assert book.best_ask().price == 101


def test_buy_crosses_multiple_asks_at_each_ask_price():
    book = match_orders(parse_seq("sell:100:1,sell:102:1,buy:103:2"))
    assert [(t.price, t.quantity) for t in book.trades] == [(100, 1), (102, 1)]


def test_order_validation():
    with pytest.raises(MarketError):
        Order(1, "hold", 100, 1)
    with pytest.raises(MarketError):
        Order(1, "buy", 0, 1)
    with pytest.raises(MarketError):
        Order(1, "buy", 100, 0)
    with pytest.raises(MarketError):
        parse_seq("buy:100")
    with pytest.raises(MarketError):
        simulate(ticks=0)


def test_simulation_is_deterministic_and_non_negative_surplus():
    first = simulate(seed=3, ticks=10)
    second = simulate(seed=3, ticks=10)
    assert first.to_dict() == second.to_dict()
    assert first.surplus >= 0
    assert first.volume == sum(trade.quantity for trade in first.trades)
    if first.trades:
        assert first.average_price > 0


def test_different_seeds_differ():
    assert simulate(seed=1, ticks=6).to_dict() != simulate(seed=2, ticks=6).to_dict()


def test_load_orders_and_rendering(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text(json.dumps({"orders": [{"order_id": 1, "side": "sell", "price": 10, "quantity": 2}]}),
                    encoding="utf-8")
    assert load_orders(str(path))[0].price == 10
    book = match_orders(parse_seq("sell:100:1,buy:105:1"))
    text = render_book(book)
    assert "trades: 1" in text and "best bid" in text
    with pytest.raises(OSError):
        load_orders(str(tmp_path / "missing.json"))


def test_cli_match_sim_and_exit_codes(tmp_path, capsys):
    assert main(["match", "--orders", "sell:100:2,buy:101:1"]) == 0
    assert "trades: 1" in capsys.readouterr().out

    capsys.readouterr()
    assert main(["match", "--orders", "sell:100:2,buy:101:1", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["trades"][0]["price"] == 100

    assert main(["sim", "--seed", "5", "--ticks", "5", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["seed"] == 5 and data["ticks"] == 5

    assert main(["match"]) == 2
    assert main(["match", str(tmp_path / "missing.json")]) == 2
    assert main(["sim", "--ticks", "0"]) == 2
    assert main(["demo"]) == 0
