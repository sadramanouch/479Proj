import os
import csv

def validate_csv_headers(directory, required_headers):
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    for file in csv_files:
        filepath = os.path.join(directory, file)
        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader, None)
            if headers:
                if not set(required_headers).issubset(set(headers)):
                    print(f"File '{file}' is missing required headers.")
            else:
                print(f"File '{file}' is empty.")

if __name__ == '__main__':
    directory = '.'  # Current directory
    required_headers = ['issue_id', 'issue_number', 'issue_title', 'issue_body', 'comment_body']
    validate_csv_headers(directory, required_headers)