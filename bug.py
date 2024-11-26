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
        "render performance", "load time issue", "slow response time", "resource-intensive",
        "performance bottleneck", "lagging interface", "slow rendering", "inefficient algorithm",
        "unoptimized loop", "excessive API calls", "unnecessary re-renders", "performance profiling needed"
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
        "snapshot test error", "test assertion failure", "test flakiness", "e2e test issue",
        "testing error", "jest issue", "mocha error", "jasmine problem", "test runner error",
        "test suite failure", "test coverage issue", "assertion failure", "end-to-end testing problem"
    ],
    "Security Vulnerabilities": [
        "security vulnerability", "xss", "csrf", "injection attack", "vulnerability",
        "secure coding", "security flaw", "authentication error", "authorization error",
        "data exposure", "buffer overflow", "sensitive data leak", "insecure dependency",
        "encryption error", "decryption issue", "hashing error", "ssl/tls problem",
        "certificate error", "cryptographic algorithm issue", "key management problem"
    ],
    "Async/Await Issues": [
        "async error", "await issue", "promise rejection", "async function error",
        "deadlock", "async stack trace", "unhandled promise", "async race condition",
        "async callback error", "async flow issue", "async exception",
        "concurrency error", "race condition", "thread safety issue", "mutex error",
        "event loop error", "async iterator error", "promise chain problem"
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
        "error type mismatch", "exception handling error", "custom error class issue",
        "error notification failure", "error tracking tool integration", "error message formatting error"
    ],
    "Version Compatibility Issues": [
        "version compatibility", "typescript version issue", "library version mismatch",
        "dependency version conflict", "typescript upgrade issue", "framework version error",
        "migration error", "upgrade issue", "breaking changes", "deprecated feature",
        "backward compatibility error", "api changes"
    ],
    "Logging and Monitoring Issues": [
        "logging error", "monitoring issue", "log message error", "logging configuration",
        "monitoring tool integration", "log level issue", "log format error",
        "logging configuration issue", "log rotation problem", "centralized logging problem",
        "logging verbosity issue"
    ],
    "IDE and Editor Issues": [
        "ide error", "visual studio code issue", "intellisense not working", "syntax highlighting problem",
        "code completion error", "editor crash", "debugging issue", "code navigation error",
        "refactoring tool error", "editor plugin issue", "autocomplete failure"
    ],
    "React and JSX Issues": [
        "react error", "jsx syntax error", "component type error", "props typing issue",
        "state management error", "hooks type error", "functional component issue",
        "class component typing error", "react native error", "react router issue",
        "redux integration error", "context api error"
    ],
    "Migration and Upgrade Issues": [
        "migration error", "upgrade issue", "breaking changes", "deprecated feature",
        "typescript upgrade problem", "version incompatibility", "migration guide needed",
        "legacy code issue", "backward compatibility error", "api changes"
    ],
    "State Management Issues": [
        "state error", "state management problem", "redux typing error", "mobx issue",
        "context state error", "store type error", "state update issue",
        "unidirectional data flow error", "observable state problem", "reducer function error"
    ],
    "Type Definition File Issues": [
        "type definition error", ".d.ts file error", "ambient declaration issue",
        "declaration merging problem", "definitelytyped error", "missing types",
        "ambient module error", "external module declaration issue", "global type error",
        "namespace declaration problem"
    ],
    "Operator and Expression Issues": [
        "operator overloading error", "spread operator issue", "rest parameter error",
        "destructuring assignment problem", "optional chaining error", "nullish coalescing issue",
        "template literal error", "tagged template literal problem", "conditional expression error",
        "logical operator issue"
    ],
    "Data Binding and Template Issues": [
        "data binding error", "template syntax issue", "interpolation problem",
        "one-way binding error", "two-way binding issue", "event binding problem",
        "template parse error", "directive error", "binding context issue",
        "template variable error"
    ],
    "Localization and Internationalization Issues": [
        "localization error", "internationalization issue", "i18n problem", "l10n error",
        "locale data error", "currency format issue", "date format error", "translation missing",
        "unicode error", "encoding problem", "language pack missing", "right-to-left language support",
        "multilingual support issue", "character set problem"
    ],
    "Build Tool and Process Issues": [
        "webpack error", "babel transpilation issue", "gulp task error", "grunt problem",
        "rollup bundling error", "build script failure", "minification issue", "source map error",
        "hot module replacement problem", "build optimization error"
    ],
    "Polyfills and Compatibility Issues": [
        "polyfill error", "compatibility issue", "es5/es6 target error", "core-js problem",
        "promise polyfill missing", "symbol polyfill issue", "browser compatibility error",
        "transpiler configuration error", "legacy browser support problem", "feature detection error"
    ],
    "Interoperability Issues": [
        "interoperability error", "interop issue", "javascript integration problem",
        "commonjs module error", "es module issue", "default export problem",
        "named export error", "require vs. import issue", "module wrapper error",
        "mixing module systems problem"
    ],
    "Third-Party Library Integration Issues": [
        "library integration error", "third-party module issue", "plugin conflict",
        "package compatibility problem", "sdk error", "api integration issue",
        "external service error", "dependency injection problem", "library typing error",
        "module augmentation issue"
    ],
    "Database and ORM Issues": [
        "database connection error", "orm typing issue", "sequelize error", "typeorm problem",
        "prisma issue", "query builder error", "model definition problem", "data retrieval error",
        "transaction error", "database schema mismatch"
    ],
    "Network and API Communication Issues": [
        "http request error", "axios issue", "fetch api problem", "rest api error",
        "graphql query issue", "websocket error", "cors error", "api response handling problem",
        "network timeout error", "authentication token issue"
    ],
    "File System and Path Issues": [
        "file system error", "path resolution problem", "fs module error", "file read/write issue",
        "directory not found", "file permission error", "symbolic link problem", "path normalization issue",
        "file watcher error", "glob pattern error"
    ],
    "Time and Date Handling Issues": [
        "date parsing error", "time zone issue", "date formatting problem", "moment.js error",
        "date-fns issue", "timestamp error", "daylight saving time problem", "duration calculation error",
        "countdown timer issue", "chronograph error"
    ],
    "Asynchronous Programming Issues": [
        "concurrency error", "race condition", "deadlock", "thread safety issue", "mutex error",
        "asynchronous callback problem", "event loop error", "scheduling issue", "async iterator error",
        "promise chain problem"
    ],
    "Memory and Resource Management Issues": [
        "memory leak", "resource exhaustion", "garbage collection issue", "memory allocation error",
        "stack overflow", "heap overflow", "memory corruption", "buffer overflow",
        "resource cleanup error", "file handle leak"
    ],
    "Cryptography and Security Issues": [
        "encryption error", "decryption issue", "hashing error", "ssl/tls problem",
        "certificate error", "cryptographic algorithm issue", "secure token error",
        "key management problem", "authentication failure", "security protocol error"
    ],
    "Styling and CSS Integration Issues": [
        "css module error", "styled-components issue", "emotion styling error", "sass/scss problem",
        "less error", "style loader issue", "css-in-js error", "stylelint problem",
        "responsive design issue", "theme provider error"
    ],
    "GraphQL Integration Issues": [
        "graphql error", "apollo client issue", "schema stitching problem", "query syntax error",
        "mutation error", "resolver function issue", "graphql type error", "subscription error",
        "graphql code generation problem", "caching issue"
    ],
    "Mobile Development Issues": [
        "react native error", "expo issue", "mobile build error", "native module problem",
        "platform-specific code error", "android issue", "ios error", "device compatibility problem",
        "touch event error", "mobile ui issue"
    ],
    "WebAssembly and Low-Level Issues": [
        "webassembly error", "wasm module issue", "binary compilation error", "memory access error",
        "low-level api problem", "performance optimization error", "rust integration issue",
        "assemblyscript error", "simd instruction problem", "threading issue in wasm"
    ],
    "Cross-Browser Compatibility Issues": [
        "cross-browser issue", "browser-specific error", "internet explorer problem", "safari error",
        "chrome bug", "firefox issue", "mobile browser problem", "css prefix error",
        "html5 feature support issue", "browser api compatibility error"
    ],
    "Package Management Issues": [
        "npm error", "yarn issue", "package.json problem", "dependency resolution error",
        "package lockfile issue", "npm script error", "versioning problem",
        "peer dependency conflict", "package installation error", "scoped package issue"
    ],
    "Cloud Services and Deployment Issues": [
        "aws error", "azure issue", "google cloud problem", "serverless function error",
        "deployment script issue", "ci/cd pipeline error", "docker container problem",
        "kubernetes deployment error", "environment variable issue", "cloud service integration error"
    ],
    "Accessibility and Usability Issues": [
        "accessibility error", "aria attribute issue", "screen reader problem",
        "keyboard navigation error", "focus management issue", "contrast ratio error",
        "tab order problem", "accessible form error", "wcag compliance issue",
        "user experience problem"
    ],
    "Documentation and Comment Issues": [
        "missing documentation", "outdated comment", "incorrect jsdoc annotation",
        "api documentation error", "code readability issue", "documentation generation problem",
        "typedoc error", "annotation syntax error", "inline comment issue",
        "misleading documentation"
    ],
    "Error Message Clarity Issues": [
        "unclear error message", "ambiguous warning", "misleading exception",
        "insufficient error details", "error message formatting issue", "stack trace problem",
        "user-friendly error needed", "logging verbosity issue", "error code confusion",
        "debug information missing"
    ],
    "Animation and Transition Issues": [
        "animation error", "transition timing issue", "css animation problem",
        "frame drop", "performance lag in animation", "keyframe error",
        "animation library issue", "gesture handling problem", "animation interruption",
        "transition effect error"
    ],
    "Dependency Injection Issues": [
        "dependency injection error", "inversion of control problem", "service provider issue",
        "singleton pattern error", "constructor injection problem", "di container error",
        "provider resolution issue", "lifecycle management error", "scoped dependency problem",
        "module injection error"
    ],
    "Command-Line Interface (CLI) Tool Issues": [
        "cli error", "command parsing issue", "argument handling error", "option flag problem",
        "user input error", "output formatting issue", "terminal compatibility problem",
        "stdin/stdout error", "script execution error", "shell command issue"
    ],
    "Streaming and Buffering Issues": [
        "stream error", "buffering problem", "data flow issue", "backpressure error",
        "stream piping problem", "real-time data error", "multimedia streaming issue",
        "audio/video sync error", "chunk processing error", "network latency issue"
    ],
    "Serialization and Deserialization Issues": [
        "json parse error", "serialization problem", "deserialization error",
        "circular reference issue", "data contract error", "xml parsing error",
        "binary serialization issue", "data transformation error", "object mapping problem",
        "schema validation error"
    ],
    "Build Output and Artifact Issues": [
        "output file error", "artifact generation problem", "distribution package issue",
        "code minification error", "source map problem", "asset bundling error",
        "file hashing issue", "cdn deployment error", "output directory problem",
        "versioning in build artifacts"
    ],
    "Event Handling Issues": [
        "event listener error", "callback issue", "event emitter problem", "custom event error",
        "event bubbling issue", "event delegation problem", "asynchronous event handling error",
        "race condition in events", "dom event issue", "synthetic event error"
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
