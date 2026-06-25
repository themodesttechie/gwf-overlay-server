import json
import os

# === CLAUDE API BODY ===
system_prompt = (
    "You are a content strategist for GrowWest Finance, an Australian mortgage brokerage (growwestfinance.com.au).\n\n"
    "COMPLIANCE RULES:\n"
    "- Never state specific interest rates as guaranteed or current\n"
    "- Never make promises about loan approval or borrowing amounts\n"
    "- Always use hedging language: may, could, speak to a broker, subject to assessment\n"
    "- Do not constitute personal financial advice\n\n"
    "BRAND VOICE: Professional but approachable. Australian English (stamp duty, offset account, serviceability). Clear, jargon-free.\n\n"
    "BRANDING: Navy #1B2A4A, gold #C9A84C. Handle: @growwestfinance. Website: growwestfinance.com.au\n\n"
    "HOOK STANDARD: Under 10 words, provocative or counter-intuitive, never generic. Examples: Your bank is NOT your friend at renewal time. | Most first buyers dont know this one fee exists.\n\n"
    "CRITICAL OUTPUT RULES:\n"
    "- Return ONLY valid JSON. No markdown fences, no code blocks, no explanation before or after.\n"
    "- Do NOT use double-quote characters inside any string value. Use single quotes if quoting is needed within values.\n"
    "- Must be parseable by JSON.parse() without modification."
)

user_prompt = (
    "Generate complete social media content for GrowWest Finance.\n\n"
    "Pillar: {{1.1}}\n"
    "Idea: {{1.2}}\n"
    "Post Format: {{1.3}}\n\n"
    "RULES:\n"
    "- If the Idea field above is empty or blank, YOU MUST generate a trending, engaging content idea based on the Pillar. Never leave idea empty.\n"
    "- If Post Format is carousel, generate 3 distinct image prompts and 3 slide overlay texts.\n"
    "- If Post Format is single_image (or anything other than carousel), leave carousel text and extra image prompt fields as empty strings.\n\n"
    "Return a JSON object with exactly these keys: idea, image_prompt, image_prompt_2, image_prompt_3, post_title, hook, hashtags, caption_tiktok_ig, caption_facebook, caption_linkedin, carousel_1_text, carousel_2_text, carousel_3_text\n\n"
    "Field requirements:\n"
    "- idea: The content idea. If input Idea was blank, generate a fresh trending idea for this pillar.\n"
    "- image_prompt: Detailed Gemini image generation prompt. Modern Australian property/finance lifestyle photography. Incorporate brand colors navy #1B2A4A and gold #C9A84C as subtle accents. Clean professional look suitable for social media. NO text overlays on the image. High quality, well-lit, aspirational. If carousel, this is for slide 1 only.\n"
    "- image_prompt_2: Slide 2 image prompt. Only populate if carousel format, otherwise empty string.\n"
    "- image_prompt_3: Slide 3 image prompt. Only populate if carousel format, otherwise empty string.\n"
    "- post_title: Clear descriptive title for the post.\n"
    "- hook: Under 10 words, punchy scroll-stopping opening line.\n"
    "- hashtags: 22 relevant hashtags including #GrowWestFinance #HomeLoan #MortgageBroker #AustralianProperty #PropertyInvestment #FirstHomeBuyer #RealEstate #FinanceTips #MelbourneProperty #MortgageExpert\n"
    "- caption_tiktok_ig: TikTok/Instagram caption. Line 1: the hook on its own line. Lines 2-4: 2-3 short value sentences with emojis like house, money, key emojis. Strong CTA (DM us / Book a call / Link in bio). Blank line then exactly 22 hashtags. Caption body under 150 words.\n"
    "- caption_facebook: Facebook caption. Open with a relatable first-home buyer scenario or surprising fact. Add 2 key value points with line breaks and 1-2 emojis. End with an open question inviting comments. Keep under 220 words. End with 5-7 hashtags.\n"
    "- caption_linkedin: LinkedIn post. Open with a bold insight or surprising data point about Australian property or mortgages. Use 3 bullet points each starting with the unicode right arrow symbol for actionable takeaways. Close with a thought-leadership question CTA. Use line breaks between sections. Keep under 280 words. End with 8-10 professional hashtags.\n"
    "- carousel_1_text: Short punchy text overlay for carousel slide 1 - max 15 words. Empty string if not carousel.\n"
    "- carousel_2_text: Text overlay for slide 2. Empty string if not carousel.\n"
    "- carousel_3_text: Text overlay for slide 3. Empty string if not carousel.\n\n"
    "IMPORTANT - ALL THREE captions (tiktok_ig, facebook, linkedin) must end with this disclaimer:\n"
    "General information only. Not personal financial advice. Speak to a qualified mortgage broker before making any financial decisions. Credit criteria, fees and charges apply. Grow West Finance | ACL [NUMBER]\n\n"
    "For carousel format: Make the 3 image prompts visually distinct but cohesive as a branded series. Slide texts should tell a progression or educational story.\n"
    "For single_image format: All carousel_*_text and image_prompt_2/image_prompt_3 must be empty strings."
)

claude_body = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 3000,
    "system": system_prompt,
    "messages": [{"role": "user", "content": user_prompt}]
}

claude_body_str = json.dumps(claude_body)

# === HELPER FUNCTIONS ===
def gemini_body(prompt_ref):
    return json.dumps({
        "contents": [{"parts": [{"text": "{{" + prompt_ref + "}}"}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
    })

def overlay_body(gemini_module_id):
    return json.dumps({
        "image_base64": "{{" + str(gemini_module_id) + ".data.candidates[].content.parts[].inlineData.data}}",
        "position": "top-left"
    })

def make_gemini(mod_id, prompt_ref, x, y):
    return {
        "id": mod_id,
        "module": "http:MakeRequest",
        "version": 4,
        "parameters": {"authenticationType": "noAuth"},
        "mapper": {
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={os.environ.get('GEMINI_API_KEY', '')}",
            "method": "post",
            "contentType": "json",
            "inputMethod": "jsonString",
            "jsonStringBodyContent": gemini_body(prompt_ref),
            "parseResponse": True,
            "stopOnHttpError": True,
            "allowRedirects": True,
            "shareCookies": False,
            "requestCompressedContent": True
        },
        "metadata": {"designer": {"x": x, "y": y}}
    }

def make_overlay(mod_id, gemini_mod_id, x, y):
    return {
        "id": mod_id,
        "module": "http:ActionSendData",
        "version": 3,
        "parameters": {"handleErrors": True, "useNewZLibDeCompress": True},
        "mapper": {
            "url": "https://gwf-overlay-server.onrender.com/overlay",
            "data": overlay_body(gemini_mod_id),
            "method": "post",
            "headers": [],
            "bodyType": "raw",
            "contentType": "application/json",
            "parseResponse": True,
            "followRedirect": True,
            "gzip": True,
            "useMtls": False,
            "serializeUrl": False,
            "shareCookies": False,
            "useQuerystring": False,
            "followAllRedirects": False,
            "rejectUnauthorized": True,
            "ca": "",
            "qs": [],
            "authUser": "",
            "authPass": "",
            "timeout": ""
        },
        "metadata": {"designer": {"x": x, "y": y}}
    }

def make_download(mod_id, overlay_mod_id, x, y):
    return {
        "id": mod_id,
        "module": "http:ActionGetFile",
        "version": 3,
        "parameters": {"handleErrors": False, "useNewZLibDeCompress": True},
        "mapper": {
            "url": "{{" + str(overlay_mod_id) + ".data.url}}",
            "method": "get",
            "headers": [],
            "qs": [],
            "followRedirect": True,
            "followAllRedirects": False,
            "shareCookies": False,
            "gzip": True,
            "useMtls": False,
            "serializeUrl": False,
            "useQuerystring": False,
            "rejectUnauthorized": True,
            "ca": "",
            "authUser": "",
            "authPass": "",
            "timeout": ""
        },
        "metadata": {"designer": {"x": x, "y": y}}
    }

def make_dropbox_upload(mod_id, download_mod_id, overlay_mod_id, x, y):
    return {
        "id": mod_id,
        "module": "dropbox:UploadFile",
        "version": 3,
        "parameters": {"__IMTCONN__": 1},
        "mapper": {
            "folder": "/Marketing/GWFCreatives",
            "name": "{{" + str(overlay_mod_id) + ".data.filename}}",
            "data": "{{" + str(download_mod_id) + ".data}}",
            "overwrite": True
        },
        "metadata": {"designer": {"x": x, "y": y}}
    }

def make_sheets_update(mod_id, values, x, y):
    return {
        "id": mod_id,
        "module": "google-sheets:updateRow",
        "version": 2,
        "parameters": {"__IMTCONN__": 13880676},
        "mapper": {
            "from": "drive",
            "mode": "select",
            "values": values,
            "sheetId": "Pillar Schedule",
            "rowNumber": "{{1.__ROW_NUMBER__}}",
            "spreadsheetId": "/148w-F3L_tbQfPr9BHruaxp76q9ZL0jlLmTzPo85g5SA",
            "includesHeaders": True,
            "useColumnHeaders": False,
            "valueInputOption": "USER_ENTERED"
        },
        "metadata": {
            "designer": {"x": x, "y": y},
            "restore": {
                "parameters": {
                    "__IMTCONN__": {
                        "data": {"scoped": "true", "connection": "google"},
                        "label": "GrowWest Finance (growwestfinance@gmail.com)"
                    }
                }
            }
        }
    }

# === BUILD BLUEPRINT ===
blueprint = {
    "name": "GrowWest - Content Generate (Scenario A) v2",
    "flow": [
        # Module 1: Google Sheets Search Rows — filter Status = "To do"
        {
            "id": 1,
            "module": "google-sheets:filterRows",
            "version": 2,
            "parameters": {"__IMTCONN__": 13880676},
            "mapper": {
                "from": "drive",
                "limit": "10",
                "filter": [[{"a": "E", "b": "To do", "o": "text:equal"}]],
                "sheetId": "Pillar Schedule",
                "sortOrder": "asc",
                "spreadsheetId": "148w-F3L_tbQfPr9BHruaxp76q9ZL0jlLmTzPo85g5SA",
                "tableFirstRow": "A1:Z1",
                "includesHeaders": True,
                "valueRenderOption": "FORMATTED_VALUE",
                "dateTimeRenderOption": "FORMATTED_STRING"
            },
            "metadata": {
                "designer": {"x": 0, "y": 0},
                "restore": {
                    "parameters": {
                        "__IMTCONN__": {
                            "data": {"scoped": "true", "connection": "google"},
                            "label": "GrowWest Finance (growwestfinance@gmail.com)"
                        }
                    },
                    "expect": {
                        "from": {"label": "Select from My Drive"},
                        "sheetId": {"mode": "chose", "label": "Pillar Schedule"},
                        "spreadsheetId": {"mode": "chose", "label": "GrowWest Social Media Automation"},
                        "includesHeaders": {"mode": "chose", "label": "Yes"},
                        "valueRenderOption": {"mode": "chose", "label": "Formatted value"},
                        "dateTimeRenderOption": {"mode": "chose", "label": "Formatted string"},
                        "sortOrder": {"mode": "chose", "label": "Ascending"},
                        "tableFirstRow": {"label": "A-Z"}
                    }
                },
                "parameters": [
                    {"name": "__IMTCONN__", "type": "account:google", "label": "Connection", "required": True}
                ]
            }
        },
        # Module 2: HTTP — Claude API call (single call for all content)
        {
            "id": 2,
            "module": "http:ActionSendData",
            "version": 3,
            "parameters": {"handleErrors": True, "useNewZLibDeCompress": True},
            "mapper": {
                "url": "https://api.anthropic.com/v1/messages",
                "data": claude_body_str,
                "method": "post",
                "headers": [
                    {"name": "x-api-key", "value": os.environ.get("ANTHROPIC_API_KEY", "")},
                    {"name": "anthropic-version", "value": "2023-06-01"},
                    {"name": "content-type", "value": "application/json"}
                ],
                "timeout": "300",
                "bodyType": "raw",
                "contentType": "application/json",
                "parseResponse": True,
                "followRedirect": True,
                "gzip": True,
                "useMtls": False,
                "serializeUrl": False,
                "shareCookies": False,
                "useQuerystring": False,
                "followAllRedirects": False,
                "rejectUnauthorized": True,
                "ca": "",
                "qs": [],
                "authUser": "",
                "authPass": ""
            },
            "metadata": {"designer": {"x": 300, "y": 0}}
        },
        # Module 3: JSON Parse — extract Claude's JSON response
        {
            "id": 3,
            "module": "json:ParseJSON",
            "version": 1,
            "parameters": {},
            "mapper": {"json": "{{2.data.content[1].text}}"},
            "metadata": {
                "designer": {"x": 600, "y": 0},
                "interface": [
                    {"name": "idea", "type": "text", "label": "idea"},
                    {"name": "image_prompt", "type": "text", "label": "image_prompt"},
                    {"name": "image_prompt_2", "type": "text", "label": "image_prompt_2"},
                    {"name": "image_prompt_3", "type": "text", "label": "image_prompt_3"},
                    {"name": "post_title", "type": "text", "label": "post_title"},
                    {"name": "hook", "type": "text", "label": "hook"},
                    {"name": "hashtags", "type": "text", "label": "hashtags"},
                    {"name": "caption_tiktok_ig", "type": "text", "label": "caption_tiktok_ig"},
                    {"name": "caption_facebook", "type": "text", "label": "caption_facebook"},
                    {"name": "caption_linkedin", "type": "text", "label": "caption_linkedin"},
                    {"name": "carousel_1_text", "type": "text", "label": "carousel_1_text"},
                    {"name": "carousel_2_text", "type": "text", "label": "carousel_2_text"},
                    {"name": "carousel_3_text", "type": "text", "label": "carousel_3_text"}
                ]
            }
        },
        # Module 4: Google Sheets Update — write ALL Claude-generated content
        make_sheets_update(4, {
            "2": "{{if(1.2; 1.2; 3.idea)}}",  # C = Idea (only overwrite if originally blank)
            "4": "Content Generated",     # E = Status
            "6": "{{3.image_prompt}}",    # G = Image Prompt
            "8": "{{3.post_title}}",      # I = Post Title
            "9": "{{3.hook}}",            # J = Hook
            "10": "{{3.hashtags}}",       # K = Hash Tags
            "11": "{{3.caption_tiktok_ig}}",  # L = Caption (TikTok/IG)
            "12": "{{3.caption_facebook}}",   # M = Caption 2 (Facebook)
            "13": "{{3.caption_linkedin}}",   # N = Caption 3 (LinkedIn)
            "14": "{{3.carousel_1_text}}",    # O = Carousel 1 Text
            "16": "{{3.carousel_2_text}}",    # Q = Carousel 2 Text
            "18": "{{3.carousel_3_text}}"     # S = Carousel 3 Text
        }, 900, 0),
        # Module 100: Router — split by Post Format
        {
            "id": 100,
            "module": "builtin:BasicRouter",
            "version": 1,
            "mapper": None,
            "metadata": {"designer": {"x": 1200, "y": 0}},
            "routes": [
                # ===== ROUTE 1: SINGLE IMAGE =====
                {
                    "flow": [
                        make_gemini(10, "3.image_prompt", 1500, -200),
                        make_overlay(11, 10, 1800, -200),
                        make_download(12, 11, 2100, -200),
                        make_dropbox_upload(13, 12, 11, 2400, -200),
                        make_sheets_update(14, {
                            "4": "Processed",            # E = Status
                            "7": "{{13.path_display}}"   # H = Dropbox Image Location
                        }, 2700, -200)
                    ],
                    "label": "Single Image",
                    "filter": {
                        "name": "Single Image",
                        "conditions": [[{
                            "a": "{{1.3}}",
                            "b": "carousel",
                            "o": "text:notequal"
                        }]]
                    }
                },
                # ===== ROUTE 2: CAROUSEL (3 images) =====
                {
                    "flow": [
                        # --- Slide 1 ---
                        make_gemini(20, "3.image_prompt", 1500, 200),
                        make_overlay(21, 20, 1800, 200),
                        make_download(22, 21, 2100, 200),
                        make_dropbox_upload(23, 22, 21, 2400, 200),
                        # --- Slide 2 ---
                        make_gemini(30, "3.image_prompt_2", 2700, 200),
                        make_overlay(31, 30, 3000, 200),
                        make_download(32, 31, 3300, 200),
                        make_dropbox_upload(33, 32, 31, 3600, 200),
                        # --- Slide 3 ---
                        make_gemini(40, "3.image_prompt_3", 3900, 200),
                        make_overlay(41, 40, 4200, 200),
                        make_download(42, 41, 4500, 200),
                        make_dropbox_upload(43, 42, 41, 4800, 200),
                        # --- Final update: all Dropbox paths + status ---
                        make_sheets_update(50, {
                            "4": "Processed",              # E = Status
                            "7": "{{23.path_display}}",    # H = Dropbox Image Location (slide 1 / main)
                            "15": "{{23.path_display}}",   # P = Carousel 1 Image
                            "17": "{{33.path_display}}",   # R = Carousel 2 Image
                            "19": "{{43.path_display}}"    # T = Carousel 3 Image
                        }, 5100, 200)
                    ],
                    "label": "Carousel",
                    "filter": {
                        "name": "Carousel",
                        "conditions": [[{
                            "a": "{{1.3}}",
                            "b": "carousel",
                            "o": "text:equal"
                        }]]
                    }
                }
            ]
        }
    ],
    "metadata": {
        "instant": False,
        "version": 1,
        "scenario": {
            "roundtrips": 1,
            "maxErrors": 3,
            "autoCommit": True,
            "autoCommitTriggerLast": True,
            "sequential": False,
            "confidential": False,
            "dataloss": False,
            "dlq": False,
            "freshVariables": False
        },
        "designer": {"orphans": []},
        "zone": "eu2.make.com"
    }
}

# Write output
output = json.dumps(blueprint, indent=4, ensure_ascii=False)
outpath = "C:/Users/fuzzy/OneDrive/Documents/Claude projects/GrowwestFinance_MVP/scenario_A_v2_blueprint.json"
with open(outpath, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Blueprint generated: {len(output)} chars, {output.count(chr(10))} lines")
print(f"Modules in main flow: {len(blueprint['flow'])}")
route1_count = len(blueprint['flow'][-1]['routes'][0]['flow'])
route2_count = len(blueprint['flow'][-1]['routes'][1]['flow'])
print(f"Single Image route: {route1_count} modules")
print(f"Carousel route: {route2_count} modules")
print(f"Total modules: {len(blueprint['flow']) + route1_count + route2_count}")
print(f"Saved to: {outpath}")
