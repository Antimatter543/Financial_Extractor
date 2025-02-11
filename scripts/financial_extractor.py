
# Method 2: Using pdfplumber (better at maintaining formatting)
import pdfplumber

def read_pdf_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_pdf_by_pages(pdf_path):
    # Dictionary to store text from each page
    pages_text = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        # Get text from each page
        for page_num, page in enumerate(pdf.pages, 1):
            pages_text[f"page_{page_num}"] = page.extract_text()
    
    return pages_text


pdf_path = "./pdf_inputs/fwc_sample_financial_statement 1.pdf" 

# Using pdfplumber
print("\n=== Using pdfplumber ===")
try:
    text_pdfplumber = read_pdf_pdfplumber(pdf_path)
    print(text_pdfplumber)  # Print first 500 characters
except Exception as e:
    print(f"pdfplumber error: {e}")



pages = extract_pdf_by_pages(pdf_path)

# # Now you can access any page individually
# for page_num, text in pages.items():
#     print(f"\n=== {page_num} ===\n")
#     print(text)
#     print("\n" + "="*50 + "\n")  # separator between pages

print('pages', pages)


import re

def clean_text(text):
    # Remove page headers and footers
    text = re.sub(r'FS 023 Sample financial statement.*?\| p\. \d+', '', text)
    text = re.sub(r'The above statement should be read in conjunction with the notes\.', '', text)
    text = re.sub(r'© Commonwealth of Australia.*?legal advice\.', '', text, flags=re.DOTALL)
    return text.strip()

# Clean each page
cleaned_pages = {page_num: clean_text(text) for page_num, text in pages.items()}

# Look at cleaned text for first page
# print(cleaned_pages['page_5'])

import pandas as pd

def extract_income_statement(cleaned_pages):
    # Combine pages 1 and 2 which contain the income statement
    text = cleaned_pages['page_5']
    
    lines = []
    for line in text.split('\n'):
        # Look for lines with amounts
        match = re.search(r'([A-Za-z\s–]+)\s+(?:\d[A-Z])?\s*([\d,]+|-)\s+([\d,]+|-)', line)
        if match:
            item = match.group(1).strip()
            last_year = match.group(2).replace(',', '')
            prev_year = match.group(3).replace(',', '')
            
            # Convert to numeric, handling '-' as 0
            last_year = 0 if last_year == '-' else float(last_year)
            prev_year = 0 if prev_year == '-' else float(prev_year)
            
            lines.append({
                'Item': item,
                'Last Year': last_year,
                'Previous Year': prev_year
            })
    
    df = pd.DataFrame(lines)
    return df

income_statement_df = extract_income_statement(cleaned_pages)
print("Income Statement:")
print(income_statement_df)  # Jupyter will show this as a nice table