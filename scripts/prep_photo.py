#!/usr/bin/env python3
"""
prep_photo.py

Prepare a portrait photo for clean ASCII conversion.

Pipeline
--------
1. Remove background using rembg
2. Improve local contrast using CLAHE
3. Brighten midtones slightly
4. Composite subject onto a pure white background
5. Save as grayscale PNG

Usage
-----
python scripts/prep_photo.py source-photo.jpg

or

python scripts/prep_photo.py input.jpg output.png
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove


# -------------------------------
# Configuration
# -------------------------------

MAX_WIDTH = 1200

CLAHE_CLIP = 2.6
CLAHE_TILE = (8, 8)

BRIGHTNESS_ALPHA = 1.05
BRIGHTNESS_BETA = 18

MASK_BLUR = 1.2


# -------------------------------
# Paths
# -------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))

INPUT = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(HERE, "..", "source-photo.jpg")
)

OUTPUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(HERE, "..", "source-prepped.png")
)


# -------------------------------
# Validation
# -------------------------------

if not os.path.exists(INPUT):
    print(f"\n❌ Input image not found:\n{INPUT}")
    sys.exit(1)

print("\nPreparing image...")
print(f"Input : {INPUT}")
print(f"Output: {OUTPUT}")


# -------------------------------
# Load image
# -------------------------------

img = Image.open(INPUT).convert("RGBA")

# Resize very large images
if img.width > MAX_WIDTH:
    ratio = MAX_WIDTH / img.width
    img = img.resize(
        (
            MAX_WIDTH,
            int(img.height * ratio),
        ),
        Image.LANCZOS,
    )

print(f"Image size: {img.width} x {img.height}")


# -------------------------------
# Background removal
# -------------------------------

print("Removing background...")

cutout = remove(img)

rgb = np.array(cutout.convert("RGB"))
alpha = np.array(cutout.getchannel("A"))

print("Background removed.")


# -------------------------------
# Convert to grayscale
# -------------------------------

gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

print("Applying CLAHE...")

clahe = cv2.createCLAHE(
    clipLimit=CLAHE_CLIP,
    tileGridSize=CLAHE_TILE,
)

gray = clahe.apply(gray)

print("Improving brightness...")

gray = cv2.convertScaleAbs(
    gray,
    alpha=BRIGHTNESS_ALPHA,
    beta=BRIGHTNESS_BETA,
)

# -------------------------------
# Smooth mask
# -------------------------------

mask = alpha.astype(np.float32) / 255.0

mask = cv2.GaussianBlur(
    mask,
    (0, 0),
    MASK_BLUR,
)

# -------------------------------
# White background composite
# -------------------------------

print("Compositing onto white...")

output = (
    gray.astype(np.float32) * mask
    + 255 * (1.0 - mask)
)

output = np.clip(output, 0, 255).astype(np.uint8)

Image.fromarray(output, mode="L").save(OUTPUT)

print("\n✅ Done!")
print(f"Saved to:\n{OUTPUT}")