"""
path_utils.py

Utility functions for managing file paths and directory structures.
"""

import os

def get_base_name(pdf_path: str) -> str:
    """Extract a clean base name from PDF path for use in directory naming."""
    # Get just the filename without extension
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    # Clean up the name (remove spaces, make lowercase)
    return base.replace(" ", "_").lower()

def setup_directory_structure(pdf_path: str) -> tuple[str, str, str]:
    """
    Creates necessary directories for a given PDF input and returns relevant paths.
    
    Args:
        pdf_path: Path to the input PDF file
    
    Returns:
        tuple: (data_dir, report_dir, base_name) paths for the specific PDF
    """
    base_name = get_base_name(pdf_path)
    
    # Create specific directories for this PDF
    data_dir = os.path.join("data", base_name)
    report_dir = os.path.join("reports", base_name)
    
    # Ensure directories exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    return data_dir, report_dir, base_name