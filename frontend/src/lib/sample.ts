/**
 * Built-in sample figures.
 *
 * Loaded only when neither the API nor a published data.json is available, so
 * the dashboard can always be demonstrated. The UI shows a banner whenever
 * these are in use, because sample numbers must never be mistaken for real
 * survey results.
 */

import type { WirePayload } from "./wire";

export const SAMPLE_PAYLOAD: WirePayload = {
  "weights": {
    "users": 16,
    "freq": 15,
    "train": 15,
    "flow": 15,
    "tasks": 8,
    "cover": 10,
    "prof": 10,
    "comp": 5,
    "agent": 3,
    "automate": 3
  },
  "targets": {
    "org": 70,
    "quarter": 65,
    "min": 40,
    "byDept": {}
  },
  "waves": [
    {
      "label": "Wave 1 \u00b7 Aug 2026 (sample)",
      "departments": [
        {
          "name": "IT",
          "function": "Technology",
          "staff": 24,
          "mix": {
            "leadership": 1,
            "manager": 4,
            "specialist": 15,
            "support": 4
          },
          "metrics": {
            "users": 92,
            "freq": 89,
            "train": 100,
            "flow": 88,
            "tasks": 86,
            "cover": 82,
            "prof": 90,
            "comp": 100,
            "agent": 32,
            "automate": 39
          },
          "sessions": 9.2,
          "cases": 18,
          "tools": [
            [
              "Claude (Enterprise)",
              88
            ],
            [
              "GitHub Copilot",
              71
            ],
            [
              "Microsoft 365 Copilot",
              54
            ]
          ],
          "processes": [
            "Ticket triage and first-line response drafting",
            "Code review and test generation",
            "Infrastructure runbook drafting",
            "Vendor documentation summarising"
          ],
          "gap": "Use is concentrated in the engineering team; night-shift service desk still works manually.",
          "opportunity": "Publish the ticket-triage assistant as a shared service other departments can call.",
          "aiAgentsCount": 4,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 5,
          "aiAutomationsPersonal": 3
        },
        {
          "name": "Digital Transformation",
          "function": "Technology",
          "staff": 11,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 6,
            "support": 1
          },
          "metrics": {
            "users": 90,
            "freq": 87,
            "train": 98,
            "flow": 86,
            "tasks": 84,
            "cover": 80,
            "prof": 88,
            "comp": 100,
            "agent": 31,
            "automate": 38
          },
          "sessions": 9.0,
          "cases": 18,
          "tools": [
            [
              "Claude (Enterprise)",
              90
            ],
            [
              "Microsoft 365 Copilot",
              68
            ],
            [
              "Power Automate AI Builder",
              44
            ]
          ],
          "processes": [
            "Automation opportunity mapping",
            "Internal AI tool evaluation",
            "Change management communications",
            "Rollout playbook drafting"
          ],
          "gap": "Small team driving change across the business, but adoption in other departments still lags behind their own.",
          "opportunity": "Formalise the team as the internal AI centre of excellence, with a repeatable onboarding kit per department.",
          "aiAgentsCount": 2,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 2,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Marketing",
          "function": "Commercial",
          "staff": 18,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 11,
            "support": 3
          },
          "metrics": {
            "users": 83,
            "freq": 80,
            "train": 91,
            "flow": 79,
            "tasks": 77,
            "cover": 73,
            "prof": 81,
            "comp": 95,
            "agent": 29,
            "automate": 35
          },
          "sessions": 8.3,
          "cases": 17,
          "tools": [
            [
              "Claude (Enterprise)",
              79
            ],
            [
              "Adobe Firefly",
              63
            ],
            [
              "Canva Magic Studio",
              58
            ]
          ],
          "processes": [
            "Campaign copy in Arabic and English",
            "Launch content for Mina Al Arab releases",
            "Social listening summaries",
            "Press release first drafts"
          ],
          "gap": "Compliance is the weak point. Some image generation still happens in personal accounts.",
          "opportunity": "Move all creative work into approved tools and reuse the brand-voice prompt library.",
          "aiAgentsCount": 3,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 3,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Sales",
          "function": "Commercial",
          "staff": 34,
          "mix": {
            "leadership": 2,
            "manager": 6,
            "specialist": 20,
            "support": 6
          },
          "metrics": {
            "users": 71,
            "freq": 68,
            "train": 79,
            "flow": 67,
            "tasks": 65,
            "cover": 61,
            "prof": 69,
            "comp": 83,
            "agent": 25,
            "automate": 30
          },
          "sessions": 7.1,
          "cases": 14,
          "tools": [
            [
              "Claude (Enterprise)",
              64
            ],
            [
              "Microsoft 365 Copilot",
              49
            ],
            [
              "Custom RAK sales assistant",
              41
            ]
          ],
          "processes": [
            "Lead follow-up messages",
            "Objection handling scripts",
            "Unit comparison summaries",
            "CRM note clean-up"
          ],
          "gap": "Agents in the field use AI on personal phones, outside any company account.",
          "opportunity": "A mobile-approved assistant converts unmanaged use into measured, compliant use.",
          "aiAgentsCount": 4,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 5,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Customer Relations",
          "function": "Commercial",
          "staff": 22,
          "mix": {
            "leadership": 1,
            "manager": 4,
            "specialist": 10,
            "support": 7
          },
          "metrics": {
            "users": 68,
            "freq": 65,
            "train": 76,
            "flow": 64,
            "tasks": 62,
            "cover": 58,
            "prof": 66,
            "comp": 80,
            "agent": 24,
            "automate": 29
          },
          "sessions": 6.8,
          "cases": 14,
          "tools": [
            [
              "Claude (Enterprise)",
              61
            ],
            [
              "Microsoft 365 Copilot",
              47
            ],
            [
              "Custom RAK service assistant",
              35
            ]
          ],
          "processes": [
            "Complaint response drafting",
            "Arabic and English reply translation",
            "Handover note summarising",
            "Knowledge base updates"
          ],
          "gap": "Evening and weekend shifts use AI far less than weekday teams.",
          "opportunity": "Response templates generated once and reused would lift the whole shift pattern.",
          "aiAgentsCount": 2,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 4,
          "aiAutomationsPersonal": 2
        },
        {
          "name": "Hospitality",
          "function": "Commercial",
          "staff": 19,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 9,
            "support": 6
          },
          "metrics": {
            "users": 62,
            "freq": 59,
            "train": 70,
            "flow": 58,
            "tasks": 56,
            "cover": 52,
            "prof": 60,
            "comp": 74,
            "agent": 22,
            "automate": 26
          },
          "sessions": 6.2,
          "cases": 12,
          "tools": [
            [
              "Claude (Enterprise)",
              55
            ],
            [
              "Microsoft 365 Copilot",
              42
            ],
            [
              "Canva Magic Studio",
              26
            ]
          ],
          "processes": [
            "Guest communication drafting",
            "Event proposal writing",
            "Feedback summarising",
            "Menu and signage copy"
          ],
          "gap": "Front-of-house staff have little desk time, so AI use is mostly back-office.",
          "opportunity": "A guest-messaging assistant on shared tablets would bring AI to the floor, not just the office.",
          "aiAgentsCount": 2,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 2,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Human Resources",
          "function": "Corporate Services",
          "staff": 14,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 8,
            "support": 2
          },
          "metrics": {
            "users": 64,
            "freq": 61,
            "train": 72,
            "flow": 60,
            "tasks": 58,
            "cover": 54,
            "prof": 62,
            "comp": 76,
            "agent": 22,
            "automate": 27
          },
          "sessions": 6.4,
          "cases": 13,
          "tools": [
            [
              "Claude (Enterprise)",
              57
            ],
            [
              "Microsoft 365 Copilot",
              52
            ],
            [
              "Otter / Teams AI notes",
              29
            ]
          ],
          "processes": [
            "Job description drafting",
            "CV screening summaries",
            "Policy rewriting in plain English",
            "Interview note summarising"
          ],
          "gap": "Strong training numbers, weak daily use. People trained, then returned to old habits.",
          "opportunity": "Tie AI use to the recruitment cycle so it becomes part of the process, not an extra step.",
          "aiAgentsCount": 2,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 2,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Finance",
          "function": "Corporate Services",
          "staff": 26,
          "mix": {
            "leadership": 1,
            "manager": 5,
            "specialist": 16,
            "support": 4
          },
          "metrics": {
            "users": 58,
            "freq": 55,
            "train": 66,
            "flow": 54,
            "tasks": 52,
            "cover": 48,
            "prof": 56,
            "comp": 70,
            "agent": 20,
            "automate": 24
          },
          "sessions": 5.8,
          "cases": 12,
          "tools": [
            [
              "Microsoft 365 Copilot",
              58
            ],
            [
              "Claude (Enterprise)",
              44
            ],
            [
              "Power Automate AI Builder",
              21
            ]
          ],
          "processes": [
            "Variance commentary drafting",
            "Invoice data extraction",
            "Board pack summarising",
            "Contract payment term checks"
          ],
          "gap": "Data sensitivity makes the team cautious; most work stays in spreadsheets.",
          "opportunity": "An approved closed environment for financial data removes the main blocker.",
          "aiAgentsCount": 3,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 3,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Risk Management & Control",
          "function": "Corporate Services",
          "staff": 10,
          "mix": {
            "leadership": 1,
            "manager": 2,
            "specialist": 6,
            "support": 1
          },
          "metrics": {
            "users": 53,
            "freq": 50,
            "train": 61,
            "flow": 49,
            "tasks": 47,
            "cover": 43,
            "prof": 51,
            "comp": 65,
            "agent": 19,
            "automate": 22
          },
          "sessions": 5.3,
          "cases": 11,
          "tools": [
            [
              "Microsoft 365 Copilot",
              50
            ],
            [
              "Claude (Enterprise)",
              38
            ],
            [
              "Power Automate AI Builder",
              19
            ]
          ],
          "processes": [
            "Risk register summarising",
            "Control testing documentation",
            "Incident report drafting",
            "Policy gap analysis"
          ],
          "gap": "Work is judgement-heavy and sensitive, so the team is deliberately cautious about what goes into any AI tool.",
          "opportunity": "A closed-environment control-testing assistant would save the most repetitive part of the job first.",
          "aiAgentsCount": 1,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 1,
          "aiAutomationsPersonal": 0
        },
        {
          "name": "Internal Audit",
          "function": "Corporate Services",
          "staff": 8,
          "mix": {
            "leadership": 1,
            "manager": 2,
            "specialist": 4,
            "support": 1
          },
          "metrics": {
            "users": 49,
            "freq": 46,
            "train": 57,
            "flow": 45,
            "tasks": 43,
            "cover": 39,
            "prof": 47,
            "comp": 61,
            "agent": 17,
            "automate": 21
          },
          "sessions": 4.9,
          "cases": 10,
          "tools": [
            [
              "Microsoft 365 Copilot",
              47
            ],
            [
              "Claude (Enterprise)",
              35
            ]
          ],
          "processes": [
            "Audit finding write-ups",
            "Working paper summarising",
            "Sample testing checklists"
          ],
          "gap": "Independence concerns mean the team hasn't yet agreed what AI use is appropriate for audit evidence.",
          "opportunity": "A written AI-use protocol for audit work would unlock this small but influential team.",
          "aiAgentsCount": 1,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 1,
          "aiAutomationsPersonal": 0
        },
        {
          "name": "Development",
          "function": "Technical",
          "staff": 31,
          "mix": {
            "leadership": 2,
            "manager": 6,
            "specialist": 17,
            "support": 6
          },
          "metrics": {
            "users": 45,
            "freq": 42,
            "train": 53,
            "flow": 41,
            "tasks": 39,
            "cover": 35,
            "prof": 43,
            "comp": 57,
            "agent": 16,
            "automate": 19
          },
          "sessions": 4.5,
          "cases": 9,
          "tools": [
            [
              "Microsoft 365 Copilot",
              41
            ],
            [
              "Claude (Enterprise)",
              33
            ],
            [
              "Otter / Teams AI notes",
              24
            ]
          ],
          "processes": [
            "Consultant report summarising",
            "Meeting minutes",
            "Tender clarification drafting",
            "Progress report writing"
          ],
          "gap": "Site-based staff have limited desk time and patchy device access.",
          "opportunity": "Mobile summarising of site reports is the highest-value quick win.",
          "aiAgentsCount": 3,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 2,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Facilities & Community Management",
          "function": "Technical",
          "staff": 28,
          "mix": {
            "leadership": 1,
            "manager": 5,
            "specialist": 13,
            "support": 9
          },
          "metrics": {
            "users": 43,
            "freq": 40,
            "train": 51,
            "flow": 39,
            "tasks": 37,
            "cover": 33,
            "prof": 41,
            "comp": 55,
            "agent": 15,
            "automate": 18
          },
          "sessions": 4.3,
          "cases": 9,
          "tools": [
            [
              "Microsoft 365 Copilot",
              39
            ],
            [
              "Claude (Enterprise)",
              30
            ],
            [
              "Custom RAK service assistant",
              18
            ]
          ],
          "processes": [
            "Tenant notice drafting",
            "Maintenance request summarising",
            "Handover checklists",
            "Owner association correspondence"
          ],
          "gap": "Technicians and support staff are a third of the team and barely use AI.",
          "opportunity": "Short task-based training on one repeated job beats broad general training here.",
          "aiAgentsCount": 3,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 2,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Administration",
          "function": "Corporate Services",
          "staff": 16,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 7,
            "support": 5
          },
          "metrics": {
            "users": 38,
            "freq": 35,
            "train": 46,
            "flow": 34,
            "tasks": 32,
            "cover": 28,
            "prof": 36,
            "comp": 50,
            "agent": 13,
            "automate": 16
          },
          "sessions": 3.8,
          "cases": 8,
          "tools": [
            [
              "Microsoft 365 Copilot",
              36
            ],
            [
              "Claude (Enterprise)",
              25
            ],
            [
              "Otter / Teams AI notes",
              15
            ]
          ],
          "processes": [
            "Correspondence drafting",
            "Document filing and naming",
            "Travel and visa letters",
            "Meeting scheduling summaries"
          ],
          "gap": "The work is routine and repetitive, ideal for AI, but nobody has mapped it.",
          "opportunity": "A one-day workflow mapping session would likely double this department's score.",
          "aiAgentsCount": 1,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 1,
          "aiAutomationsPersonal": 0
        },
        {
          "name": "Construction",
          "function": "Technical",
          "staff": 41,
          "mix": {
            "leadership": 2,
            "manager": 7,
            "specialist": 17,
            "support": 15
          },
          "metrics": {
            "users": 34,
            "freq": 31,
            "train": 42,
            "flow": 30,
            "tasks": 28,
            "cover": 24,
            "prof": 32,
            "comp": 46,
            "agent": 12,
            "automate": 14
          },
          "sessions": 3.4,
          "cases": 7,
          "tools": [
            [
              "Microsoft 365 Copilot",
              31
            ],
            [
              "Claude (Enterprise)",
              22
            ],
            [
              "Power Automate AI Builder",
              12
            ]
          ],
          "processes": [
            "Shift handover notes",
            "Incident report drafting",
            "Supplier coordination emails",
            "Checklist generation"
          ],
          "gap": "Largest headcount, lowest coverage. The biggest single drag on the org-wide rate.",
          "opportunity": "Every point gained here moves the organisation number more than anywhere else.",
          "aiAgentsCount": 2,
          "aiAgentsPersonal": 1,
          "aiAutomationsCount": 3,
          "aiAutomationsPersonal": 0
        },
        {
          "name": "Procurement & Tendering",
          "function": "Corporate Services",
          "staff": 12,
          "mix": {
            "leadership": 1,
            "manager": 3,
            "specialist": 6,
            "support": 2
          },
          "metrics": {
            "users": 33,
            "freq": 30,
            "train": 41,
            "flow": 29,
            "tasks": 27,
            "cover": 23,
            "prof": 31,
            "comp": 45,
            "agent": 12,
            "automate": 14
          },
          "sessions": 3.3,
          "cases": 7,
          "tools": [
            [
              "Microsoft 365 Copilot",
              29
            ],
            [
              "Claude (Enterprise)",
              19
            ],
            [
              "Power Automate AI Builder",
              9
            ]
          ],
          "processes": [
            "Tender document comparison",
            "Supplier response summarising",
            "Purchase order checks"
          ],
          "gap": "Only one or two people trained; the rest have never opened an approved tool.",
          "opportunity": "Bid comparison is slow and rule-based, the natural place to start.",
          "aiAgentsCount": 1,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 1,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Management",
          "function": "Leadership",
          "staff": 9,
          "mix": {
            "leadership": 6,
            "manager": 3,
            "specialist": 0,
            "support": 0
          },
          "metrics": {
            "users": 47,
            "freq": 44,
            "train": 55,
            "flow": 43,
            "tasks": 41,
            "cover": 37,
            "prof": 45,
            "comp": 59,
            "agent": 16,
            "automate": 20
          },
          "sessions": 4.7,
          "cases": 9,
          "tools": [
            [
              "Claude (Enterprise)",
              42
            ],
            [
              "Microsoft 365 Copilot",
              30
            ]
          ],
          "processes": [
            "Board pack review notes",
            "Strategic memo drafting",
            "Meeting preparation summaries"
          ],
          "gap": "Leadership uses AI personally more than they've asked their teams to, so adoption below them lags what they'd expect.",
          "opportunity": "Leadership visibly using and endorsing specific tools is often the fastest way to move the rest of the org.",
          "aiAgentsCount": 1,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 1,
          "aiAutomationsPersonal": 1
        },
        {
          "name": "Legal",
          "function": "Corporate Services",
          "staff": 7,
          "mix": {
            "leadership": 1,
            "manager": 2,
            "specialist": 3,
            "support": 1
          },
          "metrics": {
            "users": 24,
            "freq": 21,
            "train": 32,
            "flow": 20,
            "tasks": 18,
            "cover": 14,
            "prof": 22,
            "comp": 36,
            "agent": 8,
            "automate": 10
          },
          "sessions": 2.4,
          "cases": 5,
          "tools": [
            [
              "Microsoft 365 Copilot",
              21
            ],
            [
              "Claude (Enterprise)",
              14
            ]
          ],
          "processes": [
            "Clause comparison",
            "Contract summarising"
          ],
          "gap": "Confidentiality concerns and no approved workflow for legal documents.",
          "opportunity": "A closed no-training-on-data environment plus a written legal AI protocol unlocks this team.",
          "aiAgentsCount": 0,
          "aiAgentsPersonal": 0,
          "aiAutomationsCount": 0,
          "aiAutomationsPersonal": 0
        }
      ]
    }
  ]
};