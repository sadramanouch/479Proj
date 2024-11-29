import os
import csv
import re
from collections import defaultdict
from langdetect import detect, DetectorFactory
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

# Ensure consistent results from langdetect
DetectorFactory.seed = 0

# Download NLTK resources (only need to run once)
nltk.download('wordnet')
nltk.download('omw-1.4')  # For WordNet to work properly

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Define bug categories and associated keywords
BUG_CATEGORIES = {
    "Invalid Function Parameters": [
        "invalid parameter", "wrong argument", "type mismatch", "incorrect parameter", "argument error",
        "parameter undefined", "unexpected type", "null value", "undefined variable", "missing argument",
        "extra argument", "optional parameter missing", "default parameter error"
    ],
    "Type System Errors": [
        "type error", "typescript error", "interface not found", "missing type", "type declaration",
        "type incompatibility", "type assertion", "generic type", "type inference", "union type error",
        "intersection type error", "conditional type error", "type narrowing", "type widening",
        "inferred type mismatch", "type coercion error", "structural typing", "duck typing"
    ],
    "Compilation Errors": [
        "compilation error", "tsc error", "typescript compiler", "compiling issue",
        "compile time error", "type checking error", "syntax error", "transpilation error",
        "compiler warning", "build time error", "transpile error"
    ],
    "Runtime Errors": [
        "runtime error", "unhandled exception", "undefined is not a function", "null reference",
        "stack overflow", "out of memory", "unexpected runtime behavior", "runtime type error",
        "runtime exception", "memory leak", "performance degradation at runtime"
    ],
    "Configuration Issues": [
        "tsconfig", "typescript configuration", "compiler options", "config error",
        "configuration file error", "tsconfig.json", "build configuration", "typescript settings",
        "compiler flag error", "path alias configuration"
    ],
    "Integration Issues": [
        "integration error", "framework integration", "react typescript error",
        "angular typescript issue", "vue typescript integration", "eslint typescript",
        "webpack typescript", "babel typescript integration", "jest typescript error",
        "redux typescript issue", "next.js typescript error"
    ],
    "Syntax Errors": [
        "syntax error", "missing semicolon", "unexpected token", "invalid syntax",
        "parsing error", "bracket mismatch", "colon expected", "comma expected",
        "semicolon expected", "parenthesis mismatch", "curly brace error", "arrow function syntax error"
    ],
    "Dependency Issues": [
        "dependency error", "package not found", "npm types error", "yarn error",
        "typescript dependency", "missing dependency", "dependency conflict",
        "typescript types missing", "module not found", "peer dependency error",
        "package version mismatch", "typings error"
    ],
    "Performance Issues": [
        "performance issue", "slow build", "memory leak", "high cpu usage",
        "performance degradation", "optimization needed", "latency issue",
        "render performance", "load time issue", "slow response time", "resource-intensive",
        "performance bottleneck", "lagging interface", "slow rendering", "inefficient algorithm",
        "unoptimized loop", "excessive api calls", "unnecessary re-renders", "performance profiling needed"
    ],
    "Tooling Errors": [
        "linting error", "eslint error", "prettier error", "editor issue",
        "ide integration issue", "typescript language server error", "vscode typescript error",
        "code formatter error", "debugger issue", "plugin error", "tslint error"
    ],
    "Testing Issues": [
        "test failure", "unit test error", "integration test issue", "jest typescript error",
        "test coverage issue", "test setup error", "mocking error", "test environment issue",
        "snapshot test error", "test assertion failure", "test flakiness", "e2e test issue",
        "testing error", "test runner error", "test suite failure", "assertion failure"
    ],
    # Add more categories as needed
}

# Function to check if text is in English
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False

# Preprocessing function to clean text
def preprocess_text(text):
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`.*?`', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()

# Modified function to expand keywords without nltk.word_tokenize
def expand_keywords(keywords):
    expanded_keywords = set()
    for keyword in keywords:
        # Tokenize and lemmatize the keyword using simple split
        words = keyword.split()
        for word in words:
            lemmatized_word = lemmatizer.lemmatize(word.lower())
            expanded_keywords.add(lemmatized_word)
            # Add synonyms
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    expanded_keywords.add(lemma.name().lower())
    return expanded_keywords

# Expand keywords for each category
EXPANDED_BUG_CATEGORIES = {}
for category, keywords in BUG_CATEGORIES.items():
    EXPANDED_BUG_CATEGORIES[category] = expand_keywords(keywords)

# Function to classify a single issue into one category
def classify_issue(issue_text):
    # Tokenize and lemmatize the issue text using simple split
    issue_tokens = set(issue_text.split())
    issue_lemmas = set(lemmatizer.lemmatize(token.lower()) for token in issue_tokens)

    # Calculate scores for each category
    category_scores = {}
    for category, keywords in EXPANDED_BUG_CATEGORIES.items():
        matches = issue_lemmas & keywords
        if matches:
            category_scores[category] = len(matches)
    
    if category_scores:
        # Assign the issue to the category with the highest score
        # In case of a tie, the category that comes first in BUG_CATEGORIES is chosen
        max_score = max(category_scores.values())
        best_categories = [cat for cat, score in category_scores.items() if score == max_score]
        for category in BUG_CATEGORIES.keys():
            if category in best_categories:
                return category
    else:
        return None

# Function to load all CSV files in the given directory
def load_csv_files(directory):
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    all_issues = []
    for file in csv_files:
        filepath = os.path.join(directory, file)
        print(f"Processing file: {filepath}")
        try:
            with open(filepath, mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                # Check if all required headers are present
                required_headers = {'issue_id', 'issue_number', 'issue_title', 'issue_body', 'comment_body'}
                if not required_headers.issubset(reader.fieldnames):
                    print(f"Skipping file '{file}': Missing required headers.")
                    continue
                for row in reader:
                    all_issues.append(row)
        except Exception as e:
            print(f"Error processing file '{file}': {e}")
    return all_issues

# Function to process and classify issues
def process_and_classify_issues(issues):
    classification_counts = defaultdict(int)
    classified_issues = []

    for issue in issues:
        # Combine and preprocess text
        combined_text = ' '.join([
            issue.get('issue_title', ''),
            issue.get('issue_body', ''),
            issue.get('comment_body', '')
        ])
        combined_text = preprocess_text(combined_text)

        # Remove entries that are not in English
        if not is_english(combined_text):
            continue

        # Classify issue
        category = classify_issue(combined_text)

        if category:
            classification_counts[category] += 1
            classified_issues.append({
                'issue_id': issue.get('issue_id', ''),
                'issue_number': issue.get('issue_number', ''),
                'issue_title': issue.get('issue_title', ''),
                'issue_body': issue.get('issue_body', ''),
                'categories': category
            })
        else:
            classified_issues.append({
                'issue_id': issue.get('issue_id', ''),
                'issue_number': issue.get('issue_number', ''),
                'issue_title': issue.get('issue_title', ''),
                'issue_body': issue.get('issue_body', ''),
                'categories': 'Uncategorized'
            })

    return classification_counts, classified_issues

# Function to write classified issues to a new CSV
def write_classified_issues_to_csv(classified_issues, output_filename='classified_issues.csv'):
    fieldnames = ['issue_id', 'issue_number', 'issue_title', 'issue_body', 'categories']
    with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for issue in classified_issues:
            writer.writerow(issue)
    print(f'Classified issues exported to {output_filename}')

# Function to write classification summary to a CSV
def write_classification_summary_to_csv(classification_counts, output_filename='classification_summary.csv'):
    with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Bug Category', 'Count'])
        for category, count in classification_counts.items():
            writer.writerow([category, count])
    print(f'Classification summary exported to {output_filename}')

# Main execution block
if __name__ == '__main__':
    directory = 'cleaned_csv_files'  # Directory containing your cleaned CSV files
    print("Loading CSV files...")
    issues = load_csv_files(directory)
    print(f"Total issues loaded: {len(issues)}")

    if not issues:
        print("No issues to process.")
    else:
        print("Processing and classifying issues...")
        classification_counts, classified_issues = process_and_classify_issues(issues)

        print("Writing classified issues to CSV...")
        write_classified_issues_to_csv(classified_issues)

        print("Writing classification summary to CSV...")
        write_classification_summary_to_csv(classification_counts)

        print("Classification process completed.")
