# How this project works

A plain English walkthrough. No prior Python needed.

---

## 1. What we are actually building

**The problem.** RAK Properties is running Claude AI training. Afterwards somebody
will ask: did it work? To answer that you need a number before the training and
the same number after, measured the same way both times.

**The solution.** A survey that everybody fills in twice, a set of rules that
turns those answers into a score out of 100 per department, and a dashboard that
shows those scores.

That is the whole system. Everything else is plumbing.

---

## 2. The three parts

Think of a restaurant.

| Part | Restaurant | Here |
|---|---|---|
| Frontend | The dining room. What customers see. | React. The dashboard on screen. |
| Backend | The kitchen. Does the work, nobody sees it. | Python. Scores the survey. |
| Database | The store room. Keeps things between services. | PostgreSQL. Holds the results. |

They talk to each other over HTTP, the same way your browser talks to any
website. The frontend asks a question, the backend answers with JSON.

```
Browser  ──asks──▶  Python API  ──reads──▶  PostgreSQL
         ◀──JSON──              ◀──rows───
```

**Important:** these are three separate programs. You can run the frontend
without the backend, which is exactly what it does today.

---

## 3. Your frontend is complete

Twenty six files under `frontend/`. It is React and TypeScript, which you already
know from the LMS.

```
frontend/
  index.html            the page the browser opens
  package.json          the dependency list
  public/data.json      survey results, as a plain file
  src/
    main.tsx            starts React
    App.tsx             lays out the page
    styles.css          all the styling, lifted from your HTML dashboard
    components/         10 files, one per section of the page
    hooks/
      useDashboard.ts   all the state lives here
    lib/
      scoring.ts        turns 8 indicators into one adoption rate
      treemap.ts        works out the size of each box
      api.ts            fetches the data
      export.ts         the Excel button
      logo.ts           the RAK logo, embedded
      sample.ts         demo figures
```

**Run it on its own:**

```bash
cd frontend
npm install
npm run dev
```

Open the address it prints. That is it. No Python, no database. It reads
`public/data.json` and draws the dashboard.

**Why it works without a backend.** `src/lib/api.ts` tries three places in order:

1. The Python API, at `/api/v1/dashboard`
2. A plain file, `data.json`, sitting next to the page
3. Built-in demo numbers

So it works today from a file, and the moment the Python API is running it uses
that instead. Nothing to change.

---

## 4. What the Python is for

You could stop at step 3 and have a working dashboard. So why Python at all?

Because of the step in between. After the survey closes you get a spreadsheet
with roughly 200 rows, one per person, with answers like "Most days" and
"4 to 6 times". The dashboard needs 13 rows, one per department, with numbers
out of 100.

Somebody has to do that conversion. Doing it by hand in Excel takes hours, and
worse, you cannot prove you did it the same way in November as in August. If the
method drifts between the two waves, the comparison is meaningless and the whole
exercise was pointless.

Python does that conversion in seconds and does it identically every time.

**That is the entire reason the backend exists.** The login, the database, the
API are all in service of that one job.

---

## 5. Python for a JavaScript developer

Only five differences matter for reading this code.

| JavaScript | Python |
|---|---|
| `{ }` braces for blocks | Indentation. Four spaces means "inside" |
| `const x = 5;` | `x = 5` (no const, no semicolon) |
| `function foo() {}` | `def foo():` |
| `// comment` | `# comment` |
| `import x from "y"` | `from y import x` |

A function looks like this:

```python
def clamp(value, low=0, high=100):
    """Keep a score between 0 and 100."""
    return max(low, min(high, value))
```

The text in triple quotes is a docstring. It is documentation, not code.
`low=0` is a default argument, same idea as JavaScript.

That is genuinely most of what you need to read every file in this project.

---

## 6. Every backend file, in plain English

### The important ones

**`app/services/scoring.py`** is the heart of the system. Given eight numbers
out of 100, it produces one adoption rate. It also decides the maturity bands
and whether a department is above target. It touches no database and no network,
which is what makes it easy to test.

**`app/services/ingest.py`** turns a raw survey spreadsheet into those eight
numbers. It finds the right columns even when the question wording changes,
converts "Most days" into 88, and handles people who skipped questions. This is
the messiest file because it deals with data made by humans.

**`app/models/models.py`** describes the eight database tables. It is the shape
of the store room: departments, waves, responses, scores, users, targets.

**`app/main.py`** is the starting point. It switches the API on and connects the
routes.

### The routes, which are the API's endpoints

Each file is a set of URLs the frontend can call.

| File | What it handles |
|---|---|
| `routes/auth.py` | Logging in, and "who am I" |
| `routes/dashboard.py` | One request that returns everything the dashboard needs |
| `routes/waves.py` | Creating a survey wave, uploading responses, publishing |
| `routes/departments.py` | Adding and renaming departments |
| `routes/config.py` | Weights and targets |

### The supporting cast

| File | Job |
|---|---|
| `app/core/config.py` | Settings: database address, secret key |
| `app/core/security.py` | Password hashing and login tokens |
| `app/db/session.py` | Opens and closes database connections |
| `app/db/base.py` | Shared bits every table has, like created date |
| `app/schemas/schemas.py` | The exact shape of every request and response |
| `app/api/deps.py` | Works out who is logged in and what they may see |
| `app/services/dashboard.py` | Gathers the data for the dashboard response |
| `scripts/seed.py` | Fills a brand new database with the 13 departments |
| `alembic/` | Creates and updates the database tables |
| `tests/` | 135 automated checks |

The `__init__.py` files are empty. Python needs them to treat a folder as
importable. Ignore them.

---

## 7. How the whole thing runs, in order

### The one command version

```bash
docker compose up --build
```

Docker starts PostgreSQL, creates the tables, and starts the Python API. Then in
a second terminal:

```bash
cd frontend
npm run dev
```

You now have a database on port 5432, an API on 8000, and the dashboard on 5173.

### The manual version, so you understand each step

```bash
cd backend

# 1. A private space for this project's Python packages,
#    the same idea as node_modules but for Python.
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install the packages, like npm install
pip install -r requirements.txt

# 3. Point it at a database
cp .env.example .env               # then edit DATABASE_URL and SECRET_KEY

# 4. Create the tables
alembic upgrade head

# 5. Put the 13 departments and your admin account in
ADMIN_EMAIL=you@rakproperties.ae ADMIN_PASSWORD='something-strong' python -m scripts.seed

# 6. Start the API
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`. FastAPI generates a page listing every
endpoint, with a Try it out button. You can log in and call the API from there
without writing any code. This is the fastest way to understand what the backend
does.

### Run the tests

```bash
DATABASE_URL="sqlite+pysqlite:///:memory:" pytest -q
```

135 checks in under a minute, no database server needed.

---

## 8. The actual working cycle, once it is live

1. Survey closes. Download responses from Microsoft Forms as Excel.
2. Log into the dashboard as an admin.
3. Create a wave, for example "Wave 1, before training".
4. Upload the Excel file, plus the HR headcount file.
5. Python scores it and reports back: how many responses, which departments,
   and any warnings such as "Operations: only 22% responded, too few to draw
   conclusions from".
6. Check the numbers. Nobody else can see them yet.
7. Press publish. Now leadership sees them.
8. After the training, repeat as Wave 2. The dashboard draws the comparison.

---

## 9. Decisions we made and why

These are worth knowing, because somebody will ask.

**Raw responses are kept, not just the scores.** If a scoring rule is ever
corrected, every wave can be re-scored from the original answers. Delete the raw
data and the numbers can never be checked again.

**Headcount is stored per wave.** People join and leave. If you recalculated
August's response rate using November's headcount, last year's conclusions would
quietly change.

**The adoption rate is never stored.** It depends on the weights, and the
weights are adjustable on screen. A saved value would eventually disagree with
what the dashboard shows.

**The organisation rate is weighted by headcount.** A 9 person team at 82% and a
41 person team at 36% is not a 59% organisation. A plain average would let small
enthusiastic teams hide the fact that most of the company is not using AI.

**Missing data shows as nothing, never as zero.** Zero reads as "adoption
collapsed". Nothing reads as "we did not measure it". Telling those two apart is
the whole reason for running the survey twice.

**A head of department sees only their own department.** The survey promised
staff that reporting would be by department, never by person. A league table
visible to everyone would change how people answer next time.

**Scored is not the same as published.** A wave that has been uploaded but not
checked is invisible to leadership. Half-checked figures reaching a board meeting
is exactly what that setting prevents.

---

## 10. What to learn first

If you want to understand the Python, read the files in this order. Each one
depends only on the ones before it.

1. `app/services/scoring.py` — pure logic, no database, well commented
2. `tests/test_scoring.py` — the same rules written as questions and answers
3. `app/models/models.py` — the shape of the database
4. `app/api/routes/auth.py` — the smallest route file, only two endpoints
5. `app/api/routes/waves.py` — the biggest one, where uploads happen

Skip `alembic/`, `__init__.py` files and `conftest.py` until you need them.

---

## 11. Where things live

```
rak-ai-adoption/
├── README.md              overview, architecture, API table
├── docker-compose.yml     runs database and API together
├── backend/               Python
│   ├── app/               the application
│   ├── alembic/           database migrations
│   ├── scripts/seed.py    starting data
│   ├── tests/             135 tests
│   └── requirements.txt   dependencies
├── frontend/              React, complete and runnable today
└── docs/
    └── HOW-IT-WORKS.md    this file
```
