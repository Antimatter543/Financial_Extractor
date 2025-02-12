"""
preprocess_data.py

This script handles:
- Extracting raw text from financial PDFs.
- Cleaning and structuring financial data.
- Splitting the document into separate financial tables.

Functions:
- extract_full_text(pdf_path): Extracts text from a given PDF file.
- clean_text(raw_text): Cleans extracted text (removes headers, footers, and formatting issues).
- split_into_sections_regex(cleaned_text): Splits cleaned text into individual financial tables.

Usage:
>>> from scripts.preprocess_data import extract_full_text, clean_text, split_into_sections_regex
>>> raw_text = extract_full_text("../pdf_inputs/sample.pdf")
>>> cleaned_text = clean_text(raw_text)
>>> segmented_tables = split_into_sections_regex(cleaned_text)
"""

import re
import pdfplumber # pdfplumber IS SLOWER BTW by a fair bit, but it also does give much nicer formatting.

def extract_full_text(pdf_path):
    """
    Extracts full text from a given PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"  # Append text from each page and add a newline
    return full_text

def clean_text(raw_text):
    """
    Cleans extracted text by removing headers, footers, and unnecessary formatting.

    Args:
        raw_text (str): The extracted raw text from the PDF.

    Returns:
        str: Cleaned text with unwanted parts removed.
    """
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        if not re.search(r"FS 023|Fact Sheet FS 023|p\.\s*\d+", line, re.IGNORECASE): # Improved condition
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    # Get rid of end of document text
    cleaned_text = re.sub(r'© Commonwealth of Australia.*?legal advice\.', '', cleaned_text, flags=re.DOTALL) # DOTALL allows the match to continue across multiple lines
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text).strip()
    return cleaned_text


def split_into_sections_regex(cleaned_text):
    """
    Splits cleaned financial statement text into separate financial tables using regex.

    Args:
        cleaned_text (str): The cleaned financial statement text.

    Returns:
        list: A list of text sections corresponding to financial tables.
    """
    
    # Regex pattern to match variations like:
    # - "The above statement should be read in conjunction with the notes."
    # - "Above statement must be considered along with the notes."
    # - "above statement should be read carefully with the notes."
    stop_pattern = r"(?:The\s*)?above statement .*? with the notes\.?"

    # Split using regex
    sections = re.split(stop_pattern, cleaned_text, flags=re.IGNORECASE)

    # Remove extra whitespace and filter empty sections
    sections = [sec.strip() for sec in sections if sec.strip()]

    if len(sections) != 4:
        print(f"Warning: Expected 4 sections, but found {len(sections)}")

    return sections


if __name__ == "__main__":
    pdf_path = "../pdf_inputs/fwc_sample_financial_statement 1.pdf"
    full_text = extract_full_text(pdf_path)
    print(full_text)





