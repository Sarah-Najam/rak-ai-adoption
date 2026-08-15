#!/usr/bin/env python3
"""
RAK Properties AI Adoption Index
Turns raw Microsoft Forms survey responses into the data.json the dashboard reads.

    pip install pandas openpyxl
    python score_survey.py --wave1 wave1.xlsx --headcount headcount.xlsx --out data.json

Adding the second wave later:

    python score_survey.py --wave1 wave1.xlsx --wave2 wave2.xlsx \
                           --headcount headcount.xlsx --out data.json

Every scoring rule lives in this file. Run it the same way for both waves and the
comparison stays honest. If you change a rule, re-score both waves, never just one.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas is not installed. Run: pip install pandas openpyxl")


# ---------------------------------------------------------------------------
# 1. HOW EACH SURVEY QUESTION IS FOUND
#
# Microsoft Forms exports the full question text as the column heading, and
# people edit question wording. So rather than matching the heading exactly, we
# look for a few distinctive words. Add alternatives here if a column is missed.
# ---------------------------------------------------------------------------

COLUMN_HINTS = {
    "department":  ["which department do you work in"],
    "level":       ["which best describes your level"],
    "tenure":      ["how long have you worked at rak"],
    "used_30d":    ["used any ai tool for work in the last 30"],
    "tools":       ["which of these have you used for work in the last 30"],
    "top_tool":    ["which one do you use most"],
    "days":        ["on how many days do you use ai"],
    "times":       ["how many separate times"],
    "since":       ["how long have you been using ai for work"],
    "device":      ["where do you mostly use it"],
    "workflow":    ["how often is ai part of how you do your job"],
    "last_task":   ["think about the last time you used ai"],
    "regular":     ["which of these do you use ai for regularly"],
    "task_count":  ["how many work tasks did ai help you with"],
    "time_saved":  ["how much time does ai save you"],
    "quality":     ["changed the quality of your work"],
    "checks":      ["do you check ai output"],
    "coverage":    ["what share of them do you now use ai for"],
    "idea1":       ["name up to three tasks", "task 1"],
    "idea2":       ["task 2"],
    "idea3":       ["task 3"],
    "blockers":    ["what stops you using ai more"],
    "no_go":       ["should not be used"],
    "account":     ["which account do you normally use"],
    "pasted":      ["have you put any of these into a personal ai account"],
    "disclose":    ["tell colleagues when a document"],
    "training":    ["have you completed any ai training"],
    "confidence":  ["how confident do you feel using ai"],
    "usefulness":  ["how useful do you think ai could be"],
    "support":     ["what support would help you most"],
    "why_not":     ["why have you not used ai for work"],
    "would_use":   ["how likely would you be to use it"],
    "repetitive":  ["most repetitive part of your job"],
}

# Part F: one column per question. Matched by the "F1." style prefix if present,
# otherwise by position among columns that contain the answer marker.
KNOWLEDGE_ANSWERS = {
    "F1": "deciding which contractor",
    "F2": "write a short email to a buyer",
    "F3": "you did not tell it who it is for",
    "F4": "known behavio",
    "F5": "producing a first draft",
    "F6": "give it two or three examples",
    "F7": "customer's name",
    "F8": "tell it what is wrong",
    "F9": "trained on information up to a point in time",
    "F10": "you, the person who sent the report",
}

# ---------------------------------------------------------------------------
# 2. ANSWER TO NUMBER CONVERSIONS
#    These are Part J of the survey document, in code.
# ---------------------------------------------------------------------------

WORKFLOW_POINTS = [                       # D1
    ("every working day", 100),
    ("most days", 88),
    ("several times a week", 70),
    ("about once a week", 45),
    ("rarely", 20),
    ("never", 0),
]

COVERAGE_POINTS = [                       # E1
    ("almost all", 100),
    ("more than three quarters", 85),
    ("half to three quarters", 63),
    ("quarter to a half", 38),
    ("under a quarter", 15),
    ("none of them", 0),
]

DAYS_VALUES = [                           # C3
    ("5 or more", 5.0), ("4 day", 4.0), ("3 day", 3.0),
    ("2 day", 2.0), ("1 day", 1.0), ("less than one", 0.5),
]

TIMES_VALUES = [                          # C4
    ("more than 10", 12.0), ("7 to 10", 8.5), ("4 to 6", 5.0),
    ("2 to 3", 2.5), ("once", 1.0),
]

TASK_VALUES = [                           # D4
    ("more than 60", 75.0), ("31 to 60", 45.0), ("16 to 30", 23.0),
    ("6 to 15", 10.0), ("1 to 5", 3.0), ("none", 0.0),
]

SESSION_TARGET = 5.0     # sessions per user per week that scores 100
TASK_TARGET = 20.0       # AI-assisted tasks per user per month that scores 100

ACCOUNT_PENALTY = [                       # G1
    ("always a personal", 40),
    ("mostly a personal", 25),
    ("about half and half", 15),
]
PASTED_PENALTY = 12                       # per category selected at G2
UNSURE_PENALTY = 10                       # "I prefer not to say"

LEVEL_KEYS = [
    ("leadership", "leadership"),
    ("manager", "manager"),
    ("specialist", "specialist"),
    ("support", "support"),
]

METRIC_ORDER = ["users", "freq", "train", "flow", "tasks", "cover", "prof", "comp"]

DEFAULT_WEIGHTS = {"users": 20, "freq": 15, "train": 15, "flow": 15,
                   "tasks": 10, "cover": 10, "prof": 10, "comp": 5}

FUNCTIONS = {
    "information technology": "Technology",
    "marketing & communications": "Commercial",
    "marketing and communications": "Commercial",
    "sales": "Commercial",
    "customer service": "Commercial",
    "learning & development": "Corporate Services",
    "learning and development": "Corporate Services",
    "human resources": "Corporate Services",
    "finance": "Corporate Services",
    "administration": "Corporate Services",
    "procurement": "Corporate Services",
    "legal": "Corporate Services",
    "project development": "Technical",
    "property management": "Technical",
    "operations": "Technical",
}


# ---------------------------------------------------------------------------
# 3. HELPERS
# ---------------------------------------------------------------------------

def norm(text):
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def find_column(df, hints):
    """First column whose heading contains any of the hint phrases."""
    for col in df.columns:
        low = norm(col)
        for hint in hints:
            if hint in low:
                return col
    return None


def map_columns(df):
    found, missing = {}, []
    for key, hints in COLUMN_HINTS.items():
        col = find_column(df, hints)
        if col is None:
            missing.append(key)
        found[key] = col
    return found, missing


def points_from(value, table, default=0.0):
    low = norm(value)
    for phrase, points in table:
        if phrase in low:
            return float(points)
    return float(default)


def is_yes(value):
    low = norm(value)
    return low.startswith("yes")


def split_multi(value):
    """Forms writes multi-select answers as a semicolon separated string."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [p.strip() for p in re.split(r"[;\n]", str(value)) if p.strip()]


def safe_mean(values, default=0.0):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else default


def clamp(v):
    return max(0.0, min(100.0, float(v)))


# ---------------------------------------------------------------------------
# 4. THE EIGHT INDICATORS
# ---------------------------------------------------------------------------

def score_department(rows, cols, knowledge_cols):
    """rows is a list of dict-like survey responses for one department."""
    n = len(rows)
    if n == 0:
        return None

    users_yes = [r for r in rows if is_yes(r.get(cols["used_30d"]))]

    # --- 1. Active AI users (weight 20) ---------------------------------
    users = len(users_yes) / n * 100

    # --- 2. Usage frequency (weight 15) ---------------------------------
    sessions = []
    for r in rows:
        if r not in users_yes:
            sessions.append(0.0)
            continue
        days = points_from(r.get(cols["days"]), DAYS_VALUES, 0.0)
        times = points_from(r.get(cols["times"]), TIMES_VALUES, 0.0)
        sessions.append(days * times)
    avg_sessions = safe_mean(sessions)
    freq = min(100.0, avg_sessions / SESSION_TARGET * 100)

    # --- 3. Training completion (weight 15) -----------------------------
    trained = 0
    for r in rows:
        answers = split_multi(r.get(cols["training"]))
        if any(norm(a).startswith("yes") for a in answers):
            trained += 1
    train = trained / n * 100

    # --- 4. AI in weekly workflow (weight 15) ---------------------------
    flow = safe_mean([
        points_from(r.get(cols["workflow"]), WORKFLOW_POINTS, 0.0) if r in users_yes else 0.0
        for r in rows
    ])

    # --- 5. AI-assisted task volume (weight 10) -------------------------
    task_counts = [
        points_from(r.get(cols["task_count"]), TASK_VALUES, 0.0) if r in users_yes else 0.0
        for r in rows
    ]
    avg_tasks = safe_mean(task_counts)
    tasks = min(100.0, avg_tasks / TASK_TARGET * 100)

    # --- 6. Eligible workflows covered (weight 10) ----------------------
    cover = safe_mean([
        points_from(r.get(cols["coverage"]), COVERAGE_POINTS, 0.0) if r in users_yes else 0.0
        for r in rows
    ])

    # --- 7. Proficiency (weight 10) -------------------------------------
    # Everyone answers Part F, including non-users.
    prof_scores = []
    for r in rows:
        correct = total = 0
        for qid, col in knowledge_cols.items():
            if col is None:
                continue
            total += 1
            if KNOWLEDGE_ANSWERS[qid] in norm(r.get(col)):
                correct += 1
        if total:
            prof_scores.append(correct / total * 100)
    prof = safe_mean(prof_scores)

    # --- 8. Safe use of AI (weight 5) -----------------------------------
    # Users only. A department with fewer than five users is flagged below.
    safe_scores = []
    for r in users_yes:
        s = 100.0
        s -= points_from(r.get(cols["account"]), ACCOUNT_PENALTY, 0.0)
        for item in split_multi(r.get(cols["pasted"])):
            low = norm(item)
            if low.startswith("none of the above"):
                continue
            s -= UNSURE_PENALTY if "prefer not to say" in low else PASTED_PENALTY
        safe_scores.append(max(0.0, s))
    comp = safe_mean(safe_scores, default=0.0)

    # --- supporting detail for the drill-down ---------------------------
    tool_counter = Counter()
    for r in users_yes:
        for t in split_multi(r.get(cols["tools"])):
            tool_counter[t] += 1
    tools = [[name, round(count / max(1, len(users_yes)) * 100)]
             for name, count in tool_counter.most_common(3)]

    proc_counter = Counter()
    for r in users_yes:
        for t in split_multi(r.get(cols["regular"])):
            if not norm(t).startswith("none of these"):
                proc_counter[t] += 1
    processes = [name for name, _ in proc_counter.most_common(4)]

    ideas = []
    for r in rows:
        for key in ("idea1", "idea2", "idea3"):
            col = cols.get(key)
            if col and str(r.get(col) or "").strip():
                ideas.append(str(r.get(col)).strip())

    blocker_counter = Counter()
    for r in rows:
        for b in split_multi(r.get(cols["blockers"])):
            if not norm(b).startswith("nothing stops me"):
                blocker_counter[b] += 1
    gap = blocker_counter.most_common(1)[0][0] if blocker_counter else "Not recorded"
    opportunity = ideas[0] if ideas else "Not recorded"

    use_cases = len(set(norm(i) for i in ideas)) + len(proc_counter)

    return {
        "metrics": {
            "users": round(clamp(users), 1),
            "freq": round(clamp(freq), 1),
            "train": round(clamp(train), 1),
            "flow": round(clamp(flow), 1),
            "tasks": round(clamp(tasks), 1),
            "cover": round(clamp(cover), 1),
            "prof": round(clamp(prof), 1),
            "comp": round(clamp(comp), 1),
        },
        "sessions": round(avg_sessions, 1),
        "cases": use_cases,
        "tools": tools,
        "processes": processes,
        "gap": gap,
        "opportunity": opportunity,
        "_respondents": n,
        "_users": len(users_yes),
        "_ideas": ideas,
    }


# ---------------------------------------------------------------------------
# 5. RUNNING A WAVE
# ---------------------------------------------------------------------------

def read_any(path):
    if str(path).lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)


def load_headcount(path):
    """department, total headcount, and the split by level."""
    df = read_any(path)
    out = {}
    lookup = {norm(c): c for c in df.columns}

    def col(*names):
        for n in names:
            for key, original in lookup.items():
                if n in key:
                    return original
        return None

    c_dept = col("department")
    c_total = col("total", "headcount", "staff")
    if not c_dept or not c_total:
        sys.exit("The headcount file needs a department column and a total headcount column.")

    for _, row in df.iterrows():
        name = str(row[c_dept]).strip()
        if not name or name.lower() == "nan":
            continue
        mix = {}
        for key, _ in LEVEL_KEYS:
            c = col(key)
            mix[key] = int(row[c]) if c and not pd.isna(row[c]) else 0
        out[norm(name)] = {
            "name": name,
            "staff": int(row[c_total]),
            "mix": mix,
            "function": FUNCTIONS.get(norm(name), "Unassigned"),
        }
    return out


def score_wave(path, label, headcount, verbose=True):
    df = read_any(path)
    cols, missing = map_columns(df)

    knowledge_cols = {}
    for qid in KNOWLEDGE_ANSWERS:
        knowledge_cols[qid] = find_column(df, [qid.lower() + ".", qid.lower() + ":"])

    if verbose:
        print(f"\n{label}")
        print(f"  {len(df)} responses, {len(df.columns)} columns")
        if missing:
            print(f"  columns not found: {', '.join(missing)}")
            print("  (add a distinctive phrase to COLUMN_HINTS if one of these matters)")
        found_k = [q for q, c in knowledge_cols.items() if c]
        print(f"  knowledge check questions matched: {len(found_k)} of {len(KNOWLEDGE_ANSWERS)}")

    if not cols["department"]:
        sys.exit("Could not find the department question. Check COLUMN_HINTS['department'].")

    rows = df.to_dict("records")
    grouped = defaultdict(list)
    for r in rows:
        dept = str(r.get(cols["department"]) or "").strip()
        if dept and dept.lower() != "nan":
            grouped[norm(dept)].append(r)

    departments = []
    for key, dept_rows in sorted(grouped.items()):
        scored = score_department(dept_rows, cols, knowledge_cols)
        if not scored:
            continue

        hc = headcount.get(key)
        name = hc["name"] if hc else str(dept_rows[0].get(cols["department"])).strip()
        staff = hc["staff"] if hc else len(dept_rows)
        mix = hc["mix"] if hc else {}
        function = hc["function"] if hc else FUNCTIONS.get(key, "Unassigned")

        rate = sum(scored["metrics"][m] * DEFAULT_WEIGHTS[m] for m in METRIC_ORDER) / 100
        response_rate = len(dept_rows) / staff * 100 if staff else 0

        if verbose:
            flag = ""
            if response_rate < 40:
                flag = "  <-- response rate under 40%, do not draw conclusions"
            elif response_rate < 60:
                flag = "  <-- provisional, response rate under 60%"
            if scored["_users"] < 5:
                flag += "  [safe-use score based on fewer than 5 users]"
            print(f"    {name:<32} rate {rate:5.1f}   "
                  f"{len(dept_rows):>3}/{staff:<3} responded ({response_rate:4.0f}%){flag}")

        departments.append({
            "name": name,
            "function": function,
            "staff": staff,
            "mix": mix,
            "metrics": scored["metrics"],
            "sessions": scored["sessions"],
            "cases": scored["cases"],
            "tools": scored["tools"],
            "processes": scored["processes"],
            "gap": scored["gap"],
            "opportunity": scored["opportunity"],
        })

    return {"label": label, "departments": departments}


# ---------------------------------------------------------------------------
# 6. MAIN
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Score the AI adoption survey into data.json")
    ap.add_argument("--wave1", required=True, help="Wave 1 responses (xlsx or csv)")
    ap.add_argument("--wave2", help="Wave 2 responses, once you have them")
    ap.add_argument("--headcount", required=True, help="HR headcount file (xlsx or csv)")
    ap.add_argument("--out", default="data.json")
    ap.add_argument("--label1", default="Wave 1 (before training)")
    ap.add_argument("--label2", default="Wave 2 (after training)")
    ap.add_argument("--org-target", type=float, default=70)
    ap.add_argument("--quarter-target", type=float, default=65)
    ap.add_argument("--minimum", type=float, default=40)
    args = ap.parse_args()

    headcount = load_headcount(args.headcount)
    print(f"Headcount file: {len(headcount)} departments")

    waves = [score_wave(args.wave1, args.label1, headcount)]
    if args.wave2:
        waves.append(score_wave(args.wave2, args.label2, headcount))

    data = {
        "weights": DEFAULT_WEIGHTS,
        "targets": {"org": args.org_target, "quarter": args.quarter_target,
                    "min": args.minimum, "byDept": {}},
        "waves": waves,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = sum(len(w["departments"]) for w in waves)
    print(f"\nWrote {args.out}: {len(waves)} wave(s), {total} department rows.")
    print("Put it next to the dashboard HTML file and refresh the page.")


if __name__ == "__main__":
    main()
