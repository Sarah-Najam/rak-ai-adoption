# AI Adoption Index

Measures how effectively each department in an organisation is adopting AI, and
whether training actually changes that.

Built for RAK Properties, a UAE property developer running an internal Claude AI
training programme, who needed to answer one question honestly: did it work?

![React](https://img.shields.io/badge/React-18-black)
![TypeScript](https://img.shields.io/badge/TypeScript-strict-black)
![Python](https://img.shields.io/badge/Python-3.12-black)
![FastAPI](https://img.shields.io/badge/FastAPI-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-black)
![Tests](https://img.shields.io/badge/tests-135%20passing-black)

---

## The problem

Most AI adoption reporting counts logins. That number is easy to get and close
to worthless.

A department where every person opened the tool once out of curiosity and never
returned looks identical to one where AI is genuinely part of the daily work.
Same login count, completely different reality. Adoption is not access. Adoption
is whether the work changed.

So this measures eight indicators instead, normalises each to a 0-100 score, and
combines them with weights the organisation controls.

| Indicator | Weight | The question behind it |
|---|---|---|
| Active AI users | 20% | Is anyone using it at all? |
| Usage frequency | 15% | Occasionally, or as a habit? |
| Training completion | 15% | Have people been shown how? |
| AI in weekly workflow | 15% | Is it part of the job, or a novelty? |
| AI-assisted task volume | 10% | How much work does it actually touch? |
| Eligible workflows covered | 10% | Of the work that could use AI, how much does? |
| Proficiency | 10% | Do people know how to use it well? |
| Safe use of AI | 5% | Is it happening inside approved accounts? |

The weights are adjustable in the interface. That is what turns the dashboard
from a report into an argument leadership can have: if proficiency matters more
to you than raw usage, move the slider and watch the ranking change.

---

## The interface

The primary view is a **squarified treemap**. Each department is a box, and the
area of the box is its adoption rate, so the question people actually ask (who
is ahead, who is behind) is answered by size before anyone reads a number.

The layout is implemented from the algorithm rather than taken from a charting
library. A naive treemap slices the rectangle the same way every time and
produces long thin slivers that cannot be compared by eye. The squarified
version builds rows and keeps adding to a row while the worst aspect ratio in it
improves, which keeps every box close to square.

Also included: drill-down per department, wave-over-wave trends, maturity bands,
editable targets, six filters, and Excel export.

---

## Architecture

```
   Survey responses (xlsx/csv)
              |
              v
   +------------------------+
   |  Ingest + scoring      |   pandas, pure functions
   |  FastAPI service       |   fully unit tested
   +------------------------+
              |
              v
        PostgreSQL              raw responses + derived scores
              |
              v
   +------------------------+
   |  REST API              |   JWT auth, four roles
   +------------------------+
              |  JSON
              v
   +------------------------+
   |  React + TypeScript    |   treemap, drill-down, live weighting
   +------------------------+
```

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL
**Frontend:** React 18, TypeScript (strict), Vite, hand-rolled SVG charting
**Infrastructure:** Docker Compose, deployable to Vercel, Render and Neon

---

## Design decisions

The interesting part of this project is not the CRUD. It is the set of decisions
below, each of which has a test pinning it down.

**The organisation rate is weighted by headcount.**
A 9-person team at 82% and a 41-person team at 36% is not a 59% organisation. An
unweighted mean lets small enthusiastic teams hide the fact that most of the
company is not using AI.

**Missing data returns null, never zero.**
Zero reads as "adoption collapsed". Null reads as "we did not measure it". The
distinction is the entire point of running the survey twice, so it survives all
the way from the scoring model to the gap in the trend line.

**The adoption rate is never stored.**
It depends on the weights, and the weights are adjustable at runtime. A stored
value would eventually disagree with what the screen shows.

**Raw survey responses are kept alongside the calculated scores.**
Scores are derived data. If a scoring rule is corrected, every wave can be
re-scored from the original answers. Discard the raw responses and the numbers
become permanently unauditable.

**Headcount is versioned per wave.**
People join and leave. Recalculating an old response rate against today's
headcount would quietly rewrite last year's conclusions.

**Weights are versioned, not overwritten.**
When leadership changes what adoption means, the previous set stays so an
earlier report remains reproducible.

**Response rate gates publication.**
With no telemetry behind the numbers, a department's score is only as good as
who answered. Above 60% it is reliable, 40 to 60% provisional, below 40% no
conclusions are drawn. Enforced in the model, not left to whoever writes the
slide.

**Scored is not published.**
A wave that has been imported but not checked is visible to admins only.
Half-checked figures reaching a board meeting is exactly what that status
prevents.

**Access is scoped by role.**
A head of department sees only their own department. The survey promised staff
that reporting stays at department level, and a league table visible to everyone
would change how people answer the next round.

---

## Testing

```bash
cd backend
DATABASE_URL="sqlite+pysqlite:///:memory:" pytest -q
# 135 passed
```

| Area | Tests | Focus |
|---|---|---|
| Scoring model | 53 | Weighting, maturity bands, level adjustments, wave comparison |
| Ingest | 45 | Reworded questions, blank answers, non-users, thin samples |
| API | 37 | Authentication, role scoping, upload, publication rules |

The scoring model is written as pure functions with no database and no HTTP,
which is what makes that level of coverage cheap. The suite runs on in-memory
SQLite, because tests that need infrastructure are tests people stop running.

The API tests are weighted towards access control, since a mistake there is
silent: a broken chart is obvious the moment somebody looks at it, a head of
department seeing every other team's score is not.

---

## Running it

```bash
# everything: Postgres, migrations, API
docker compose up --build

# frontend
cd frontend
npm install
npm run dev
```

Dashboard on `localhost:5173`, API docs on `localhost:8000/docs`.

The frontend also runs standalone against a static `data.json`, with no backend
at all. `loadDashboard` tries the API first, then the published file, then
built-in samples, so the same build works as a static site or as a full
application.

---

## Structure

```
backend/
  app/
    services/scoring.py    the model, pure and fully tested
    services/ingest.py     survey export to department scores
    api/routes/            auth, dashboard, waves, departments, config
    models/                SQLAlchemy schema
  alembic/                 migrations
  tests/                   135 tests
frontend/
  src/
    lib/treemap.ts         squarified treemap layout
    lib/scoring.ts         client-side weighting for live sliders
    hooks/useDashboard.ts  single source of truth for UI state
    components/            one per section of the page
docs/                      architecture, deployment, survey design
```

---

## A note on the data

The figures in this repository are illustrative samples, not measured results.
The dashboard says so on screen whenever it is running on them.

The underlying survey is self-reported, so absolute levels run high: people
remember the weeks they used a tool and forget the weeks they did not. What the
system is designed to measure is the **change between waves**, where the same
people answer the same questions and the overstatement largely cancels out.
