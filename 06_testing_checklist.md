# Deliverable 6 — Step-by-Step Testing Checklist

Run these tests in order before activating the full automated scenario. Each test is independent — you can pass/fail each one separately.

---

## Pre-Test Setup

Before testing anything, confirm these are ready:

- [ ] Google Sheet created with `Pillar Schedule` and `Errors` tabs, at least 2 rows of data including today's date
- [ ] Airtable base created with `Content Posts` table and all fields from schema
- [ ] Predis.ai account active, brand kit configured, brand ID noted
- [ ] Google Drive folder created: `GrowwestFinance/Social/Assets/2026-03/`
- [ ] Anthropic API key active (check console.anthropic.com — ensure you have credits)
- [ ] Make.com account active, both scenarios imported (but NOT activated yet)
- [ ] All placeholder values replaced in both scenario JSONs

---

## Test 1 — Claude API Call (Isolated)

Test that the Claude API accepts your key and returns valid JSON.

**Run this in your terminal (or use a REST client like Postman/Hoppscotch):**

```bash
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 1500,
    "system": "You are a content strategist for an Australian mortgage brokerage. Return ONLY valid JSON — no markdown, no code fences.",
    "messages": [{
      "role": "user",
      "content": "Generate a social media content brief for the pillar: Refinancing. Return JSON with these fields: hook (string), body_points (array of 3 strings), cta (string), compliance_flag (boolean), pillar (string), post_format (string). Make it compliance-safe for Australian financial services."
    }]
  }'
```

**Expected response structure:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "{\"hook\": \"...\", \"body_points\": [\"...\", \"...\", \"...\"], ...}"
    }
  ],
  "stop_reason": "end_turn"
}
```

**Pass criteria:**
- [ ] HTTP 200 response received
- [ ] `content[0].text` contains a string that starts with `{`
- [ ] That string is valid JSON (paste it into https://jsonlint.com to verify)
- [ ] The JSON contains all expected fields
- [ ] No specific interest rates are mentioned (compliance check)

**Fail — common causes:**
- HTTP 401: API key wrong or inactive — check console.anthropic.com
- HTTP 529: API overloaded — retry in 60 seconds
- Response contains markdown `` ```json `` fences: prompt needs to be stronger — the full system prompt in the scenario handles this

---

## Test 2 — JSON Parse Verification

Test that the JSON Claude returns can be cleanly parsed.

**Take the `content[0].text` value from Test 1 and:**

1. Paste it into https://jsonlint.com
2. Click "Validate JSON"
3. If valid → pass
4. If invalid → check for:
   - Trailing commas
   - Unescaped double quotes inside strings
   - Missing closing braces

**In Make.com, test the JSON Parse module:**
1. Open Scenario A in Make.com
2. Right-click Module 3 (JSON Parse) > Run this module only
3. In the input field, paste the raw Claude response text
4. Click Run
5. Check the output shows individual fields (hook, body_points, cta, etc.)

**Pass criteria:**
- [ ] JSON parses without errors
- [ ] All 10 fields are accessible as individual variables in Make.com
- [ ] `body_points` shows as an array with 3 items
- [ ] `compliance_flag` shows as boolean (not string "true"/"false")

---

## Test 3 — Predis.ai API Call (Isolated)

Test that the Predis.ai API accepts your credentials and queues an image.

```bash
curl -X POST https://brain.predis.ai/predis_api/v1/create_content/ \
  -H "Authorization: YOUR_PREDIS_API_KEY" \
  -F "brand_id=YOUR_PREDIS_BRAND_ID" \
  -F "text=Your bank is not your friend at renewal time. Most lenders roll you onto a higher variable rate when your fixed term expires. A broker compares dozens of lenders in minutes. DM us RATES for a free comparison." \
  -F "media_type=single_image" \
  -F "model_version=4" \
  -F "color_palette_type=brand" \
  -F "n_posts=1"
```

**Expected response:**
```json
{
  "post_ids": ["some_post_id_here"],
  "post_status": "inProgress",
  "errors": []
}
```

**Pass criteria:**
- [ ] HTTP 200 response received
- [ ] `post_ids` array contains exactly one string ID
- [ ] `errors` array is empty
- [ ] Note the `post_ids[0]` value — you'll use it in Test 4

**Fail — common causes:**
- HTTP 401: API key wrong — check app.predis.ai > Pricing & Account > Rest API
- HTTP 400 `Invalid brand_id`: Brand ID wrong — check app.predis.ai > Pricing & Account > Brands
- HTTP 400 `Text must be at least 20 characters`: Text field too short
- HTTP 400 `Max concurrent generation limit reached`: You already have 10+ images generating — wait for them to complete

---

## Test 4 — Predis.ai Webhook Receipt

Test that Make.com's Scenario B webhook receives the Predis.ai callback.

1. In Make.com, open Scenario B
2. Click the webhook module (Module 1) > Click **Copy address to clipboard** to get the webhook URL
3. Register this URL in Predis.ai: app.predis.ai > My Account > API tab > Webhook URL > Save
4. Wait 2–5 minutes after running Test 3 (for Predis.ai to finish generating)
5. In Make.com, check the webhook's history: Webhooks tab > find your webhook > click **History**

**Pass criteria:**
- [ ] A POST request appears in the webhook history within 10 minutes of the Test 3 call
- [ ] The payload contains `"status": "completed"`
- [ ] The payload contains `generated_media` array with at least one `url`
- [ ] The URL in `generated_media[0].url` is accessible (open it in a browser — you should see the generated image)

**If no webhook arrives within 15 minutes:**
- Check Predis.ai account for errors (app.predis.ai > Posts tab)
- Verify webhook URL is saved correctly in Predis.ai settings
- Check Make.com scenario is active (Scenario B must be ON to receive webhooks)

---

## Test 5 — Asset Download Verification

Test that Make.com can download the Predis.ai asset before the URL expires.

1. Copy a fresh `generated_media[].url` from a recent webhook payload
2. In Make.com, open Scenario B > right-click Module 2 (HTTP Download) > Run this module
3. In the URL field, paste the Predis.ai asset URL
4. Run the module

**Pass criteria:**
- [ ] Module returns HTTP 200
- [ ] Response body has content (binary data — not empty)
- [ ] Response headers show `content-type: image/jpeg` or `image/png`
- [ ] File size is greater than 10KB (a valid image, not an error page)

**Fail — URL expired:**
- If you get a 403 or 404, the 1-hour expiry has passed
- Generate a new image using Test 3 and immediately test download

---

## Test 6 — Google Drive Upload

Test that the downloaded binary uploads correctly to Google Drive.

1. In Make.com Scenario B, run Modules 2+3 together (right-click Module 3 > Run from here)
2. If Module 2 produced binary data, Module 3 (Google Drive upload) should receive it
3. Check your Google Drive folder after the run

**Pass criteria:**
- [ ] New file appears in `GrowwestFinance/Social/Assets/2026-03/` folder
- [ ] File can be opened and shows the generated image correctly
- [ ] Module 3 output includes `webViewLink` (a `https://drive.google.com/file/d/...` URL)
- [ ] Opening `webViewLink` in a browser shows the image (not a "permission denied" error)

**Setting up sharing:**
By default Google Drive files are private. To make the email preview work, you need the file to be viewable by anyone with the link. Either:
- Option A: Set the Drive folder to "Anyone with the link can view" (affects all files in folder)
- Option B: Have Make.com call the Drive API to set sharing after upload (advanced — Phase 2)

For MVP, use Option A: Right-click the `/GrowwestFinance/Social/Assets/` folder in Drive > Share > Change to "Anyone with the link" > Viewer.

---

## Test 7 — Airtable Record Creation (Scenario A — Module 6)

Test the full Scenario A flow end-to-end in manual/test mode.

1. In Make.com, open Scenario A
2. Click **Run once** (manual trigger — does not wait for the 6am cron)
3. Watch each module execute in sequence
4. After completion, check Airtable

**Pass criteria:**
- [ ] Module 1 (Google Sheets) returns a row with today's pillar
- [ ] Module 2 (Claude HTTP) returns HTTP 200
- [ ] Module 3 (JSON Parse) outputs all 10 fields
- [ ] Module 4 (Predis.ai) returns HTTP 200 with a `post_ids` array
- [ ] Module 5 (JSON Parse Predis) outputs the `post_ids` array
- [ ] Module 6 (Airtable Create) creates a new record in the `Content Posts` table
- [ ] New Airtable record has Status = `Generating`
- [ ] New Airtable record has Hook, CTA, all 3 captions populated
- [ ] New Airtable record has `Predis Post ID` field populated with the Predis post ID

---

## Test 8 — Airtable Record Update (Scenario B — Modules 4+5)

Test that Scenario B correctly finds and updates the record created in Test 7.

1. Get the Predis post ID from the Airtable record created in Test 7
2. In Make.com Scenario B, right-click Module 4 (Airtable Search)
3. Run it manually with the post ID from step 1
4. Check that it finds the correct Airtable record
5. Run Module 5 (Airtable Update) and verify Status changes to `Review`

**Pass criteria:**
- [ ] Module 4 returns a record where `Predis Post ID` matches the test ID
- [ ] Module 5 updates the record successfully
- [ ] Airtable record now shows Status = `Review`
- [ ] Airtable record now shows `Asset Drive URL` populated

---

## Test 9 — Gmail Notification Email

Test that the approval email arrives correctly and is readable on mobile.

1. Run Scenario B fully (or run just Module 6 with test data)
2. Check the business owner's email inbox

**Pass criteria:**
- [ ] Email arrives within 5 minutes
- [ ] Subject line shows correct pillar name and today's date
- [ ] Hook is displayed prominently at the top
- [ ] TikTok/IG caption is visible
- [ ] LinkedIn caption is visible
- [ ] If compliance_flag was true, the yellow warning section is visible
- [ ] "Review & Approve in Airtable" button links directly to the correct Airtable record
- [ ] Email renders correctly on mobile (test by viewing on a phone)
- [ ] If the Google Drive image URL is set to public, the image previews in the email

---

## Test 10 — Full End-to-End Test

Run the complete system from trigger to email.

1. In Make.com, activate both Scenario A and Scenario B
2. Manually trigger Scenario A by clicking **Run once**
3. Wait up to 10 minutes for Predis.ai to generate the image and send the webhook
4. Watch Scenario B execute automatically when the webhook arrives
5. Check all outputs

**Pass criteria — full end-to-end:**
- [ ] Scenario A completes all 6 modules with no errors
- [ ] Airtable record created with Status = `Generating`
- [ ] Predis.ai webhook received by Scenario B within 10 minutes
- [ ] Asset downloaded and uploaded to Google Drive
- [ ] Airtable record updated with Status = `Review` and Drive URL
- [ ] Email notification received with all fields populated
- [ ] "Review & Approve" link opens the correct Airtable record
- [ ] Business owner can change Status to `Approved` in Airtable

---

## What a Successful End-to-End Test Looks Like

1. **T+0:00** — Scenario A triggered manually (or by 6am cron)
2. **T+0:05** — Google Sheets returns today's pillar (e.g. "Refinancing")
3. **T+0:10** — Claude API called, returns JSON with hook, captions, etc.
4. **T+0:11** — JSON parsed into individual fields
5. **T+0:12** — Predis.ai called, returns `post_id: "abc123"`
6. **T+0:13** — Airtable record created: Status=`Generating`, all Claude fields populated, Predis Post ID=`abc123`
7. **T+2:00 to T+8:00** — Predis.ai finishes image generation (varies)
8. **T+X:00** — Predis.ai sends webhook to Make.com Scenario B
9. **T+X:01** — Scenario B receives webhook, filters pass (status=completed)
10. **T+X:02** — Asset downloaded from Predis CDN URL (races against 1hr expiry)
11. **T+X:03** — Asset uploaded to Google Drive, permanent URL obtained
12. **T+X:04** — Airtable record found by post_id, updated: Status=`Review`, Drive URL added
13. **T+X:05** — Email sent to business owner with hook preview + image + approve link
14. **Business owner** opens email on phone, clicks "Review & Approve in Airtable", reviews post, changes Status to `Approved`

---

## Error Log Monitoring

After any test run, check the `Errors` tab in your Google Sheet. If any row was written there, something failed. The `Module` column tells you which step failed. Cross-reference with Make.com's execution history for the full error details.

In Make.com: go to your scenario > click the clock icon (History) to see every execution and which modules succeeded or failed.
