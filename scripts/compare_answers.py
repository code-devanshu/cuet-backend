import pandas as pd
import os

def run_comparison(
    correct_file="output/correct_answers.xlsx",
    responses_file="output/response_data.xlsx",
    output_file="output/comparison.xlsx",
    uploads_dir="uploads"
):
    print("\n📊 Running comparison...")

    # === Load Excel files ===
    correct_df = pd.read_excel(correct_file, dtype=str)
    response_df = pd.read_excel(responses_file, dtype=str)

    # === Normalize all strings ===
    for col in ["Question ID", "Correct Option ID"]:
        correct_df[col] = correct_df[col].astype(str).str.strip()

    response_df["Question ID"] = response_df["Question ID"].astype(str).str.strip()
    response_df["Chosen Option"] = response_df["Chosen Option"].astype(str).str.strip()
    response_df["Status"] = response_df["Status"].astype(str).str.strip()

    for i in range(1, 5):
        response_df[f"Option {i} ID"] = response_df[f"Option {i} ID"].astype(str).str.strip()

    # === Merge ===
    merged_df = pd.merge(response_df, correct_df, on="Question ID", how="left")

    # === Debug output ===
    print(f"🧪 Columns after merge: {list(merged_df.columns)}")
    print(f"🧪 Total response questions: {len(response_df)}")
    print(f"🧪 Total correct questions: {len(correct_df)}")
    print(f"🧪 Merged rows: {len(merged_df)}")
    missing_correct_ids = merged_df['Correct Option ID'].isna().sum()
    print(f"⚠️ Unmatched Question IDs: {missing_correct_ids}")
    print("\n🧪 Sample QIDs from response file:", response_df["Question ID"].head().tolist())
    print("🧪 Sample QIDs from correct file:", correct_df["Question ID"].head().tolist())

    # === Add Category Column (from Source File) ===
    if "Source File" in merged_df.columns:
        merged_df["Category"] = merged_df["Source File"].str.replace(".html", "", regex=False)
    else:
        merged_df["Category"] = "Unknown"

    print(f"🧪 Unique Categories Found: {merged_df['Category'].unique()}")

    # === Find Correct Option Number ===
    def find_correct_option(row):
        for i in range(1, 5):
            if row[f"Option {i} ID"] == row["Correct Option ID"]:
                return str(i)
        return None

    merged_df["Correct Option"] = merged_df.apply(find_correct_option, axis=1)

    # === Determine correctness ===
    def determine_correctness(row):
        status = row["Status"].lower()
        chosen = row["Chosen Option"]
        correct = row["Correct Option"]
        if "not answered" in status or "--" in chosen or chosen == "":
            return "NA"
        return "True" if chosen == correct else "False"

    merged_df["Is Correct"] = merged_df.apply(determine_correctness, axis=1)

    # === Save full comparison for debugging ===
    merged_df.to_excel(output_file, index=False)
    print(f"\n✅ Comparison saved to: {output_file}")

    # === Summary per category ===
    summary = []
    print("\n📊 Summary by Category:")

    grouped = merged_df.groupby("Category")

    for category, group in grouped:
        total = len(group)
        attempted = group[group["Is Correct"] != "NA"].shape[0]
        correct = group[group["Is Correct"] == "True"].shape[0]
        incorrect = group[group["Is Correct"] == "False"].shape[0]
        not_answered = total - attempted

        summary.append({
            "Category": category,
            "Total": total,
            "Attempted": attempted,
            "Correct": correct,
            "Incorrect": incorrect,
            "Not Answered": not_answered,
            "Score": correct * 5 - incorrect  # 📘 CUET scoring logic: +5 for correct, -1 for incorrect
        })

        print(f"\n📚 {category}")
        print(f"   🧮 Total        : {total}")
        print(f"   ✏️ Attempted    : {attempted}")
        print(f"   ✅ Correct      : {correct}")
        print(f"   ❌ Incorrect    : {incorrect}")
        print(f"   🚫 Not Answered : {not_answered}")
        print(f"   🧾 Score        : {correct * 5 - incorrect}")

    # === Extract student info ===
    student_info = {}
    if "Name" in correct_df.columns and "Application No" in correct_df.columns:
        student_info = {
            "Name": correct_df["Name"].iloc[0],
            "Application No": correct_df["Application No"].iloc[0]
        }

    # === Cleanup uploaded and temp files ===
    print("\n🧹 Cleaning up uploaded and intermediate files...")
    for file in os.listdir(uploads_dir):
        os.remove(os.path.join(uploads_dir, file))

    for file in [correct_file, responses_file, output_file]:
        if os.path.exists(file):
            os.remove(file)

    print("🧼 Cleanup complete.")

    return {
        "student": student_info,
        "summary": summary
    }

# === Run standalone ===
if __name__ == "__main__":
    result = run_comparison()
    print("\n📤 Final Summary JSON:")
    print(result)
