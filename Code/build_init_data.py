from __future__ import annotations

import ast
import os
import random
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

SRC_ROOT = Path("filtered_data")
SRC_CSV = SRC_ROOT / "clean_annotations.csv"
SRC_IMAGES = SRC_ROOT / "images"

OUT_ROOT = Path("init_data")
TARGET_SIZE = (512, 512) 
SPLITS = ("train", "val", "test")
NUM_SAMPLES = 100
SEED = 42

OLD_W, OLD_H = 912, 1520 

BOX_COLOURS: dict[str, str] = {
    "Mass": "red",
    "Suspicious Calcification": "blue",
    "Architectural Distortion": "orange",
    "Focal Asymmetry": "green",
    "Asymmetry": "cyan",
    "Skin Thickening": "magenta",
    "Suspicious Lymph Node": "yellow",
    "Nipple Retraction": "purple",
    "Global Asymmetry": "lime",
    "Skin Retraction": "pink",
}
DEFAULT_COLOUR = "white"


def parse_categories(value) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(i).strip() for i in parsed if str(i).strip()]
    except (SyntaxError, ValueError):
        pass
    return [text]


def draw_boxes(img: Image.Image, rows: pd.DataFrame) -> Image.Image:
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for _, row in rows.iterrows():
        x0, y0, x1, y1 = row["new_xmin"], row["new_ymin"], row["new_xmax"], row["new_ymax"]
        if any(pd.isna(v) for v in (x0, y0, x1, y1)):
            continue
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(TARGET_SIZE[0], x1); y1 = min(TARGET_SIZE[1], y1)
        if x0 >= x1 or y0 >= y1:
            continue

        labels = parse_categories(row.get("finding_categories"))
        label_text = ", ".join(labels) if labels else "Lesion"
        colour = DEFAULT_COLOUR
        for lab in labels:
            if lab in BOX_COLOURS:
                colour = BOX_COLOURS[lab]
                break
        draw.rectangle([x0, y0, x1, y1], outline=colour, width=2)
        draw.text((x0, max(y0 - 14, 0)), label_text, fill=colour, font=font)
    return img


def main() -> None:
    print("Loading annotations …")
    df = pd.read_csv(SRC_CSV, low_memory=False)

    tw, th = TARGET_SIZE
    sx = tw / OLD_W
    sy = th / OLD_H

    for col_old, col_new in [
        ("resized_xmin", "new_xmin"),
        ("resized_xmax", "new_xmax"),
    ]:
        df[col_new] = df[col_old] * sx

    for col_old, col_new in [
        ("resized_ymin", "new_ymin"),
        ("resized_ymax", "new_ymax"),
    ]:
        df[col_new] = df[col_old] * sy

    df["height"] = th
    df["width"] = tw

    df = df.drop(columns=["resized_xmin", "resized_ymin", "resized_xmax", "resized_ymax"])

    out = OUT_ROOT
    if out.exists():
        import shutil
        shutil.rmtree(out)

    images_out = out / "images"
    for s in SPLITS:
        (images_out / s).mkdir(parents=True)
    samples_dir = out / "resized_boxes"
    samples_dir.mkdir(parents=True)

    print("Resizing images …")
    count = 0
    for split in SPLITS:
        src_folder = SRC_IMAGES / split
        dst_folder = images_out / split
        for fname in sorted(os.listdir(src_folder)):
            src_path = src_folder / fname
            img = cv2.imread(str(src_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            resized = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(dst_folder / fname), resized)
            count += 1
            if count % 1000 == 0:
                print(f"  … {count} images resized")

    print(f"  Total resized: {count}")

    csv_out = out / "dataset.csv"
    df.to_csv(csv_out, index=False)
    print(f"Dataset CSV written → {csv_out}  ({len(df)} rows)")

    print("Drawing sample boxes …")
    has_lesion = ~df["finding_categories"].astype(str).str.contains("No Finding")
    lesion_df = df[has_lesion]
    lesion_img_ids = lesion_df["image_id"].unique().tolist()

    rng = random.Random(SEED)
    sample_ids = rng.sample(lesion_img_ids, min(NUM_SAMPLES, len(lesion_img_ids)))

    drawn = 0
    for img_id in sample_ids:
        rows = lesion_df[lesion_df["image_id"] == img_id]
        split = rows.iloc[0]["split"]
        src_path = images_out / split / img_id
        if not src_path.exists():
            continue
        pil_img = Image.open(src_path)
        pil_img = draw_boxes(pil_img, rows)
        pil_img.save(samples_dir / img_id)
        drawn += 1

    print(f"  Sample images with boxes: {drawn}")

    split_counts = {s: len(os.listdir(images_out / s)) for s in SPLITS}
    print(f"\ninit_data summary:")
    for s in SPLITS:
        print(f"  {s:5s}: {split_counts[s]} images")
    print(f"  resized_boxes: {drawn} samples")
    print("Done")


if __name__ == "__main__":
    main()
