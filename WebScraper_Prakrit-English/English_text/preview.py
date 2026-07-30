"""
preview.py
----------
Stream and preview a small sample of the dataset BEFORE downloading,
so you can check data quality without saving anything.

Usage:
    python preview.py                  # shows 20 rows
    python preview.py --rows 50        # shows 50 rows
    python preview.py --skip 5000      # skip first 5000, then show 20
"""

import argparse
from datasets import load_dataset

# ── Configuration (keep in sync with get_data.py) ─────────────────────────────
DATASET_NAME  = "allenai/nllb"
LANGUAGE_PAIR = "eng_Latn-fra_Latn"
SPLIT         = "train"
# ───────────────────────────────────────────────────────────────────────────────


def preview(dataset_name: str, lang_pair: str, split: str, rows: int, skip: int) -> None:
    print(f"\nDataset : {dataset_name}")
    print(f"Pair    : {lang_pair}")
    print(f"Split   : {split}")
    print(f"Skipping: {skip} rows  |  Showing: {rows} rows\n")
    print("─" * 80)

    dataset = load_dataset(dataset_name, lang_pair, split=split, streaming=True, trust_remote_code=True)

    shown = 0
    for idx, row in enumerate(dataset):
        if idx < skip:
            continue
        if shown >= rows:
            break

        translation = row.get("translation", {})
        english = translation.get("eng_Latn", "").strip()
        french  = translation.get("fra_Latn", "").strip()

        shown += 1
        print(f"[{idx + 1}]")
        print(f"  EN: {english}")
        print(f"  FR: {french}")
        print()

    print("─" * 80)
    print(f"Previewed {shown} rows (dataset index {skip + 1} – {skip + shown}).")
    print("Run get_data.py to download the full dataset once you're happy with the quality.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview NLLB dataset rows before downloading.")
    parser.add_argument("--rows", type=int, default=20, help="Number of rows to preview (default: 20)")
    parser.add_argument("--skip", type=int, default=0,  help="Skip this many rows before previewing (default: 0)")
    args = parser.parse_args()

    preview(DATASET_NAME, LANGUAGE_PAIR, SPLIT, rows=args.rows, skip=args.skip)


if __name__ == "__main__":
    main()
