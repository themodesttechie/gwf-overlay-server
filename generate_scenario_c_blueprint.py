import json

GOOGLE_CONN = 13880676
SPREADSHEET_ID = "148w-F3L_tbQfPr9BHruaxp76q9ZL0jlLmTzPo85g5SA"
BUFFER_TIKTOK_PROFILE = "69c54343af47dacb6958de88"

blueprint = {
    "name": "GWF - Daily TikTok Post (Scenario C)",
    "flow": [
        # Module 1: Google Sheets - Search Rows (find 1 row with Status = "Processed")
        {
            "id": 1,
            "module": "google-sheets:filterRows",
            "version": 2,
            "parameters": {"__IMTCONN__": GOOGLE_CONN},
            "mapper": {
                "from": "drive",
                "limit": "1",
                "filter": [[{"a": "E", "b": "Processed", "o": "text:equal"}]],
                "sheetId": "Pillar Schedule",
                "sortOrder": "asc",
                "spreadsheetId": SPREADSHEET_ID,
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
        # Module 2: Dropbox - Create/Update a Share Link (convert file path to public URL)
        {
            "id": 2,
            "module": "dropbox:createUpdateShareLink",
            "version": 1,
            "parameters": {"__IMTCONN__": 1},
            "mapper": {
                "path": "{{1.H}}",
                "selectBy": "map"
            },
            "metadata": {
                "designer": {"x": 300, "y": 0},
                "restore": {
                    "parameters": {
                        "__IMTCONN__": {
                            "data": {"scoped": "true", "connection": "dropbox"},
                            "label": "My Dropbox connection"
                        }
                    }
                }
            }
        },
        # Module 3: Buffer - Create Update (post to TikTok)
        {
            "id": 3,
            "module": "buffer:createAnUpdate",
            "version": 1,
            "parameters": {"__IMTCONN__": 1},
            "mapper": {
                "text": "{{1.L}}",
                "profileIds": [BUFFER_TIKTOK_PROFILE],
                "attachment": True,
                "picture": "{{2.downloadUrl}}",
                "thumbnail": "{{2.downloadUrl}}",
                "now": True
            },
            "metadata": {
                "designer": {"x": 600, "y": 0},
                "restore": {
                    "parameters": {
                        "__IMTCONN__": {
                            "data": {"scoped": "true", "connection": "buffer"},
                            "label": "My Buffer connection"
                        }
                    }
                }
            }
        },
        # Module 4: Google Sheets - Update a Row (set Status to "Posted")
        {
            "id": 4,
            "module": "google-sheets:updateRow",
            "version": 2,
            "parameters": {"__IMTCONN__": GOOGLE_CONN},
            "mapper": {
                "from": "drive",
                "mode": "select",
                "values": {
                    "4": "Posted"
                },
                "sheetId": "Pillar Schedule",
                "rowNumber": "{{1.__ROW_NUMBER__}}",
                "spreadsheetId": "/" + SPREADSHEET_ID,
                "includesHeaders": True,
                "useColumnHeaders": False,
                "valueInputOption": "USER_ENTERED"
            },
            "metadata": {
                "designer": {"x": 900, "y": 0},
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
            "slots": None,
            "confidential": False,
            "dataloss": False,
            "dlq": False,
            "freshVariables": False
        },
        "designer": {"orphans": []},
        "zone": "eu2.make.com"
    }
}

output = json.dumps(blueprint, indent=4, ensure_ascii=False)
outpath = "C:/Users/fuzzy/OneDrive/Documents/Claude projects/GrowwestFinance_MVP/scenario_C_tiktok_post_blueprint.json"
with open(outpath, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Blueprint generated: {len(output)} chars")
print(f"Modules: {len(blueprint['flow'])}")
print(f"Flow: Google Sheets (Search) -> Dropbox (Share Link) -> Buffer (TikTok Post) -> Google Sheets (Update Status)")
print(f"Saved to: {outpath}")
