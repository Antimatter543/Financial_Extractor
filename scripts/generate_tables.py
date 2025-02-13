"""
generate_tables.py

This script handles:
- Sending segmented financial tables to GenAI for structured extraction.
- Extracting financial data in JSON format and converting it to CSV.
- Saving structured CSVs to the `/data` directory.

Functions:
- gemini_financial_extraction(tabular_text, model): Calls GenAI to extract structured financial tables.
- clean_json_response(text): Ensures valid JSON extraction by stripping unnecessary formatting.
- save_csv(table_name, csv_content, directory): Saves structured CSV data properly.
- process_and_save_tables(segmented_tables): Processes all tables, extracts financial data, and saves CSVs.

Usage:
>>> from scripts.generate_tables import process_and_save_tables
>>> process_and_save_tables(segmented_tables)
"""



from dotenv import load_dotenv
import os
import google.genai.types as types
import json
import re

from scripts.config import get_genai_client


## Using free tier so 15RPM w/ 1 million context window
def gemini_financial_extraction(tabular_text: str, model: str = "gemini-2.0-flash"):
    """
    Extracts financial data from raw table text using GenAI and returns structured JSON.

    Args:
        tabular_text (str): The financial table text.
        model (str): The AI model to use (default: "gemini-2.0-flash").

    Returns:
        google.genai.types.GenerateContentResponse: AI-generated structured financial data in JSON format.
    """
    client = get_genai_client()
    
    response =  client.models.generate_content(
    model=model, 
    config=types.GenerateContentConfig(
        system_instruction="Extract financial information from the following text and return it in a JSON FORMAT with two primary keys:\n 1. `table_name`: (The name of the financial table (e.g 'Income Statement')).\n 2. `csv_data`:The extracted financial data in valid CSV format. .\n Ignore notes if they exist and replace any '-' sections with a 0. DO NOT ADD OR REMOVE NEGATIVE SIGNS THAT DO NOT EXIST.",
        ),
    contents=tabular_text
    )

    return response


def clean_json_response(text):
    """
    Extracts valid JSON content from AI-generated text by removing markdown code blocks and unnecessary formatting.

    Args:
        text (str): AI response containing JSON.

    Returns:
        str: Extracted valid JSON string, or None if no valid JSON found.
    """
    # Remove ```json ... ``` wrapping
    text = re.sub(r"```json\s*", "", text)  # Remove opening block
    text = re.sub(r"\s*```$", "", text)  # Remove closing block
    
    # Extract only the valid JSON part
    match = re.search(r"\{.*\}", text, re.DOTALL)  # Match JSON structure
    if match:
        return match.group(0)  # Return extracted JSON
    return None


def save_csv(table_name: str, csv_content: str, directory: str):
    """Saves extracted CSV data to a file in the specified directory."""
    safe_table_name = table_name.replace(" ", "_").lower()
    file_path = os.path.join(directory, f"{safe_table_name}.csv")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(csv_content)

    print(f"✅ Saved: {file_path}")

def process_and_save_tables(segmented_tables, output_dir: str):
    """
    Processes segmented tables and saves CSVs to the specified output directory.
    
    Args:
        segmented_tables (list): List of table text segments to process
        output_dir (str): Directory where CSV files should be saved
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, table_text in enumerate(segmented_tables):
        response = gemini_financial_extraction(table_text)
        json_data = clean_json_response(response.text)

        if not json_data:
            print(f"❌ No valid JSON found for table {idx+1}")
            continue

        try:
            parsed_data = json.loads(json_data)
            table_name = parsed_data.get("table_name", f"financial_table_{idx+1}")
            csv_content = parsed_data.get("csv_data", "")
            save_csv(table_name, csv_content, output_dir)
        except json.JSONDecodeError:
            print(f"❌ Failed to parse JSON for table {idx+1}")
            continue