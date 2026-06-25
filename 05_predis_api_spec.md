# Deliverable 5 — Predis.ai API Call Specification

## Overview

Predis.ai's image generation is **asynchronous**. The `create_content` call returns immediately with a `post_id`, but the actual image is delivered minutes later via webhook. This is why the system uses two Make.com scenarios.

---

## Authentication

**Header name:** `Authorization`
**Header value:** Your raw API key (no "Bearer" prefix)
**Example:**
```
Authorization: abc123def456ghi789
```

**Where to find your API key:**
1. Log into https://app.predis.ai
2. Go to **Pricing & Account** (top right menu)
3. Click **Rest API** tab
4. Copy the API key shown

**Where to find your Brand ID:**
1. Same location: **Pricing & Account** > **Brands** tab
2. Copy the brand ID shown next to your brand name

---

## Endpoint 1: Create Content (Scenario A — Module 4)

### Request

```
URL:    https://brain.predis.ai/predis_api/v1/create_content/
Method: POST
Body:   multipart/form-data (NOT application/json)
```

**Critical:** The body must be `multipart/form-data`, not JSON. This is the most common mistake. In Make.com, set the HTTP module `bodyType` to `Multipart/Form-Data`.

### Request Fields

| Field | Required | Type | Value in Make.com |
|---|---|---|---|
| `brand_id` | Yes | String | `YOUR_PREDIS_BRAND_ID` |
| `text` | Yes | String (min 20 chars, 3+ words) | Claude hook + body points concatenated |
| `media_type` | No | String | `{{3.post_format}}` (from Claude JSON parse) |
| `model_version` | No | String | `"4"` (recommended — better quality) |
| `color_palette_type` | No | String | `"brand"` (uses your registered brand kit) |
| `n_posts` | No | Integer | `"1"` |

### Text Field Mapping

The `text` field is what Predis.ai uses to generate the visual. Map it like this in Make.com:

```
{{3.hook}} {{3.body_points[1]}} {{3.body_points[2]}} {{3.body_points[3]}} {{3.cta}}
```

This concatenates the hook + all 3 body points + CTA into a single string that Predis.ai uses to understand the content context.

**Minimum length check:** The `text` field must be at least 20 characters and 3 words. Claude's hook alone is always under this, which is why we concatenate. If the concatenated result is somehow short, add a fallback: `{{3.hook}} {{3.body_points[1]}} Visit growwestfinance.com.au`.

### Synchronous Response (always returned immediately)

```json
{
  "post_ids": ["abc123def456"],
  "post_status": "inProgress",
  "errors": []
}
```

**Note:** `post_status` is always `"inProgress"` in this response regardless of how fast generation is. The actual completed post comes via webhook.

In Make.com Scenario A, Module 5 (JSON Parse) extracts the `post_ids` array, then Module 6 (Airtable) stores `post_ids[1]` as the `Predis Post ID` field.

### Error Response Examples

```json
// Invalid API key
HTTP 401
{"error": "Invalid API key"}

// Brand ID not found
HTTP 400
{"errors": ["Invalid brand_id"], "post_ids": []}

// Rate limit exceeded (per-minute)
HTTP 429
{"error": "Rate limit exceeded. Try again in 60 seconds."}

// Too many concurrent generations (>10 in-progress)
HTTP 400
{"errors": ["Max concurrent generation limit reached"], "post_ids": []}

// Text too short
HTTP 400
{"errors": ["Text must be at least 20 characters and 3 words"], "post_ids": []}
```

---

## Endpoint 2: Webhook Callback (Scenario B — Module 1 trigger)

Predis.ai POSTs this payload to your registered webhook URL when generation completes:

### Successful Generation Payload

```json
{
  "status": "completed",
  "post_id": "abc123def456",
  "brand_id": "YOUR_BRAND_ID",
  "caption": "The caption Predis generated (may differ from Claude's caption)",
  "generated_media": [
    {
      "url": "https://cdn.predis.ai/generated/abc123def456_image.jpg"
    }
  ]
}
```

**Key field:** `generated_media[0].url` (In Make.com 1-based indexing: `{{1.generated_media[1].url}}`)

The URL is a **time-limited CDN URL** that expires approximately **1 hour** after generation. Make.com Scenario B must download this file immediately when the webhook fires.

### Failed Generation Payload

```json
{
  "status": "error",
  "post_id": "abc123def456"
}
```

The webhook filter in Scenario B (on Module 1) only processes webhooks where `status = "completed"`. Failed webhooks are ignored by default — add error handling if you want to log failures.

### Carousel Payload (multiple images)

When `media_type = "carousel"`, the `generated_media` array contains multiple items:

```json
{
  "status": "completed",
  "post_id": "abc123def456",
  "generated_media": [
    {"url": "https://cdn.predis.ai/generated/abc123_slide1.jpg"},
    {"url": "https://cdn.predis.ai/generated/abc123_slide2.jpg"},
    {"url": "https://cdn.predis.ai/generated/abc123_slide3.jpg"}
  ]
}
```

**MVP handling:** In this MVP, only `generated_media[1].url` (the first image) is downloaded and stored. For full carousel support in Phase 2, iterate through all items and store each as a separate Google Drive file.

---

## Endpoint 3: Get Posts (polling fallback)

If the webhook fails, use this endpoint to manually retrieve completed posts:

```
URL:    https://brain.predis.ai/predis_api/v1/get_posts/
Method: GET
```

Query parameters:
```
brand_id=YOUR_BRAND_ID&media_type=single_image&page_n=1&items_n=5
```

Response:
```json
{
  "posts": [
    {
      "post_id": "abc123def456",
      "urls": ["https://cdn.predis.ai/..."],
      "caption": "...",
      "media_type": "single_image"
    }
  ],
  "total_pages": 12,
  "errors": []
}
```

The asset URL is in `posts[].urls[0]` (not `generated_media` — different format from the webhook).

---

## Rate Limits

| Endpoint | Limit | What happens when exceeded |
|---|---|---|
| `create_content/` | 60 requests/min | HTTP 429 — wait 60 seconds |
| `get_posts/` | 60 requests/min | HTTP 429 — wait 60 seconds |
| Concurrent generations | 10 simultaneous | HTTP 400 |

**At 2 posts/day:** Far below rate limits. No rate limit concerns for this use case.

---

## Webhook Registration

1. Log into https://app.predis.ai
2. Click **My Account** (top right)
3. Click the **API** tab
4. Find the **Webhook URL** field
5. Paste your Make.com Scenario B webhook URL

**Only one webhook URL is supported per account.** If you have multiple Make.com scenarios or environments (dev/prod), you'll need to use a webhook routing tool (like webhook.site for testing) to fan out to multiple destinations.

**Localhost URLs cannot be used.** When testing locally, use ngrok or similar tunnelling service. For Make.com, the webhook URL is always a public `https://hook.eu1.make.com/...` URL — no tunnelling needed.

---

## Make.com HTTP Module Configuration Summary

### Module 4 (Scenario A) — Create Content

```
Module:     http:ActionSendData
URL:        https://brain.predis.ai/predis_api/v1/create_content/
Method:     POST
Headers:    Authorization: YOUR_PREDIS_API_KEY
Body type:  Multipart/Form-Data
Fields:
  brand_id:           YOUR_PREDIS_BRAND_ID
  text:               {{3.hook}} {{3.body_points[1]}} {{3.body_points[2]}} {{3.body_points[3]}} {{3.cta}}
  media_type:         {{3.post_format}}
  model_version:      4
  color_palette_type: brand
  n_posts:            1
Parse response:  ON
```

### Module 2 (Scenario B) — Download Asset

```
Module:         http:ActionSendData
URL:            {{1.generated_media[1].url}}
Method:         GET
Headers:        (none)
Body type:      Empty
Parse response: OFF   ← Important: OFF here, we want raw binary
Follow redirects: ON
```

The response `.body` contains the raw binary image data that gets passed directly to the Google Drive upload module.

---

## Brand Kit Setup in Predis.ai

Before running the system, ensure your brand kit is configured in Predis.ai:

1. Log into https://app.predis.ai
2. Go to **Brand Kit** section
3. Upload the Grow West Finance logo (minimum 500x500px, PNG with transparent background preferred)
4. Set brand colours:
   - Primary: your brand's primary colour (e.g. navy blue)
   - Secondary: your brand's secondary colour
   - Accent: your brand's accent colour
5. Set brand fonts if available (or use Predis.ai's font suggestions)
6. Save the brand kit

When `color_palette_type: "brand"` is set in the API call, Predis.ai uses this saved brand kit automatically. Without this, Predis.ai uses AI-suggested colours that may not match the brand.
