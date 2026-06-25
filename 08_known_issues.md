# Deliverable 8 — Known Issues and Workarounds

---

## Issue 1 — Predis.ai Asset URL Expiry (1 Hour)

### The problem
The URL in `generated_media[].url` from the Predis.ai webhook is a time-limited CDN link that expires approximately 1 hour after generation. If Make.com Scenario B is slow to process (queue backlog, network issues, Make.com downtime), the URL may expire before the download step executes.

### How to detect it
- Module 2 (HTTP Download) returns HTTP 403 or 404
- The downloaded file size is 0 bytes or a few hundred bytes (an error HTML page, not an image)
- The error log in your Google Sheets `Errors` tab shows: "Asset download failed. URL may have expired."

### Workarounds

**Workaround A — Use Predis.ai's `get_posts` endpoint as fallback (recommended)**

Add an error handler on Module 2 that calls `GET https://brain.predis.ai/predis_api/v1/get_posts/?brand_id=YOUR_BRAND_ID&media_type=single_image&items_n=10` and searches the returned array for a post where `post_id` matches `{{1.post_id}}`. If found, use the URL from `urls[0]` instead.

Note: It is not confirmed whether `get_posts` URLs also expire — test this. If they do, proceed to Workaround B.

**Workaround B — Shorten the delay between generation and webhook processing**

Make.com free plan processes queued operations periodically. Scenario B (webhook) is event-driven and should trigger near-instantly when the webhook arrives. Ensure Scenario B is set to **On** (active) at all times — not just when Scenario A runs. An inactive Scenario B will queue webhooks and process them later, potentially after URL expiry.

**Workaround C — Store the Predis post_id and manually re-fetch**

If the image URL has expired and no fallback works:
1. Find the Airtable record with Status = `Generating` (not updated to `Review`)
2. Log into app.predis.ai > Posts — find the post by date
3. Right-click the post image > Copy image address
4. In Airtable, manually paste the URL into `Predis Asset URL` field
5. Manually download the image and upload to the correct Google Drive folder
6. Paste the Drive URL into `Asset Drive URL` and change Status to `Review`

**Workaround D — Contact Predis.ai support**

Predis.ai may be able to extend URL expiry for API customers or provide a permanent link endpoint. Worth raising on their support chat if this becomes a recurring problem.

---

## Issue 2 — Make.com Free Plan Operation Count

### Calculation

| Scenario | Modules per run | Runs per day | Ops/day |
|---|---|---|---|
| Scenario A (Generate) | 6 modules | 2 posts | 12 |
| Scenario B (Complete) | 6 modules | 2 webhooks | 12 |
| **Daily total** | | | **24** |
| **Monthly total (31 days)** | | | **744** |

**Free plan limit:** 1,000 operations/month
**Used:** ~744 ops/month (74.4% of allowance)
**Buffer:** ~256 ops/month for retries, manual test runs, and error handlers

### Risk scenarios

| Scenario | Additional ops | Risk |
|---|---|---|
| Error handlers fire (onerror modules) | +1–3 ops per failure | Low — only fires on failure |
| Manual "Run once" testing | +12 ops per full test | Medium — exhausted quickly with heavy testing |
| Google Drive folder creation (monthly) | +1 op | Negligible |
| Adding a 3rd post per day | +12 ops/day = +372/month | **Exceeds free plan** |

### Staying within the limit

- Run full end-to-end tests no more than 4–5 times per month
- Use the isolated module tests (Test 1–5 in the testing checklist) instead of full runs where possible
- Monitor usage in Make.com: Dashboard > Usage — check before mid-month
- If approaching 900 ops, pause Scenario A for a few days to conserve

### When to upgrade

Make.com's Core plan (~$10.59 USD/month) includes 10,000 ops/month. Upgrade when:
- Adding a 3rd daily post
- Adding Phase 2 publishing modules (each platform publish = additional ops)
- Monthly usage consistently above 800 ops

---

## Issue 3 — Claude API JSON Parsing Failures

### The problem
Despite a strong system prompt, Claude occasionally returns malformed JSON or wraps the JSON in markdown code fences (`` ```json ... ``` ``). This causes Module 3 (JSON Parse) to fail.

### How to detect it
- Module 3 throws a "JSON parse error" or similar
- The error handler writes to the Errors sheet with the raw Claude output
- Airtable record is never created for that day's post

### Root causes and fixes

**Cause A: Claude wraps response in markdown fences**
Raw output looks like:
```
```json
{"hook": "...", ...}
```
```

Fix: In the JSON Parse module, instead of mapping directly from `{{2.data.content[1].text}}`, add a text preprocessing step using Make.com's built-in functions to strip the fences:

```
{{replace(replace(2.data.content[1].text; "```json"; ""); "```"; "")}}
```

Add this as a Tools > Set Variable module between Module 2 and Module 3, then feed the cleaned variable into the JSON Parse module.

**Cause B: Claude adds explanation text before or after the JSON**
Output looks like: `Here is the content brief: {"hook": "..."} Let me know if you need changes.`

Fix: Use Make.com's `substring` function to extract only the JSON portion. Or strengthen the system prompt with: "Your response must begin with `{` and end with `}`. No text before or after."

**Cause C: Special characters in captions break JSON**
Australian content often includes `$`, `%`, `&`, quote marks inside strings. These require proper JSON escaping.

Fix: The Claude system prompt already instructs JSON-safe output. If failures persist, add a fallback: if JSON parse fails, store the raw Claude response in Airtable's `Notes` field for manual review, then send an email alert.

**Cause D: Max tokens too low — JSON truncated mid-output**
If Claude's output is cut off, the JSON will be incomplete and unparseable.

Fix: Increase `max_tokens` from 1500 to 2000. At claude-sonnet-4-6 pricing (~$3 AUD per 1M output tokens), the cost increase is negligible (~$0.002 per post).

### Recommended fallback flow

Add an error handler to Module 3 that:
1. Writes the raw Claude response to the Errors sheet (column C)
2. Creates a minimal Airtable record with Status = `Review`, pillar name, and a note saying "Manual review required — JSON parse failed. See Errors sheet."
3. Sends an alert email to the business owner

---

## Issue 4 — API Rate Limits

### Anthropic Claude API

| Limit type | Default limit | Impact |
|---|---|---|
| Requests per minute | 50 RPM (Tier 1) | No risk at 2 posts/day |
| Tokens per minute | 40,000 TPM (Tier 1) | No risk — each call uses ~1,500 tokens |
| Tokens per day | 1,000,000 TPD | No risk |

At 2 posts per day (2 API calls), you are far below all rate limits. No mitigation needed.

If you scale to dozens of posts per day (unlikely for this use case), upgrade your Anthropic usage tier at console.anthropic.com.

### Predis.ai API

| Limit | Value |
|---|---|
| Requests per minute | 60 RPM |
| Concurrent generations | 10 simultaneous |

At 2 posts per day, neither limit is relevant. If you ever test by firing many calls in quick succession, wait 60 seconds between batches.

### Gmail (via Make.com)

Gmail via Make.com has a sending limit of 500 emails/day on personal Gmail accounts. At 2 notification emails/day, this is not a concern.

---

## Issue 5 — Predis.ai Generation Failure (Fallback to Manual)

### The problem
Predis.ai generation occasionally fails (their webhook sends `"status": "error"`). When this happens, Scenario B receives the webhook but the filter (`status = completed`) blocks processing, so the Airtable record stays at Status = `Generating` indefinitely.

### Detection
- Check Airtable for records stuck in `Generating` status for more than 30 minutes
- Set an Airtable automation: if Status = `Generating` and `Created Date` is more than 1 day ago, send an alert email

### Fallback procedure — Manual image creation via Canva

When Predis.ai fails, create the post visual manually:

1. Go to canva.com and open the Grow West Finance brand template
2. Create a new post using the hook and body points from the Airtable record (Status = `Generating`)
3. Export as PNG (1080×1080 for single image, 1080×1350 for carousel cover)
4. Upload manually to the correct Google Drive folder: `GrowwestFinance/Social/Assets/YYYY-MM/`
5. Right-click the uploaded file > Share > Copy link
6. Paste the link into the Airtable record `Asset Drive URL` field
7. Change Status from `Generating` to `Review`
8. The record will now appear in the Review Queue view

**Canva brand template setup:**
- Create a 1080×1080 template in Canva with the Grow West Finance brand colours and logo
- Save it to your Canva brand kit for quick reuse
- Keep it simple: logo top-left, hook text large in centre, brand colour background, website URL bottom-right

---

## Issue 6 — Google Drive Monthly Folder ID

### The problem
The Google Drive upload module (Scenario B, Module 3) uses a static folder ID (`YOUR_GOOGLE_DRIVE_MONTHLY_FOLDER_ID`). This must be updated manually at the start of each month, or the files will continue uploading to the previous month's folder.

### Workaround A — Manual monthly update (simplest for MVP)

On the 1st of each month:
1. Create a new folder in Google Drive: `GrowwestFinance/Social/Assets/YYYY-MM/` (e.g. `2026-04`)
2. Right-click the new folder > Get ID from URL (the string after `/folders/`)
3. Open Make.com Scenario B > Edit Module 3 (Google Drive) > Update `folderId` with the new ID
4. Save the scenario

Set a monthly calendar reminder: "Update Make.com Drive folder ID — 1st of month"

### Workaround B — Dynamic folder creation (automated, more ops)

Add a Google Drive module before the upload step that:
1. Searches for a folder named `{{formatDate(now; "YYYY-MM")}}` inside the parent Assets folder
2. If not found, creates it
3. Uses the found/created folder ID for the upload

This costs 2 additional Make.com operations per run (~120 extra ops/month) but eliminates the monthly manual step. Implement this in Phase 2 when you're confident the system works.

---

## Issue 7 — Airtable Direct Record Links

### The problem
The "Review & Approve in Airtable" button in the approval email uses a direct record URL. Airtable direct record URLs have this format:
`https://airtable.com/BASE_ID/TABLE_ID/RECORD_ID`

The Base ID and Table ID are static (they don't change), but the Record ID changes for each new record. Make.com's Airtable create module returns the new record's ID, which Scenario B uses when it updates the record and sends the email.

### What can go wrong
- If you change the Airtable base or table name, the Base ID and Table ID don't change (they're internal IDs, not name-based)
- If you duplicate the base, the new base gets a different Base ID — update the email template
- If the business owner doesn't have Airtable access or is logged out, the link will prompt for login

### Fix
Ensure the business owner has an Airtable account invited to the base with at least **Editor** access (to change Status fields). Send them the base link separately so they bookmark it.

---

## Issue 8 — AEST vs AEDT Timezone Handling

### The problem
Australia uses two timezones depending on daylight saving:
- **AEST** (UTC+10): April to October (daylight saving ends)
- **AEDT** (UTC+11): October to April (daylight saving active)

The Make.com cron runs at a fixed UTC offset. If the scenario is set to 20:00 UTC (= 06:00 AEST), during AEDT it will actually fire at 07:00 AEDT — one hour late.

### Workaround
Set the cron to run at **19:00 UTC** (= 06:00 AEDT) during daylight saving months (October–April), and manually update to **20:00 UTC** (= 06:00 AEST) when daylight saving ends in April.

Set calendar reminders:
- **First Sunday in April** — Update Make.com scenario to 20:00 UTC (AEST begins)
- **First Sunday in October** — Update Make.com scenario to 19:00 UTC (AEDT begins)

Alternative: Run the cron at 20:00 UTC year-round and accept that during AEDT the post generates at 07:00 instead of 06:00. For a content pipeline, a 1-hour variance is acceptable.

---

## Issue 9 — Google Sheets Date Format Matching

### The problem
Make.com's `formatDate(now; "DD/MM/YYYY")` may not match the date format in your Google Sheet if the sheet cell format differs. Google Sheets can display dates differently based on locale settings even when the underlying value is the same.

### Symptoms
- Module 1 (Google Sheets search) returns zero rows even though today's date exists in the sheet
- The cron runs at the right time but no pillar is found

### Fix
1. In the Google Sheet, ensure Column A is formatted as **Plain text** (not Date format)
2. To force this: select Column A > Format > Number > **Plain text**
3. Re-enter the dates in Column A as plain text strings: `23/03/2026`, `24/03/2026`, etc.
4. In Make.com, verify the date formula: `{{formatDate(addHours(now; 10); "DD/MM/YYYY")}}` (with AEST offset)

If the issue persists, use Day Number (Column D) as an alternative lookup:
- Calculate today's day number in Make.com: `{{ceil(mod(dateDifference(now; parseDate("23/03/2026"; "DD/MM/YYYY"); "days"); 9)) + 1}}`
- Search Column D for that number instead of searching Column A for the date

---

## Issue 10 — ACL (Australian Credit Licence) Number

### The problem
The compliance disclaimer appended to all captions includes `[ACL NUMBER]` as a placeholder. Publishing content with `[ACL NUMBER]` literally in the caption would look unprofessional and potentially raise compliance concerns.

### Fix — Required before going live
1. Confirm with the business owner whether Grow West Finance holds its own ACL or operates as a credit representative under an aggregator's licence
2. If own ACL: replace `[ACL NUMBER]` with the actual ACL number in the Claude system prompt
3. If credit representative: replace the disclaimer with: `Grow West Finance | Credit Representative [CR NUMBER] of [Aggregator Name] | ACL [AGGREGATOR ACL NUMBER]`
4. Update the system prompt in Scenario A, Module 2 (the `data` field in the HTTP mapper)

This change must be made in the Make.com scenario body text, not just in the `01_claude_prompt.md` documentation file.

---

## Summary Table

| Issue | Severity | Effort to fix | Action |
|---|---|---|---|
| Predis URL expiry | Medium | Low | Add `get_posts` fallback to error handler |
| Op count management | Low | None | Monitor monthly, stay under 900 |
| Claude JSON parse failure | Medium | Low | Add text-clean step + fallback record creation |
| API rate limits | None | None | No action needed at this scale |
| Predis generation failure | Low | None | Use Canva fallback procedure |
| Monthly Drive folder ID | Low | Low | Set calendar reminder, update manually |
| Airtable record links | Low | None | Ensure business owner has Airtable access |
| AEST/AEDT timezone | Low | Low | Set calendar reminders for DST transitions |
| Google Sheets date format | Low | Low | Set Column A to Plain text |
| ACL number placeholder | **High** | Low | **Must fix before first live post** |
