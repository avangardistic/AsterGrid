"""ST-12 arm-request machine + slot wiring (Phase 7h-2, E3).

All inputs literal; no clock. Timestamps are ISO-8601-Z microsecond strings.
"""

import dataclasses

import pytest

from astergrid.core.fold import _empty_state
from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import (
    ArmBlockCode,
    ArmRequestState,
    expire_on_restart,
    is_legal_arm_transition,
    supersede_request,
)

_TS = "2026-09-25T00:00:00.000000Z"
_TS2 = "2026-09-25T00:00:05.000000Z"

_LEGAL = (
    ("IDLE", "PRECHECK"),
    ("PRECHECK", "AWAITING_APPROVAL"),
    ("PRECHECK", "ARMED"),
    ("PRECHECK", "BLOCKED"),
    ("AWAITING_APPROVAL", "ARMED"),
    ("AWAITING_APPROVAL", "BLOCKED"),
    ("AWAITING_APPROVAL", "PRECHECK"),
    ("BLOCKED", "PRECHECK"),
)
_ILLEGAL = (
    ("IDLE", "ARMED"),
    ("IDLE", "BLOCKED"),
    ("PRECHECK", "IDLE"),
    ("ARMED", "PRECHECK"),  # ARMED terminal
    ("ARMED", "BLOCKED"),  # ARMED terminal
    ("BLOCKED", "ARMED"),
    ("AWAITING_APPROVAL", "IDLE"),
)


def _req(**over: object) -> ArmRequestState:
    base: dict[str, object] = {
        "cloid": "c1",
        "request_seq": 0,
        "status": "PRECHECK",
        "timestamp": _TS,
    }
    base.update(over)
    return ArmRequestState(**base)  # type: ignore[arg-type]


# --------------------------- transition graph ---------------------------


def test_all_legal_edges_pass() -> None:
    for frm, to in _LEGAL:
        assert is_legal_arm_transition(frm, to) is True, (frm, to)


def test_illegal_edges_and_armed_terminal() -> None:
    for frm, to in _ILLEGAL:
        assert is_legal_arm_transition(frm, to) is False, (frm, to)
    # ARMED has no outgoing edge at all.
    for to in ("IDLE", "PRECHECK", "AWAITING_APPROVAL", "ARMED", "BLOCKED"):
        assert is_legal_arm_transition("ARMED", to) is False, to


def test_unknown_status_raises() -> None:
    with pytest.raises(ValueError):
        is_legal_arm_transition("BOGUS", "PRECHECK")
    with pytest.raises(ValueError):
        is_legal_arm_transition("PRECHECK", "BOGUS")


# --------------------------- supersede / restart ---------------------------


def test_supersede_pending_marks_superseded() -> None:
    for status in ("PRECHECK", "AWAITING_APPROVAL"):
        out = supersede_request(_req(status=status))
        assert out.status == "BLOCKED"
        assert out.block_code == ArmBlockCode.ARM_SUPERSEDED


def test_supersede_terminal_rejected() -> None:
    with pytest.raises(ValueError):
        supersede_request(_req(status="ARMED"))
    with pytest.raises(ValueError):
        supersede_request(_req(status="BLOCKED", block_code=ArmBlockCode.ARM_TIMEOUT))


def test_re_request_supersede_creates_new_seq() -> None:
    # old pending request superseded; new request at seq+1 in PRECHECK.
    old = _req(status="AWAITING_APPROVAL", request_seq=0)
    superseded = supersede_request(old)
    new = _req(status="PRECHECK", request_seq=old.request_seq + 1, timestamp=_TS2)
    assert superseded.status == "BLOCKED"
    assert superseded.block_code == ArmBlockCode.ARM_SUPERSEDED
    assert new.request_seq == 1
    assert new.status == "PRECHECK"
    # legality of the AWAITING_APPROVAL→PRECHECK re-request edge.
    assert is_legal_arm_transition("AWAITING_APPROVAL", "PRECHECK") is True


def test_policy_swap_supersede_uses_same_rule() -> None:
    out = supersede_request(_req(status="AWAITING_APPROVAL"))
    assert out.block_code == ArmBlockCode.ARM_SUPERSEDED


def test_restart_fail_closed_for_pending() -> None:
    for status in ("PRECHECK", "AWAITING_APPROVAL"):
        out = expire_on_restart(_req(status=status))
        assert out.status == "BLOCKED"
        assert out.block_code == ArmBlockCode.ARM_TIMEOUT


def test_restart_leaves_terminal_rows_unchanged() -> None:
    armed = _req(status="ARMED")
    assert expire_on_restart(armed) == armed
    blocked = _req(status="BLOCKED", block_code=ArmBlockCode.ARM_DENIED)
    assert expire_on_restart(blocked) == blocked


# --------------------------- record validation (inv.4 / P12) -------------------


def test_request_seq_and_status_validation() -> None:
    with pytest.raises(ValueError):
        _req(request_seq=-1)
    with pytest.raises(ValueError):
        _req(request_seq=True)  # bool rejected
    with pytest.raises(ValueError):
        _req(status="BOGUS")
    with pytest.raises(ValueError):
        _req(cloid="")


def test_block_code_coherence() -> None:
    with pytest.raises(ValueError):  # BLOCKED requires a code
        _req(status="BLOCKED")
    with pytest.raises(ValueError):  # non-BLOCKED must not carry a code
        _req(status="PRECHECK", block_code=ArmBlockCode.ARM_TIMEOUT)
    ok = _req(status="BLOCKED", block_code=ArmBlockCode.ARM_DENIED)
    assert ok.block_code == ArmBlockCode.ARM_DENIED


def test_timestamp_validation() -> None:
    with pytest.raises(ValueError):
        _req(timestamp="2026-09-25 00:00:00")  # not ISO-Z-micros
    with pytest.raises(ValueError):
        _req(timestamp="2026-09-25T00:00:00Z")  # missing microseconds
    with pytest.raises(ValueError):
        _req(timestamp="not-a-timestamp")


def test_operator_identity_optional_but_nonempty() -> None:
    assert _req(operator_identity="ops-1").operator_identity == "ops-1"
    with pytest.raises(ValueError):
        _req(operator_identity="")


def test_record_carries_identity_and_timestamp() -> None:
    row = _req(
        status="BLOCKED", block_code=ArmBlockCode.ARM_DENIED, operator_identity="svc"
    )
    obj = row.to_canonical_obj()
    assert obj["cloid"] == "c1"
    assert obj["request_seq"] == 0
    assert obj["timestamp"] == _TS
    assert obj["block_code"] == "ARM_DENIED"
    assert obj["operator_identity"] == "svc"


# --------------------------- slot wiring / persistence ---------------------


def test_st12_slot_accepts_sorted_and_serializes() -> None:
    rows = (
        _req(cloid="a", request_seq=0),
        _req(cloid="a", request_seq=1, timestamp=_TS2),
        _req(cloid="b", request_seq=0),
    )
    state = dataclasses.replace(_empty_state(), st12_operator_arm_requests=rows)
    obj = state.to_canonical_obj()
    dumped = canonical_dumps(obj)
    assert '"timestamp"' in dumped
    assert obj["st12_operator_arm_requests"][1]["timestamp"] == _TS2


def test_st12_unsorted_rejected() -> None:
    rows = (_req(cloid="b", request_seq=0), _req(cloid="a", request_seq=0))
    with pytest.raises(ValueError):
        dataclasses.replace(_empty_state(), st12_operator_arm_requests=rows)


def test_st12_duplicate_identity_rejected() -> None:
    rows = (_req(cloid="a", request_seq=0), _req(cloid="a", request_seq=0))
    with pytest.raises(ValueError):
        dataclasses.replace(_empty_state(), st12_operator_arm_requests=rows)
