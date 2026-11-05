import os

base = r"C:\Users\harini\Downloads\drive-download-20261101T162443Z-1-001"

readmes = ["README.md", "README (2).md", "README (3).md", "README (4).md"]
for r in readmes:
    p = os.path.join(base, r)
    print(f"\n=======================================================")
    print(f"FILE: {r} ({os.path.getsize(p)} bytes)")
    print(f"=======================================================")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = [f.readline() for _ in range(40)]
        print("".join(lines))
