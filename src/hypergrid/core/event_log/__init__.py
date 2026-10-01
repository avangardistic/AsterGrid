"""hypergrid.core.event_log — the append-only log (Phase 7b).

The log-as-truth substrate of CAND-B: the port plus an in-memory and a SQLite
implementation. Single-writer; the log is the sole allocator of log_sequence /
monotonic_counter (R-SEQ-1). No fold, no domain logic.
"""

from hypergrid.core.event_log.memory import InMemoryEventLog
from hypergrid.core.event_log.port import EventLogPort
from hypergrid.core.event_log.sqlite import SqliteEventLog

__all__ = ["EventLogPort", "InMemoryEventLog", "SqliteEventLog"]
