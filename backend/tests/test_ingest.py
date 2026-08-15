"""
Tests for the ingest service.

These focus on the cases that actually go wrong with real survey exports:
reworded questions, blank answers, people who skipped whole sections, and
departments that appear in the survey but not in the HR file.
"""

import pandas as pd
import pytest

from app.services.ingest import (
    ColumnMap,
    DAYS_PER_WEEK,
    TIMES_PER_DAY,
    WORKFLOW_POINTS,
    find_column,
    ingest_wave,
    is_yes,
    lookup,
    map_columns,
    normalise,
    score_department,
    split_multi,
)

# ---------------------------------------------------------------------------
# Building a survey export in the shape Microsoft Forms produces
# ---------------------------------------------------------------------------

Q = {
    "department": "B1. Which department do you work in?",
    "level": "B2. Which best describes your level?",
    "used_30d": "B4. Have you used any AI tool for work in the last 30 days?",
    "tools": "C1. Which of these have you used for work in the last 30 days?",
    "top_tool": "C2. Which one do you use most?",
    "days": "C3. In a normal week, on how many days do you use AI for work?",
    "times": "C4. On a day when you use it, how many separate times do you go to an AI tool?",
    "workflow": "D1. In a normal working week, how often is AI part of how you do your job?",
    "regular_tasks": "D3. Which of these do you use AI for regularly?",
    "task_count": "D4. Roughly how many work tasks did AI help you with in the last month?",
    "coverage": "E1. Think about the tasks you repeat every week. Roughly what share of them do you now use AI for?",
    "idea1": "E2. Name up to three tasks. Task 1",
    "blockers": "E3. What stops you using AI more?",
    "account": "G1. When you use AI for work, which account do you normally use?",
    "pasted": "G2. In the last 30 days, have you put any of these into a personal AI account?",
    "training": "H1. Have you completed any AI training?",
    "F1": "F1. Which of these is the least suitable to hand to an AI tool?",
    "F4": "F4. An AI tool gives you a confident, well-written answer that turns out to be wrong. This is:",
}

RIGHT_F1 = "Deciding which contractor should be awarded a tender"
WRONG_F1 = "Drafting a reply to a routine customer enquiry"
RIGHT_F4 = "A known behaviour of these tools that you have to check for"
WRONG_F4 = "A sign the tool is broken and should be reported"


def heavy_user(department="Sales", **overrides):
    row = {
        Q["department"]: department,
        Q["level"]: "Specialist or professional",
        Q["used_30d"]: "Yes",
        Q["tools"]: "Claude, on a company account;Microsoft 365 Copilot",
        Q["top_tool"]: "Claude, on a company account",
        Q["days"]: "5 or more days",
        Q["times"]: "4 to 6 times",
        Q["workflow"]: "Every working day; it is part of my routine",
        Q["regular_tasks"]: "Writing or improving something;Summarising something long",
        Q["task_count"]: "31 to 60",
        Q["coverage"]: "More than three quarters",
        Q["idea1"]: "Summarising consultant reports",
        Q["blockers"]: "Nothing stops me, I use it as much as I want to",
        Q["account"]: "Always a company provided account",
        Q["pasted"]: "None of the above",
        Q["training"]: "Yes, RAK Properties Claude AI Basic training",
        Q["F1"]: RIGHT_F1,
        Q["F4"]: RIGHT_F4,
    }
    row.update(overrides)
    return row


def non_user(department="Sales", **overrides):
    row = {
        Q["department"]: department,
        Q["level"]: "Support, administrative, technical or site staff",
        Q["used_30d"]: "No, never",
        Q["blockers"]: "I do not know how to start",
        Q["training"]: "No, none",
        Q["F1"]: WRONG_F1,
        Q["F4"]: WRONG_F4,
    }
    row.update(overrides)
    return row


def frame(rows):
    return pd.DataFrame(rows)


HEADCOUNTS = {
    "sales": {"name": "Sales", "staff": 10, "function": "Commercial"},
    "legal": {"name": "Legal", "staff": 10, "function": "Corporate Services"},
}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

class TestNormalise:
    def test_collapses_whitespace_and_lowercases(self):
        assert normalise("  Most   Days\n") == "most days"

    def test_none_becomes_an_empty_string(self):
        assert normalise(None) == ""


class TestSplitMulti:
    def test_splits_the_semicolon_separated_answer_forms_produces(self):
        assert split_multi("Claude;Copilot") == ["Claude", "Copilot"]

    def test_blank_answers_give_an_empty_list(self):
        assert split_multi(None) == []
        assert split_multi(float("nan")) == []

    def test_stray_separators_do_not_create_empty_entries(self):
        assert split_multi("Claude;;Copilot;") == ["Claude", "Copilot"]


class TestIsYes:
    @pytest.mark.parametrize("answer", ["Yes", "yes", "Yes, the Basic training"])
    def test_recognises_a_yes(self, answer):
        assert is_yes(answer)

    @pytest.mark.parametrize("answer", ["No, never", "No, but I have used one before", None, ""])
    def test_everything_else_is_not_a_yes(self, answer):
        # "No, but I have used one before" must not count. It is a no for the
        # last 30 days, which is what the indicator measures.
        assert not is_yes(answer)


class TestLookup:
    def test_finds_the_phrase_anywhere_in_the_answer(self):
        assert lookup("Every working day; it is part of my routine", WORKFLOW_POINTS) == 100

    def test_a_blank_answer_returns_the_default(self):
        assert lookup("", WORKFLOW_POINTS, default=0) == 0

    def test_an_unrecognised_answer_returns_the_default(self):
        assert lookup("Sometimes I suppose", WORKFLOW_POINTS, default=0) == 0

    def test_longer_phrases_win_over_shorter_ones_they_contain(self):
        # "less than one day" contains "1 day" as a substring risk; ordering in
        # the table must resolve it to 0.5, not 1.0.
        assert lookup("Less than one day", DAYS_PER_WEEK) == 0.5

    def test_more_than_ten_is_not_read_as_ten(self):
        assert lookup("More than 10 times", TIMES_PER_DAY) == 12.0


# ---------------------------------------------------------------------------
# Column matching
# ---------------------------------------------------------------------------

class TestFindColumn:
    def test_matches_on_a_distinctive_phrase_not_the_whole_heading(self):
        columns = ["B4. Have you used any AI tool for work in the last 30 days?"]
        assert find_column(columns, ("used any ai tool for work in the last 30",)) == columns[0]

    def test_survives_the_question_being_reworded_around_the_phrase(self):
        columns = ["4. Hi! Have you used any AI tool for work in the last 30 days at all?"]
        assert find_column(columns, ("used any ai tool for work in the last 30",)) is not None

    def test_returns_none_when_nothing_matches(self):
        assert find_column(["Timestamp", "Email"], ("department",)) is None


class TestMapColumns:
    def test_reports_which_questions_it_could_not_find(self):
        mapping = map_columns(frame([{"Timestamp": 1, Q["department"]: "Sales"}]))
        assert "used_30d" in mapping.missing
        assert "department" not in mapping.missing

    def test_finds_the_knowledge_check_columns(self):
        mapping = map_columns(frame([heavy_user()]))
        assert mapping.knowledge["F1"] == Q["F1"]
        assert mapping.knowledge["F9"] is None

    def test_collects_every_free_text_idea_box(self):
        mapping = map_columns(frame([heavy_user()]))
        assert Q["idea1"] in mapping.ideas


# ---------------------------------------------------------------------------
# Scoring a department
# ---------------------------------------------------------------------------

class TestScoreDepartment:
    def test_a_department_of_heavy_users_scores_near_the_top(self):
        rows = [heavy_user() for _ in range(4)]
        mapping = map_columns(frame(rows))
        scores, _, users = score_department(frame(rows).to_dict("records"), mapping)
        assert users == 4
        assert scores.users == 100
        assert scores.flow == 100
        assert scores.freq == 100          # 5 days x 5 sessions, capped
        assert scores.comp == 100

    def test_a_department_of_non_users_scores_zero_on_usage(self):
        rows = [non_user() for _ in range(4)]
        mapping = map_columns(frame(rows))
        scores, _, users = score_department(frame(rows).to_dict("records"), mapping)
        assert users == 0
        assert (scores.users, scores.freq, scores.flow, scores.tasks, scores.cover) == (0, 0, 0, 0, 0)

    def test_non_users_stay_in_the_denominator(self):
        # Three keen users among ten people is not a fully adopted department.
        rows = [heavy_user() for _ in range(3)] + [non_user() for _ in range(7)]
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.users == 30
        assert scores.flow == pytest.approx(30, abs=0.1)

    def test_safe_use_ignores_non_users_rather_than_scoring_them_full_marks(self):
        # Otherwise a department earns a perfect safety score by not using AI.
        rows = [heavy_user(), non_user(), non_user()]
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.comp == 100

    def test_pasting_sensitive_data_into_a_personal_account_costs_points(self):
        rows = [heavy_user(**{
            Q["account"]: "Mostly a personal account",
            Q["pasted"]: "Customer or buyer personal details;Contract or legal text",
        })]
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.comp == pytest.approx(100 - 25 - 12 - 12)

    def test_the_safe_use_score_never_goes_below_zero(self):
        rows = [heavy_user(**{
            Q["account"]: "Always a personal account",
            Q["pasted"]: ("Customer or buyer personal details;Financial figures that are not public;"
                          "Contract or legal text;Internal strategy, board or project documents;"
                          "Employee or HR information"),
        })]
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.comp == 0

    def test_everyone_answers_the_knowledge_check_including_non_users(self):
        rows = [heavy_user(), non_user()]     # one all right, one all wrong
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.prof == 50

    def test_missing_answers_do_not_crash_the_scorer(self):
        rows = [heavy_user(**{Q["days"]: None, Q["workflow"]: "", Q["coverage"]: None})]
        mapping = map_columns(frame(rows))
        scores, _, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert scores.freq == 0
        assert scores.flow == 0

    def test_an_empty_department_returns_zeros_rather_than_dividing_by_zero(self):
        mapping = map_columns(frame([heavy_user()]))
        scores, evidence, users = score_department([], mapping)
        assert users == 0
        assert scores.users == 0
        assert evidence.gap == "Not recorded"


class TestEvidence:
    def test_top_tools_are_a_share_of_users_not_of_everyone(self):
        rows = [heavy_user(), non_user()]
        mapping = map_columns(frame(rows))
        _, evidence, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert evidence.tools[0][1] == 100

    def test_the_opportunity_is_the_most_repeated_idea_not_the_first_typed(self):
        rows = [
            heavy_user(**{Q["idea1"]: "One-off thing nobody else said"}),
            heavy_user(**{Q["idea1"]: "Summarising consultant reports"}),
            heavy_user(**{Q["idea1"]: "Summarising consultant reports"}),
        ]
        mapping = map_columns(frame(rows))
        _, evidence, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert evidence.opportunity == "Summarising consultant reports"

    def test_nothing_stops_me_is_not_reported_as_a_gap(self):
        rows = [heavy_user() for _ in range(3)]
        mapping = map_columns(frame(rows))
        _, evidence, _ = score_department(frame(rows).to_dict("records"), mapping)
        assert evidence.gap == "Not recorded"


# ---------------------------------------------------------------------------
# Whole wave
# ---------------------------------------------------------------------------

class TestIngestWave:
    def test_groups_responses_by_department(self):
        rows = [heavy_user("Sales"), heavy_user("Sales"), non_user("Legal")]
        results, report = ingest_wave(frame(rows), HEADCOUNTS)
        assert report.departments == 2
        assert sorted(r.name for r in results) == ["Legal", "Sales"]

    def test_uses_the_hr_headcount_not_the_number_who_replied(self):
        rows = [heavy_user("Sales") for _ in range(4)]
        results, _ = ingest_wave(frame(rows), HEADCOUNTS)
        sales = results[0]
        assert sales.headcount == 10
        assert sales.respondents == 4
        assert sales.response_rate == 40.0

    def test_flags_a_department_whose_response_rate_is_too_low(self):
        rows = [heavy_user("Sales") for _ in range(2)]     # 2 of 10
        _, report = ingest_wave(frame(rows), HEADCOUNTS)
        assert any("too few to draw conclusions" in w for w in report.warnings)

    def test_flags_a_safe_use_score_based_on_a_handful_of_users(self):
        rows = [heavy_user("Sales") for _ in range(4)] + [non_user("Sales") for _ in range(4)]
        _, report = ingest_wave(frame(rows), HEADCOUNTS)
        assert any("safe-use score is based on" in w for w in report.warnings)

    def test_reports_a_department_missing_from_the_hr_file(self):
        rows = [heavy_user("Marketing & Communications")]
        _, report = ingest_wave(frame(rows), HEADCOUNTS)
        assert "Marketing & Communications" in report.unmatched_departments

    def test_warns_when_no_headcount_file_was_supplied(self):
        rows = [heavy_user("Sales")]
        _, report = ingest_wave(frame(rows), {})
        assert any("No headcount file" in w for w in report.warnings)

    def test_blank_department_answers_are_skipped(self):
        rows = [heavy_user("Sales"), heavy_user(""), heavy_user(None)]
        results, _ = ingest_wave(frame(rows), HEADCOUNTS)
        assert len(results) == 1

    def test_department_names_match_regardless_of_case_and_spacing(self):
        rows = [heavy_user("  sales "), heavy_user("SALES")]
        results, report = ingest_wave(frame(rows), HEADCOUNTS)
        assert len(results) == 1
        assert results[0].name == "Sales"          # display name from the HR file
        assert report.unmatched_departments == []

    def test_a_missing_department_question_is_a_clear_error(self):
        with pytest.raises(ValueError, match="department question"):
            ingest_wave(frame([{"Timestamp": 1, "Anything": 2}]), HEADCOUNTS)

    def test_the_report_says_how_many_knowledge_questions_were_found(self):
        _, report = ingest_wave(frame([heavy_user("Sales")]), HEADCOUNTS)
        assert report.knowledge_questions_found == 2      # only F1 and F4 in the fixture
