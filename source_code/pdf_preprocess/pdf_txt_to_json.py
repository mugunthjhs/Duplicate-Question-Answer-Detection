import re
import json

# File paths
txt_path = "source_code\pdf_preprocess\output_pdf.txt"
json_path = "source_code\data\pdf_preprocessed.json"

# Regex patterns for parsing
numbered_q_pattern = re.compile(r"^(\d+)\.\s+(.*)")
keyword_pattern = re.compile(r"^Keywords\s*[:：]", re.IGNORECASE)
separator_pattern = re.compile(r"^[-]{3,}$")
mcq_option_pattern = re.compile(r"^[A-Z]\)\s+(.*)")

# Section headers from the text
MCQ_MARKER = "MULTIPLE CHOICE QUESTIONS"
SHORT_MARKER = "ANSWER THE FOLLOWING QUESTIONS WITH TWO OR THREE SENTENCES"
LONG_MARKER = "ANSWER THE FOLLOWING QUESTIONS BRIEFLY"

# Parse a section based on its type
def parse_section(lines, qtype, question_counter_start):
    questions = []
    i = 0
    question_counter = question_counter_start

    while i < len(lines):
        match = numbered_q_pattern.match(lines[i])
        if not match:
            i += 1
            continue

        current_q_num = int(match.group(1))
        q_lines = []
        options = []
        a_lines = []
        keyword_lines = []

        # Collect question lines (and options for MCQ)
        while i < len(lines) and not separator_pattern.match(lines[i]):
            line = lines[i].strip()
            if qtype == "MCQ":
                option_match = mcq_option_pattern.match(line)
                if option_match:
                    options.append(option_match.group(1).strip())
                else:
                    q_lines.append(line)
            else:
                q_lines.append(line)
            i += 1

        if i < len(lines) and separator_pattern.match(lines[i]):
            i += 1  # Skip separator

        # Collect answer lines and keywords
        while i < len(lines):
            line = lines[i].strip()
            next_q_match = numbered_q_pattern.match(line)
            if (next_q_match and int(next_q_match.group(1)) > current_q_num) or line in [MCQ_MARKER, SHORT_MARKER, LONG_MARKER]:
                break

            if keyword_pattern.match(line):
                keyword_content = line[line.find(":") + 1:].strip()
                if keyword_content:
                    keyword_lines.append(keyword_content)
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    next_q_in_kw_match = numbered_q_pattern.match(next_line)
                    if (next_q_in_kw_match and int(next_q_in_kw_match.group(1)) > current_q_num) or next_line in [MCQ_MARKER, SHORT_MARKER, LONG_MARKER]:
                        break
                    keyword_lines.append(next_line)
                    i += 1
                break
            else:
                a_lines.append(line)
                i += 1

        # Format question and answer
        question_text = " ".join(q_lines)
        question_text = re.sub(r"^\d+\.\s*", "", question_text, count=1).strip()
        correct_answer_raw = "\n".join(a_lines).strip()
        keywords_flat = ", ".join(keyword_lines)
        keywords = [k.strip() for k in keywords_flat.split(",") if k.strip()]

        # Build final JSON structure
        question_obj = {
            "questionNUM": f"pdf_{question_counter}",
            "questionType": qtype,
            "question": question_text,
        }

        if qtype == "MCQ":
            question_obj["options"] = options
            cleaned_answer = re.sub(r"^Answer:\s*", "", correct_answer_raw, flags=re.IGNORECASE)
            cleaned_answer = re.sub(r"^[A-Z]\)\s*", "", cleaned_answer).strip()
            question_obj["correctAnswer"] = cleaned_answer
        else:
            cleaned_answer = re.sub(r"^Answer:\s*", "", correct_answer_raw, flags=re.IGNORECASE).strip()
            question_obj["correctAnswer"] = cleaned_answer
            question_obj["answerKeyword"] = keywords

        questions.append(question_obj)
        question_counter += 1

    return questions, question_counter

# Read the cleaned text file
with open(txt_path, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# Helper to find section start index
def find_section_index(marker, line_list):
    for idx, line in enumerate(line_list):
        if marker in line:
            return idx
    return -1

# Identify section ranges
mcq_start = find_section_index(MCQ_MARKER, lines)
short_start = find_section_index(SHORT_MARKER, lines)
long_start = find_section_index(LONG_MARKER, lines)

end_mcq = short_start if short_start != -1 else (long_start if long_start != -1 else len(lines))
end_short = long_start if long_start != -1 else len(lines)

# Slice sections
mcq_lines = lines[mcq_start + 1 : end_mcq] if mcq_start != -1 else []
short_lines = lines[short_start + 1 : end_short] if short_start != -1 else []
long_lines = lines[long_start + 1 :] if long_start != -1 else []

# Parse all sections
question_counter = 1
mcqs, question_counter = parse_section(mcq_lines, "MCQ", question_counter)
shorts, question_counter = parse_section(short_lines, "Short Answer", question_counter)
longs, question_counter = parse_section(long_lines, "Long Answer", question_counter)

all_questions = mcqs + shorts + longs

# Export final JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_questions, f, indent=4, ensure_ascii=False)

print(f"✅ Exported {len(all_questions)} questions to {json_path}")
