"""
Quick test — runs overlay on a sample image and saves result locally.
Usage: python test_overlay.py
"""
import io
import os
from PIL import Image
import sys

sys.path.insert(0, os.path.dirname(__file__))

LOGO_PATH = r"C:\Users\fuzzy\Downloads\GWF transparent logo.png"
TEST_IMAGE = r"C:\Users\fuzzy\Downloads\gwf_nb_background.jpg"
OUTPUT_PATH = r"C:\Users\fuzzy\Downloads\gwf_overlay_test.png"

# Import the overlay function directly
from overlay_server import overlay_logo

def test():
    if not os.path.exists(LOGO_PATH):
        print(f"ERROR: Logo not found at {LOGO_PATH}")
        return
    if not os.path.exists(TEST_IMAGE):
        print(f"ERROR: Test image not found at {TEST_IMAGE}")
        return

    source = Image.open(TEST_IMAGE)
    logo   = Image.open(LOGO_PATH)

    for pos in ["top-left", "top-right", "bottom-left", "bottom-right"]:
        result = overlay_logo(source.copy(), logo.copy(), pos, scale=0.25, padding=20)
        out = OUTPUT_PATH.replace(".png", f"_{pos}.png")
        result.save(out)
        print(f"Saved: {out}")

    print("\nDone! Check your Downloads folder.")

if __name__ == "__main__":
    test()
