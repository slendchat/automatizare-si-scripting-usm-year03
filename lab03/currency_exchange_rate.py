#!/usr/bin/env python3
"""Thin wrapper so cron can invoke the lab02 package."""
from currency_exchange_rate.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
