import csv
from pathlib import Path

CSV_FILE = Path("targets.csv")


def normalize_enabled(value: str) -> bool:
    if value is None:
        return False
    v = str(value).strip().lower()
    return v in {"y", "yes", "true", "1", "사용", "활성"}


def load_target_sites():
    if not CSV_FILE.exists():
        return []

    targets = []

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = (row.get("지자체명") or "").strip()
            url = (row.get("검색URL") or "").strip()
            enabled = normalize_enabled(row.get("사용여부", "Y"))

            if not enabled:
                continue

            if not name or not url:
                continue

            targets.append((name, url))

    return targets


TARGET_SITES = load_target_sites()
