"""SubDecisionRecord + PassReport extension (Phase 7h-4b-2, E2)."""

import dataclasses

import pytest

from astergrid.core.pass_engine import PassReport
from astergrid.core.serialization import canonical_dumps
from astergrid.core.transitions import StageReport, SubDecisionRecord
from astergrid.core.transitions.pass_report_ext import STAGE_ORDER


def _rec(**over: object) -> SubDecisionRecord:
    base: dict[str, object] = {
        "stage": "P6",
        "sub_kind": "CANCEL_SELECT",
        "subject": "c1",
        "outcome": "EMITTED",
    }
    base.update(over)
    return SubDecisionRecord(**base)  # type: ignore[arg-type]


def test_frozen() -> None:
    r = _rec()
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.subject = "x"  # type: ignore[misc]


def test_bad_stage_and_kind() -> None:
    with pytest.raises(ValueError):
        _rec(stage="P9")
    with pytest.raises(ValueError):
        _rec(sub_kind="NOT_A_KIND")


def test_kind_outcome_mismatch() -> None:
    with pytest.raises(ValueError):  # CANCEL_SELECT only allows EMITTED
        _rec(sub_kind="CANCEL_SELECT", outcome="ARMED")
    with pytest.raises(ValueError):  # ARMING_EVAL cannot be ISSUED
        _rec(sub_kind="ARMING_EVAL", outcome="ISSUED", subject="c1")
    # valid combos
    assert _rec(sub_kind="ARMING_EVAL", outcome="WAITING").outcome == "WAITING"
    assert (
        _rec(
            sub_kind="LADDER_ISSUANCE_BU", subject="G00-C06-BU", outcome="EMPTY"
        ).outcome
        == "EMPTY"
    )


def test_subject_shapes() -> None:
    # order-kind subject must be a non-empty cloid
    with pytest.raises(ValueError):
        _rec(sub_kind="CANCEL_SELECT", subject="")
    # ladder-kind subject must match G..-C..-{BU|SL}
    with pytest.raises(ValueError):
        _rec(sub_kind="LADDER_ISSUANCE_SL", subject="c1", outcome="ISSUED")
    with pytest.raises(ValueError):
        _rec(sub_kind="LADDER_ISSUANCE_SL", subject="G0-C6-SL", outcome="ISSUED")
    assert (
        _rec(
            sub_kind="LADDER_ISSUANCE_SL", subject="G00-C06-SL", outcome="ISSUED"
        ).subject
        == "G00-C06-SL"
    )


def test_empty_reason_code_rejected() -> None:
    with pytest.raises(ValueError):
        _rec(reason_codes=("",))
    assert _rec(reason_codes=("X",)).reason_codes == ("X",)


def test_canonical_round_trip() -> None:
    r = _rec(reason_codes=("EXHAUSTED_TRAVERSAL_CANCEL",), notes="n")
    obj = r.to_canonical_obj()
    assert set(obj) == {
        "stage",
        "sub_kind",
        "subject",
        "outcome",
        "reason_codes",
        "notes",
    }
    canonical_dumps(obj)


def test_passreport_backward_compat_and_canonical() -> None:
    stage = StageReport("P6", "NO_OP", (), "P6: no sub-decisions")
    pr = PassReport(stages=(stage,))
    assert pr.sub_decisions == ()  # default preserved
    obj = pr.to_canonical_obj()
    assert obj["sub_decisions"] == []
    canonical_dumps(obj)


def test_stage_order_map() -> None:
    assert STAGE_ORDER == {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
        "P5": 5,
        "P6": 6,
    }
