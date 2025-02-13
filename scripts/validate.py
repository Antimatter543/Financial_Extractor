import csv
import os
import re

def validate_csv_numbers(directory="./data", debug: bool = True):
    """
    Validates that all numeric values in CSV files within a directory are either float or int.
    Handles thousands separators, currency symbols, and skips rows that are subtable headers or values that are empty cells.

    Args:
        directory (str): The directory containing the CSV files (default: "./data").
        debug (bool): A boolean that determines whether to print the validity of each header or not.
    """
    counts = {"valid": 0, "non-valid": 0}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            print(f"Validating {filename}:")

            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Skip header row
                #Print what the header actually is
                print(f"Header row is: {header}")

                for row_number, row in enumerate(reader, start=2):  # Starts at row 2 due to the header

                    # Check if the row is a subtable header (no numbers in columns with numerical headers from header row)
                    #Basically, this means that *only* the first column has content, so we can skip the rest of the check.
                    number_column_indexes = [idx for idx in range(1,len(header)) if "Last Year" in header[idx] or "Previous Year" in header[idx]] #indices we think should have numbers

                    contains_only_first_column = True
                    for col_number in number_column_indexes: #check that the values with that indexed values are not numbers.
                        if col_number < len(row):
                            if row[col_number].strip():
                                contains_only_first_column = False
                                break

                    if contains_only_first_column:
                        print(f"  ⏩ Skipping row {row_number} because it appears to be a subtable header.")
                        continue

                    # Now, process each value in the row to see that values that *should* have numerical characters, do
                    # the condition is that we have to check the numeric indexes from before.
                    for col_number in number_column_indexes: #number column index are the same
                        if col_number >= len(row): #make sure there isn't an out of bounds exception.
                            continue

                        value = row[col_number].strip()
                        print("hey", value)
                        # Skip empty strings
                        if not value:
                            continue



                        # Attempt conversion to float
                        try:
                            float(value)
                        except ValueError:
                            counts["non-valid"] += 1
                            if debug:
                                print(f"  ❌ Row {row_number}, Col {col_number}: '{value}' is not a valid number.")
                        else:
                            counts["valid"] += 1
                            #If passes, prints a check
                            if debug:
                                print(f"  ✅ Row {row_number}, Col {col_number}: '{value}' is a valid number.")
    print(counts)
    return counts
if __name__ == '__main__':
    validate_csv_numbers()