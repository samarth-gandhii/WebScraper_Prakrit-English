import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_prakrit_pairs(r_value=3):
    url = f"http://prakrit.info/prakrit/reader.html?r={r_value}"
    dataset = []

    print(f"Opening rendered page: {url}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_selector(".text-pair", timeout=30000)

        text_pairs = page.query_selector_all(".text-pair")
        print(f"Found {len(text_pairs)} text-pair elements")

        for idx, pair in enumerate(text_pairs, start=1):
            prakrit_verse = ""
            indic_container = pair.query_selector(".indic-text")
            if indic_container:
                deva_spans = indic_container.query_selector_all("[data-script='Deva']")
                texts = [span.inner_text().strip() for span in deva_spans if span.inner_text().strip()]
                if texts:
                    prakrit_verse = " ".join(texts)
                else:
                    prakrit_verse = indic_container.inner_text().strip()
                prakrit_verse = " ".join(prakrit_verse.split())

            english_translation = ""
            translation_container = pair.query_selector(".translation")
            if translation_container:
                english_translation = translation_container.inner_text().strip()
                english_translation = " ".join(english_translation.split())

            if prakrit_verse and english_translation:
                dataset.append({
                    "Prakrit": prakrit_verse,
                    "English": english_translation
                })
            else:
                missing = []
                if not prakrit_verse:
                    missing.append("Prakrit")
                if not english_translation:
                    missing.append("English")
                print(f"Skipping pair #{idx}: missing {', '.join(missing)}")

        browser.close()

    save_data(dataset)
def save_data(dataset, csv_path="prakrit_translations.csv", json_path="prakrit_translations.json"):
    import json
    from pathlib import Path
    import pandas as pd

    csv_file = Path(csv_path)
    json_file = Path(json_path)

    # Append to CSV (create header if file doesn't exist)
    df = pd.DataFrame(dataset)
    write_header = not csv_file.exists()
    df.to_csv(csv_file, index=False, mode="a", header=write_header, encoding="utf-8-sig")

    # Merge into JSON array (read existing array, extend, write back)
    if json_file.exists():
        try:
            with json_file.open("r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = [existing]
        except (json.JSONDecodeError, OSError):
            existing = []
        existing.extend(dataset)
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)
    else:
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)

    print(f"Appended {len(dataset)} rows to {csv_file} and merged into {json_file}")
# def save_data(dataset):
#     if not dataset:
#         print("No pairs found. The HTML structure might have changed.")
#         return

#     # Convert to a DataFrame for easy manipulation and exporting
#     df = pd.DataFrame(dataset)
    
#     # Save to CSV for easy spreadsheet viewing
#     df.to_csv("prakrit_translations.csv", index=False, encoding="utf-8-sig")
    
#     # Save to JSON, which is ideal for ML model ingestion
#     df.to_json("prakrit_translations.json", orient="records", force_ascii=False, indent=4)
    
#     print(f"Success! Extracted {len(dataset)} valid pairs.")
#     print("Files saved: 'prakrit_translations.csv' and 'prakrit_translations.json'")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape prakrit.info reader pages for Prakrit-English pairs")
    parser.add_argument("-r", "--reader", type=int, default=2, help="reader page id (the r query param)")
    args = parser.parse_args()

    scrape_prakrit_pairs(args.reader)


if __name__ == "__main__":
    main()