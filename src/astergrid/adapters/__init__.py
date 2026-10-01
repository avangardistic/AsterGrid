"""astergrid.adapters — side-effect boundary (Phase 7b+).

The ONLY place side effects occur: venue I/O (REST/WS), persistence I/O,
signing, and the operator surface. Adapters deliver recorded inputs to the
core and carry out committed effects; they never make domain decisions.
`asyncio` is permitted here (never in `core/`). Phase 7a: empty.
"""

__all__: list[str] = []
