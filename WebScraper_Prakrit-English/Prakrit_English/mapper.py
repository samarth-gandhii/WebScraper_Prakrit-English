# import re
# import json
# import csv

# def process_datasets():
#     print("Reading files...")
    
#     with open('eng.md', 'r', encoding='utf-8') as f:
#         eng_content = f.read()
        
#     with open('prakrit.md', 'r', encoding='utf-8') as f:
#         prakrit_content = f.read()

#     # 1. Parse the English Text
#     # Looks for a starting number, the poem text, and the bracketed verse number at the end
#     eng_pattern = re.compile(r'(?:^|\n)\d+\s*\n(.*?)(?:\[(\d+)\])', re.DOTALL)
#     eng_matches = eng_pattern.findall(eng_content)
    
#     english_dict = {}
#     for text, num in eng_matches:
#         clean_text = text.strip()
#         if clean_text:
#             english_dict[int(num)] = clean_text

#     print(f"Extracted {len(english_dict)} English translations.")

#     # 2. Parse the Prakrit Text
#     prakrit_dict = {}
#     devanagari_to_arabic = str.maketrans('०१२३४५६७८९', '0123456789')
    
#     # Loop through every line in the Prakrit document
#     for line in prakrit_content.split('\n'):
#         line = line.strip()
#         if not line:
#             continue
            
#         # Regex to catch the verse text and the number after the word 'गाहा' (Gaha)
#         match = re.search(r'^(.*?)/\s*गाहा([०-९\d]+)', line)
#         if match:
#             text = match.group(1).strip()
#             num_str = match.group(2)
#             # Convert Devanagari numerals to standard integers
#             num = int(num_str.translate(devanagari_to_arabic))
            
#             # If the verse already exists (like the 1st half), append this 2nd half to it
#             if num in prakrit_dict:
#                 prakrit_dict[num] += " " + text
#             else:
#                 prakrit_dict[num] = text

#     print(f"Extracted {len(prakrit_dict)} Prakrit verses.")

#     # 3. Merge the Data
#     dataset = []
#     # Loop through the parsed English dictionary and find its Prakrit match
#     for verse_num in sorted(english_dict.keys()):
#         if verse_num in prakrit_dict:
#             dataset.append({
#                 "verse_number": verse_num,
#                 "prakrit": prakrit_dict[verse_num],
#                 "english": english_dict[verse_num]
#             })

#     print(f"Successfully mapped {len(dataset)} pairs!")

#     # 4. Export to JSON
#     with open('sattasai_dataset.json', 'w', encoding='utf-8') as f:
#         json.dump(dataset, f, ensure_ascii=False, indent=4)
#     print("Saved -> sattasai_dataset.json")

#     # 5. Export to CSV
#     with open('sattasai_dataset.csv', 'w', encoding='utf-8', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=["verse_number", "prakrit", "english"])
#         writer.writeheader()
#         writer.writerows(dataset)
#     print("Saved -> sattasai_dataset.csv")

# if __name__ == "__main__":
#     process_datasets()

import re
import json
import csv

def process_datasets():
    print("Reading files...")
    
    try:
        with open('eng.md', 'r', encoding='utf-8') as f:
            eng_content = f.read()
        with open('prakrit.md', 'r', encoding='utf-8') as f:
            prakrit_content = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure eng.md and prakrit.md are in the same folder.")
        return

    # --- 1. PARSE ENGLISH TEXT ---
    print("Parsing English translations...")
    # Find all bracketed verse numbers (e.g., [583])
    matches = list(re.finditer(r'\[(\d+)\]', eng_content))
    
    english_dict = {}
    last_pos = 0
    
    for match in matches:
        verse_num = int(match.group(1))
        
        # Extract the raw text block between the previous bracket and this one
        chunk = eng_content[last_pos:match.start()].strip()
        last_pos = match.end()
        
        # Split the chunk into lines
        lines = chunk.split('\n')
        poem_lines = []
        
        # Read bottom-up to capture only the poem!
        # This stops reading the moment it hits an isolated digit (the poem number or page number)
        for line in reversed(lines):
            stripped = line.strip()
            if stripped.isdigit():
                break  
            if stripped:  # Skip empty lines
                poem_lines.append(stripped)
        
        # Reverse the lines back to normal order and combine them
        poem_lines.reverse()
        clean_text = '\n'.join(poem_lines)
        clean_text = re.sub(r'\s*\d+$', '', clean_text)
        clean_text = re.sub(r'\d+', '', clean_text)
        
        if clean_text:
            english_dict[verse_num] = clean_text

    print(f"Extracted {len(english_dict)} clean English translations.")

    # --- 2. PARSE PRAKRIT TEXT ---
    print("Parsing Prakrit verses...")
    prakrit_dict = {}
    devanagari_to_arabic = str.maketrans('०१२३४५६७८९', '0123456789')
    
    for line in prakrit_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Matches format: "पसुवइणो रोसारुण... / गाहा१कख"
        match = re.search(r'^(.*?)\s*/+\s*गाहा\s*([०-९\d]+)', line)
        if match:
            text = match.group(1).strip()
            num_str = match.group(2)
            
            # Convert Devanagari numerals to standard integers
            num = int(num_str.translate(devanagari_to_arabic))
            
            # Stitch parts of the verse together if it spans multiple lines (ka-kha, ga-gha)
            if num in prakrit_dict:
                prakrit_dict[num] += " " + text
            else:
                prakrit_dict[num] = text

    print(f"Extracted {len(prakrit_dict)} Prakrit verses.")

    # --- 3. MERGE DATA ---
    dataset = []
    for verse_num in sorted(english_dict.keys()):
        if verse_num in prakrit_dict:
            dataset.append({
                "verse_number": verse_num,
                "prakrit": prakrit_dict[verse_num],
                "english": english_dict[verse_num]
            })

    print(f"Successfully mapped {len(dataset)} perfect pairs!")

    # --- 4. EXPORT ---
    if dataset:
        with open('sattasai_dataset.json', 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)
        print("Saved cleanly to -> sattasai_dataset.json")

        with open('sattasai_dataset.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["verse_number", "prakrit", "english"])
            writer.writeheader()
            writer.writerows(dataset)
        print("Saved cleanly to -> sattasai_dataset.csv")

if __name__ == "__main__":
    process_datasets()