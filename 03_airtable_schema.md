# Deliverable 3 — Airtable Base Schema

## Base Setup

**Base name:** GrowWest Social Media
**Table name:** Content Posts
**Plan:** Free (1,000 records — see capacity note below)

---

## Complete Field Definitions

Create fields in this exact order in Airtable. Field names are case-sensitive and must match exactly what is used in the Make.com scenario JSON.

### Primary Fields

| Field Name | Field Type | Configuration |
|---|---|---|
| `Post Title` | Single line text | Set as the primary field. Auto-populated by formula (see below) OR leave for manual naming |
| `Status` | Single select | See options below |
| `Pillar` | Single select | See options below |
| `Post Format` | Single select | Options: `single_image`, `carousel` |
| `Created Date` | Date | Date format: DD/MM/YYYY, no time |
| `Platforms` | Multiple select | See options below |

### Content Fields

| Field Name | Field Type | Configuration |
|---|---|---|
| `Hook` | Single line text | Max length: 100 chars |
| `Body Point 1` | Long text | Rich text: OFF |
| `Body Point 2` | Long text | Rich text: OFF |
| `Body Point 3` | Long text | Rich text: OFF |
| `CTA` | Single line text | Max length: 150 chars |
| `Caption TikTok IG` | Long text | Rich text: OFF |
| `Caption Facebook` | Long text | Rich text: OFF |
| `Caption LinkedIn` | Long text | Rich text: OFF |

### Compliance Fields

| Field Name | Field Type | Configuration |
|---|---|---|
| `Compliance Flag` | Checkbox | Default: unchecked |
| `Compliance Note` | Long text | Rich text: OFF. Only populated when Compliance Flag is checked. |

### Asset & Integration Fields

| Field Name | Field Type | Configuration |
|---|---|---|
| `Predis Post ID` | Single line text | Stores the post_id returned by Predis.ai API |
| `Predis Asset URL` | URL | Original Predis.ai URL (expires 1 hour — for reference only) |
| `Asset Drive URL` | URL | Permanent Google Drive shareable URL |
| `Asset Drive File ID` | Single line text | Google Drive file ID (for programmatic access) |
| `Asset Generated At` | Date | Date + time format, includes time |

### Approval Fields

| Field Name | Field Type | Configuration |
|---|---|---|
| `Approved By` | Single line text | Business owner fills in manually |
| `Approved Date` | Date | Date format: DD/MM/YYYY |
| `Rejection Reason` | Long text | Rich text: OFF. Filled in when Status = Rejected |
| `Notes` | Long text | Rich text: ON. General notes/feedback field |

### Formula Fields (read-only, auto-calculated)

| Field Name | Field Type | Formula |
|---|---|---|
| `Post Title` | Formula | `CONCATENATE({Pillar}, " — ", {Created Date})` |
| `Airtable Record URL` | Formula | `CONCATENATE("https://airtable.com/", "YOUR_BASE_ID", "/", "YOUR_TABLE_ID", "/", RECORD_ID())` |

> Replace `YOUR_BASE_ID` and `YOUR_TABLE_ID` in the formula with your actual IDs after creating the base.

---

## Status Field Options (with colour codes)

Set up in this exact order — Airtable assigns colours sequentially by default.

| Option Name | Colour | Meaning |
|---|---|---|
| `Generating` | Grey | Predis.ai is generating the image (set by Scenario A) |
| `Review` | Yellow | Ready for human review (set by Scenario B) |
| `Approved` | Green | Business owner approved — ready for Phase 2 publishing |
| `Rejected` | Red | Business owner rejected — needs rework or discard |
| `Published` | Blue | Post has been published to social platforms |
| `Archived` | Light grey | Old or unused post |

**How to set colours in Airtable:**
1. Click the `Status` field header > Edit field
2. Click each option to expand > Click the colour dot to change it
3. Use these hex values for closest match:
   - Generating: `#9E9E9E`
   - Review: `#FFC107`
   - Approved: `#4CAF50`
   - Rejected: `#F44336`
   - Published: `#2196F3`
   - Archived: `#E0E0E0`

---

## Pillar Field Options

Add all 9 options in this order:

1. Home loans
2. Refinancing
3. First home buyers
4. Investment property
5. Interest rates and market updates
6. Finance mistakes to avoid
7. Myth busting
8. Case studies and success stories
9. Step-by-step guidance

---

## Platforms Field Options (Multiple Select)

| Option | Colour |
|---|---|
| TikTok | Black (`#000000`) |
| Instagram | Purple (`#C13584`) |
| Facebook | Blue (`#1877F2`) |
| LinkedIn | Blue (`#0A66C2`) |

---

## Views to Create

### View 1: Review Queue

This is the primary working view for the business owner.

1. Click **+ Add view** > **Grid view**
2. Name it: `Review Queue`
3. **Filter:** Status is `Review`
4. **Sort:** Created Date → ascending (oldest first)
5. **Hide fields:** Predis Post ID, Predis Asset URL, Asset Drive File ID, Asset Generated At, Airtable Record URL
6. **Field order:** Status, Created Date, Pillar, Hook, Compliance Flag, Asset Drive URL, Caption TikTok IG, Notes, Approved By

### View 2: Content Calendar

1. Click **+ Add view** > **Gallery view**
2. Name it: `Content Calendar`
3. **Cover image:** Asset Drive URL (note: Google Drive links may not preview — see workaround in `08_known_issues.md`)
4. **Fields shown:** Pillar, Status, Hook, Created Date

### View 3: All Posts (Default)

Keep the default grid view and rename to `All Posts`. No filters — shows everything.

### View 4: Approved (Ready to Publish)

1. Grid view named `Approved`
2. **Filter:** Status is `Approved`
3. **Sort:** Approved Date → ascending

---

## Airtable Automation — Status Change to "Approved"

This automation prepares Phase 2 publishing. Set it up now so the trigger is in place.

**To create:**
1. In your base, click **Automations** tab (top right)
2. Click **+ New automation**
3. Name it: `Post Approved — Notify for Publishing`

**Trigger:**
- Type: `When record matches conditions`
- Table: `Content Posts`
- Condition: `Status` is `Approved`

**Action (Phase 2 placeholder):**
- Type: `Send email` (temporary placeholder — replace with Make.com webhook in Phase 2)
- To: `YOUR_BUSINESS_OWNER_EMAIL`
- Subject: `Post approved and ready to publish — {{Pillar}} — {{Created Date}}`
- Body:
  ```
  A post has been approved and is ready for publishing.

  Pillar: {{Pillar}}
  Hook: {{Hook}}
  Format: {{Post Format}}
  Asset: {{Asset Drive URL}}

  This automation is a placeholder. Phase 2 will connect this to Make.com for automatic social publishing.
  ```

**Note:** In Phase 2, replace the email action with an HTTP request to a Make.com webhook that triggers the publishing scenario.

---

## Capacity Planning

Free Airtable plan limits: 1,000 records per base.

| Posts per day | Records per month | Months until limit |
|---|---|---|
| 1 post/day | ~30 records | 33 months |
| 2 posts/day | ~60 records | 16 months |
| 4 posts/day | ~120 records | 8 months |

**At 2 posts/day:** You have approximately 16 months before hitting the free limit.

**Action at 12 months:** Either upgrade Airtable OR archive/delete published posts older than 6 months. Use the `Archived` status to filter and bulk-delete old records.

---

## Getting Your Airtable IDs

After creating the base, you'll need the Base ID and Table ID for the Make.com scenario:

**Base ID:**
- Go to https://airtable.com/api
- Click your base name
- The URL shows: `https://airtable.com/YOUR_BASE_ID/api/docs`
- Alternatively: the base URL is `https://airtable.com/appXXXXXXXXXXXXXX` — the `appXXXXXXXXXXXXXX` part is your Base ID

**Table ID:**
- Open Airtable > your base > your table
- Look at the URL: `https://airtable.com/appXXXXXXX/tblYYYYYYYYYYYY/...`
- The `tblYYYYYYYYYYYY` part is your Table ID

**Connection in Make.com:**
- In Make.com, go to Connections
- Create a new Airtable connection using your Airtable Personal Access Token
- Get your token from: https://airtable.com/create/tokens
- Required scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
