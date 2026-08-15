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
    "users": 20,
    "freq": 15,
    "train": 15,
    "flow": 15,
    "tasks": 10,
    "cover": 10,
    "prof": 10,
    "comp": 5
  },
  "targets": {
    "org": 70,
    "quarter": 65,
    "min": 40,
    "byDept": {}
  },
  "waves": [
    {
      "label": "Wave 1 · Aug 2026 (sample)",
      "departments": [
        {
          "name": "Information Technology",
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
            "freq": 95,
            "train": 98,
            "flow": 90,
            "tasks": 88,
            "cover": 86,
            "prof": 94,
            "comp": 98
          },
          "sessions": 8.6,
          "cases": 19,
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
          "opportunity": "Publish the ticket-triage assistant as a shared service other departments can call."
        },
        {
          "name": "Marketing & Communications",
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
            "freq": 88,
            "train": 90,
            "flow": 84,
            "tasks": 86,
            "cover": 74,
            "prof": 80,
            "comp": 72
          },
          "sessions": 7.4,
          "cases": 16,
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
          "opportunity": "Move all creative work into approved tools and reuse the brand-voice prompt library."
        },
        {
          "name": "Learning & Development",
          "function": "Corporate Services",
          "staff": 9,
          "mix": {
            "leadership": 1,
            "manager": 2,
            "specialist": 5,
            "support": 1
          },
          "metrics": {
            "users": 89,
            "freq": 76,
            "train": 100,
            "flow": 78,
            "tasks": 70,
            "cover": 68,
            "prof": 74,
            "comp": 88
          },
          "sessions": 6.1,
          "cases": 12,
          "tools": [
            [
              "Claude (Enterprise)",
              92
            ],
            [
              "Microsoft 365 Copilot",
              44
            ],
            [
              "Otter / Teams AI notes",
              38
            ]
          ],
          "processes": [
            "Course outline and assessment drafting",
            "Training needs analysis",
            "Session summaries and follow-ups",
            "Nomination and attendance reporting"
          ],
          "gap": "High skill, small team, so capacity limits how much they can support other departments.",
          "opportunity": "Turn the internal Claude programme into a repeatable cycle run by departmental champions."
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
            "freq": 74,
            "train": 68,
            "flow": 72,
            "tasks": 78,
            "cover": 64,
            "prof": 66,
            "comp": 58
          },
          "sessions": 5.2,
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
          "opportunity": "A mobile-approved assistant converts unmanaged use into measured, compliant use."
        },
        {
          "name": "Customer Service",
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
            "freq": 70,
            "train": 72,
            "flow": 66,
            "tasks": 74,
            "cover": 60,
            "prof": 62,
            "comp": 64
          },
          "sessions": 5.0,
          "cases": 11,
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
          "opportunity": "Response templates generated once and reused would lift the whole shift pattern."
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
            "freq": 58,
            "train": 80,
            "flow": 60,
            "tasks": 52,
            "cover": 54,
            "prof": 58,
            "comp": 76
          },
          "sessions": 4.1,
          "cases": 9,
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
          "opportunity": "Tie AI use to the recruitment cycle so it becomes part of the process, not an extra step."
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
            "freq": 54,
            "train": 66,
            "flow": 52,
            "tasks": 48,
            "cover": 46,
            "prof": 54,
            "comp": 82
          },
          "sessions": 3.6,
          "cases": 8,
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
          "opportunity": "An approved closed environment for financial data removes the main blocker."
        },
        {
          "name": "Project Development",
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
            "freq": 48,
            "train": 56,
            "flow": 44,
            "tasks": 50,
            "cover": 40,
            "prof": 46,
            "comp": 60
          },
          "sessions": 3.1,
          "cases": 7,
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
          "opportunity": "Mobile summarising of site reports is the highest-value quick win."
        },
        {
          "name": "Property Management",
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
            "freq": 44,
            "train": 52,
            "flow": 40,
            "tasks": 46,
            "cover": 38,
            "prof": 42,
            "comp": 58
          },
          "sessions": 2.9,
          "cases": 6,
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
          "opportunity": "Short task-based training on one repeated job beats broad general training here."
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
            "freq": 42,
            "train": 50,
            "flow": 36,
            "tasks": 40,
            "cover": 34,
            "prof": 38,
            "comp": 62
          },
          "sessions": 2.7,
          "cases": 5,
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
          "opportunity": "A one-day workflow mapping session would likely double this department's score."
        },
        {
          "name": "Operations",
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
            "freq": 36,
            "train": 44,
            "flow": 32,
            "tasks": 38,
            "cover": 30,
            "prof": 34,
            "comp": 54
          },
          "sessions": 2.4,
          "cases": 5,
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
          "opportunity": "Every point gained here moves the organisation number more than anywhere else."
        },
        {
          "name": "Procurement",
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
            "train": 38,
            "flow": 28,
            "tasks": 26,
            "cover": 24,
            "prof": 30,
            "comp": 58
          },
          "sessions": 2.1,
          "cases": 4,
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
          "opportunity": "Bid comparison is slow and rule-based, the natural place to start."
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
            "freq": 20,
            "train": 28,
            "flow": 18,
            "tasks": 16,
            "cover": 14,
            "prof": 22,
            "comp": 40
          },
          "sessions": 1.5,
          "cases": 3,
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
          "opportunity": "A closed no-training-on-data environment plus a written legal AI protocol unlocks this team."
        }
      ]
    }
  ]
};
