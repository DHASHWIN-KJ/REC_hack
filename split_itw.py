import csv, os, shutil, sys

root = sys.argv[1]
for d in ("real", "fake"):
    os.makedirs(os.path.join(root, d), exist_ok=True)

moved = 0
with open(os.path.join(root, "meta.csv"), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        src = os.path.join(root, row["file"])
        if os.path.exists(src):
            dst = "real" if row["label"] == "bona-fide" else "fake"
            shutil.move(src, os.path.join(root, dst, row["file"]))
            moved += 1
print("Moved", moved, "files")