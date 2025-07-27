import fitz  # PyMuPDF
import re

pdf_path = "input_files\Machine_Task.pdf"
txt_path = "source_code\pdf_preprocess\output_pdf.txt"

# --- Constants ---

blocks_to_remove = [
    "CBSE – GRADE – 10 \nSCIENCE \nCHAPTER - 9 LIGHT: REFLECTION AND REFRACTION",
    "CHAPTER 9 \nLIGHT: REFLECTION AND REFRACTION",
    "--- PAGE BREAK ---\nCBSE – GRADE – 10 \nSCIENCE \nCHAPTER - 9 LIGHT: REFLECTION AND REFRACTION"
]

special_sentences = {
    "MULTIPLE CHOICE QUESTIONS",
    "ANSWER THE FOLLOWING QUESTIONS WITH TWO OR THREE SENTENCES",
    "ANSWER THE FOLLOWING QUESTIONS BRIEFLY"
}

remove_patterns = [
    r"^\d{1,3}\s*$",
    r"^\s*[•\-\–\—\*]+\s*$"
]
combined_noise_pattern = re.compile("|".join(remove_patterns), re.IGNORECASE)

main_question_pattern = re.compile(r"^(\d{1,3})\.\s+")
subpoint_pattern = re.compile(r"^\d+\.\s+")

# --- Utility Functions ---

def remove_exact_blocks(text, blocks):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    for block in blocks:
        text = text.replace(block, "")
    return text

def merge_split_lines(lines):
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if (
            line == "ANSWER THE FOLLOWING QUESTIONS WITH TWO OR THREE"
            and i + 1 < len(lines)
            and lines[i + 1].strip() == "SENTENCES"
        ):
            merged.append("ANSWER THE FOLLOWING QUESTIONS WITH TWO OR THREE SENTENCES")
            i += 2
        else:
            merged.append(line)
            i += 1
    return merged

def clean_and_structure_lines(lines):
    cleaned = []
    inside_answer = False
    skip_explanation = False

    for line in lines:
        stripped = line.strip()
        if not stripped or combined_noise_pattern.match(stripped):
            continue

        if stripped.startswith("Explanation:"):
            skip_explanation = True
            continue
        if skip_explanation:
            if stripped.startswith(tuple("ABCD")) or main_question_pattern.match(stripped) or stripped.startswith("Answer:"):
                skip_explanation = False
            else:
                continue

        if stripped.startswith("Answer:"):
            cleaned.append("-----------------------------") 
            cleaned.append(stripped)
            inside_answer = True
            continue

        if stripped in special_sentences:
            cleaned.append("")
            cleaned.append(stripped)
            cleaned.append("")
            continue

        if main_question_pattern.match(stripped) and not subpoint_pattern.match(stripped):
            inside_answer = False
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            cleaned.append(stripped)
            continue

        if inside_answer and subpoint_pattern.match(stripped):
            cleaned.append(stripped)
        else:
            cleaned.append(stripped)

    return cleaned

def insert_spacing_before_questions(lines):
    final_lines = []
    last_question_number = 0

    for i, line in enumerate(lines):
        match = main_question_pattern.match(line)
        if match:
            current_q = int(match.group(1))
            if current_q == last_question_number + 1:
                if final_lines and final_lines[-1] != "":
                    final_lines.append("")
                last_question_number = current_q
        final_lines.append(line)

    return final_lines

# --- Main Execution ---

def process_pdf_to_clean_text(pdf_path, txt_path):
    doc = fitz.open(pdf_path)
    all_cleaned_lines = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        raw_text = page.get_text()

        text = remove_exact_blocks(raw_text, blocks_to_remove)
        lines = text.split('\n')
        merged_lines = merge_split_lines(lines)
        structured_lines = clean_and_structure_lines(merged_lines)

        all_cleaned_lines.extend(structured_lines)

    doc.close()

    final_lines = insert_spacing_before_questions(all_cleaned_lines)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(final_lines) + '\n')

    print(f"✅ Cleaned text saved to {txt_path}")

# Run it
process_pdf_to_clean_text(pdf_path, txt_path)
