import fitz  # PyMuPDF
import re
import pandas as pd
import os
import glob

UPLOADS_DIR = "uploads"
OUTPUT_FILE = "output/response_data.xlsx"

def extract_text_from_pdf(pdf_path):
    print(f"📄 Extracting text from: {pdf_path}")
    doc = fitz.open(pdf_path)
    all_text = []

    for i, page in enumerate(doc):
        print(f"   ↳ Page {i + 1}/{len(doc)}")
        all_text.append(page.get_text())

    return "\n".join(all_text)

def extract_question_blocks(full_text):
    pattern = re.compile(
        r"Question ID\s*[:：]?\s*(\d+)\s*"
        r"Option 1 ID\s*[:：]?\s*(\d+)\s*"
        r"Option 2 ID\s*[:：]?\s*(\d+)\s*"
        r"Option 3 ID\s*[:：]?\s*(\d+)\s*"
        r"Option 4 ID\s*[:：]?\s*(\d+)\s*"
        r"Status\s*[:：]?\s*(.*?)\s*"
        r"Chosen Option\s*[:：]?\s*(\d+|--)",
        re.IGNORECASE | re.DOTALL
    )

    matches = pattern.findall(full_text)
    data = []

    for match in matches:
        data.append({
            "Question ID": match[0],
            "Option 1 ID": match[1],
            "Option 2 ID": match[2],
            "Option 3 ID": match[3],
            "Option 4 ID": match[4],
            "Status": match[5].strip().replace("\n", " "),
            "Chosen Option": match[6]
        })

    return data

def process_all_pdfs():
    all_questions = []
    pdf_paths = glob.glob(os.path.join(UPLOADS_DIR, "*.pdf"))

    if not pdf_paths:
        print("⚠️ No PDF files found in uploads/")
        return

    for path in pdf_paths:
        text = extract_text_from_pdf(path)
        questions = extract_question_blocks(text)
        all_questions.extend(questions)
        print(f"✅ {len(questions)} questions extracted from {os.path.basename(path)}\n")

    print(f"📊 Total questions combined: {len(all_questions)}")

    df = pd.DataFrame(all_questions)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"📁 Excel saved as: {OUTPUT_FILE}")

# === Run when executed directly ===
if __name__ == "__main__":
    process_all_pdfs()
