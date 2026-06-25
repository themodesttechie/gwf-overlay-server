# Deliverable 4 — Google Sheet Pillar Rotation Template

## Sheet Setup

**Sheet name (tab):** `Pillar Schedule`
**Create a second tab named:** `Errors` (used by Make.com for error logging)

---

## Column Structure

| Column | Header | Format | Notes |
|---|---|---|---|
| A | Date | DD/MM/YYYY (plain text) | Pre-populated dates |
| B | Pillar | Plain text | One of the 9 content pillars |
| C | Post Format | Plain text | `single_image` or `carousel` |
| D | Day Number | Number | 1–9, cycling |
| E | Status | Plain text | Leave blank — Make.com writes "Done" here when processed |
| F | Notes | Plain text | Optional manual notes |

### Row 1 (Header row)

```
A1: Date    B1: Pillar    C1: Post Format    D1: Day Number    E1: Status    F1: Notes
```

---

## 30-Day Pre-Populated Data (starting 23/03/2026)

Copy-paste this data starting from row 2:

```
Date         | Pillar                                  | Post Format  | Day Number
23/03/2026   | Home loans                              | single_image | 1
24/03/2026   | Refinancing                             | carousel     | 2
25/03/2026   | First home buyers                       | single_image | 3
26/03/2026   | Investment property                     | carousel     | 4
27/03/2026   | Interest rates and market updates       | single_image | 5
28/03/2026   | Finance mistakes to avoid               | carousel     | 6
29/03/2026   | Myth busting                            | single_image | 7
30/03/2026   | Case studies and success stories        | carousel     | 8
31/03/2026   | Step-by-step guidance                   | single_image | 9
01/04/2026   | Home loans                              | single_image | 1
02/04/2026   | Refinancing                             | carousel     | 2
03/04/2026   | First home buyers                       | single_image | 3
04/04/2026   | Investment property                     | carousel     | 4
05/04/2026   | Interest rates and market updates       | single_image | 5
06/04/2026   | Finance mistakes to avoid               | carousel     | 6
07/04/2026   | Myth busting                            | single_image | 7
08/04/2026   | Case studies and success stories        | carousel     | 8
09/04/2026   | Step-by-step guidance                   | single_image | 9
10/04/2026   | Home loans                              | single_image | 1
11/04/2026   | Refinancing                             | carousel     | 2
12/04/2026   | First home buyers                       | single_image | 3
13/04/2026   | Investment property                     | carousel     | 4
14/04/2026   | Interest rates and market updates       | single_image | 5
15/04/2026   | Finance mistakes to avoid               | carousel     | 6
16/04/2026   | Myth busting                            | single_image | 7
17/04/2026   | Case studies and success stories        | carousel     | 8
18/04/2026   | Step-by-step guidance                   | single_image | 9
19/04/2026   | Home loans                              | single_image | 1
20/04/2026   | Refinancing                             | carousel     | 2
21/04/2026   | First home buyers                       | single_image | 3
```

---

## Formula for Future Rows (self-extending rotation)

To extend the schedule beyond the 30 pre-populated rows, use these formulas starting at row 32 (after the last pre-populated row):

**Column A (Date):** `=A31+1`
*(This adds 1 day to the previous row's date — drag down to extend)*

**Column D (Day Number):**
`=MOD(D31,9)+1`
*(Cycles 1 through 9 indefinitely — drag down to extend)*

**Column B (Pillar):**
```
=CHOOSE(D32,"Home loans","Refinancing","First home buyers","Investment property","Interest rates and market updates","Finance mistakes to avoid","Myth busting","Case studies and success stories","Step-by-step guidance")
```

**Column C (Post Format):**
```
=IF(OR(D32=1,D32=3,D32=5,D32=7,D32=9),"single_image","carousel")
```

> **How to use:** Fill A32 with `=A31+1`, D32 with `=MOD(D31,9)+1`, then fill B32 and C32 with the formulas above. Select A32:F32 and drag down as many rows as needed. The schedule self-extends automatically.

---

## Make.com Formula — Reading Today's Row

In the Make.com Google Sheets `searchRows` module, the filter condition should be:

**Column to filter:** `Date` (Column A)
**Comparison:** `Equal to`
**Value:** `{{formatDate(now; "DD/MM/YYYY")}}`

This uses Make.com's built-in `formatDate` function to format today's date in the same DD/MM/YYYY format as the sheet.

> **Important timezone note:** Make.com's `now` variable uses UTC by default. To get today's date in AEST (UTC+10), use: `{{formatDate(addHours(now; 10); "DD/MM/YYYY")}}`
> During AEDT (daylight saving, October–April): use `addHours(now; 11)` instead.
> The scenario runs at 20:00 UTC which is 06:00 AEST — so `formatDate(now; "DD/MM/YYYY")` at 20:00 UTC will return the *previous* calendar day. Use `addHours(now; 10)` to get the correct AEST date.

---

## Errors Sheet Structure

The second tab `Errors` is written to by Make.com when any module fails. Set up with these headers in row 1:

```
A1: Timestamp    B1: Module    C1: Error    D1: Pillar    E1: Scenario
```

Leave rows 2+ empty — Make.com appends error rows automatically.

To monitor errors, set a Google Sheets notification (Tools > Notifications) to email you when any cell in column C is modified.

---

## Getting Your Google Sheet ID

After creating the sheet, find the ID in the URL:
```
https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
```

The long string between `/d/` and `/edit` is the Sheet ID. Copy it into the Make.com scenario JSON where it says `YOUR_GOOGLE_SHEET_ID`.

---

## Important: Column Name Matching

Make.com's Google Sheets module references columns by their **header name** (Row 1 values). The column headers in the scenario JSON are:
- `Date` — Column A header
- `Pillar` — Column B header
- `Post Format` — Column C header
- `Day Number` — Column D header

These must match exactly (case-sensitive) with your Row 1 headers. If you rename a column header in the sheet, update the Make.com scenario mapper accordingly.
