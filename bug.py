import os
import csv
import re
from collections import defaultdict

# Define bug categories and associated keywords
BUG_CATEGORIES = {
    "Invalid Function Parameters": [
        "invalid parameter", "wrong argument", "type mismatch", "incorrect parameter", "argument error",
        "parameter undefined", "unexpected type", "null value", "undefined variable", "missing argument",
        "extra argument", "optional parameter missing", "default parameter error"
    ],
    "DOM-related Issues": [
        "dom", "document object model", "element not found", "selector error", "event binding",
        "render issue", "update dom", "dom manipulation", "element not updating", "dom traversal",
        "event listener error", "dom rendering", "element visibility", "dom update failure"
    ],
    "Type System Errors": [
        "type error", "typescript error", "interface not found", "missing type", "type declaration",
        "type incompatibility", "type assertion", "generic type", "type inference", "union type error",
        "intersection type error", "conditional type error", "type narrowing", "type widening",
        "inferred type mismatch", "type coercion error"
    ],
    "Interface Issues": [
        "interface", "implement interface", "extends interface", "interface mismatch", "interface error",
        "interface definition", "interface property", "interface method", "abstract class error",
        "interface inheritance", "interface implementation", "interface property mismatch"
    ],
    "Other TypeScript-specific Bugs": [
        "decorator error", "namespace conflict", "module resolution", "enum issue",
        "type alias", "tuple error", "type guard", "type narrowing", "async typing",
        "namespace error", "decorator syntax", "module import error", "decorator usage",
        "enum type error", "type alias conflict", "tuple type mismatch", "async function error"
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
        "performance issue", "slow build", "memory leak", "high CPU usage",
        "performance degradation", "optimization needed", "latency issue",
        "render performance", "load time issue", "slow response time", "resource-intensive"
    ],
    "Build Errors": [
        "build error", "build failed", "build process issue", "build script error",
        "continuous integration build error", "build pipeline failure", "webpack build error",
        "rollup build issue", "parcel build error", "vite build failure"
    ],
    "Tooling Errors": [
        "linting error", "eslint error", "prettier error", "editor issue",
        "ide integration issue", "typescript language server error", "vscode typescript error",
        "code formatter error", "debugger issue", "plugin error", "tslint error"
    ],
    "Code Quality Issues": [
        "code smell", "maintainability issue", "refactor needed", "technical debt",
        "code duplication", "poor code structure", "complexity issue", "code readability",
        "spaghetti code", "code inconsistency", "anti-pattern", "tight coupling"
    ],
    "Testing Issues": [
        "test failure", "unit test error", "integration test issue", "jest typescript error",
        "test coverage issue", "test setup error", "mocking error", "test environment issue",
        "snapshot test error", "test assertion failure", "test flakiness", "e2e test issue"
    ],
    "Security Vulnerabilities": [
        "security vulnerability", "XSS", "CSRF", "injection attack", "vulnerability",
        "secure coding", "security flaw", "authentication error", "authorization error",
        "data exposure", "buffer overflow", "sensitive data leak", "insecure dependency"
    ],
    "Async/Await Issues": [
        "async error", "await issue", "promise rejection", "async function error",
        "deadlock", "async stack trace", "unhandled promise", "async race condition",
        "async callback error", "async flow issue", "async exception"
    ],
    "Generics Issues": [
        "generics error", "generic type issue", "type parameter error",
        "generic constraint", "generic function error", "generic interface error",
        "generic class issue", "generic type mismatch", "generic overload error"
    ],
    "Module Resolution Errors": [
        "module not found", "module resolution error", "import error",
        "export error", "module alias issue", "path resolution error",
        "relative import error", "absolute import issue", "module boundary error",
        "module circular dependency", "dynamic import error"
    ],
    "Error Handling Issues": [
        "error handling", "try catch issue", "error boundary error", "unhandled exception",
        "error propagation", "error logging issue", "error message unclear",
        "error type mismatch"
    ],
    "Version Compatibility Issues": [
        "version compatibility", "typescript version issue", "library version mismatch",
        "dependency version conflict", "typescript upgrade issue", "framework version error"
    ],
    "Logging and Monitoring Issues": [
        "logging error", "monitoring issue", "log message error", "logging configuration",
        "monitoring tool integration", "log level issue", "log format error"
    ]
}


# Function to load all CSV files in the current directory
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

# Function to classify a single issue based on keywords
def classify_issue(issue_text):
    issue_text = issue_text.lower()
    categories_found = set()
    for category, keywords in BUG_CATEGORIES.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', issue_text):
                categories_found.add(category)
                break  # Avoid duplicate category entries for multiple keywords
    return list(categories_found)

# Function to process issues and classify them
def process_and_classify_issues(issues):
    classification_counts = defaultdict(int)
    classified_issues = []

    for issue in issues:
        # Combine relevant fields for keyword searching
        combined_text = ' '.join([
            issue.get('issue_title', ''),
            issue.get('issue_body', ''),
            issue.get('comment_body', '')
        ]).lower()

        categories = classify_issue(combined_text)
        if categories:
            for category in categories:
                classification_counts[category] += 1
            classified_issues.append({
                'issue_id': issue.get('issue_id', ''),
                'issue_number': issue.get('issue_number', ''),
                'issue_title': issue.get('issue_title', ''),
                'issue_body': issue.get('issue_body', ''),
                'categories': '; '.join(categories)
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

if __name__ == '__main__':
    directory = '.'  # Current directory
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
