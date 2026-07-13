import json
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


def scrape_wordlists(r_value=3, json_path="prakrit_translations.json"):
    url = f"http://prakrit.info/prakrit/reader.html?r={r_value}"
    results = []

    print(f"Opening page: {url}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_selector(".text-pair", timeout=30000)
        page.wait_for_function(
            """() => Array.from(document.querySelectorAll('.translitWrapper[data-language="pra"]'))
                .some(el => /[\u0900-\u097F]/.test((el.textContent || '').trim()))""",
            timeout=30000,
        )

        text_pairs = page.query_selector_all(".text-pair")
        print(f"Found {len(text_pairs)} text-pair elements")

        for idx, pair in enumerate(text_pairs, start=1):
            # Extract translation text (English)
            english = ""
            translation_container = pair.query_selector(".translation")
            if translation_container:
                english = translation_container.inner_text().strip()
                english = " ".join(english.split())

            # Extract bibliography label (e.g. Ollett 2017: p. 118)
            bibl_text = ""
            bibl_link = ""
            bibl_el = pair.query_selector(".bibl-link")
            if bibl_el:
                bibl_text = bibl_el.inner_text().strip()
                href = bibl_el.get_attribute("href") or ""
                if href:
                    bibl_link = urljoin(url, href)

            # Extract word-list entries within this pair
            wordlist = []
            wl_container = pair.query_selector(".word-list")
            if wl_container:
                # Prefer structured list items
                li_elems = wl_container.query_selector_all("ul.stabaka > li")
                if not li_elems:
                    li_elems = wl_container.query_selector_all("li")

                def parse_wordlist_text(text):
                    cleaned = " ".join(text.split())
                    if "=" not in cleaned:
                        return "", ""

                    left, right = cleaned.split("=", 1)
                    pra = re.sub(r"^e\s*", "", left).strip()
                    san = right.strip().replace("[", "").replace("]", "")
                    return pra, san

                def collect_text(elements):
                    parts = []
                    for el in elements:
                        text = " ".join(el.inner_text().split())
                        if text:
                            parts.append(text)
                    return " ".join(parts).strip()

                for li in li_elems:
                    pra = collect_text(li.query_selector_all("span.translitWrapper[data-language='pra']"))
                    if not pra:
                        pra = collect_text(li.query_selector_all("span.translit[data-language='pra'] span.translitWrapper"))

                    san = collect_text(li.query_selector_all("a span.translitWrapper[data-language='san']"))
                    if not san:
                        san = collect_text(li.query_selector_all("span.translitWrapper[data-language='san']"))

                    if not pra or not san:
                        fallback_pra, fallback_san = parse_wordlist_text(li.inner_text())
                        if not pra:
                            pra = fallback_pra
                        if not san:
                            san = fallback_san

                    if pra or san:
                        wordlist.append({"Prakrit": pra, "Sanskrit": san})

                # Early verses on some pages use inline word-list text instead of li elements.
                if not wordlist:
                    inline_text = wl_container.inner_text().strip()
                    inline_lines = [line.strip() for line in inline_text.splitlines() if line.strip()]

                    for line in inline_lines:
                        if "=" not in line:
                            continue

                        pra, san = parse_wordlist_text(line)

                        if pra or san:
                            wordlist.append({"Prakrit": pra, "Sanskrit": san})

            if english or wordlist:
                results.append({
                    "English": english,
                    "WordList": wordlist,
                    "Bibliography": bibl_text,
                    "BibliographyLink": bibl_link,
                })

        browser.close()

    # Merge into JSON file
    json_file = Path(json_path)
    if json_file.exists():
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = [data]
        except (json.JSONDecodeError, OSError):
            data = []
    else:
        data = []

    merged = 0
    for item in results:
        eng = item.get("English", "").strip()
        wl = item.get("WordList", [])
        bibl = item.get("Bibliography", "").strip()
        bibl_link = item.get("BibliographyLink", "").strip()
        if not eng:
            # If no English translation available, skip merging but still report
            continue

        # Try to find an existing entry by fuzzy match (substring both ways)
        matched = False
        for entry in data:
            entry_eng = (entry.get("English") or "").strip()
            if not entry_eng:
                continue
            if eng == entry_eng or eng in entry_eng or entry_eng in eng:
                # merge wordlist
                existing_wl = entry.get("WordList") or []
                # avoid duplicates
                for w in wl:
                    if w not in existing_wl:
                        existing_wl.append(w)
                entry["WordList"] = existing_wl
                if bibl:
                    prev = entry.get("Bibliography", "")
                    if bibl not in prev:
                        entry["Bibliography"] = (prev + (" " if prev else "") + bibl).strip()
                if bibl_link:
                    entry["BibliographyLink"] = bibl_link
                matched = True
                merged += 1
                break

        if not matched:
            new_entry = {"English": eng, "WordList": wl}
            if bibl:
                new_entry["Bibliography"] = bibl
            if bibl_link:
                new_entry["BibliographyLink"] = bibl_link
            data.append(new_entry)
            merged += 1

    # Write back
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Processed {len(results)} pairs, merged {merged} items into {json_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape prakrit.info word-lists and merge into JSON")
    parser.add_argument("-r", "--reader", type=int, default=2, help="reader page id (r query param)")
    parser.add_argument("-j", "--json", default="prakrit_translations.json", help="path to translations JSON")
    args = parser.parse_args()

    scrape_wordlists(args.reader, args.json)


if __name__ == "__main__":
    main()
