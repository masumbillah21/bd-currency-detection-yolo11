# RUN ONLY ONCE

import os
import shutil
import random

# ===== CONFIG =====
BASE_DIR = "dataset"
TRAIN_RATIO = 0.8
VALID_RATIO = 0.1
TEST_RATIO = 0.1

IMAGE_EXTS = (".jpg", ".jpeg", ".png")

random.seed(42)

# ===== PATHS =====
train_img_dir = os.path.join(BASE_DIR, "train/images")
train_lbl_dir = os.path.join(BASE_DIR, "train/labels")

valid_img_dir = os.path.join(BASE_DIR, "valid/images")
valid_lbl_dir = os.path.join(BASE_DIR, "valid/labels")

test_img_dir = os.path.join(BASE_DIR, "test/images")
test_lbl_dir = os.path.join(BASE_DIR, "test/labels")

# ===== CREATE DIRS =====
for d in [
    valid_img_dir, valid_lbl_dir,
    test_img_dir, test_lbl_dir
]:
    os.makedirs(d, exist_ok=True)

# ===== COLLECT FILES =====
images = [
    f for f in os.listdir(train_img_dir)
    if f.lower().endswith(IMAGE_EXTS)
]

images.sort()
random.shuffle(images)

total = len(images)
train_end = int(total * TRAIN_RATIO)
valid_end = train_end + int(total * VALID_RATIO)

train_files = images[:train_end]
valid_files = images[train_end:valid_end]
test_files = images[valid_end:]

# ===== MOVE FILES =====
def move(files, img_dst, lbl_dst):
    for img in files:
        name, _ = os.path.splitext(img)
        lbl = name + ".txt"

        shutil.move(
            os.path.join(train_img_dir, img),
            os.path.join(img_dst, img)
        )

        lbl_src = os.path.join(train_lbl_dir, lbl)
        if os.path.exists(lbl_src):
            shutil.move(
                lbl_src,
                os.path.join(lbl_dst, lbl)
            )

move(valid_files, valid_img_dir, valid_lbl_dir)
move(test_files, test_img_dir, test_lbl_dir)

print("Dataset split completed!")
print(f"Train: {len(train_files)}")
print(f"Valid: {len(valid_files)}")
print(f"Test : {len(test_files)}")
