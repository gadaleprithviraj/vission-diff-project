import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Any

# Import the original algorithm from the project root.
# In a serverless deployment the working directory is not guaranteed to be the repo root,
# so we must insert the actual project root at the front of the import path.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from task_2_code import detect_changes as original_detect_changes

def process_images(before_path: str, after_path: str) -> Dict[str, Any]:
    """Run the existing change‑detection pipeline and return result file paths.

    Returns a dict with keys:
        before_path, after_path, diff_path, annotated_path, regions
    """
    before = cv2.imread(before_path)
    after = cv2.imread(after_path)
    if before is None or after is None:
        raise ValueError("Unable to read one of the input images.")

    # Run original detection to get annotated image with boxes
    annotated = original_detect_changes(before, after)

    # Re‑create pipeline to also obtain diff image and region boxes
    gB = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gA = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
    _, diff = __import__('skimage.metrics').metrics.structural_similarity(gB, gA, full=True)
    diff = (1 - diff) * 255
    diff = diff.astype('uint8')
    combined = cv2.addWeighted(diff, 0.7, cv2.absdiff(gB, gA), 0.3, 0)
    thresh = cv2.adaptiveThreshold(
        combined, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 5
    )
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((7,7), np.uint8))
    clean = cv2.morphologyEx(clean, cv2.MORPH_OPEN, np.ones((7,7), np.uint8))
    cnts, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions: List[Dict[str, int]] = []
    for c in cnts:
        if cv2.contourArea(c) < 400:
            continue
        x, y, w, h = cv2.boundingRect(c)
        regions.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})

    # Save temporary result images
    tmp_dir = Path(__file__).parent / "temp"
    tmp_dir.mkdir(exist_ok=True)
    before_tmp = tmp_dir / "before.jpg"
    after_tmp = tmp_dir / "after.jpg"
    diff_tmp = tmp_dir / "diff.jpg"
    annotated_tmp = tmp_dir / "annotated.jpg"
    cv2.imwrite(str(before_tmp), before)
    cv2.imwrite(str(after_tmp), after)
    cv2.imwrite(str(diff_tmp), diff)
    cv2.imwrite(str(annotated_tmp), annotated)

    return {
        "before_path": str(before_tmp),
        "after_path": str(after_tmp),
        "diff_path": str(diff_tmp),
        "annotated_path": str(annotated_tmp),
        "regions": regions,
    }
