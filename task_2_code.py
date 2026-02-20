import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

INPUT = "input"
task_2_output = "task_2_output"
os.makedirs(task_2_output, exist_ok=True)

def detect_changes(before, after):
    # Grayscale
    gB = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gA = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # SSIM difference (structural changes)
    _, diff = ssim(gB, gA, full=True)
    diff = (1 - diff) * 255
    diff = diff.astype("uint8")

    # Combine SSIM + AbsDiff
    combined = cv2.addWeighted(diff, 0.7, cv2.absdiff(gB, gA), 0.3, 0)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        combined, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 5
    )

    # Morphology cleanup
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((7,7), np.uint8))
    clean = cv2.morphologyEx(clean, cv2.MORPH_OPEN, np.ones((7,7), np.uint8))

    # Contours (changes)
    cnts, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated = after.copy()

    for c in cnts:
        if cv2.contourArea(c) < 400: 
            continue
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(annotated, (x,y), (x+w, y+h), (0,0,255), 3)

    return annotated


# ----------- Main Loop -----------
files = sorted(os.listdir(INPUT))
before_files = [f for f in files if f.endswith(".jpg") and "~2" not in f]

for bf in before_files:
    base = bf[:-4]
    before_path = os.path.join(INPUT, f"{base}.jpg")
    after_path  = os.path.join(INPUT, f"{base}~2.jpg")

    if not os.path.exists(after_path):
        print(f"[SKIP] No after-image for {base}")
        continue

    before = cv2.imread(before_path)
    after  = cv2.imread(after_path)

    annotated = detect_changes(before, after)

    # Save exactly as assignment requires:
    cv2.imwrite(os.path.join(task_2_output, f"{base}.jpg"), before)
    cv2.imwrite(os.path.join(task_2_output, f"{base}~3.jpg"), annotated)

    print(f"[DONE] {base}")
