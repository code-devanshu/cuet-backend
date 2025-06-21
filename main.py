# === main.py ===
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
import sys
import uvicorn
from typing import List
from scripts.compare_answers import run_comparison

app = FastAPI()

# ✅ Allow frontend from Vercel
origins = [
    "https://cuet-frontend.vercel.app",
    "http://localhost:3000",  # for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_script(script_path: str):
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"\n✅ STDOUT from {os.path.basename(script_path)}:\n{result.stdout}")
        print(f"⚠️ STDERR from {os.path.basename(script_path)}:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Script execution failed: {e}")
        raise


@app.post("/upload")
async def upload_files(
    response_pdfs: List[UploadFile] = File(...),
    html_files: List[UploadFile] = File(...)
):
    # Save PDFs
    for pdf in response_pdfs:
        pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)
        with open(pdf_path, "wb") as f:
            content = await pdf.read()
            f.write(content)

    # Save HTMLs using original name
    for html in html_files:
        html_path = os.path.join(UPLOAD_DIR, html.filename)
        with open(html_path, "wb") as f:
            content = await html.read()
            f.write(content)

    # Run scripts
    run_script("scripts/extract_pdf.py")
    run_script("scripts/extract_correct_option.py")

    summary = run_comparison()
    return {"success": True, "summary": summary}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
