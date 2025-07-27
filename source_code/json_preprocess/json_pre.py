import json

# File paths
input_path = "input_files\\Machine_Task.json"
output_path = "source_code\\data\\json_preprocessed.json"

# Load the original JSON
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

new_questions = []

# Process each question
for i, item in enumerate(data["questions"], start=1):
    reordered = {"questionNUM": f"json_{i}"}

    # Clean and normalize question text
    if "question" in item:
        item["question"] = item["question"].replace("\n", "")
        while "  " in item["question"]:
            item["question"] = item["question"].replace("  ", " ")

    reordered.update(item)
    new_questions.append(reordered)

# Update the question list
data["questions"] = new_questions

# Save cleaned JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
