import os
import csv
import re
from langdetect import detect, DetectorFactory
from collections import defaultdict

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

# Define relevant keywords for TypeScript bugs
RELEVANT_KEYWORDS = [
    'typescript', 'tsconfig', '.ts', 'type error', 'interface', 'compiler', 'tsc',
    'type declaration', 'type inference', 'type assertion', 'interface error',
    'compiler options', 'type system', 'type mismatch', 'type coercion', 'generic type',
    'module', 'import', 'export', 'decorator', 'enum', 'namespace', 'tuple', 'type guard',
    'async', 'promise', 'observable', 'typescript-eslint', 'declaration file', 'ambient declaration',
    'strict typing', 'any type', 'unknown type', 'never type', 'union type', 'intersection type',
    'structural typing', 'duck typing', 'typescript compiler api', 'transpile', 'emit', 'typescript language service',
    'decorator metadata', 'mapped type', 'conditional type', 'distributive conditional types', 'keyof',
    'indexed access type', 'symbol', 'iterator', 'iterable', 'generator', 'typescript version',
    'lib.d.ts', 'declaration merging', 'module augmentation', 'triple-slash directive', 'jsx', 'tslint',
    'abstract class', 'type parameter', 'infer', 'literal type', 'readonly', 'unique symbol', 'typescript error ts'
]

# Function to check if text is in English
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False

# Function to determine if the issue is relevant
def is_relevant(text):
    text = text.lower()
    for keyword in RELEVANT_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return True
    return False

# Function to clean a single CSV file
def clean_csv_file(input_filepath, output_filepath):
    cleaned_rows = []
    total_rows = 0
    skipped_non_english = 0
    skipped_irrelevant = 0

    with open(input_filepath, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if not fieldnames:
            print(f"Skipping file '{input_filepath}': No header row found.")
            return

        required_fields = {'issue_id', 'issue_number', 'issue_title', 'issue_body', 'comment_body'}
        if not required_fields.issubset(set(fieldnames)):
            print(f"Skipping file '{input_filepath}': Missing required fields.")
            return

        for row in reader:
            total_rows += 1
            issue_title = row.get('issue_title', '')
            issue_body = row.get('issue_body', '')
            comment_body = row.get('comment_body', '')

            combined_text = ' '.join([issue_title, issue_body, comment_body])

            # Remove entries that are not in English
            if not is_english(combined_text):
                skipped_non_english += 1
                continue

            # Remove entries that are not relevant
            if not is_relevant(combined_text):
                skipped_irrelevant += 1
                continue

            cleaned_rows.append(row)

    # Write cleaned data to a new CSV file
    if cleaned_rows:
        with open(output_filepath, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        print(f"Processed '{input_filepath}':")
        print(f"  Total issues: {total_rows}")
        print(f"  Non-English issues removed: {skipped_non_english}")
        print(f"  Irrelevant issues removed: {skipped_irrelevant}")
        print(f"  Cleaned issues saved to '{output_filepath}'\n")
    else:
        print(f"No relevant English issues found in '{input_filepath}'.\n")

# Function to process all CSV files in a directory
def clean_all_csv_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    csv_files = [file for file in os.listdir(input_directory) if file.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the specified directory.")
        return

    for filename in csv_files:
        input_filepath = os.path.join(input_directory, filename)
        output_filepath = os.path.join(output_directory, filename)

        clean_csv_file(input_filepath, output_filepath)

# Example usage
if __name__ == '__main__':
    input_dir = 'input_csv_files'    # Directory containing your 11 CSV files
    output_dir = 'cleaned_csv_files' # Directory to save cleaned CSV files

    print("Starting the cleaning process...\n")
    clean_all_csv_files(input_dir, output_dir)
    print("Cleaning process completed.")
