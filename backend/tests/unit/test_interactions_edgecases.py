"""Additional unit tests for _filter_by_item_id edge cases and boundaries."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id, kind: str = "attempt") -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind=kind)


def test_filter_returns_empty_when_no_interaction_has_item_id() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 99)
    assert result == []


def test_filter_ignores_objects_with_item_id_none() -> None:
    # Use a lightweight object missing a concrete item id to simulate incomplete records
    class Partial:
        def __init__(self, id, learner_id, item_id):
            self.id = id
            self.learner_id = learner_id
            self.item_id = item_id
            self.kind = "view"

    incomplete = Partial(1, 1, None)
    good = _make_log(2, 2, 1)
    interactions = [incomplete, good]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 2


def test_filter_accepts_zero_and_negative_item_ids() -> None:
    interactions = [_make_log(1, 1, 0), _make_log(2, 2, -1), _make_log(3, 3, 1)]
    res_zero = _filter_by_item_id(interactions, 0)
    assert len(res_zero) == 1
    assert res_zero[0].item_id == 0

    res_neg = _filter_by_item_id(interactions, -1)
    assert len(res_neg) == 1
    assert res_neg[0].item_id == -1


def test_filter_with_non_int_item_id_does_not_match_ints() -> None:
    interactions = [_make_log(1, 1, 1)]
    # Passing a string should not match integer ids
    result = _filter_by_item_id(interactions, "1")
    assert result == []


def test_filter_preserves_order_and_returns_all_duplicates() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 1), _make_log(3, 3, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert [i.id for i in result] == [1, 2]
