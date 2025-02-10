
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


pdf_path = "fwc_sample_financial_statement 1.pdf" 

# Using pdfplumber
print("\n=== Using pdfplumber ===")
try:
    text_pdfplumber = read_pdf_pdfplumber(pdf_path)
    print(text_pdfplumber)  # Print first 500 characters
except Exception as e:
    print(f"pdfplumber error: {e}")



pages = extract_pdf_by_pages(pdf_path)

# Now you can access any page individually
for page_num, text in pages.items():
    print(f"\n=== {page_num} ===\n")
    print(text)
    print("\n" + "="*50 + "\n")  # separator between pages