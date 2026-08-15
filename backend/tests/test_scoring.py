"""
Tests for the scoring model.

These matter more than they look. The whole programme rests on Wave 1 and Wave 2
being scored the same way, so the rules need to be pinned down somewhere that
fails loudly when someone changes them by accident.
"""

import pytest

from app.services.scoring import (
    BANDS,
    DEFAULT_WEIGHTS,
    DepartmentResult,
    Indicator,
    IndicatorScores,
    Level,
    Movement,
    TargetStatus,
    adjusted_scores,
    adoption_rate,
    band_for,
    clamp,
    compare_waves,
    normalise_weights,
    organisation_rate,
    scale_to_target,
    target_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def strong() -> IndicatorScores:
    """Roughly the IT department in the sample data."""
    return IndicatorScores(
        users=92, freq=95, train=98, flow=90,
        tasks=88, cover=86, prof=94, comp=98,
    )


@pytest.fixture
def weak() -> IndicatorScores:
    """Roughly the Legal department in the sample data."""
    return IndicatorScores(
        users=24, freq=20, train=28, flow=18,
        tasks=16, cover=14, prof=22, comp=40,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestClamp:
    def test_leaves_values_in_range_alone(self):
        assert clamp(57.3) == 57.3

    def test_pulls_back_values_outside_the_range(self):
        assert clamp(140) == 100
        assert clamp(-12) == 0


class TestScaleToTarget:
    def test_hitting_the_target_scores_full_marks(self):
        assert scale_to_target(5.0, 5.0) == 100

    def test_half_the_target_scores_half(self):
        assert scale_to_target(2.5, 5.0) == 50

    def test_exceeding_the_target_does_not_exceed_100(self):
        # Otherwise one very active department could mask a weakness elsewhere.
        assert scale_to_target(12.0, 5.0) == 100

    def test_a_target_of_zero_is_rejected(self):
        with pytest.raises(ValueError):
            scale_to_target(3.0, 0)


class TestNormaliseWeights:
    def test_default_weights_already_sum_to_100(self):
        assert sum(DEFAULT_WEIGHTS.values()) == 100

    def test_weights_are_rescaled_to_sum_to_100(self):
        result = normalise_weights({"users": 30, "freq": 30})
        assert sum(result.values()) == pytest.approx(100)
        assert result["users"] == pytest.approx(50)

    def test_relative_importance_survives_rescaling(self):
        result = normalise_weights({"users": 40, "freq": 20, "train": 20})
        assert result["users"] == pytest.approx(result["freq"] * 2)

    def test_negative_weights_are_treated_as_zero(self):
        result = normalise_weights({"users": 50, "freq": -10})
        assert result["freq"] == 0

    def test_all_zero_weights_is_an_error(self):
        with pytest.raises(ValueError):
            normalise_weights({"users": 0, "freq": 0})


# ---------------------------------------------------------------------------
# Adoption rate
# ---------------------------------------------------------------------------

class TestAdoptionRate:
    def test_matches_a_hand_calculated_weighted_mean(self, strong):
        # 92*.20 + 95*.15 + 98*.15 + 90*.15 + 88*.10 + 86*.10 + 94*.10 + 98*.05
        assert adoption_rate(strong) == pytest.approx(92.55, abs=0.01)

    def test_all_zeros_scores_zero(self):
        assert adoption_rate(IndicatorScores()) == 0

    def test_all_hundreds_scores_one_hundred(self):
        perfect = IndicatorScores(**{f.name: 100 for f in IndicatorScores.__dataclass_fields__.values()})
        assert adoption_rate(perfect) == 100

    def test_result_always_lands_inside_the_range(self, strong, weak):
        for scores in (strong, weak, IndicatorScores(users=100)):
            assert 0 <= adoption_rate(scores) <= 100

    def test_raising_a_weight_moves_the_rate_toward_that_indicator(self, weak):
        # Legal is weak everywhere except safe use, where it sits at 40.
        # Weighting safe use heavily should therefore lift the overall rate.
        base = adoption_rate(weak)
        weights = dict(DEFAULT_WEIGHTS)
        weights[Indicator.SAFE_USE] = 60
        assert adoption_rate(weak, weights) > base

    def test_unnormalised_weights_give_the_same_answer_as_normalised_ones(self, strong):
        doubled = {k: v * 2 for k, v in DEFAULT_WEIGHTS.items()}
        assert adoption_rate(strong, doubled) == pytest.approx(adoption_rate(strong))


# ---------------------------------------------------------------------------
# Employee level
# ---------------------------------------------------------------------------

class TestLevelAdjustment:
    def test_all_levels_changes_nothing(self, strong):
        assert adjusted_scores(strong, Level.ALL) == strong.as_dict()

    def test_support_staff_score_lower_on_behavioural_indicators(self, weak):
        adjusted = adjusted_scores(weak, Level.SUPPORT)
        assert adjusted[Indicator.ACTIVE_USERS] < weak.users

    def test_structural_indicators_are_not_adjusted(self, weak):
        # Training completion is counted from records, not estimated, so
        # seniority must not move it.
        adjusted = adjusted_scores(weak, Level.SUPPORT)
        assert adjusted[Indicator.TRAINING] == weak.train

    def test_adjustment_cannot_push_a_score_below_zero(self):
        barely = IndicatorScores(users=4)
        adjusted = adjusted_scores(barely, Level.SUPPORT)
        assert adjusted[Indicator.ACTIVE_USERS] == 0

    def test_adjustment_cannot_push_a_score_above_one_hundred(self):
        nearly = IndicatorScores(users=98)
        adjusted = adjusted_scores(nearly, Level.LEADERSHIP)
        assert adjusted[Indicator.ACTIVE_USERS] == 100


# ---------------------------------------------------------------------------
# Maturity bands
# ---------------------------------------------------------------------------

class TestBands:
    def test_bands_cover_the_whole_range_without_gaps(self):
        for lower, upper in zip(BANDS, BANDS[1:]):
            assert upper.low == lower.high + 1

    @pytest.mark.parametrize(
        "rate,expected",
        [(0, "Emerging"), (25, "Emerging"), (26, "Developing"), (50, "Developing"),
         (51, "Established"), (75, "Established"), (76, "Advanced"), (90, "Advanced"),
         (91, "Leading"), (100, "Leading")],
    )
    def test_boundaries_land_in_the_right_band(self, rate, expected):
        assert band_for(rate).name == expected

    def test_a_fractional_rate_uses_the_lower_band(self):
        # 25.4 is not yet Developing. Rounding up here would quietly promote
        # departments that have not moved.
        assert band_for(25.4).name == "Emerging"


# ---------------------------------------------------------------------------
# Organisation roll-up
# ---------------------------------------------------------------------------

def dept(name, headcount, **scores) -> DepartmentResult:
    return DepartmentResult(
        name=name,
        headcount=headcount,
        respondents=headcount,
        scores=IndicatorScores(**scores),
    )


class TestOrganisationRate:
    def test_weights_by_headcount_not_by_department(self):
        # A 9-person team at 100 and a 41-person team at 0 is not 50.
        results = [
            dept("Small", 9, users=100, freq=100, train=100, flow=100,
                 tasks=100, cover=100, prof=100, comp=100),
            dept("Large", 41),
        ]
        rate = organisation_rate(results)
        assert rate == pytest.approx(9 / 50 * 100, abs=0.1)
        assert rate < 50

    def test_empty_input_returns_none_rather_than_zero(self):
        # Zero would read as "nobody is using AI" when the truth is "no data".
        assert organisation_rate([]) is None

    def test_departments_with_no_headcount_are_skipped(self):
        results = [dept("Real", 10, users=50), dept("Empty", 0, users=100)]
        assert organisation_rate(results) == pytest.approx(adoption_rate(IndicatorScores(users=50)))


class TestReliability:
    @pytest.mark.parametrize(
        "respondents,headcount,expected",
        [(10, 10, "reliable"), (6, 10, "reliable"),
         (5, 10, "provisional"), (4, 10, "provisional"),
         (3, 10, "insufficient"), (0, 10, "insufficient")],
    )
    def test_thresholds(self, respondents, headcount, expected):
        d = DepartmentResult(name="X", headcount=headcount, respondents=respondents)
        assert d.reliability() == expected

    def test_no_headcount_is_insufficient(self):
        assert DepartmentResult(name="X", headcount=0, respondents=5).reliability() == "insufficient"


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

class TestTargetStatus:
    def test_at_target_counts_as_above(self):
        assert target_status(70, 70, 40) is TargetStatus.ABOVE

    def test_within_ten_points_is_on_track(self):
        assert target_status(61, 70, 40) is TargetStatus.ON_TRACK

    def test_more_than_ten_points_short_is_below(self):
        assert target_status(59, 70, 40) is TargetStatus.BELOW

    def test_under_the_minimum_is_critical_even_when_close_to_target(self):
        # Critical must win. A department below the floor is a risk regardless
        # of how its own target happens to be set.
        assert target_status(35, 40, 40) is TargetStatus.CRITICAL


# ---------------------------------------------------------------------------
# Wave comparison
# ---------------------------------------------------------------------------

class TestCompareWaves:
    def test_reports_the_movement_for_a_department_in_both_waves(self):
        before = [dept("Sales", 34, users=40)]
        after = [dept("Sales", 34, users=80)]
        movement = compare_waves(before, after)[0]
        assert movement.delta == pytest.approx(8.0, abs=0.01)

    def test_a_department_missing_from_a_wave_gives_none_not_zero(self):
        before = [dept("Sales", 34, users=40)]
        after = [dept("Sales", 34, users=40), dept("New Team", 5, users=10)]
        by_name = {m.name: m for m in compare_waves(before, after)}
        assert by_name["New Team"].before is None
        assert by_name["New Team"].delta is None

    def test_departments_come_back_in_a_stable_order(self):
        before = [dept("Zeta", 5), dept("Alpha", 5)]
        after = [dept("Alpha", 5)]
        assert [m.name for m in compare_waves(before, after)] == ["Alpha", "Zeta"]


class TestMovement:
    def test_delta_is_none_when_either_side_is_missing(self):
        assert Movement("X", None, 60).delta is None
        assert Movement("X", 60, None).delta is None

    def test_a_fall_is_reported_as_negative(self):
        assert Movement("X", 60, 52).delta == -8
