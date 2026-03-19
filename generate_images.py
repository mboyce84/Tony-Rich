import requests
import base64
import os
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyCdUpt1QZGWUsic5Icq0siOwHlION1jSYM"
OUT_DIR = r"c:\Users\mboyc\Tony Rich\Images"

IMAGES = [
    {
        "filename": "belly-frustrated.png",
        "prompt": "Black woman standing at home looking down at her lower belly with a tired and frustrated expression, wearing casual clothes like a fitted t-shirt and jeans, soft natural indoor lighting, relatable real-body lifestyle photo, authentic and empathetic, not a model",
        "ratio": "3:4"
    },
    {
        "filename": "belly-mirror.png",
        "prompt": "Black woman standing sideways in front of a bathroom mirror looking at her midsection with a concerned expression, wearing leggings and a fitted top, soft warm home lighting, authentic real-body lifestyle photo, candid and relatable",
        "ratio": "3:4"
    },
]

def try_imagen3(prompt, ratio):
    """Try Imagen 4 model."""
    for model in ["imagen-4.0-generate-001", "imagen-4.0-fast-generate-001"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={API_KEY}"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": ratio}
        }
        r = requests.post(url, json=payload, timeout=90)
        if r.status_code == 200:
            data = r.json()
            b64 = data.get("predictions", [{}])[0].get("bytesBase64Encoded")
            if b64:
                return base64.b64decode(b64)
        print(f"  {model}: HTTP {r.status_code} - {r.text[:150]}")
    return None

def try_gemini_flash(prompt):
    """Try Gemini 2.0 Flash image generation."""
    for model in [
        "gemini-3.1-flash-image-preview",
        "gemini-3-pro-image-preview",
    ]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
        }
        r = requests.post(url, json=payload, timeout=90)
        if r.status_code == 200:
            data = r.json()
            for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    return base64.b64decode(part["inlineData"]["data"])
            print(f"  {model}: 200 OK but no image in response")
            print(f"  Response keys: {list(data.keys())}")
        else:
            print(f"  {model}: HTTP {r.status_code} - {r.text[:200]}")
    return None

for img in IMAGES:
    print(f"\nGenerating {img['filename']}...")

    result = try_imagen3(img["prompt"], img["ratio"])

    if not result:
        print("  Imagen failed, trying Gemini Flash...")
        result = try_gemini_flash(img["prompt"])

    if result:
        path = os.path.join(OUT_DIR, img["filename"])
        with open(path, "wb") as f:
            f.write(result)
        print(f"  SAVED ({len(result)//1024} KB)")
    else:
        print(f"  FAILED - both methods returned nothing")

print("\nDone.")
