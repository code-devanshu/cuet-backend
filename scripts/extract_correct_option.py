from bs4 import BeautifulSoup
import pandas as pd
import glob
import os

UPLOADS_DIR = "uploads"
OUTPUT_FILE = "output/correct_answers.xlsx"

def extract_qid_and_correct_option_from_html(file_path):
    print(f"\n📄 Processing file: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    qids = soup.find_all("span", id=lambda x: x and "lbl_QuestionNo" in x)
    corrects = soup.find_all("span", id=lambda x: x and "lbl_RAnswer" in x)

    print(f"   ➕ Found {len(qids)} Question IDs")
    print(f"   ✅ Found {len(corrects)} Correct Option IDs")

    if len(qids) != len(corrects):
        print(f"⚠️ Mismatch in {os.path.basename(file_path)}: {len(qids)} QIDs vs {len(corrects)} Answers")

    data = []
    source_file = os.path.basename(file_path)

    for i in range(min(len(qids), len(corrects))):
        qid = qids[i].text.strip()
        correct_id = corrects[i].text.strip()

        data.append({
            "Question ID": qid,
            "Correct Option ID": correct_id,
            "Source File": source_file
        })

        print(f"   🟡 QID: {qid}, Correct Option: {correct_id}, File: {source_file}")

    print(f"✅ Extracted {len(data)} Q&A pairs from {source_file}")
    return data

def process_all_html_files():
    html_files = glob.glob(os.path.join(UPLOADS_DIR, "*.html"))
    print(f"\n🔎 Found {len(html_files)} HTML files in {UPLOADS_DIR}/")

    all_data = []
    for file in html_files:
        data = extract_qid_and_correct_option_from_html(file)
        all_data.extend(data)

    if not all_data:
        print("⚠️ No question-answer pairs found.")
        return

    df = pd.DataFrame(all_data)

    # Remove any rows with missing Source File, QID or Correct Option ID
    df.dropna(subset=["Question ID", "Correct Option ID", "Source File"], inplace=True)

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n📁 Excel saved: {OUTPUT_FILE}")

# === Run it ===
if __name__ == "__main__":
    process_all_html_files()
