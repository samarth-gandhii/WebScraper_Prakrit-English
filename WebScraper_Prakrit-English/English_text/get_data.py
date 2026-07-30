"""
get_data.py
-----------
Downloads the English side of the allenai/nllb dataset (eng_Latn-fra_Latn split)
from HuggingFace and saves the first MAX_ROWS rows to three output formats:

  - english_dataset.csv   (columns: id, english)
  - english_dataset.txt   (one sentence per line)
  - english_dataset.json  (list of {"id": int, "english": str} objects)

Usage:
    python get_data.py
"""

import json
import csv
import os
from datasets import load_dataset

# ── Configuration ──────────────────────────────────────────────────────────────
DATASET_NAME   = "allenai/nllb"
LANGUAGE_PAIR  = "eng_Latn-fra_Latn"
SPLIT          = "train"
SKIP_ROWS      = 5_000   # skip this many rows from the start
MAX_ROWS       = 10_000  # how many rows to collect after skipping

OUTPUT_DIR     = os.path.dirname(os.path.abspath(__file__))
CSV_PATH       = os.path.join(OUTPUT_DIR, "english_dataset.csv")
TXT_PATH       = os.path.join(OUTPUT_DIR, "english_dataset.txt")
JSON_PATH      = os.path.join(OUTPUT_DIR, "english_dataset.json")
# ───────────────────────────────────────────────────────────────────────────────


def load_english_sentences(dataset_name: str, lang_pair: str, split: str, skip: int, max_rows: int) -> list[dict]:
    """Load up to max_rows English sentences from the NLLB dataset, skipping the first skip rows."""
    print(f"Loading dataset: {dataset_name} | pair: {lang_pair} | split: {split}")
    print(f"Skipping first {skip:,} rows, then collecting {max_rows:,} rows …")
    dataset = load_dataset(dataset_name, lang_pair, split=split, streaming=True, trust_remote_code=True)

    records = []
    collected = 0
    for idx, row in enumerate(dataset):
        if idx < skip:
            continue
        if collected >= max_rows:
            break
        # NLLB stores sentence pairs under row["translation"]
        translation = row.get("translation", {})
        english_text = translation.get("eng_Latn", "").strip()  # same key for all eng_Latn pairs
        if english_text:
            records.append({"id": idx + 1, "english": english_text})
            collected += 1

        if collected % 1000 == 0 and collected > 0:
            print(f"  Collected {collected} rows (dataset index {idx + 1}) …")

    print(f"Total records collected: {len(records)}")
    return records


def save_csv(records: list[dict], path: str) -> None:
    """Save records to a CSV file with columns: id, english."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "english"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved CSV  → {path}")


def save_txt(records: list[dict], path: str) -> None:
    """Save one English sentence per line to a plain-text file."""
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(rec["english"] + "\n")
    print(f"Saved TXT  → {path}")


def save_json(records: list[dict], path: str) -> None:
    """Save records as a JSON array."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON → {path}")


def main() -> None:
    records = load_english_sentences(DATASET_NAME, LANGUAGE_PAIR, SPLIT, skip=SKIP_ROWS, max_rows=MAX_ROWS)

    if not records:
        print("No records found. Check dataset name / language pair and try again.")
        return

    save_csv(records, CSV_PATH)
    save_txt(records, TXT_PATH)
    save_json(records, JSON_PATH)

    print("\nDone! Files written:")
    for path in (CSV_PATH, TXT_PATH, JSON_PATH):
        size_kb = os.path.getsize(path) / 1024
        print(f"  {os.path.basename(path):30s}  {size_kb:8.1f} KB")


if __name__ == "__main__":
    main()
