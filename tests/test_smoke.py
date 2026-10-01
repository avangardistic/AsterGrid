"""Smoke test: every package imports cleanly (no domain logic exercised)."""

import importlib


def test_packages_import_cleanly() -> None:
    for name in (
        "astergrid",
        "astergrid.core",
        "astergrid.adapters",
        "astergrid.runtime",
        "astergrid.runtime.logging_setup",
        "astergrid.operator",
        "astergrid.config",
        "astergrid.config.schema",
    ):
        assert importlib.import_module(name) is not None
