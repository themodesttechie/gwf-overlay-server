# GrowWest Finance — Social Media Automation MVP

## Overview

Automated social media content pipeline for growwestfinance.com.au. Generates 2 compliance-safe posts per day across TikTok, Instagram, Facebook, and LinkedIn using Claude AI + Predis.ai visuals, with an Airtable approval dashboard.

## Architecture

The system uses **two coordinated Make.com scenarios** due to Predis.ai's asynchronous image generation:

```
SCENARIO A — GrowWest_Generate (runs daily at 6am AEST)
  Cron → Google Sheets (get pillar) → Claude API → JSON Parse
  → Predis.ai create_content → JSON Parse (get post_id)
  → Airtable create record (Status: "Generating")

SCENARIO B — GrowWest_Complete (triggered by Predis.ai webhook)
  Predis.ai Webhook → Download asset → Google Drive upload
  → Airtable find record (by post_id) → Airtable update (Status: "Review")
  → Gmail notification to business owner
```

## Deliverables Index

| File | Purpose |
|---|---|
| `01_claude_prompt.md` | Master Claude API prompt template |
| `02a_make_scenario_A_generate.json` | Make.com Scenario A blueprint (importable) |
| `02b_make_scenario_B_complete.json` | Make.com Scenario B blueprint (importable) |
| `03_airtable_schema.md` | Airtable base schema and setup instructions |
| `04_google_sheet_template.md` | Google Sheet structure, 30-row data, formulas |
| `05_predis_api_spec.md` | Predis.ai API specification |
| `06_testing_checklist.md` | Step-by-step testing guide |
| `07_approval_email.html` | HTML approval email template |
| `08_known_issues.md` | Known issues and workarounds |

## Setup Order

1. Create Google Sheet (see `04_google_sheet_template.md`)
2. Create Airtable base (see `03_airtable_schema.md`)
3. Configure Predis.ai brand kit and webhook URL
4. Create Google Drive folder: `GrowwestFinance/Social/Assets/`
5. Import Scenario A into Make.com and add connections
6. Deploy Scenario B webhook and register URL in Predis.ai
7. Run tests (see `06_testing_checklist.md`)

## Monthly Cost (AUD)

| Service | Cost |
|---|---|
| Make.com | $0 (free, ~744 ops/month used of 1,000) |
| Claude API | ~$15 |
| Predis.ai | ~$28 (Core annual plan) |
| Google Workspace | $0 |
| Airtable | $0 (free) |
| **Total** | **~$43/month** |
