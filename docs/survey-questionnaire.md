# RAK Properties AI Adoption Survey

**Owner:** Learning & Development
**Purpose:** measure AI adoption across every department, before and after the Claude AI Training Programme
**Data source:** this survey only. No admin consoles, no LMS extract, no workshops.
**Length:** about 10 minutes for AI users, about 6 minutes for non-users
**Runs twice:** Wave 1 before the training, Wave 2 six to eight weeks after it
**Reporting level:** department only. No individual is ever named or scored.

---

## 1. Read this first

### 1.1 What changes when the survey is the only source

Every one of the eight dashboard indicators now comes from a question in this document. That works, but it changes what the numbers mean, and it is better to understand that now than to discover it when leadership asks.

Self-reported adoption always runs higher than measured adoption. People remember the weeks they used a tool and forget the weeks they did not, and nobody wants to be the person who answers "never". Expect the absolute figures to sit somewhere above reality.

That is not a reason to abandon the approach. It is a reason to be clear about which number you defend:

> The **level** is approximate. The **change between Wave 1 and Wave 2** is the real result.

Because the same people answer the same questions the same way both times, the overstatement is roughly the same in both waves and cancels out of the comparison. A department that moves from 38 to 61 has genuinely moved, even if neither figure is exact. Say this out loud in the leadership presentation before anyone else says it for you.

### 1.2 The one thing that will break the comparison if you ignore it

Each head of department is nominating around two people for the Basic training. In Operations, that is 2 people out of 41. If you compare whole-department adoption before and after, the trained people will be diluted to nothing and the dashboard will show almost no movement, even if the training worked perfectly.

So Wave 2 must be able to split the results three ways:

1. **People who attended the training.** This is where you will see real movement, and it is the honest measure of whether the training worked.
2. **Colleagues in the same department who did not attend.** This measures spread. If this group moves too, the trained people are teaching others, which is the actual goal of a nomination-based programme.
3. **The department as a whole.** This is what feeds the dashboard and what leadership sees.

One extra question in Wave 2 (question A3 below) makes all three cuts possible. Without it you will have spent two survey rounds and learned very little.

### 1.3 One thing you do need from HR

Not a system integration, just a spreadsheet: the headcount of each department, split by level. You need it for two reasons. It lets you calculate response rate, so you know whether a department's score is trustworthy. And it lets the dashboard show employees assessed, which is one of the executive summary figures.

Ask HR for one file with: department, business function, location, total headcount, and headcount split into leadership, managers, specialists, and support or site staff. That is all.

### 1.4 Three decisions to lock before you send it

**Run it anonymously.** Part G asks whether people have pasted company information into a personal AI account. Nobody answers that honestly with their name attached, and a dishonest compliance number is worse than none.

**Use a self-generated linking code.** Anonymous surveys usually cannot be matched across waves, which weakens the comparison. A code the person generates themselves solves this without collecting anything identifying. See question A2.

**Agree definitions in writing.** Get IT, HR and L&D to sign off on what counts as "an AI tool", what "approved" means, and what counts as "work use". Write the definitions into the form itself. Ambiguous definitions are the most common reason a second wave turns out not to be comparable.

### 1.5 Timing

| When | What |
|---|---|
| Now, week 1 | Lock definitions. Build the form in Microsoft Forms. Translate to Arabic. |
| Week 1 | Pilot with 8 to 10 people across three departments. Fix anything confusing. |
| Week 2 | **Wave 1 opens.** Must close before the first training session. |
| Week 3 | Wave 1 closes. Score and load the dashboard as the baseline. |
| 19 and 20 August | Basic training runs. |
| September | Advanced training runs. |
| 6 to 8 weeks after the last session | **Wave 2 opens.** Identical wording. |

Do not run Wave 2 in the week after training. What you would measure is enthusiasm, not adoption. Habits either survive the return to normal workload or they do not, and six to eight weeks is long enough to find out.

---

## 2. Introduction text for the form

> **RAK Properties AI Adoption Survey**
>
> This survey helps us understand how AI is actually being used across the company today, so we can put training and tools where they will help most. We will run it again after the Claude AI Training Programme to see what has changed.
>
> It takes about 10 minutes. Your answers are anonymous. We report results by department only, never by person, and nothing you write here goes to your line manager as individual feedback.
>
> Please answer honestly, including where the answer is "I do not use it". A department showing low usage is not a problem for you. It tells us where to focus support next.
>
> **In this survey, "AI tool" means** any tool that generates text, images, code or analysis from what you type, such as Claude, ChatGPT, Microsoft Copilot, Gemini, or a similar assistant. It does not mean autocorrect, spell check, search, or the recommendation features built into everyday software.
>
> **"Work use" means** using it for a RAK Properties task, on any device, on any account.
>
> Questions: Learning & Development.

---

## PART A. Setting up the comparison

**A1. Which survey round is this?**
Pre-filled by the form, not asked.
- Wave 1, before training
- Wave 2, after training

**A2. Please create your personal code.**
Free text, 4 characters. Show this instruction exactly:

> This lets us compare your answers between the two surveys without knowing who you are. Please build it the same way both times:
> the **first two letters of your mother's first name**, followed by the **last two digits of your mobile number**.
> Example: mother named Fatima, mobile ending 47, code is **FA47**.

**A3. Did you attend the RAK Properties Claude AI Training?**
**Wave 2 only.** Single choice.
- Yes, the Basic training
- Yes, the Basic and the Advanced training
- No, I was not nominated
- I was nominated but could not attend

---

## PART B. About your role

*Feeds: the department, business function, location and employee level filters.*

**B1. Which department do you work in?**
Single choice.
Human Resources · Finance · Information Technology · Marketing & Communications · Sales · Legal · Procurement · Operations · Learning & Development · Property Management · Customer Service · Project Development · Administration · Other (please type)

**B2. Which best describes your main work location?**
Single choice.
- Julphar Towers head office
- Mina Al Arab
- Hayat Island site office
- Split between office and site
- Mostly remote or travelling

**B3. Which best describes your level?**
Single choice.
- Leadership (head of department and above)
- Manager or team leader
- Specialist or professional
- Support, administrative, technical or site staff

**B4. How long have you worked at RAK Properties?**
Single choice.
Less than 6 months · 6 to 12 months · 1 to 3 years · More than 3 years

**B5. Have you used any AI tool for work in the last 30 days?**
Single choice. **This is the routing question and it carries the largest single indicator.**
- Yes
- No, but I have used one before
- No, never

> Branching: "Yes" goes to Part C. Both "No" answers jump to Part I, then continue to Part F and Part H.

---

## PART C. Which tools you use

*Feeds: usage frequency, most-used tools, and the AI tool filter.*

**C1. Which of these have you used for work in the last 30 days?**
Multiple choice, select all that apply.
- Claude, on a company account
- Claude, on a personal account
- Microsoft 365 Copilot
- Copilot in Teams for meeting notes
- GitHub Copilot
- Adobe Firefly
- Canva Magic Studio
- Power Automate AI Builder
- ChatGPT, on a personal account
- Gemini, on a personal account
- Another tool (please type)

**C2. Which one do you use most?**
Single choice, same list.

**C3. In a normal week, on how many days do you use AI for work?**
Single choice.
Less than one day · 1 day · 2 days · 3 days · 4 days · 5 or more days

**C4. On a day when you use it, how many separate times do you go to an AI tool?**
Single choice.
Once · 2 to 3 times · 4 to 6 times · 7 to 10 times · More than 10 times

**C5. How long have you been using AI for work?**
Single choice.
Less than 1 month · 1 to 3 months · 3 to 6 months · 6 to 12 months · More than 12 months

**C6. Where do you mostly use it?**
Single choice.
- On my work computer
- On my personal computer
- On my mobile phone
- Split between computer and phone

> *This matters for Operations, Property Management and Project Development, where staff are on site and a desktop-only tool cannot reach them.*

---

## PART D. How AI fits into your actual work

*Feeds: the workflow indicator and the task volume indicator.*

**D1. In a normal working week, how often is AI part of how you do your job?**
Single choice. **This single question carries the workflow indicator.**
- Never
- Rarely, only when I remember to try it
- About once a week
- Several times a week
- Most days
- Every working day, it is part of my routine

**D2. Think about the last time you used AI for work. What was it for?**
Single choice.
- Writing or improving something (email, report, proposal, post)
- Summarising something long (document, meeting, thread)
- Translating between Arabic and English
- Analysing numbers or data
- Checking or reviewing someone else's work
- Answering a question or looking something up
- Generating an image or design
- Writing or fixing code or a formula
- Planning or structuring a piece of work
- Something else (please type)

**D3. Which of these do you use AI for regularly?**
Multiple choice, same list as D2, plus "None of these regularly".

**D4. Roughly how many work tasks did AI help you with in the last month?**
Single choice.
None · 1 to 5 · 6 to 15 · 16 to 30 · 31 to 60 · More than 60

**D5. Roughly how much time does AI save you in a normal week?**
Single choice.
No time saved · Under 30 minutes · 30 minutes to 1 hour · 1 to 3 hours · 3 to 5 hours · More than 5 hours

> *Not scored into the adoption rate. It is the first thing leadership will ask about, so collect it now rather than running a third survey later.*

**D6. Has AI changed the quality of your work, not just the speed?**
Single choice.
Much better · Slightly better · No difference · Slightly worse · Much worse · Too early to say

**D7. Do you check AI output before you use it?**
Single choice.
- Always, every time
- Usually
- Only when it matters
- Rarely
- Never

> *Not scored, but track it. If usage climbs between waves while checking falls, the training has created a risk instead of removing one.*

---

## PART E. Work that could use AI but does not yet

*Feeds: the eligible workflow coverage indicator, plus the gap and opportunity text in the drill-down.*

**E1. Think about the tasks you repeat every week. Roughly what share of them do you now use AI for?**
Single choice.
- None of them
- Under a quarter
- About a quarter to a half
- About half to three quarters
- More than three quarters
- Almost all of them

**E2. Name up to three tasks you repeat regularly where you think AI could help but you are not using it yet.**
Three free text boxes.

> *The most valuable question in the survey. It produces each department's opportunity list in the words of the people who do the work, and it is the only place the dashboard's opportunity text can come from now that there are no workshops.*

**E3. What stops you using AI more?**
Multiple choice, select all that apply.
- I do not have time to learn it
- I do not know what it can do for my kind of work
- I am not confident the output is accurate
- I am not sure what I am allowed to put into it
- The tool I have access to is not good enough for my work
- I do not have easy access on the device I actually work on
- My work is too specialised or too confidential for it
- My team does not use it, so there is no habit
- Nothing stops me, I use it as much as I want to
- Something else (please type)

**E4. Is there any part of your work where you think AI should not be used?**
Free text, optional.

---

## PART F. Knowledge check

*Feeds: the proficiency and readiness indicator. **Asked of everyone**, including people who do not use AI. Nine questions, one mark each.*

**What this part is for.** Proficiency is one of the eight things the dashboard scores. You cannot get it by asking "how good are you with AI?", because people guess, and confident people guess high. So instead we ask nine short questions with right and wrong answers. The same nine questions run again after the training, and the change in the average score is the clearest evidence you will have that the training taught people something.

**What the questions test.** Not tool features, and nothing that goes out of date. They test the four things a person needs to use AI safely and usefully at work:

1. Knowing what AI should and should not be trusted with (F1, F9)
2. Knowing that a confident answer can still be wrong, and checking it (F2, F4)
3. Knowing how to get a usable result: give it the source material, correct it, show it examples (F3, F7, F8)
4. Knowing what is safe to type in, and why a company account is different (F5, F6)

Introduce it with this line:

> These nine questions check what the company as a whole knows, not what you personally know. Your score is never shown to anyone and never linked to you. Please answer without looking anything up. If you do not use AI, please still answer. Your best guess is useful to us.

---

**F1. Which of these is the least suitable to hand to an AI tool?**
- A. Drafting a reply to a routine customer enquiry
- B. Shortening a paragraph so it is clearer
- C. Deciding which contractor should be awarded a tender ✓
- D. Summarising a long report that you give it

**F2. An AI tool gives you a clear, confident answer. Can you assume it is correct?**
- A. Yes, if it sounds confident
- B. Yes, if it is a company approved tool
- C. Yes, if it gives you the same answer twice
- D. No, it can be wrong even when it sounds certain, so it needs checking ✓

**F3. You need a summary of a 40 page consultant report. Which approach gives the most reliable summary?**
- A. Ask the AI what it knows about reports from that consultant
- B. Give it the report itself and ask it to summarise only what is in the document ✓
- C. Ask for a summary, then ask the AI whether its own summary is correct
- D. Ask three times and combine the answers

**F4. AI gives you a figure, such as an occupancy rate or a sales total, and you want to put it in a report. What should you do first?**
- A. Check it against the real source ✓
- B. Use it, the tool has access to our data
- C. Use it, but only in internal documents
- D. Ask the same question again and use the answer that appears twice

**F5. Which of these should not be typed into a personal AI account that you signed up for yourself?**
- A. A general question about UAE property law
- B. A request to explain a spreadsheet formula
- C. A customer's name, phone number and payment history ✓
- D. A question about the meaning of a word

**F6. What is the main difference between a company provided AI account and one you sign up for yourself?**
- A. The company account is faster
- B. What you type into a company account is covered by a business agreement and is not used to train the tool ✓
- C. The company account gives better quality answers
- D. There is no real difference

**F7. The first answer you get is not good enough. What usually works best?**
- A. Start a new chat and ask the same way again
- B. Accept it and rewrite the whole thing yourself
- C. Try a different AI tool
- D. Tell it exactly what was wrong and ask it to redo that part ✓

**F8. You want AI to write in the RAK Properties style. What works best?**
- A. Give it two or three examples of our existing writing and ask it to match them ✓
- B. Ask it to sound professional
- C. Tell it the company name and let it work the style out
- D. It is not possible, style has to be written by a person

**F9. Which of these is true about what an AI tool knows?**
- A. It is connected to our systems and can see our live data
- B. It knows everything up to today
- C. Its knowledge stops at a certain date, so recent information may be missing or wrong ✓
- D. It only knows what you type into it

---

**Answer key:** F1 C · F2 D · F3 B · F4 A · F5 C · F6 B · F7 D · F8 A · F9 C

*The correct answers are deliberately spread across all four positions. If they all sat in the same place, people would spot the pattern and the second wave would score higher for the wrong reason.*

**Marking.** One mark per correct answer, no half marks, no negative marking. Each correct answer is worth 11.1 points, so a person who scores 6 out of 9 contributes 67. Average those scores across the department to get the proficiency indicator.

**What a score means.** Below 40 means people do not yet know the basics and are probably taking AI output at face value, which is a risk rather than a benefit. Between 40 and 70 means the habits are forming but verification and data handling are patchy. Above 70 means the department can be trusted to use AI on real work without close supervision.

---

## PART G. Safe use of AI

*Feeds: the dashboard's eighth indicator. Asked only of people who use AI. Anonymity matters most here.*

**Note on wording.** RAK Properties does not currently have a written AI usage policy, so this part does not ask whether people have read one. It measures behaviour instead: what account people use, what they put into it, and whether they know who to ask. That is the honest thing to measure today, and it is also the evidence you will need if you decide to write a policy later.

Because of this, the dashboard's eighth indicator is better labelled **Safe use of AI** rather than **Policy compliance** until a policy exists. The calculation and the 5% weight do not change.

**G1. As far as you know, does RAK Properties have any rules about using AI at work?**
Not scored. This measures how clear things are, not whether anyone is at fault.
- Yes, and I know what they are
- I think there are some, but I am not sure what
- No, I do not think there are any
- I do not know

**G2. When you use AI for work, which account do you normally use?**
- Always a company provided account
- Mostly a company account, sometimes personal
- About half and half
- Mostly a personal account
- Always a personal account
- I did not know the company provides one

**G3. In the last 30 days, have you put any of these into a personal AI account?**
Multiple choice, select all that apply.
- Customer or buyer personal details
- Financial figures that are not public
- Contract or legal text
- Internal strategy, board or project documents
- Employee or HR information
- None of the above
- I prefer not to say

**G4. Do you tell colleagues when a document you share was drafted with AI help?**
Always · Usually · Sometimes · Never · It has not come up

**G5. If you were unsure whether a particular use of AI was acceptable, would you know who to ask?**
Yes, I know exactly who · I think so · No

**G6. Would short, clear written guidance on what you can and cannot use AI for make you more comfortable using it?**
Not scored. This is the business case for writing the policy, in the staff's own words.
- Yes, it would make a real difference
- Yes, a little
- No difference either way
- No, I am comfortable already

> **Expect G1 to look bad, and do not treat that as a failure.** With no policy in place, most people will answer "I do not know". That result, sitting next to whatever G3 turns up, is the argument for writing a one page guidance note before the training rather than after it. People who have just been taught to use AI well, with no guidance on what they may put into it, are the exact group most likely to paste something they should not.

---

## PART H. Everyone answers this part

**H1. Have you completed any AI training?**
Multiple choice, select all that apply.
- Yes, RAK Properties Claude AI Basic training
- Yes, RAK Properties Claude AI Advanced training
- Yes, other training provided by RAK Properties
- Yes, training I found myself outside the company
- No, but I have been nominated for the Claude training
- No, none

**H2. How confident do you feel using AI in your work today?**
Scale 1 to 5. 1 = not at all confident, 5 = very confident.

**H3. How useful do you think AI could be for your specific job?**
Scale 1 to 5. 1 = not useful at all, 5 = extremely useful.

> *H2 against H3 is the most useful chart you will produce. High usefulness with low confidence is a training problem you can fix this quarter. Low usefulness is a belief problem that needs a demonstration on that team's own work instead.*

**H4. What support would help you most?**
Multiple choice, maximum two.
- Hands-on training using my own real tasks
- Short written guides for my specific job
- A colleague in my team I can ask
- Ready-made prompts for tasks I do often
- Clear rules on what I can and cannot put in
- Better access on my phone or site device
- A tool connected to our own systems and data
- Nothing, I am fine as I am

**H5. Anything else you want to tell us about AI at RAK Properties?**
Free text, optional.

**H6. Since the training, has the way you use AI changed?**
**Wave 2 only.** Single choice. Not scored, used as a sense check against the calculated movement.
- I use it much more
- I use it a little more
- No change
- I use it less
- I did not attend the training

---

## PART I. Non-user branch

*Only for people who answered "No" at B5. They answer this, then Part F, then Part H.*

**I1. Why have you not used AI for work?**
Multiple choice, select all that apply.
- I do not have access to a tool
- I did not know I was allowed to
- I do not know how to start
- I do not think it applies to my work
- I do not have time
- I tried it and it was not useful
- I have concerns about accuracy or confidentiality
- My manager has not asked me to
- Something else (please type)

**I2. If a tool were set up for you and you were shown how, how likely would you be to use it?**
Scale 1 to 5.

**I3. What is the most repetitive part of your job?**
Free text.

> *This is how you find the quick wins in Operations, Property Management and Administration, where the largest headcount and the lowest adoption sit together.*

---

## PART J. Turning answers into the eight dashboard scores

Every indicator is a number from 0 to 100, calculated per department, from this survey alone. Apply exactly the same rules in both waves.

Throughout: **"all respondents"** means everyone in that department who submitted the survey, including non-users. Non-users score 0 on usage-based indicators. They are not excluded, because excluding them would make a department with three keen users look fully adopted.

### J1. Active AI users, weight 20%

From **B5**.

`users = respondents in the department who answered "Yes" ÷ all respondents in the department × 100`

### J2. Usage frequency, weight 15%

From **C3 and C4**. Multiply the midpoints to get sessions per week, average across all respondents, then score against a target of 5 sessions per week.

| C3 answer | Days used | | C4 answer | Times per day |
|---|---|---|---|---|
| Less than one day | 0.5 | | Once | 1 |
| 1 day | 1 | | 2 to 3 times | 2.5 |
| 2 days | 2 | | 4 to 6 times | 5 |
| 3 days | 3 | | 7 to 10 times | 8.5 |
| 4 days | 4 | | More than 10 | 12 |
| 5 or more days | 5 | | | |

`sessions per week = days × times per day` (non-users = 0)
`freq = minimum of 100, and (department average sessions ÷ 5 × 100)`

### J3. AI training completion, weight 15%

From **H1**.

`train = respondents who selected any "Yes" option ÷ all respondents × 100`

In Wave 1 this will be low in most departments, which is correct and is exactly what makes the Wave 2 comparison meaningful.

### J4. AI in weekly workflow, weight 15%

From **D1**. Non-users score 0.

| D1 answer | Points |
|---|---|
| Never | 0 |
| Rarely, only when I remember | 20 |
| About once a week | 45 |
| Several times a week | 70 |
| Most days | 88 |
| Every working day | 100 |

`flow = average points across all respondents`

### J5. AI-assisted task volume, weight 10%

From **D4**. Non-users score 0.

| D4 answer | Tasks used |
|---|---|
| None | 0 |
| 1 to 5 | 3 |
| 6 to 15 | 10 |
| 16 to 30 | 23 |
| 31 to 60 | 45 |
| More than 60 | 75 |

`tasks = minimum of 100, and (department average tasks ÷ 20 × 100)`

### J6. Eligible workflows covered, weight 10%

From **E1**. Non-users score 0.

| E1 answer | Points |
|---|---|
| None of them | 0 |
| Under a quarter | 15 |
| A quarter to a half | 38 |
| Half to three quarters | 63 |
| More than three quarters | 85 |
| Almost all of them | 100 |

`cover = average points across all respondents`

### J7. Proficiency and readiness, weight 10%

From **Part F**, answered by everyone.

`prof = (department average number of correct answers ÷ 9) × 100`

### J8. Safe use of AI, weight 5%

Shown in the dashboard as the eighth indicator. From **Part G**, answered only by users. G1 and G6 are diagnostic and are not scored, because there is no policy for anyone to have complied with. Start each user at 100 and subtract:

| Condition | Deduction |
|---|---|
| G2 is "about half and half" | 15 |
| G2 is "mostly a personal account" | 25 |
| G2 is "always a personal account" | 40 |
| G2 is "I did not know the company provides one" | 20 |
| Each category selected at G3, other than "None of the above" | 12 |
| G3 is "I prefer not to say" | 12 |
| G5 is "No" | 10 |

Floor each person at 0, then average **across users only**.

If a department has fewer than five users in Wave 1, mark its compliance figure as provisional. An average of two people is not a department score.

`comp = average across users in the department`

### J9. What fills the drill-down panel

| Dashboard field | Source |
|---|---|
| Total employees | HR headcount file |
| Active AI users (count) | B5 "Yes" rate applied to HR headcount |
| Most-used AI tools with percentages | C1 and C2 |
| AI-enabled processes | The most-selected options at D3, written out |
| Number of AI use cases | Count of distinct task types named across D2, D3 and E2 |
| Key gap | Most-selected option at E3, written as a sentence |
| Opportunity | Most-repeated theme in the E2 free text |
| Employee level and location breakdowns | B2 and B3 |

---

## PART K. Running it

### Response rate is now the whole ballgame

With no console data behind it, a department's score is only as good as who bothered to answer. Enthusiastic AI users answer AI surveys. Set a floor:

- **60% or above:** publish the score normally.
- **40% to 59%:** publish, marked provisional in the dashboard.
- **Below 40%:** show the department in the grid but do not draw conclusions from its movement between waves.

Use the HR headcount file to calculate this for each department.

Operations, Property Management and Administration will be the hardest to reach and matter most to the organisation-wide figure. Do not rely on email for them. Ask supervisors to give people ten minutes in a team meeting with a shared tablet, or print paper copies and enter the responses yourself.

### Getting people to answer

Send from a senior sponsor, not from L&D. Response rates roughly double.

Send Monday morning. Reminder Thursday to departments below 50%. Second reminder the following Monday, this time from each head of department to their own team rather than a company-wide email. Close Friday.

Say in the invitation that the results decide where training goes next. That is true, and it is the only incentive that reliably works.

### Wave 2 must be identical

Do not improve the wording. Do not add better answer options. Do not drop a question because it seemed unclear. Any change to a scored question breaks the comparison for that indicator, and you will not be able to tell whether the number moved because behaviour changed or because the question changed.

The only additions permitted in Wave 2 are A3, H6, and the H1 options for the Claude training, all of which are new information rather than changes to existing questions.

If a question genuinely does not work, note it, keep it unchanged for Wave 2, and fix it in Wave 3.

### Reading the results

**A department where confidence (H2) is high but B5 usage is low.** People believe they could use it and are not. That is a permission and habit problem, not a skills problem, and a head of department can fix it in a week.

**A department where training completion is high but D1 is low.** Training happened and did not stick. More training will not help. Attach AI to one specific recurring process in that department instead.

**Free-text answers at E2 repeating across departments.** If four departments all name "summarising consultant reports", that is one assistant worth building once, not four training sessions worth running.

**Usage up but D7 checking down, between waves.** The training increased use faster than it increased judgement. Address it before the next round.

---

## PART L. Output file

Score into one row per department per wave, matching the CSV the dashboard exports:

```
month, department, business_function, location, total_employees,
leadership, managers, specialists, support_site,
active_users_last_30_days, avg_ai_sessions_per_user_per_week,
staff_trained_pct, staff_using_ai_weekly_pct,
ai_assisted_tasks_per_user_per_month, eligible_workflows_covered_pct,
avg_proficiency_score_0_100, policy_compliant_usage_pct,
documented_use_cases, top_tool_1, top_tool_1_usage_pct,
top_tool_2, top_tool_2_usage_pct, top_tool_3, top_tool_3_usage_pct,
ai_enabled_processes_semicolon_separated, key_gap, opportunity
```

Load Wave 1 as the baseline month and Wave 2 as the comparison month, so the dashboard's trend line and the "vs previous" figures work without any modification.

Keep both waves of raw responses, together with a copy of the exact form as it was sent. In six months, when someone asks whether the improvement was real, the raw file and the original wording are the only things that will answer them.
