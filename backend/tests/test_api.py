"""
API tests.

Weighted towards access control, because that is where a mistake is silent. A
broken chart is obvious the moment somebody looks at it; a head of department
who can see every other department's score is not, and it breaks the promise the
survey made to staff.
"""

import io

import pandas as pd
import pytest

from app.models.models import Role, WaveStatus
from tests.conftest import PASSWORD


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_needs_no_authentication(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_valid_credentials_return_a_token(self, client, users):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": users["admin"].email, "password": PASSWORD},
        )
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        assert response.json()["access_token"]

    def test_wrong_password_is_rejected(self, client, users):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": users["admin"].email, "password": "not-it"},
        )
        assert response.status_code == 401

    def test_unknown_email_gives_the_same_message_as_a_wrong_password(self, client, users):
        # Different messages would turn the login form into a way of finding out
        # who works here.
        unknown = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@rakproperties.ae", "password": PASSWORD},
        )
        wrong = client.post(
            "/api/v1/auth/login",
            json={"email": users["admin"].email, "password": "not-it"},
        )
        assert unknown.status_code == wrong.status_code == 401
        assert unknown.json()["detail"] == wrong.json()["detail"]

    def test_a_deactivated_account_cannot_log_in(self, client, users):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": users["disabled"].email, "password": PASSWORD},
        )
        assert response.status_code == 401

    def test_the_password_hash_is_never_returned(self, client, auth):
        response = client.get("/api/v1/auth/me", headers=auth("admin"))
        assert response.status_code == 200
        assert "hashed_password" not in response.json()
        assert "password" not in response.json()


class TestAuthentication:
    def test_a_protected_route_rejects_an_anonymous_caller(self, client):
        assert client.get("/api/v1/dashboard").status_code == 401

    def test_a_protected_route_rejects_a_nonsense_token(self, client):
        response = client.get(
            "/api/v1/dashboard", headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert response.status_code == 401

    def test_me_returns_the_signed_in_user(self, client, auth, users):
        response = client.get("/api/v1/auth/me", headers=auth("hod"))
        assert response.status_code == 200
        assert response.json()["email"] == users["hod"].email
        assert response.json()["role"] == Role.HOD.value


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

class TestAccessControl:
    def test_leadership_sees_every_department(self, client, auth, published_wave):
        payload = client.get("/api/v1/dashboard", headers=auth("leadership")).json()
        names = {d["name"] for d in payload["waves"][0]["departments"]}
        assert names == {"Information Technology", "Operations"}

    def test_a_head_of_department_sees_only_their_own(self, client, auth, published_wave):
        payload = client.get("/api/v1/dashboard", headers=auth("hod")).json()
        names = {d["name"] for d in payload["waves"][0]["departments"]}
        assert names == {"Information Technology"}

    def test_a_viewer_sees_no_department_breakdown(self, client, auth, published_wave):
        # Viewers get the organisation picture without a league table of teams.
        payload = client.get("/api/v1/dashboard", headers=auth("viewer")).json()
        assert payload["waves"][0]["departments"] == []

    def test_a_viewer_cannot_change_the_weights(self, client, auth):
        response = client.put(
            "/api/v1/config/weights",
            headers=auth("viewer"),
            json={"weights": {"users": 100}, "name": "Mine"},
        )
        assert response.status_code == 403

    def test_a_head_of_department_cannot_create_departments(self, client, auth):
        response = client.post(
            "/api/v1/departments", headers=auth("hod"), json={"name": "New", "function": "X"}
        )
        assert response.status_code == 403

    def test_leadership_can_change_the_weights(self, client, auth, published_wave):
        response = client.put(
            "/api/v1/config/weights",
            headers=auth("leadership"),
            json={"weights": {"users": 40, "freq": 10}, "name": "Usage first"},
        )
        assert response.status_code == 200
        assert response.json()["users"] == 40


# ---------------------------------------------------------------------------
# Dashboard payload
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_returns_waves_weights_and_targets(self, client, auth, published_wave):
        payload = client.get("/api/v1/dashboard", headers=auth("leadership")).json()
        assert set(payload) == {"waves", "weights", "targets"}
        assert payload["targets"]["org"] == 70
        assert payload["weights"]["users"] == 20

    def test_each_department_carries_all_eight_indicators(self, client, auth, published_wave):
        payload = client.get("/api/v1/dashboard", headers=auth("leadership")).json()
        metrics = payload["waves"][0]["departments"][0]["metrics"]
        assert set(metrics) == {"users", "freq", "train", "flow", "tasks", "cover", "prof", "comp"}

    def test_an_unpublished_wave_is_hidden_from_leadership(self, client, auth, db, published_wave):
        # Scored but unchecked figures must not reach leadership by accident.
        published_wave.status = WaveStatus.SCORED
        db.commit()
        payload = client.get("/api/v1/dashboard", headers=auth("leadership")).json()
        assert payload["waves"] == []

    def test_an_admin_can_see_a_scored_wave_before_it_is_published(self, client, auth, db, published_wave):
        published_wave.status = WaveStatus.SCORED
        db.commit()
        payload = client.get("/api/v1/dashboard", headers=auth("admin")).json()
        assert len(payload["waves"]) == 1

    def test_reliability_is_reported_with_every_department(self, client, auth, published_wave):
        payload = client.get("/api/v1/dashboard", headers=auth("leadership")).json()
        for department in payload["waves"][0]["departments"]:
            assert department["reliability"] in {"reliable", "provisional", "insufficient"}


# ---------------------------------------------------------------------------
# Departments
# ---------------------------------------------------------------------------

class TestDepartments:
    def test_creating_a_department(self, client, auth):
        response = client.post(
            "/api/v1/departments",
            headers=auth("leadership"),
            json={"name": "Legal", "function": "Corporate Services"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Legal"

    def test_duplicate_names_are_refused(self, client, auth, departments):
        response = client.post(
            "/api/v1/departments",
            headers=auth("leadership"),
            json={"name": "Operations", "function": "Technical"},
        )
        assert response.status_code == 409

    def test_deleting_retires_rather_than_removes(self, client, auth, departments, db):
        target = departments["ops"]
        assert client.delete(f"/api/v1/departments/{target.id}", headers=auth("admin")).status_code == 204
        db.refresh(target)
        # The row survives, so historical waves still point at something real.
        assert target.is_active is False


# ---------------------------------------------------------------------------
# Waves and upload
# ---------------------------------------------------------------------------

def survey_csv() -> bytes:
    rows = []
    for _ in range(6):
        rows.append({
            "B1. Which department do you work in?": "Information Technology",
            "B4. Have you used any AI tool for work in the last 30 days?": "Yes",
            "C3. In a normal week, on how many days do you use AI for work?": "5 or more days",
            "C4. On a day when you use it, how many separate times do you go to an AI tool?": "4 to 6 times",
            "D1. In a normal working week, how often is AI part of how you do your job?": "Most days",
            "D4. Roughly how many work tasks did AI help you with in the last month?": "16 to 30",
            "E1. Think about the tasks you repeat every week. Roughly what share of them do you now use AI for?": "More than three quarters",
            "G1. When you use AI for work, which account do you normally use?": "Always a company provided account",
            "G2. In the last 30 days, have you put any of these into a personal AI account?": "None of the above",
            "H1. Have you completed any AI training?": "Yes, RAK Properties Claude AI Basic training",
        })
    return pd.DataFrame(rows).to_csv(index=False).encode()


class TestWaves:
    def test_creating_a_wave(self, client, auth):
        response = client.post(
            "/api/v1/waves", headers=auth("leadership"),
            json={"label": "Wave 2 (after training)", "sequence": 2},
        )
        assert response.status_code == 201
        assert response.json()["status"] == WaveStatus.DRAFT.value

    def test_duplicate_sequence_is_refused(self, client, auth, published_wave):
        response = client.post(
            "/api/v1/waves", headers=auth("leadership"),
            json={"label": "Another wave 1", "sequence": 1},
        )
        assert response.status_code == 409

    def test_uploading_responses_scores_the_wave(self, client, auth, departments):
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Wave 1", "sequence": 1}
        ).json()

        response = client.post(
            f"/api/v1/waves/{created['id']}/responses",
            headers=auth("admin"),
            files={"file": ("wave1.csv", io.BytesIO(survey_csv()), "text/csv")},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["responses"] == 6
        assert body["departments"] == 1

    def test_upload_warns_about_a_thin_response_rate(self, client, auth, departments):
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Wave 1", "sequence": 1}
        ).json()
        headcount = pd.DataFrame(
            [{"Department": "Information Technology", "Total headcount": 40}]
        ).to_csv(index=False).encode()

        body = client.post(
            f"/api/v1/waves/{created['id']}/responses",
            headers=auth("admin"),
            files={
                "file": ("wave1.csv", io.BytesIO(survey_csv()), "text/csv"),
                "headcount_file": ("hc.csv", io.BytesIO(headcount), "text/csv"),
            },
        ).json()
        assert any("too few to draw conclusions" in w for w in body["warnings"])

    def test_a_draft_wave_cannot_be_published(self, client, auth):
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Empty", "sequence": 9}
        ).json()
        response = client.post(f"/api/v1/waves/{created['id']}/publish", headers=auth("admin"))
        assert response.status_code == 400

    def test_publishing_a_scored_wave(self, client, auth, departments):
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Wave 1", "sequence": 1}
        ).json()
        client.post(
            f"/api/v1/waves/{created['id']}/responses",
            headers=auth("admin"),
            files={"file": ("wave1.csv", io.BytesIO(survey_csv()), "text/csv")},
        )
        response = client.post(f"/api/v1/waves/{created['id']}/publish", headers=auth("admin"))
        assert response.status_code == 200
        assert response.json()["status"] == WaveStatus.PUBLISHED.value

    def test_uploading_twice_replaces_rather_than_doubles(self, client, auth, departments):
        # Merging would double-count anyone in both files, and the resulting
        # numbers would be wrong in a way nobody could see.
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Wave 1", "sequence": 1}
        ).json()
        for _ in range(2):
            body = client.post(
                f"/api/v1/waves/{created['id']}/responses",
                headers=auth("admin"),
                files={"file": ("wave1.csv", io.BytesIO(survey_csv()), "text/csv")},
            ).json()
        assert body["responses"] == 6

    def test_an_unreadable_file_is_a_clear_error(self, client, auth):
        created = client.post(
            "/api/v1/waves", headers=auth("admin"), json={"label": "Wave 1", "sequence": 1}
        ).json()
        response = client.post(
            f"/api/v1/waves/{created['id']}/responses",
            headers=auth("admin"),
            files={"file": ("broken.csv", io.BytesIO(b"\x00\x01\x02"), "text/csv")},
        )
        assert response.status_code == 400

    def test_uploading_to_a_missing_wave_is_a_404(self, client, auth):
        response = client.post(
            "/api/v1/waves/9999/responses",
            headers=auth("admin"),
            files={"file": ("wave1.csv", io.BytesIO(survey_csv()), "text/csv")},
        )
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class TestConfiguration:
    def test_weights_are_versioned_not_overwritten(self, client, auth, db, published_wave):
        from app.models.models import WeightSet

        client.put(
            "/api/v1/config/weights",
            headers=auth("leadership"),
            json={"weights": {"users": 50}, "name": "Usage first"},
        )
        rows = db.query(WeightSet).all()
        # The old set survives so an earlier report stays reproducible.
        assert len(rows) == 2
        assert sum(1 for r in rows if r.is_active) == 1

    def test_missing_indicators_fall_back_to_the_defaults(self, client, auth, published_wave):
        response = client.put(
            "/api/v1/config/weights",
            headers=auth("leadership"),
            json={"weights": {"users": 50}, "name": "Partial"},
        )
        body = response.json()
        assert body["users"] == 50
        assert body["comp"] == 5     # untouched, from the defaults

    def test_setting_targets(self, client, auth, published_wave):
        response = client.put(
            "/api/v1/config/targets",
            headers=auth("leadership"),
            json={"org": 75, "quarter": 68, "minimum": 45, "by_department": {}},
        )
        assert response.status_code == 200
        assert response.json()["org"] == 75
        assert response.json()["min"] == 45

    @pytest.mark.parametrize("value", [-5, 105])
    def test_targets_outside_zero_to_one_hundred_are_refused(self, client, auth, value):
        response = client.put(
            "/api/v1/config/targets",
            headers=auth("leadership"),
            json={"org": value, "quarter": 60, "minimum": 40, "by_department": {}},
        )
        assert response.status_code == 422
