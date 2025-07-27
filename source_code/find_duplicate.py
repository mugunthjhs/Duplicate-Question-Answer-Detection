import json
import os
import re
from thefuzz import fuzz

# --- Configuration ---
PDF_SOURCE_FILE = r'source_code\data\pdf_preprocessed.json'         # Preprocessed PDF questions
JSON_SOURCE_FILE = r'source_code\data\json_preprocessed.json'       # Preprocessed original JSON questions
OUTPUT_FILE = r'result_output.txt'
SIMILARITY_THRESHOLD = 95  # Minimum similarity score to consider as duplicate

# Load and clean question list from a file
def load_and_process_questions(filepath):
    processed_questions = []
    filename = os.path.basename(filepath)
    print(f"--- Processing file: {filename} ---")

    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'.")
        return []
        
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # Support flexible JSON structure
            question_list = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), None)
            
            if not question_list:
                print(f"Error: Could not find a list of questions inside {filename}.")
                return []
            
            print(f"  > Found {len(question_list)} total items in the list.")
            
            for i, raw_q in enumerate(question_list):
                if not isinstance(raw_q, dict):
                    print(f"  > Warning: Skipping item #{i+1} as it is not a dictionary.")
                    continue

                question_text = raw_q.get('question')
                if not isinstance(question_text, str) or not question_text.strip():
                    q_id = raw_q.get('questionNUM', f'NO_ID_at_item_#{i+1}')
                    print(f"  > Warning: Skipping item with ID '{q_id}' due to missing 'question' text.")
                    continue
                
                # Normalize text to lowercase for comparison
                processed_questions.append({
                    'id': raw_q.get('questionNUM', f'UNKNOWN_ID_at_item_#{i+1}'),
                    'question_text': question_text.lower()
                })

            print(f"  > Successfully processed {len(processed_questions)} questions from {filename}.\n")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filename}.")
            return []
            
    return processed_questions

# Compare questions from two sources to find duplicates
def find_cross_file_duplicates(pdf_questions, json_questions, threshold):
    found_pairs = []
    print(f"--- Comparing {len(pdf_questions)} questions against {len(json_questions)} questions ---\n")
    for pdf_q in pdf_questions:
        for json_q in json_questions:
            if fuzz.ratio(pdf_q['question_text'], json_q['question_text']) >= threshold:
                found_pairs.append((pdf_q['id'], json_q['id']))
    return found_pairs

# Write formatted duplicate report to file
def write_results_to_file(pairs, pdf_count, json_count, output_path):
    pdf_filename = os.path.basename(PDF_SOURCE_FILE)
    json_filename = os.path.basename(JSON_SOURCE_FILE)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("====================================================\n")
        f.write("        Duplicate Question Analysis Report\n")
        f.write("====================================================\n\n")

        f.write("Analysis Parameters:\n")
        f.write("--------------------\n")
        f.write(f"Source File 1: {pdf_filename}\n")
        f.write(f"Source File 2: {json_filename}\n")
        f.write(f"Similarity Threshold: {SIMILARITY_THRESHOLD}%\n\n")

        f.write("Duplicate Pairs Found:\n")
        f.write("----------------------\n")
        if not pairs:
            f.write("No duplicate pairs were identified between the two files.\n\n")
        else:
            for i, (pdf_id, json_id) in enumerate(pairs, 1):
                f.write(f"Pair {i}: Question '{pdf_id}' (from {pdf_filename}) is a duplicate of Question '{json_id}' (from {json_filename}).\n")
            f.write("\n")

        f.write("Analysis Summary:\n")
        f.write("-----------------\n")
        f.write(f"Questions Analyzed from {pdf_filename}: {pdf_count}\n")
        f.write(f"Questions Analyzed from {json_filename}: {json_count}\n")
        f.write(f"Total Duplicate Pairs Identified: {len(pairs)}\n\n")
        
        f.write("====================================================\n")
    
    print(f"Analysis complete. Report generated at: {output_path}")


def main():
    pdf_questions = load_and_process_questions(PDF_SOURCE_FILE)
    json_questions = load_and_process_questions(JSON_SOURCE_FILE)
    
    if not pdf_questions or not json_questions:
        print("Execution halted. One or both files failed to provide questions.")
        return

    duplicate_pairs = find_cross_file_duplicates(pdf_questions, json_questions, SIMILARITY_THRESHOLD)
    write_results_to_file(duplicate_pairs, len(pdf_questions), len(json_questions), OUTPUT_FILE)

if __name__ == "__main__":
    main()
