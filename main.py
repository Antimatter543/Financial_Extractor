"""
main.py

This script orchestrates the full pipeline for extracting, processing, and summarizing financial statements.

Workflow:
1️⃣ Extracts text from a financial statement PDF.
2️⃣ Cleans and splits the text into structured financial tables.
3️⃣ Uses GenAI to extract financial data from tables into CSV files.
4️⃣ Generates a summary report based on extracted financial metrics.

Usage:
Run the script in the terminal:
>>> python main.py
"""

"""
main.py

This script orchestrates the full pipeline for extracting, processing, and summarizing financial statements.

Workflow:
1️⃣ Extracts text from a financial statement PDF.
2️⃣ Cleans and splits the text into structured financial tables.
3️⃣ Uses GenAI to extract financial data from tables into CSV files.
4️⃣ Generates a summary report based on extracted financial metrics.

Usage:
Run the script in the terminal:
>>> python main.py
"""

import os
from scripts.preprocess_data import extract_full_text, clean_text, split_into_sections_regex
from scripts.generate_tables import process_and_save_tables
from scripts.genai_summary import read_csv_files, generate_summary_report, save_markdown_to_pdf

# Define file paths
PDF_PATH = "./pdf_inputs/fwc_sample_financial_statement 1.pdf"
CSV_DIR = "./data"
REPORT_PATH = "./reports/summary_report.pdf"

def main():
    """Main function to run the financial data extraction and reporting pipeline."""

    print(" Step 1: Extracting text from PDF...")
    raw_text = extract_full_text(PDF_PATH)
    print("✅ Extraction complete!")

    print(" Step 2: Cleaning extracted text...")
    cleaned_text = clean_text(raw_text)
    print("✅ Cleaning complete!")

    print(" Step 3: Splitting into sections...")
    segmented_tables = split_into_sections_regex(cleaned_text)
    print(f"✅ Split into {len(segmented_tables)} sections.")

    # Generates data when needed.
    # print(" Step 4: Processing tables with GenAI and saving CSVs...")
    # process_and_save_tables(segmented_tables)
    # print("✅ All tables processed and saved as CSVs!")

    print(" Step 5: Generating financial summary report...")
    csv_text = read_csv_files(CSV_DIR)
    report_response = generate_summary_report(csv_text)

    print(" Step 6: Saving summary report as PDF...")
    save_markdown_to_pdf(report_response.text, output_path=REPORT_PATH, debug=True)
    print("✅ Financial summary saved!")

if __name__ == "__main__":
    main()
