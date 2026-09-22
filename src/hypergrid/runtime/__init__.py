"""hypergrid.runtime — the process shell (Phase 7a: logging only).

The runtime wires adapters to the pure core, owns the asyncio loop, and does
all logging (the core never logs — DECISION-023). Phase 7a provides only the
logging skeleton (`logging_setup`).
"""

__all__: list[str] = []
