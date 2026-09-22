"""Smoke test: every package imports cleanly (no domain logic exercised)."""

import importlib


def test_packages_import_cleanly() -> None:
    for name in (
        "hypergrid",
        "hypergrid.core",
        "hypergrid.adapters",
        "hypergrid.runtime",
        "hypergrid.runtime.logging_setup",
        "hypergrid.operator",
        "hypergrid.config",
        "hypergrid.config.schema",
    ):
        assert importlib.import_module(name) is not None
