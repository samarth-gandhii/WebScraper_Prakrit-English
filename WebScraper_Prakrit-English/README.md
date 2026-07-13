# Prakrit-English
## Web_Scraper_Prakrit-English

Data collection and word-list extraction for Prakrit ↔ English parallel text.


# Format of Parallel Corpora:

This repository contains two main parallel datasets:

## 1. General Prakrit-English Parallel Corpus ([prakrit_translations.json](file:///Users/samarth/SVNIT/Ancient%20Indian%20Languages/prakrit_dataset/WebScraper_Prakrit-English/prakrit_translations.json) / [prakrit_translations.csv](file:///Users/samarth/SVNIT/Ancient%20Indian%20Languages/prakrit_dataset/WebScraper_Prakrit-English/prakrit_translations.csv))

### Sources
* **Lines 1 to 8**: http://prakrit.info/prakrit/reader.html?r=1
* **Lines 9 to 16**: http://prakrit.info/prakrit/reader.html?r=3
* **Lines 17 to 116**: http://prakrit.info/prakrit/reader.html?r=4
* **Line 117**: http://prakrit.info/prakrit/reader.html?r=7
* **Lines 118 to 255**: http://prakrit.info/prakrit/reader.html?r=6
* **Lines 256 to 268**: https://www.kaggle.com/datasets/uditjain13/prakritnlp-ardhamagadhi-prakrit/data
* **Lines 269 to 272**: http://prakrit.info/prakrit/reader.html?r=2

### JSON Schema (per record)
- **Prakrit**: Full Prakrit line as shown on the site (string).
- **English**: English translation (string).
- **WordList**: Array of mappings with word-level correspondences. Each item is an object with keys **Prakrit** and **Sanskrit** (both strings). Example: `[{"Prakrit":"अमअ-","Sanskrit":"अमृत-"}, ...]`.
- **Bibliography**: Short citation text found on the page (string, optional).
- **BibliographyLink**: Absolute URL to the bibliography anchor on prakrit.info (string, optional).

### How merging works
- The scraper uses the English string as the primary merge key. If a new scrape finds an existing English entry (exact match or substring match), it updates the existing record rather than creating a duplicate.
- When merging, non-duplicate `WordList` items are appended. New `Bibliography` text is appended only if it isn't already present. `BibliographyLink` is set or replaced if the scrape provides a link.

### Sample record (excerpt)
```json
{
	"Prakrit": "अमअं पाउअकव्वं पढिउं सोउं...",
	"English": "Prakrit poetry is nectar. Those who don’t know how to recite it...",
	"WordList": [
		{"Prakrit":"अमअ-","Sanskrit":"अमृत-"},
		{"Prakrit":"पाउअ-","Sanskrit":"प्राकृत-"},
		{"Prakrit":"कव्व-","Sanskrit":"काव्य-"}
	],
	"Bibliography": "Ollett 2017",
	"BibliographyLink": "http://prakrit.info/prakrit/reader.html?r=1#Ollett2017"
}
```

---

## 2. Hāla's Sattasaī Dataset ([sattasai_dataset.json](file:///Users/samarth/SVNIT/Ancient%20Indian%20Languages/prakrit_dataset/WebScraper_Prakrit-English/sattasai_dataset.json) / [sattasai_dataset.csv](file:///Users/samarth/SVNIT/Ancient%20Indian%20Languages/prakrit_dataset/WebScraper_Prakrit-English/sattasai_dataset.csv))

This dataset contains 683 parallel verse pairs from Hāla's *Sattasaī* (*Gāthāsaptaśatī*).

### Sources
* **Prakrit text**: [Sanskrit Wikisource (गाहासत्तसई)](https://sa.wikisource.org/wiki/%E0%A4%97%E0%A4%BE%E0%A4%B9%E0%A4%BE%E0%A4%B8%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%B8%E0%A4%88)
* **English translation**: *Poems on life and love in ancient India : Hala's Sattasai* / translated from the Prakrit and introduced by Peter Khoroche and Herman Tieken. (Uniform title: *Gāthāsaptaśatī. English*)

### JSON Schema (per record)
- **verse_number**: The verse number identifier (integer).
- **prakrit**: Full Prakrit verse in Devanagari script (string).
- **english**: English translation of the verse (string).

### Sample record
```json
{
    "verse_number": 1,
    "prakrit": "पसुवइणो रोसारुणपडिमासंकंतगोरिमुहअंदम् गहिअग्घपंकअं मिअ संझासलिलंजलिं णमह",
    "english": "Already at her wedding\nPa\\rvatê’s friends knew she would be happy\nWhen S: iva tossed aside\nThe snake bracelet that frightened her. \nBow before S: iva’s offering to Twilight,\nThe water held in his cupped hand.\nReflecting Gaurê’s moonlike face,\nNow flushed with jealous anger,\nIt looks more like a crimson lotus."
}
```

---

**Usage**
1. Create and activate a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

2. Run the wordlist scraper for a reader page (example: `r=6`) and merge into the JSON:

```bash
.venv/bin/python build_dataset_wordlist.py -r 6 -j prakrit_translations.json
```

3. To run over multiple reader pages, repeat with different `-r` values or adapt the script to iterate pages.

**Notes & caveats**
- The site uses two word-list markup styles: inline early markup (`e... = ...`) and later structured `ul > li` lists. The scraper supports both.
- The site renders Devanagari transliteration via client-side scripts. The scraper prefers Devanagari spans and waits briefly to allow the transliteration layer to render; when unavailable it falls back to visible text (which may be Latin transliteration).
- Merge behavior is English-based; if you want a different key, update the script accordingly.
- Playwright and the browser driver are required; run within the virtualenv where `playwright` is installed.

**Dataset statistics (computed 2026-06-24)**

### 1. General Prakrit-English Parallel Corpus (`prakrit_translations.json`)
- **Total records (with English translation):** 272
- **Records with `WordList` entries:** 181
- **Total `WordList` item pairs extracted:** 1,361
- **Records with `Bibliography` text:** 246
- **Records with `BibliographyLink`:** 271

#### Top bibliography sources (by record count)
- Handique 2014: 135 records
- Khoroche and Tieken 2009: 82 records
- Boccali et al. 1990: 19 records
- Ollett 2017: 5 records
- Ingalls et al. 1990: 2 records
- Balbir and Besnard 1993: 1 record
- Lanman 1901: 1 record
- Pollock 2016: 1 record

### 2. Hāla's Sattasaī Dataset (`sattasai_dataset.json`)
- **Total verse pairs:** 683
- **Verse Range:** 1 to 959 (with gaps)
- **Format:** Verse mapping of Prakrit (Devanagari script) and English translations

