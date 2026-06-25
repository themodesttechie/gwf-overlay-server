"""
GWF Logo Overlay Server
=======================
Flask API that overlays the GrowWest Finance logo on any image.
Make.com calls this via HTTP module after Gemini image generation.

Endpoints:
  POST /overlay
    Body (JSON):
      {
        "image_base64": "...",   # base64 encoded image from Gemini (preferred)
        OR
        "image_url": "https://...",  # URL of source image
        "position": "bottom-right",  # top-left | top-right | bottom-left | bottom-right
        "scale": 0.20,               # optional: logo size as % of image width (default 0.20)
        "padding": 20                # optional: pixels from edge (default 20)
      }
    Returns JSON:
      {
        "url": "http://localhost:5050/images/branded_xxxxx.png",
        "filename": "branded_xxxxx.png"
      }

  GET /images/<filename>
    Returns the branded image file (accessible by Make.com via ngrok URL)

  GET /health
    Returns: {"status": "ok"}
"""

import os
import io
import uuid
import base64
import requests
from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

# Path to GWF logo (bundled in repo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# Folder to save branded images — use /tmp on cloud (ephemeral but fine for Make.com to download)
OUTPUT_FOLDER = os.environ.get("OUTPUT_FOLDER", os.path.join(BASE_DIR, "branded_images"))
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Public base URL — will be replaced by ngrok URL at runtime
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:5050")


def overlay_logo(source_image: Image.Image, logo: Image.Image, position: str, scale: float, padding: int) -> Image.Image:
    """Composite the logo onto the source image at the given position."""
    source = source_image.convert("RGBA")
    logo   = logo.convert("RGBA")

    # Resize logo relative to source image width
    logo_width  = int(source.width * scale)
    logo_ratio  = logo.height / logo.width
    logo_height = int(logo_width * logo_ratio)
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    pos_map = {
        "top-left":     (padding, padding),
        "top-right":    (source.width  - logo_width  - padding, padding),
        "bottom-left":  (padding,       source.height - logo_height - padding),
        "bottom-right": (source.width  - logo_width  - padding, source.height - logo_height - padding),
    }
    x, y = pos_map.get(position, pos_map["bottom-right"])

    composite = source.copy()
    composite.paste(logo, (x, y), logo)
    return composite.convert("RGB")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "logo_exists": os.path.exists(LOGO_PATH),
        "public_base_url": PUBLIC_BASE_URL
    })


@app.route("/overlay", methods=["POST"])
def overlay():
    data      = request.get_json(force=True)
    position  = data.get("position", "bottom-right")
    scale     = float(data.get("scale", 0.20))
    padding   = int(data.get("padding", 20))

    valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
    if position not in valid_positions:
        return jsonify({"error": f"position must be one of: {valid_positions}"}), 400

    if not os.path.exists(LOGO_PATH):
        return jsonify({"error": f"Logo not found at: {LOGO_PATH}"}), 500

    # --- Load source image from base64 OR url ---
    source_image = None

    if data.get("image_base64"):
        try:
            img_bytes = base64.b64decode(data["image_base64"])
            source_image = Image.open(io.BytesIO(img_bytes))
        except Exception as e:
            return jsonify({"error": f"Failed to decode base64 image: {str(e)}"}), 400

    elif data.get("image_url"):
        try:
            resp = requests.get(data["image_url"], timeout=30)
            resp.raise_for_status()
            source_image = Image.open(io.BytesIO(resp.content))
        except Exception as e:
            return jsonify({"error": f"Failed to download image: {str(e)}"}), 400
    else:
        return jsonify({"error": "Provide either image_base64 or image_url"}), 400

    # --- Load logo ---
    try:
        logo = Image.open(LOGO_PATH)
    except Exception as e:
        return jsonify({"error": f"Failed to load logo: {str(e)}"}), 500

    # --- Composite ---
    result = overlay_logo(source_image, logo, position, scale, padding)

    # --- Save to output folder ---
    filename = f"branded_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    result.save(output_path, format="PNG")

    # --- Return URL that Make.com can use ---
    file_url = f"{PUBLIC_BASE_URL}/images/{filename}"
    return jsonify({
        "url":      file_url,
        "filename": filename
    })


@app.route("/post-to-blotato", methods=["POST"])
def post_to_blotato():
    """Proxy endpoint for Blotato API calls.
    Accepts individual fields so Make.com doesn't need to construct nested JSON.
    This avoids the JSON escaping issue with Make.com's raw body substitution.
    """
    data = request.get_json(force=True)

    # Required fields
    account_id = data.get("accountId", "35643")
    platform = data.get("platform", "tiktok")
    text = data.get("text", "")
    media_url = data.get("mediaUrl", "")
    api_key = data.get("apiKey", "")

    # Optional TikTok target fields
    privacy = data.get("privacyLevel", "PUBLIC_TO_EVERYONE")
    auto_music = data.get("autoAddMusic", True)
    is_ai = data.get("isAiGenerated", True)

    # Build the properly structured Blotato payload
    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text": text,
                "mediaUrls": [media_url],
                "platform": platform
            },
            "target": {
                "targetType": platform,
                "privacyLevel": privacy,
                "disabledComments": False,
                "disabledDuet": False,
                "disabledStitch": False,
                "isBrandedContent": False,
                "isYourBrand": False,
                "isAiGenerated": is_ai,
                "autoAddMusic": auto_music
            }
        }
    }

    try:
        resp = requests.post(
            "https://backend.blotato.com/v2/posts",
            json=payload,
            headers={"blotato-api-key": api_key, "Content-Type": "application/json"},
            timeout=30
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/images/<filename>", methods=["GET"])
def serve_image(filename):
    """Serve a branded image by filename."""
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    import sys

    # Allow passing ngrok URL as argument: python overlay_server.py https://xxxx.ngrok-free.app
    if len(sys.argv) > 1:
        PUBLIC_BASE_URL = sys.argv[1].rstrip("/")

    print("=" * 55)
    print("  GWF Logo Overlay Server")
    print("=" * 55)
    print(f"  Logo:       {LOGO_PATH}")
    print(f"  Logo found: {os.path.exists(LOGO_PATH)}")
    print(f"  Output dir: {OUTPUT_FOLDER}")
    print(f"  Public URL: {PUBLIC_BASE_URL}")
    print()
    print("  Local:   http://localhost:5050")
    print("  Health:  http://localhost:5050/health")
    print()
    print("  Make.com HTTP module:")
    print("    Method: POST")
    print(f"    URL:    {PUBLIC_BASE_URL}/overlay")
    print('    Body:   {"image_base64":"{{23.data.candidates[1].content.parts[2].inlineData.data}}","position":"bottom-right"}')
    print("=" * 55)
    app.run(host="0.0.0.0", port=5050, debug=False)
