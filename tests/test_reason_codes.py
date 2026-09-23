"""ReasonCode: str-valued, same-line provenance, exact membership (Phase 7d)."""

import importlib.util
from pathlib import Path

from hypergrid.core.transitions.reason_codes import ReasonCode

# Codes reserved for Phase 7e/7f — MUST NOT be members yet (DECISION-013).
_FUTURE = ("RETURN_LEVEL_UNVERIFIED", "SUCCESSOR_LOCK_ACTIVE", "GENERATION_ID_LIMIT")
_SOURCE_MARKERS = ("STR-", "§", "DECISION-")
_KIND_MARKERS = ("VERBATIM", "COINED")

_EXPECTED = {
    "EVOLUTION_IN_FLIGHT_LOCKED",
    "CYCLE_TRANSITION_IN_FLIGHT_LOCKED",
    "CYCLE_LIMIT_REACHED",
    "SAME_GEN_DISABLE_BEATS_EVOLUTION",
    "ACROSS_GEN_EVOLUTION_BEFORE_CYCLE",
    "ACROSS_GEN_LOWER_GEN_ID_FIRST",
}


def _source_lines() -> list[str]:
    spec = importlib.util.find_spec("hypergrid.core.transitions.reason_codes")
    assert spec is not None
    assert spec.origin is not None
    return Path(spec.origin).read_text(encoding="utf-8").splitlines()


def test_members_are_nonempty_str() -> None:
    for member in ReasonCode:
        assert isinstance(member.value, str)
        assert member.value
        assert member.value == member.name  # value == name (auto())


def test_membership_is_exactly_the_six_phase_7d_codes() -> None:
    assert {m.name for m in ReasonCode} == _EXPECTED


def test_each_member_has_same_line_provenance() -> None:
    lines = _source_lines()
    for member in ReasonCode:
        matches = [ln for ln in lines if ln.strip().startswith(f"{member.name} =")]
        assert len(matches) == 1, member.name
        line = matches[0]
        assert any(m in line for m in _SOURCE_MARKERS), member.name
        assert any(k in line for k in _KIND_MARKERS), member.name


def test_future_codes_absent() -> None:
    for name in _FUTURE:
        assert not hasattr(ReasonCode, name)
