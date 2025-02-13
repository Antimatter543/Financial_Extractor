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
from scripts.validate import validate_csv_numbers
from scripts.genai_summary import read_csv_files, generate_summary_report, save_markdown_to_pdf
from scripts.path_utils import setup_directory_structure

def process_financial_statement(pdf_path: str):
    """Process a single financial statement PDF."""
    
    # Setup directory structure for this PDF
    data_dir, report_dir, base_name = setup_directory_structure(pdf_path)
    
    print(f"\n🔄 Processing {os.path.basename(pdf_path)}...")
    
    print(" Step 1: Extracting text from PDF...")
    raw_text = extract_full_text(pdf_path)
    print("✅ Extraction complete!")

    print(" Step 2: Cleaning extracted text...")
    cleaned_text = clean_text(raw_text)
    print("✅ Cleaning complete!")

    print(" Step 3: Splitting into sections...")
    segmented_tables = split_into_sections_regex(cleaned_text)
    print(f"✅ Split into {len(segmented_tables)} sections.")

    print(" Step 4: Processing tables with GenAI and saving CSVs...")
    process_and_save_tables(segmented_tables, output_dir=data_dir)
    print("✅ All tables processed and saved as CSVs!")
    validate_csv_numbers(data_dir, debug=True)

    print(" Step 5: Generating financial summary report...")
    csv_text = read_csv_files(data_dir)
    report_response = generate_summary_report(csv_text)

    # Create report filename based on input PDF name
    report_path = os.path.join(report_dir, f"{base_name}_summary.pdf")
    
    print(" Step 6: Saving summary report as PDF...")
    save_markdown_to_pdf(report_response.text, output_path=report_path, debug=True)
    print(f"✅ Financial summary saved to {report_path}!")

def main():
    """Main function to process all PDFs in the input directory."""
    pdf_dir = "./pdf_inputs"
    
    # Process all PDFs in the input directory
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            process_financial_statement(pdf_path)

if __name__ == "__main__":
    main()