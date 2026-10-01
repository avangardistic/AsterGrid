"""astergrid.operator — gated operator surface (Phase 7b+).

Arm approval/denial, freeze, resume, kill-switch, owner clearance — recorded
as operator events with identity + timestamp. Approval only further restricts
(never bypasses §8/§10 gates); timeout → fail-closed. Phase 7a: empty.
"""

__all__: list[str] = []
