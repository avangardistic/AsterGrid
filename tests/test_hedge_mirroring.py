"""§11.3 mirror eligibility (pure predicate; price formula = B2b STOP-item) (7g-3b).

The symmetric trigger/target price recomputation (§11.3 L883, STR-0209) is a NAME,
not a formula, in Strategy — it is the B2b STOP-item and is NOT implemented here;
this file therefore tests only the eligibility predicate.
"""

from astergrid.core.transitions import IntentTag, mirror_eligible


def test_eligible_lifecycles() -> None:
    for lifecycle in ("ACTIVE", "SUCCESSOR_CREATED", "DISABLED_AT_CYCLE_99"):
        assert mirror_eligible(lifecycle=lifecycle) is True


def test_ineligible_lifecycles_fail_closed() -> None:
    for lifecycle in (
        "CREATED",
        "EVOLUTION_PENDING",
        "CLOSED_ONLY_AS_PART_OF_BASKET",
        "SOMETHING_UNKNOWN",
        "",
    ):
        assert mirror_eligible(lifecycle=lifecycle) is False


def test_entry_intent_never_constructed() -> None:
    # mirror_eligible returns a bool, never an intent; nothing builds ENTRY_INTENT.
    assert isinstance(mirror_eligible(lifecycle="ACTIVE"), bool)
    assert (
        IntentTag.ENTRY_INTENT.value == "ENTRY_INTENT"
    )  # exists only for the invariant
