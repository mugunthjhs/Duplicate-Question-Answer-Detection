# Question & Answer Duplicate Detection

This project is a solution for the technical assignment to parse, analyze, and identify duplicate questions from a collection of PDF and JSON files. The system processes unstructured data from a PDF and structured data from a JSON file, normalizes them into a common format, and uses fuzzy string matching to detect similarities.

## Table of Contents
1. [Approach](#approach)
2. [Tools & Libraries](#tools--libraries)
3. [Project Structure](#project-structure)
4. [Development & Execution](#development--execution)
5. [Challenges & Solutions](#challenges--solutions)
6. [Output Summary](#output-summary)

---

### Approach

The problem was tackled using a multi-stage data processing pipeline. The core idea is that to compare data from two very different sources (a visually formatted PDF and a structured JSON), they must first be transformed into a **common, standardized format**.

My approach can be broken down into three main phases:

1.  **Phase 1: PDF Preprocessing & Normalization**
    *   **Text Extraction:** The text content from `Machine_Task.pdf` was extracted using the `PyMuPDF` library.
    *   **Cleaning & Structuring:** The raw extracted text was messy, containing headers, footers, page numbers, and inconsistent line breaks. I used a combination of string manipulation and Regular Expressions (`regex`) to remove this noise and structure the content. A key step was inserting a clear separator (`-----------------------------`) between a question and its corresponding answer block, which made subsequent parsing much more reliable.
    *   **Conversion to JSON:** The cleaned text file was then parsed scriptmatically. The script identifies different question types (MCQ, Short Answer, Long Answer) and extracts the question text, options (if any), and the correct answer. Each extracted question was assigned a unique ID (e.g., `pdf_1`, `pdf_2`) and saved into a standardized `pdf_preprocessed.json` file.

2.  **Phase 2: JSON Preprocessing & Normalization**
    *   The input `Machine_Task.json` was already structured but needed minor cleaning. A script was used to remove newline characters and extra spaces from the question text.
    *   To ensure clear reporting, each question was also assigned a unique, source-specific ID (e.g., `json_1`, `json_2`) and saved into `json_preprocessed.json`.

3.  **Phase 3: Duplicate Detection**
    *   With both datasets in a clean, identical JSON format, the final script (`find_duplicate.py`) loads them.
    *   It performs a cross-comparison, comparing every question from the PDF data against every question from the JSON data.
    *   To identify duplicates, I used the `thefuzz` library, which calculates a similarity ratio between two strings. This is more robust than a simple `==` check, as it can catch minor differences in wording, punctuation, or formatting.
    *   A **similarity threshold of 95%** was set. If the similarity score between two questions met or exceeded this threshold, they were flagged as a duplicate pair.
    *   Finally, the results were compiled into a clear, human-readable report in `result_output.txt`.

---

### Tools & Libraries

-   **Language:** Python 3
-   **Core Libraries:**
    -   `PyMuPDF (fitz)`: A powerful and efficient library for extracting text and metadata from PDF documents.
    -   `thefuzz`: Used for fuzzy string matching to calculate the similarity ratio between question texts. It helps identify near-duplicates, not just exact matches.
    -   `json`: Standard library for parsing and serializing JSON data.
    -   `re`: Standard library for using regular expressions, which were critical for cleaning and parsing the text extracted from the PDF.
    -   `os`: Standard library for handling file paths.

---

### Project Structure
```
Cognitec Project/
├── requirements.txt           # Project dependencies
├── result_output.txt          # Final report of duplicate questions
│
├── input_files/
│   ├── Machine_Task.json      # Original JSON data source
│   └── Machine_Task.pdf       # Original PDF data source
│
└── source_code/
    ├── find_duplicate.py      # Main script to find duplicates and generate the report
    │
    ├── data/
    │   ├── json_preprocessed.json # Cleaned and standardized JSON from the original JSON
    │   └── pdf_preprocessed.json  # Cleaned and standardized JSON from the PDF
    │
    ├── json_preprocess/
    │   └── json_add_ques_num.py   # Script to clean and format the input JSON
    │
    └── pdf_preprocess/
        ├── pdf_parsing_to_txt.py  # Script to extract raw text from PDF and clean it
        ├── output_pdf.txt         # Intermediate cleaned text file from the PDF
        └── pdf_txt_to_json.py     # Script to parse the text file into a structured JSON
```

---

### Development & Execution

To run this project, follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd Cognitec-Project
    ```

2.  **Set up a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Scripts in Order**
    The process is a pipeline. Run the scripts in the following sequence to go from raw input to final output:

    a. **Preprocess the input JSON file:**
    ```bash
    python source_code/json_preprocess/json_add_ques_num.py
    ```

    b. **Preprocess the input PDF file (2 steps):**
    ```bash
    # Step 1: Convert PDF to a clean text file
    python source_code/pdf_preprocess/pdf_parsing_to_txt.py

    # Step 2: Convert the clean text file to structured JSON
    python source_code/pdf_preprocess/pdf_txt_to_json.py
    ```

    c. **Run the final duplicate analysis:**
    ```bash
    python source_code/find_duplicate.py
    ```

5.  **Check the Output**
    The results will be available in the `result_output.txt` file in the root directory.

---

### Challenges & Solutions

1.  **Challenge: Parsing the Unstructured PDF**
    *   **Problem:** The text extracted from the PDF was a single stream of characters containing headers, footers, page numbers, and unpredictable line breaks. Differentiating between questions, options, and answers was impossible without significant cleaning.
    *   **Solution:** I implemented a multi-pass cleaning strategy. First, `regex` was used to strip known headers and footers. Then, I analyzed the text patterns and realized that an "Answer:" line consistently followed a question block. I used this pattern to programmatically insert a `-----------` separator, which created a reliable structure in the intermediate `output_pdf.txt`. This structured text was then easily parsed into a JSON format. I initially explored `pypdf2` and `pdfplumber` but found `PyMuPDF` gave the cleanest text extraction for this specific document layout.

2.  **Challenge: Normalizing Structurally Different Answers for Accurate Comparison**
    *   **Problem:** The most significant challenge was not just minor wording differences, but the fundamental structural inconsistency between answers in the PDF and JSON files, especially for "Long Answer" types.
        *   **JSON Answers:** Were typically a clean, single paragraph of text.
        *   **PDF Answers:** Were extracted as a collection of separate lines. Long answers were often formatted as a numbered list (e.g., `1. ...`, `2. ...`), with line breaks occurring both within sentences and between list items. A direct comparison of this multi-line, numbered block against a single JSON string would result in a very low similarity score, leading to **false negatives** (failing to identify true duplicates).
    *   **Solution:** To overcome this, I designed a robust answer normalization pipeline before attempting any comparison:
        1.  **Unification:** The first step was to convert the multi-line answer block from the PDF into a **canonical single-string representation**. This was done by joining all lines of the answer block, replacing newline characters with spaces.
        2.  **Structural Cleaning:** I then used `regex` to strip out structural artifacts that were not part of the core answer text. This included removing the numbered list markers (e.g., `1.`, `2.`, etc.) and any leading/trailing whitespace from the unified string.
        3.  **Fuzzy Matching on Normalized Data:** Only after both the PDF and JSON answers were transformed into a clean, single-string format did I apply the `thefuzz` library. By calculating the similarity ratio on these heavily preprocessed strings with a **95% threshold**, the system could accurately identify semantically identical answers, irrespective of their original formatting (single paragraph vs. numbered list). This preprocessing step was critical for the success of the duplicate detection.

3.  **Challenge: Traceability of Duplicates**
    *   **Problem:** When a duplicate is found, simply stating the question text is not enough. It's crucial to know which question from which source file is the duplicate.
    *   **Solution:** During the preprocessing phases, I added a unique `questionNUM` field to every question object (e.g., `pdf_1` for the first question in the PDF, `json_1` for the first in the JSON). This makes the final report in `result_output.txt` extremely clear, as it can precisely state: "Question 'pdf_1' ... is a duplicate of Question 'json_1'".

---

### Output Summary

The analysis was executed successfully, comparing 200 questions processed from `Machine_Task.pdf` against 200 questions from `Machine_Task.json`.

-   **Total Questions Analyzed from PDF:** 200
-   **Total Questions Analyzed from JSON:** 200
-   **Similarity Threshold:** 95%
-   **Total Duplicate Pairs Found:** 200

The final report, `result_output.txt`, contains a detailed list of all identified duplicate pairs.

**Sample Output from `result_output.txt`:**
```
====================================================
               Duplicate Question Analysis Report
====================================================

Analysis Parameters:
--------------------
Source File 1: pdf_preprocessed.json
Source File 2: json_preprocessed.json
Similarity Threshold: 95%

Duplicate Pairs Found:
----------------------
Pair 1: Question 'pdf_1' (from pdf_preprocessed.json) is a duplicate of Question 'json_1' (from json_preprocessed.json).
Pair 2: Question 'pdf_2' (from pdf_preprocessed.json) is a duplicate of Question 'json_2' (from json_preprocessed.json).
Pair 3: Question 'pdf_3' (from pdf_preprocessed.json) is a duplicate of Question 'json_3' (from json_preprocessed.json).
...
...
```
This indicates a complete overlap between the questions in the two source files.
