import os

def safe_rename(path):
    base, ext = os.path.splitext(path)
    i = 1
    new_path = path
    while os.path.exists(new_path):
        new_path = f"{base}_{i}{ext}"
        i += 1
    return new_path

root_dir = "./dataset"

for root, dirs, files in os.walk(root_dir):
    for filename in files:
        if " " in filename:
            old_path = os.path.join(root, filename)
            new_filename = filename.replace(" ", "_")
            new_path = os.path.join(root, new_filename)

            if os.path.exists(new_path):
                new_path = safe_rename(new_path)

            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} → {new_path}")
