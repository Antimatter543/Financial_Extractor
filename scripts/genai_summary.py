"""
genai_summary.py

This script handles:
- Reading all financial CSV tables from the `/data` directory.
- Generating a summary report using GenAI.
- Formatting the summary in Markdown.
- Saving the summary as a Markdown file and converting it to a PDF.

Functions:
- read_csv_files(directory): Reads all CSV files from a given directory and returns them as a single formatted string.
- generate_summary_report(tables): Uses GenAI to generate a financial summary based on extracted CSV data.
- save_markdown_to_pdf(markdown_text, output_path, debug): Saves the summary report as a PDF file.

Usage:
>>> from scripts.genai_summary import read_csv_files, generate_summary_report, save_markdown_to_pdf
>>> csv_text = read_csv_files()
>>> summary_text = generate_summary_report(csv_text)
>>> save_markdown_to_pdf(summary_text, "../reports/summary_report.pdf", debug=True)
"""


import glob
import google.genai.types as types
import os 
from scripts.config import get_genai_client
from markdown_pdf import MarkdownPdf, Section

def read_csv_files(directory="../data"):
    """
    Reads all CSV files from a specified directory and returns their content as a single formatted string.
    
    Args:
        directory (str): The path to the directory containing CSV files (default: "../data").
    
    Returns:
        str: A formatted string containing all CSV data, with table names as headers.
    """
    csv_files = glob.glob(f"{directory}/*.csv")  # Get all CSV files in the directory
    all_csv_text = ""  # Initialize an empty string

    for file in csv_files:
        with open(file, "r", encoding="utf-8") as f:
            all_csv_text += f"\n### {file.split('/')[-1].replace('.csv', '').title()} ###\n"
            all_csv_text += f.read()  # Append file content
            all_csv_text += "\n"

    return all_csv_text


def generate_summary_report(tables: str):
    """
    Generates a financial summary report using GenAI based on structured CSV data.

    Args:
        tables (str): The formatted CSV data as a single string.

    Returns:
        google.genai.types.GenerateContentResponse: The GenAI-generated markdown response.
    """

    client = get_genai_client()
    
    response =  client.models.generate_content(
    model="gemini-2.0-flash", 
    config=types.GenerateContentConfig(
        system_instruction="Generate a summary report in markdown that highlights the financial health of the company, given the following tables. The report should include:"
        "Key financial metrics (revenue, net income, etc.). You can display this in markdown tables, with an extra column for notes."
        "Any notable trends or observations"
        "A short narrative summary in natural language at the end."
        ),
    contents=tables,
    )

    print(f"Used {response.usage_metadata.total_token_count} tokens in total to generate summary report.")

    return response


def save_markdown_to_pdf(markdown_text, output_path="../reports/summary_report.pdf", debug=False):
    """
    Converts Markdown text to a PDF with proper formatting and saves it.

    Args:
        markdown_text (str): The markdown-formatted summary report.
        output_path (str): The file path to save the generated PDF (default: "../reports/summary_report.pdf").
        debug (bool): If True, prevents overwriting existing files by creating unique filenames.

    Returns:
        None
    """
    # Ensure the markdown starts with a Level 1 header (H1) to prevent TOC errors
    if not markdown_text.strip().startswith("# "):
        markdown_text = "# Financial Summary Report\n\n" + markdown_text  # Add default title


    # If debug mode is on, check if the file exists and create a unique filename
    if debug and os.path.exists(output_path):
        base, ext = os.path.splitext(output_path)  # Split filename and extension
        counter = 1

        # Keep incrementing filename until we find a free one
        while os.path.exists(f"{base}{counter}{ext}"):
            counter += 1

        output_path = f"{base}{counter}{ext}"


    pdf = MarkdownPdf(toc_level=3)  # Include headings up to level 3 in TOC

    # Add the markdown content as a section
    pdf.add_section(Section(markdown_text))

    # Save the PDF
    pdf.save(output_path)

    print(f"✅ Summary saved as {output_path}")