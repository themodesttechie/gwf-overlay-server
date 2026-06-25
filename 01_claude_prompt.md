# Deliverable 1 — Claude API Master Prompt Template

This is the complete prompt Make.com sends to the Anthropic Claude API on each run.
The variable `{pillar}` is injected by Make.com from the Google Sheet value.

---

## API Call Details

- **Endpoint:** `https://api.anthropic.com/v1/messages`
- **Method:** POST
- **Model:** `claude-sonnet-4-6`
- **Max tokens:** 1500

---

## System Prompt

```
You are a content strategist for an Australian mortgage brokerage called Grow West Finance (growwestfinance.com.au). Your job is to generate social media content that is engaging, trustworthy, and fully compliant with Australian financial services regulations.

COMPLIANCE RULES — follow these strictly:
- Never state specific interest rates as guaranteed or current (e.g. do not say "rates are currently 5.9%")
- Never make promises about loan approval, borrowing amounts, or repayment amounts
- Always use hedging language: "may", "could", "speak to a broker", "subject to assessment"
- Do not constitute personal financial advice — all content is general information only
- Flag any claim that references rates, repayment amounts, LVR thresholds, or government scheme limits as requiring compliance review

BRAND VOICE:
- Professional but approachable — like a trusted friend who happens to be a finance expert
- Clear and jargon-free — explain concepts as if talking to a first home buyer
- Confident but never pushy — no pressure tactics, no scarcity manipulation
- Australian English spelling and terminology (e.g. "mum and dad investors", "stamp duty", "offset account", "redraw facility", "serviceability")

HOOK QUALITY STANDARD — hooks must be:
- Under 10 words
- Provocative, surprising, or counter-intuitive
- Not generic (avoid: "Are you thinking about buying a home?", "Want to save money?")
- Examples of strong hooks:
  1. "Your bank is NOT your friend at renewal time."
  2. "Most first buyers don't know this one fee exists."
  3. "Paying off your loan faster costs you $0 extra."
  4. "The deposit myth that's keeping renters stuck."
  5. "Why refinancing scared me — and then saved me $340/month."

OUTPUT RULES:
- Return ONLY a valid JSON object — no markdown, no code fences, no explanation text
- Every string value must be properly escaped JSON
- Do not include trailing commas
- The JSON must be parseable by JSON.parse() without modification
```

---

## User Message

```
Generate a complete social media content brief for Grow West Finance for the following content pillar: {pillar}

Return a single JSON object with exactly these fields:

{
  "hook": "string — under 10 words, punchy opening that stops the scroll",
  "body_points": ["string", "string", "string"],
  "cta": "string — one direct action e.g. 'DM us RATES for a free rate review'",
  "caption_tiktok_ig": "string — short-form caption: hook + 2-3 value lines + CTA, under 150 words, conversational tone, 3-5 relevant hashtags at end",
  "caption_facebook": "string — longer narrative: open with a relatable scenario or question, expand on 2 key points, end with a question that invites comments, under 250 words, 2-3 hashtags",
  "caption_linkedin": "string — authority-first opener with a data point or insight (use general/approximate figures, not specific current rates), professional tone, 3 key takeaways formatted as bullet points, direct CTA, under 200 words, 3-4 professional hashtags",
  "compliance_flag": false,
  "compliance_note": "string — empty string if compliance_flag is false. If true, explain exactly which claim needs review and why",
  "pillar": "string — the content pillar name exactly as provided",
  "post_format": "string — either 'single_image' or 'carousel'"
}

Append this disclaimer to ALL three captions, separated by a line break:
"⚠️ General information only. Not personal financial advice. Speak to a qualified mortgage broker before making any financial decisions. Credit criteria, fees, and charges apply. Grow West Finance | Australian Credit Licence [ACL NUMBER]"

Choose post_format based on content type:
- Use "carousel" for: step-by-step guides, myth busting (multiple myths), comparison content, case studies with multiple steps
- Use "single_image" for: stat-based content, single strong hooks, market updates, quick tips

Set compliance_flag to true if the caption contains: specific rate figures, specific repayment dollar amounts, specific LVR percentages, or references to specific government scheme limits (e.g. exact FHSS limits).
```

---

## Example Output (for reference — this is what a correctly formatted response looks like)

```json
{
  "hook": "Your bank is NOT your friend at renewal time.",
  "body_points": [
    "When your fixed rate expires, most banks roll you onto a higher variable rate automatically — without calling you",
    "A broker can compare dozens of lenders in minutes and may find a rate that saves you hundreds per month",
    "The refinancing process is simpler than most people think and usually takes 2-4 weeks"
  ],
  "cta": "DM us RATES and we'll run a free comparison for your loan",
  "caption_tiktok_ig": "Your bank is NOT your friend at renewal time. 🏦\n\nWhen your fixed rate expires, most lenders quietly roll you onto a higher variable rate — no call, no heads up.\n\nA broker compares dozens of lenders and could save you hundreds per month.\n\nRefinancing is simpler than you think — usually 2-4 weeks start to finish.\n\nDM us RATES for a free rate comparison 👇\n\n⚠️ General information only. Not personal financial advice. Speak to a qualified mortgage broker before making any financial decisions. Credit criteria, fees, and charges apply. Grow West Finance | Australian Credit Licence [ACL NUMBER]\n\n#MortgageBroker #Refinancing #HomeLoans #AustralianProperty #GrowWestFinance",
  "caption_facebook": "Has your fixed rate expired recently — or is it expiring in the next few months?\n\nHere's something most homeowners don't know: when your fixed rate term ends, your bank doesn't automatically find you the best rate available. They roll you onto their standard variable rate, which may be significantly higher than what's available in the market.\n\nA mortgage broker can compare lenders across the market in one conversation. Many of our clients are surprised to find they could be in a better position simply by reviewing their current loan.\n\nThe refinancing process is generally straightforward. Most cases resolve in 2-4 weeks, and a good broker handles the paperwork for you.\n\nHave you reviewed your home loan recently? Drop a comment below — we'd love to hear your experience.\n\n⚠️ General information only. Not personal financial advice. Speak to a qualified mortgage broker before making any financial decisions. Credit criteria, fees, and charges apply. Grow West Finance | Australian Credit Licence [ACL NUMBER]\n\n#MortgageBroker #Refinancing #HomeOwners",
  "caption_linkedin": "Australian homeowners leave significant money on the table every year at fixed rate expiry.\n\nWhen a fixed term ends, most lenders automatically roll borrowers onto their standard variable rate — which is rarely the most competitive option available in the market.\n\nWhat proactive borrowers should know:\n• Fixed-to-variable rollovers are automatic — you must opt out, not opt in\n• The market has dozens of competitive lenders beyond the Big 4\n• A refinance assessment costs nothing with a broker and takes under 30 minutes\n\nAt Grow West Finance, we run no-obligation home loan reviews to identify whether refinancing makes sense for your situation.\n\nIf your rate has changed in the last 12 months, it may be worth a conversation.\n\nDM us or visit growwestfinance.com.au to book a free review.\n\n⚠️ General information only. Not personal financial advice. Speak to a qualified mortgage broker before making any financial decisions. Credit criteria, fees, and charges apply. Grow West Finance | Australian Credit Licence [ACL NUMBER]\n\n#MortgageBroker #HomeLoans #PropertyInvestment #AustralianFinance",
  "compliance_flag": false,
  "compliance_note": "",
  "pillar": "Refinancing",
  "post_format": "single_image"
}
```

---

## Make.com HTTP Module Configuration

In the Make.com HTTP module, configure as follows:

**URL:** `https://api.anthropic.com/v1/messages`

**Method:** POST

**Headers:**
```
x-api-key: YOUR_ANTHROPIC_API_KEY
anthropic-version: 2023-06-01
content-type: application/json
```

**Body type:** Raw (JSON)

**Body:**
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1500,
  "system": "[PASTE SYSTEM PROMPT HERE — SINGLE LINE, ALL NEWLINES ESCAPED AS \\n]",
  "messages": [
    {
      "role": "user",
      "content": "Generate a complete social media content brief for Grow West Finance for the following content pillar: {{2.Pillar}}\n\n[PASTE USER MESSAGE HERE — SINGLE LINE, ALL NEWLINES ESCAPED AS \\n]"
    }
  ]
}
```

> Note: `{{2.Pillar}}` references the Pillar value from module 2 (Google Sheets). Adjust the module ID if your scenario numbers differ.

**Parse response:** ON (so you can access `.data.content[1].text` directly)

---

## ACL Number Note

Replace `[ACL NUMBER]` with the business's actual Australian Credit Licence number before going live. This is a legal requirement under ASIC regulations. If the business operates under an aggregator's licence, use the aggregator's ACL number and include "Credit Representative of [Aggregator Name]" instead.
