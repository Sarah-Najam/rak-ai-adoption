# AI Adoption Index · Complete Guide

Everything about this project in one place: the problem, the design, how to
demo it, and how to load real survey data.

---

# PART 1 · The problem

## Why this exists

RAK Properties is running a Claude AI Training Programme. Each head of
department nominates around two people. Basic training in August, Advanced in
September.

At some point, someone in leadership will ask: **did it work?**

That question is impossible to answer unless you measured something before the
training and measure the same thing again afterwards. Which is what this system
does.

## Why not just count logins

The obvious approach is to pull usage numbers from the tool admin consoles and
count how many people logged in. That number is easy to get and close to
worthless.

A department where every person opened Claude once, out of curiosity, and never
returned looks identical to a department where AI is genuinely part of the daily
work. Same login count, completely different reality.

Adoption is not access. Adoption is whether the work changed.

## What we measure instead

Eight indicators, each scored out of 100, combined into one number.

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

The weights are adjustable on screen. This matters more than it sounds. It turns
the dashboard from a report into an argument leadership can have: if you think
proficiency matters more than raw usage, move the slider and watch the ranking
change.

---

# PART 2 · How it was built

## The three parts

```
   Survey responses (Excel)
             │
             ▼
   ┌──────────────────┐
   │  Python backend  │   scores the responses
   │  FastAPI         │   stores them
   └──────────────────┘
             │  JSON over HTTP
             ▼
   ┌──────────────────┐
   │  React frontend  │   draws the dashboard
   └──────────────────┘
```

**Frontend:** React, TypeScript, Vite. No chart library. The treemap is written
from the algorithm.

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL. 135 automated tests.

**Database:** eight tables. Raw responses kept alongside calculated scores.

## Why the treemap

Leadership does not read tables. They look at a screen for four seconds and want
to know who is ahead and who is behind.

In a treemap, each department is a box and the **area of the box is its adoption
rate**. Size answers the question before anyone reads a number. Colour carries
the maturity band on top of that, so the picture works from across a room.

The layout uses the squarified treemap algorithm. A naive treemap slices the
rectangle the same way every time and produces long thin slivers that are
impossible to compare by eye. The squarified version builds rows and keeps
adding to a row while the worst aspect ratio in it improves, which keeps every
box close to square. That is the difference between a chart people read and a
chart people ignore.

## Why the survey and not telemetry

Four of the eight indicators cannot be measured by any system. No admin console
knows whether AI is part of how you do your job, or how much of your repeated
work could use it, or whether you understand that a confident answer can still
be wrong.

So the data comes from a survey run twice: before the training and six to eight
weeks after. Not immediately after, because what you would measure then is
enthusiasm, not adoption. Habits either survive the return to normal workload or
they do not, and six weeks is long enough to find out.

## The honest caveat, which you should say out loud

Self-reported numbers always run high. People remember the weeks they used a
tool and forget the weeks they did not, and nobody wants to answer "never".

So the absolute level is approximate. **The change between the two waves is the
real result**, because the same people answer the same questions both times and
the overstatement largely cancels out.

Say this before someone else does. It costs nothing and it protects every other
number you present.

---

# PART 3 · Design decisions worth defending

These are the questions a sharp colleague will ask.

**"Why is the organisation number not just the average of the departments?"**

Because it is weighted by headcount. A 9-person team at 82% and a 41-person team
at 36% is not a 59% organisation. A plain average would let small enthusiastic
teams hide the fact that most of the company is not using AI.

**"What happens if a department is missing from one wave?"**

Its line shows a gap, not a drop to zero. Zero reads as "adoption collapsed".
A gap reads as "we did not measure it". Telling those apart is the entire reason
for running the survey twice.

**"Why keep the raw survey responses if you already have the scores?"**

Scores are derived data. If a scoring rule is ever corrected, every wave can be
re-scored from the original answers. Throw the raw data away and the numbers can
never be checked again.

**"Why is headcount stored per wave rather than once?"**

People join and leave. If you recalculated August's response rate using
November's headcount, last year's conclusions would quietly change.

**"Why is the adoption rate not stored in the database?"**

Because it depends on the weights, and the weights are adjustable on screen. A
stored value would eventually disagree with what the dashboard shows.

**"Can everyone see every department's score?"**

No, and deliberately. A head of department sees only their own. The survey
promised staff that reporting would be by department and never by person, and a
league table visible to everyone would change how people answer next time.

**"What stops half-checked numbers reaching the board?"**

A wave has a status. Uploaded and scored is not the same as published. Scored
figures are visible only to admins until someone presses publish.

**"What if only four people in a department answer?"**

The system flags it. Above 60% response rate a score is reliable, 40 to 60% is
provisional, below 40% no conclusions are drawn. That rule is enforced in the
code, not left to whoever writes the slide.

---

# PART 4 · Demo script

Twelve minutes. Do not explain the architecture unless someone asks.

## 1. Open with the question, not the tool (30 seconds)

> "We are about to train people on Claude. In six months someone will ask
> whether it worked. This is how we answer that with evidence instead of
> anecdote."

## 2. The headline number (1 minute)

Point at the big percentage.

> "This is the organisation-wide adoption rate. It is not a login count. It
> combines eight things, including whether AI is actually part of people's
> weekly work."

Point at the gold marker on the bar.

> "That is our target. We are currently short of it."

## 3. The grid, which is the whole point (3 minutes)

> "Every box is a department. **The size of the box is the adoption rate.**"

Let them look for a few seconds. Someone will spot Operations.

> "You can see the problem without me telling you. IT is our largest box. Legal
> is the smallest. And Operations, which has the most people of any department,
> is down here in the corner."

Hover over a box.

> "Quick read on hover."

Click it.

> "And the full picture on click: active users, training completion, which
> tools they actually use, and the gap and opportunity in their own words from
> the survey."

## 4. The part that makes it a tool, not a report (2 minutes)

Scroll to the scoring model. Drag the proficiency slider up.

> "The weights are yours to set. If you think knowing how to use AI properly
> matters more than raw usage, move this, and the ranking changes live. This is
> a decision you make, not one the dashboard makes for you."

Move it back.

## 5. Targets (1 minute)

> "You set an organisation target, department targets, and a minimum acceptable
> rate. Anything below the minimum shows as critical regardless of its own
> target, because a department under the floor is a risk either way."

## 6. Trends (1 minute)

> "Right now there is one point, because we have one survey wave. After the
> training we run the same survey again and this becomes the answer to 'did it
> work'. Nothing here is projected or estimated. Each point is a real wave."

## 7. Close with the honest caveat (1 minute)

> "One thing to be clear about. These are self-reported numbers, so the level
> is approximate. What we trust is the change between waves, because the same
> people answer the same questions both times."

## 8. Then ask them for decisions (2 minutes)

- Do we agree on these eight indicators and their weights?
- What is the organisation target?
- Do we agree reporting stays at department level, never individual?
- Who signs off before results are published?

## Questions you will be asked

**"Where does the data come from?"**
A ten-minute survey everyone fills in, twice. Plus a headcount file from HR.

**"How long does it take to update?"**
Upload the survey export. The system scores it in seconds.

**"Can we add or rename departments?"**
Yes, without a developer.

**"What if people lie?"**
Some will overstate. It is the same overstatement in both waves, so the
comparison still holds. And the knowledge check in the survey has right and
wrong answers, which cannot be talked up.

**"Why is Marketing high and Legal low?"**
Marketing does a lot of drafting work, which AI suits today. Legal has real
confidentiality constraints and no approved workflow for legal documents. The
drill-down shows exactly that.

---

# PART 5 · Loading real survey data

Three routes, from simplest to most automated. All three produce the same
result.

## Route A · Edit the file by hand

Best for the first wave, when there are 13 departments and you want to see
exactly what is happening.

1. Score the survey responses per department using the rules in the survey
   document, Part J. A pivot table does most of it.
2. Open `standalone/data.json` (or `frontend/public/data.json`) in VS Code.
3. Replace the numbers. The shape is:

```json
{
  "waves": [
    {
      "label": "Wave 1 · Before training",
      "departments": [
        {
          "name": "Information Technology",
          "function": "Technology",
          "staff": 24,
          "mix": { "leadership": 1, "manager": 4, "specialist": 15, "support": 4 },
          "metrics": {
            "users": 92, "freq": 95, "train": 98, "flow": 90,
            "tasks": 88, "cover": 86, "prof": 94, "comp": 98
          },
          "sessions": 8.6,
          "cases": 19,
          "tools": [["Claude (Enterprise)", 88]],
          "processes": ["Ticket triage"],
          "gap": "Night shift still manual",
          "opportunity": "Publish the triage assistant org-wide"
        }
      ]
    }
  ]
}
```

4. Save and refresh the browser.

For the second wave, add a second block inside `waves`. The trend chart appears
by itself.

## Route B · The scoring script

Skips the manual scoring. One command turns the raw Forms export into the file
above.

```bash
python score_survey.py --wave1 wave1.xlsx --headcount headcount.xlsx --out data.json
```

After the training:

```bash
python score_survey.py --wave1 wave1.xlsx --wave2 wave2.xlsx \
                       --headcount headcount.xlsx --out data.json
```

It prints a report as it runs, including a response-rate warning per department:

```
Information Technology     rate 88.7    16/24 responded (67%)
Legal                      rate 26.2     4/7  responded (57%)  <-- provisional
Operations                 rate 26.2    28/41 responded (68%)
```

Copy the resulting `data.json` next to the dashboard.

## Route C · The full application

For when this becomes a permanent tool.

1. Log in at `/docs` as an admin.
2. Create a wave: "Wave 1, before training".
3. Upload the survey export and the HR headcount file.
4. Read the report it returns: responses found, departments matched, warnings.
5. Check the figures. Nobody else can see them yet.
6. Press publish. Leadership sees them.

Everything is stored, so the raw responses remain available for re-scoring.

## What you need from HR either way

One spreadsheet. Department, business function, total headcount, and the split
by level (leadership, managers, specialists, support and site).

That is all. No system integration.

## The rule that matters most

**Score both waves the same way.** If you change a scoring rule, re-score both
waves, never just one. Otherwise you cannot tell whether the number moved
because behaviour changed or because the method did.

---

# PART 6 · What is built and what is not

## Complete

- Scoring model, with 53 tests covering the rules
- Ingest: raw survey export to department scores, 45 tests
- Eight-table database schema with migrations
- REST API: auth, dashboard, waves, upload, departments, configuration
- Four roles with department-level scoping
- React dashboard: treemap, drill-down, trends, filters, weight sliders, Excel export
- Standalone single-file version for sharing
- Docker Compose for the whole stack
- 135 tests passing

## Not built yet

- **Deployment.** It runs locally. Vercel for the front end, Render or Azure for
  the API, Neon for the database. Half a day.
- **A login screen in React.** The API has authentication; the dashboard
  currently reads a published file. Needed only when it goes live with real data.
- **User management UI.** Users are created through the API or the seed script.
- **Scheduled email reports.** Not required, worth considering later.

## The honest status

The measurement engine is finished and tested. The dashboard is finished. What
remains is deployment and the login screen, which are only needed once real data
exists and the thing goes live for other people.

For a demo, for client approval, and for the first survey wave, it is ready now.

---

# PART 7 · Running it

## The demo version

Open `standalone/dashboard.html`. Double click it. Nothing to install.

## The React version

```bash
cd frontend
npm install     # first time only
npm run dev
```

Then open the address it prints.

## The full stack

```bash
docker compose up --build
```

Then the front end as above. API docs at `localhost:8000/docs`.

## The tests

```bash
cd backend
pytest -q
```

---

# PART 8 · Where everything lives

```
rak-ai-adoption/
├── standalone/dashboard.html    the demo, double click it
├── frontend/                    React dashboard
│   ├── public/data.json         the numbers on screen
│   └── src/
│       ├── components/          one file per section of the page
│       ├── hooks/useDashboard.ts  all the state
│       └── lib/
│           ├── scoring.ts       eight indicators to one rate
│           └── treemap.ts       the box layout algorithm
├── backend/                     Python
│   ├── app/services/scoring.py  the model, pure and tested
│   ├── app/services/ingest.py   spreadsheet to scores
│   ├── app/api/routes/          the endpoints
│   └── tests/                   135 tests
└── docs/
    ├── COMPLETE-GUIDE.md        this file
    └── HOW-IT-WORKS.md          every file explained
```
