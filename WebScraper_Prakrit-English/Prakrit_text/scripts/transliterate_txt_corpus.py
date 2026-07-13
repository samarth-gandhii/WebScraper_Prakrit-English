#!/usr/bin/env python3
"""Transliterate the txt corpus from Latin Prakrit to Devanagari.

The corpus is mostly ISO 15919 / IAST-like Latin Prakrit with a few editorial
variants such as ï/ü/ŏ/ĕ for hiatus. This script keeps the transliteration
local and dependency-free so the CSV/JSON export can be regenerated reliably.
"""

from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


VIRAMA = "्"


@dataclass(frozen=True)
class VowelForm:
    independent: str
    dependent: str


CONSONANTS = {
    "kh": "ख",
    "gh": "घ",
    "ch": "छ",
    "jh": "झ",
    "ṭh": "ठ",
    "ḍh": "ढ",
    "th": "थ",
    "dh": "ध",
    "ph": "फ",
    "bh": "भ",
    "Kh": "ख",
    "Gh": "घ",
    "Ch": "छ",
    "Jh": "झ",
    "Th": "ठ",
    "Dh": "ढ",
    "Ph": "फ",
    "Bh": "भ",
    "k͟h": "ख़",
    "ṛh": "ढ़",
    "t̤": "त़",
    "s̱": "थ़",
    "k": "क",
    "g": "ग",
    "ṅ": "ङ",
    "c": "च",
    "j": "ज",
    "ñ": "ञ",
    "ṭ": "ट",
    "ḍ": "ड",
    "ṇ": "ण",
    "t": "त",
    "d": "द",
    "n": "न",
    "p": "प",
    "b": "ब",
    "m": "म",
    "y": "य",
    "r": "र",
    "l": "ल",
    "v": "व",
    "ś": "श",
    "ṣ": "ष",
    "s": "स",
    "h": "ह",
    "ḷ": "ळ",
    "q": "क़",
    "ġ": "ग़",
    "z": "ज़",
    "ž": "झ़",
    "ṛ": "ड़",
    "f": "फ़",
    "w": "व़",
    "K": "ख",
    "G": "घ",
    "C": "छ",
    "J": "झ",
    "T": "ठ",
    "D": "ढ",
    "N": "ण",
    "P": "फ",
    "B": "भ",
    "S": "श",
    "L": "ळ",
    "Y": "ञ",
    "Q": "क़",
    "R": "ड़",
    "F": "फ़",
    "V": "ॐ",
}

VOWELS = {
    "a": VowelForm("अ", ""),
    "ā": VowelForm("आ", "ा"),
    "i": VowelForm("इ", "ि"),
    "ī": VowelForm("ई", "ी"),
    "u": VowelForm("उ", "ु"),
    "ū": VowelForm("ऊ", "ू"),
    "ṛ": VowelForm("ऋ", "ृ"),
    "ṝ": VowelForm("ॠ", "ॄ"),
    "ḷ": VowelForm("ऌ", "ॢ"),
    "ḹ": VowelForm("ॡ", "ॣ"),
    "e": VowelForm("ऎ", "ॆ"),
    "ē": VowelForm("ए", "े"),
    "ai": VowelForm("ऐ", "ै"),
    "o": VowelForm("ऒ", "ॊ"),
    "ō": VowelForm("ओ", "ो"),
    "au": VowelForm("औ", "ौ"),
    "ê": VowelForm("ऍ", "ॅ"),
    "ô": VowelForm("ऑ", "ॉ"),
    "A": VowelForm("अ", ""),
    "Ā": VowelForm("आ", "ा"),
    "I": VowelForm("इ", "ि"),
    "Ī": VowelForm("ई", "ी"),
    "U": VowelForm("उ", "ु"),
    "Ū": VowelForm("ऊ", "ू"),
    "Ṛ": VowelForm("ऋ", "ृ"),
    "Ṝ": VowelForm("ॠ", "ॄ"),
    "Ḷ": VowelForm("ऌ", "ॢ"),
    "Ḹ": VowelForm("ॡ", "ॣ"),
    "E": VowelForm("ऎ", "ॆ"),
    "Ē": VowelForm("ए", "े"),
    "Ai": VowelForm("ऐ", "ै"),
    "O": VowelForm("ऒ", "ॊ"),
    "Ō": VowelForm("ओ", "ो"),
    "Au": VowelForm("औ", "ौ"),
    "Ê": VowelForm("ऍ", "ॅ"),
    "Ô": VowelForm("ऑ", "ॉ"),
    "ï": VowelForm("इ", ""),
    "ü": VowelForm("उ", ""),
    "ŏ": VowelForm("ओ", ""),
    "ĕ": VowelForm("ए", ""),
    "Ï": VowelForm("इ", ""),
    "Ü": VowelForm("उ", ""),
    "Ŏ": VowelForm("ओ", ""),
    "Ĕ": VowelForm("ए", ""),
}

MARKS = {
    "ṁ": "ं",
    "ṃ": "ं",
    "ḥ": "ः",
    "m̐": "ँ",
    "̃": "ँ",
    "̍": "॑",
    "́": "॑",
    "̱": "॒",
    "̲": "॒",
    "॑": "॑",
    "॒": "॒",
}

SYMBOLS = {
    "ॐ": "ॐ",
    "॥": "॥",
    "।": "।",
    "—": "—",
    "–": "–",
    "…": "…",
    "‘": "‘",
    "’": "’",
    "“": "“",
    "”": "”",
    "₹": "₹",
    "·": "·",
    "¿": "¿",
    "[": "[",
    "]": "]",
    "(": "(",
    ")": ")",
    "{": "{",
    "}": "}",
    "<": "<",
    ">": ">",
    "|": "|",
    "-": "-",
    ",": ",",
    ";": ";",
    ":": ":",
    ".": ".",
    "?": "?",
    "!": "!",
    "=": "=",
    "+": "+",
    "*": "*",
    "_": "_",
    "@": "@",
    "%": "%",
    "'": "'",
    '"': '"',
    " ": " ",
    "\n": "\n",
    "\t": "\t",
    "\xa0": " ",
}

DIGITS = {str(i): ch for i, ch in enumerate("०१२३४५६७८९")}

TOKEN_ORDER = sorted(
    set(CONSONANTS) | set(VOWELS) | set(MARKS) | set(SYMBOLS),
    key=len,
    reverse=True,
)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    replacements = {
        "ṃ": "ṁ",
        "Ṛ": "Ṛ",
        "Ṝ": "Ṝ",
        "Ḷ": "Ḷ",
        "Ḹ": "Ḹ",
        "ṝ": "ṝ",
        "ḹ": "ḹ",
        "Ï": "Ï",
        "Ü": "Ü",
        "Ŏ": "Ŏ",
        "Ĕ": "Ĕ",
        "ï": "ï",
        "ü": "ü",
        "ŏ": "ŏ",
        "ĕ": "ĕ",
        "ॅ": "ê",
        "ॉ": "ô",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(text):
        token = None
        for candidate in TOKEN_ORDER:
            if text.startswith(candidate, i):
                token = candidate
                break
        if token is None:
            tokens.append(text[i])
            i += 1
        else:
            tokens.append(token)
            i += len(token)
    return tokens


def render_consonant_cluster(cluster: list[str], virama_last: bool = False) -> str:
    if not cluster:
        return ""
    pieces = []
    for index, consonant in enumerate(cluster):
        pieces.append(consonant)
        if index < len(cluster) - 1 or virama_last:
            pieces.append(VIRAMA)
    return "".join(pieces)


def transliterate_text(text: str) -> str:
    tokens = tokenize(normalize(text))
    out: list[str] = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token in DIGITS:
            out.append(DIGITS[token])
            i += 1
            continue

        if token in SYMBOLS and token not in {" ", "\n", "\t", "\xa0"}:
            out.append(SYMBOLS[token])
            i += 1
            continue

        if token in {" ", "\n", "\t", "\xa0"}:
            out.append(SYMBOLS[token])
            i += 1
            continue

        if token in MARKS:
            out.append(MARKS[token])
            i += 1
            continue

        if token in CONSONANTS:
            cluster = [CONSONANTS[token]]
            i += 1
            while i < len(tokens) and tokens[i] in CONSONANTS:
                cluster.append(CONSONANTS[tokens[i]])
                i += 1

            if i < len(tokens) and tokens[i] in {"a", "A"}:
                out.append(render_consonant_cluster(cluster))
                i += 1
            elif i < len(tokens) and tokens[i] in VOWELS:
                vowel = VOWELS[tokens[i]]
                if vowel.dependent:
                    out.append(render_consonant_cluster(cluster[:-1], virama_last=True) + cluster[-1] + vowel.dependent)
                else:
                    out.append(render_consonant_cluster(cluster))
                    out.append(vowel.independent)
                i += 1
            else:
                out.append(render_consonant_cluster(cluster, virama_last=False))

            while i < len(tokens) and tokens[i] in MARKS:
                out.append(MARKS[tokens[i]])
                i += 1
            continue

        if token in VOWELS:
            vowel = VOWELS[token]
            out.append(vowel.independent)
            i += 1
            while i < len(tokens) and tokens[i] in MARKS:
                out.append(MARKS[tokens[i]])
                i += 1
            continue

        out.append(token)
        i += 1

    return "".join(out)


def iter_text_files(root: Path):
    yield from sorted(root.rglob("*.txt"))


def build_records(txt_root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for path in iter_text_files(txt_root):
        latin_text = path.read_text(encoding="utf-8")
        records.append(
            {
                "relative_path": str(path.relative_to(txt_root)),
                "file_name": path.name,
                "line_count": str(latin_text.count("\n") + (1 if latin_text else 0)),
                "devanagari_text": transliterate_text(latin_text),
            }
        )
    return records


def write_csv(records: list[dict[str, str]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "file_name", "line_count", "devanagari_text"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def write_json(records: list[dict[str, str]], output_path: Path) -> None:
    json_records = []
    for r in records:
        json_records.append(
            {
                "relative_path": r["relative_path"],
                "file_name": r["file_name"],
                "line_count": r["line_count"],
                "devanagari_text": (
                    r["devanagari_text"].split("\n")
                    if r["devanagari_text"]
                    else []
                ),
            }
        )
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": "txt",
        "file_count": len(json_records),
        "records": json_records,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_individual_csv(record: dict[str, str], output_path: Path) -> None:
    text = record["devanagari_text"]
    lines = text.split("\n") if text else []
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["line_number", "devanagari_text"])
        writer.writeheader()
        for idx, line in enumerate(lines, start=1):
            writer.writerow({
                "line_number": idx,
                "devanagari_text": line
            })


def write_individual_json(record: dict[str, str], output_path: Path) -> None:
    text = record["devanagari_text"]
    lines = text.split("\n") if text else []
    payload = {
        "relative_path": record["relative_path"],
        "file_name": record["file_name"],
        "line_count": record["line_count"],
        "devanagari_text": lines,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transliterate the txt corpus to Devanagari.")
    parser.add_argument(
        "--txt-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "txt",
        help="Path to the txt corpus root.",
    )
    parser.add_argument(
        "--csv-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "prakrit_texts_devanagari.csv",
        help="CSV output path.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "prakrit_texts_devanagari.json",
        help="JSON output path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = build_records(args.txt_root)
    write_csv(records, args.csv_output)
    write_json(records, args.json_output)
    print(f"Wrote {len(records)} records to {args.csv_output} and {args.json_output}")
    
    for r in records:
        txt_path = args.txt_root / r["relative_path"]
        csv_path = txt_path.with_suffix(".csv")
        json_path = txt_path.with_suffix(".json")
        write_individual_csv(r, csv_path)
        write_individual_json(r, json_path)
    print(f"Wrote individual CSV and JSON files next to original txt files in {args.txt_root}")


if __name__ == "__main__":
    main()