"""Command line interface for bidcurve."""

from __future__ import annotations

import argparse
import json
import sys

from . import (
    MarketError,
    load_orders,
    match_orders,
    parse_seq,
    render_book,
    render_simulation,
    simulate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bidcurve",
        description="Price-time priority order matching and a seeded double-auction simulation.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    match = sub.add_parser("match", help="match an explicit order list")
    match.add_argument("path", nargs="?", help="orders JSON; omit to use --orders")
    match.add_argument("--orders", help="shorthand, e.g. sell:100:5,buy:110:3")
    match.add_argument("--json", action="store_true")
    match.add_argument("--out")

    sim = sub.add_parser("sim", help="run the seeded agent simulation")
    sim.add_argument("--seed", type=int, default=7)
    sim.add_argument("--ticks", type=int, default=20)
    sim.add_argument("--buyers", type=int, default=6)
    sim.add_argument("--sellers", type=int, default=6)
    sim.add_argument("--json", action="store_true")
    sim.add_argument("--out")

    sub.add_parser("demo", help="run a sample match and simulation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "demo":
            book = match_orders(parse_seq("sell:100:5,buy:110:5,sell:104:2,buy:105:3"))
            print(render_book(book))
            print()
            print(render_simulation(simulate(seed=11, ticks=8)))
            return 0

        if args.command == "match":
            orders = parse_seq(args.orders) if args.orders else None
            if orders is None:
                if not args.path:
                    print("bidcurve: provide a JSON path or --orders", file=sys.stderr)
                    return 2
                orders = load_orders(args.path)
            book = match_orders(orders)
            output = json.dumps(
                {
                    "trades": [trade.to_dict() for trade in book.trades],
                    "best_bid": book.best_bid().price if book.best_bid() else None,
                    "best_ask": book.best_ask().price if book.best_ask() else None,
                },
                indent=2,
            ) if args.json else render_book(book)
        else:
            result = simulate(args.seed, args.ticks, args.buyers, args.sellers)
            output = json.dumps(result.to_dict(), indent=2) if args.json else render_simulation(result)
    except (OSError, KeyError, ValueError, MarketError) as exc:
        print(f"bidcurve: {exc}", file=sys.stderr)
        return 2

    print(output)
    if getattr(args, "out", None):
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
