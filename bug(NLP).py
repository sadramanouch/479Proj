import os
import csv
import re
import nltk
import string
import warnings
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Suppress warnings
warnings.filterwarnings('ignore')

# Download NLTK data files (if not already installed)
nltk.download('stopwords')
nltk.download('wordnet')

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

# Function to preprocess text
def preprocess_text(text):
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove code snippets
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize
    tokens = text.split()
    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    processed_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    # Rejoin tokens
    processed_text = ' '.join(processed_tokens)
    return processed_text

# Function to extract optimized keywords using clustering
def extract_optimized_keywords(issues, num_clusters=20, top_n_keywords=10):
    # Combine relevant fields for text analysis
    issue_texts = []
    for issue in issues:
        combined_text = ' '.join([
            issue.get('issue_title', ''),
            issue.get('issue_body', ''),
            issue.get('comment_body', '')
        ])
        processed_text = preprocess_text(combined_text)
        issue_texts.append(processed_text)

    print("Vectorizing text data...")
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, max_features=10000)
    X = vectorizer.fit_transform(issue_texts)

    print("Clustering issues...")
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)

    # Get top keywords for each cluster
    print("Extracting top keywords for each cluster...")
    terms = vectorizer.get_feature_names_out()
    cluster_keywords = {}
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    for i in range(num_clusters):
        cluster_terms = [terms[ind] for ind in order_centroids[i, :top_n_keywords]]
        cluster_keywords[f"Cluster {i+1}"] = cluster_terms

    # Assign issues to clusters
    issue_clusters = kmeans.labels_

    return cluster_keywords, issue_clusters

# Function to create new bug categories based on clusters
def create_new_bug_categories(cluster_keywords):
    new_bug_categories = {}
    for cluster_name, keywords in cluster_keywords.items():
        category_name = f"Category {cluster_name}"
        new_bug_categories[category_name] = keywords
    return new_bug_categories

# Function to classify issues using the new keywords
def classify_issues_with_new_keywords(issues, issue_clusters, cluster_keywords):
    classified_issues = []
    classification_counts = defaultdict(int)

    for idx, issue in enumerate(issues):
        cluster_id = issue_clusters[idx]
        cluster_name = f"Cluster {cluster_id+1}"
        category_name = f"Category {cluster_name}"
        classification_counts[category_name] += 1

        classified_issues.append({
            'issue_id': issue.get('issue_id', ''),
            'issue_number': issue.get('issue_number', ''),
            'issue_title': issue.get('issue_title', ''),
            'issue_body': issue.get('issue_body', ''),
            'categories': category_name
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
    total_classified = sum(classification_counts.values())
    with open(output_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Bug Category', 'Count'])
        for category, count in classification_counts.items():
            writer.writerow([category, count])
        writer.writerow(['Total Classified Issues', total_classified])
    print(f'Classification summary exported to {output_filename}')
    print(f"Total Classified Issues: {total_classified}")

if __name__ == '__main__':
    directory = '.'  # Current directory
    print("Loading CSV files...")
    issues = load_csv_files(directory)
    print(f"Total issues loaded: {len(issues)}")

    if not issues:
        print("No issues to process.")
    else:
        print("Extracting optimized keywords...")
        num_clusters = 30  # You can adjust the number of clusters
        top_n_keywords = 15  # Number of top keywords to extract per cluster
        cluster_keywords, issue_clusters = extract_optimized_keywords(issues, num_clusters, top_n_keywords)

        # Create new bug categories based on clusters
        new_bug_categories = create_new_bug_categories(cluster_keywords)

        # Optionally, you can print the new bug categories and their keywords
        for category, keywords in new_bug_categories.items():
            print(f"{category}: {', '.join(keywords)}")

        # Classify issues using the new keywords
        classification_counts, classified_issues = classify_issues_with_new_keywords(
            issues, issue_clusters, cluster_keywords
        )

        # Write classified issues and summary to CSV files
        write_classified_issues_to_csv(classified_issues)
        write_classification_summary_to_csv(classification_counts)

        print("Classification process completed.")
