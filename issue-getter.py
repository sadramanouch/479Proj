import requests
import csv
import time
import re
import sys

TOKEN = sys.argv[1]
REPO = sys.argv[2]

HEADERS = {"Authorization": f"token {TOKEN}"}

def get_repo_info_from_url(repo_url):
    pattern = r'https?://github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, repo_url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return owner, repo
    else:
        print("Invalid GitHub repository URL.")
        exit(1)

def get_issues(owner, repo):
    issues = []
    page = 1
    per_page = 100  
    for i in range(0, 40):
        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        params = {'state': 'all', 'per_page': per_page, 'page': page}
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 403:
            print("Rate limit exceeded. Please wait and try again later.")
            break
        elif response.status_code != 200:
            print(f'Error fetching issues: {response.status_code}')
            break
        page_data = response.json()
        if not page_data:
            break
        issues.extend(page_data)
        print(f"Fetched page {page} of issues.")
        page += 1
        time.sleep(1)  
    return issues

def get_comments_for_issue(owner, repo, issue_number):
    comments = []
    page = 1
    per_page = 100
    while True:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
        params = {'per_page': per_page, 'page': page}
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 403:
            print("Rate limit exceeded while fetching comments. Please wait and try again later.")
            break
        elif response.status_code != 200:
            print(f'Error fetching comments for issue {issue_number}: {response.status_code}')
            break
        page_data = response.json()
        if not page_data:
            break
        comments.extend(page_data)
        page += 1
        time.sleep(1)
    return comments

def write_issues_to_csv(issues, owner, repo):
    filename = f'{owner}_{repo}_issues.csv'
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['issue_id', 'issue_number', 'issue_title', 'state', 'issue_body', 'comment_id', 'comment_body', 'html_url']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for issue in issues:
            if 'pull_request' in issue:
                continue
            
            issue_id = issue['id']
            issue_number = issue['number']
            issue_title = issue['title']
            issue_body = issue['body']
            issue_state = issue['state']
            issue_url = issue['html_url']
            
            writer.writerow({
                'issue_id': issue_id,
                'issue_number': issue_number,
                'issue_title': issue_title,
                'issue_body': issue_body,
                'state':issue_state,
                'html_url': issue_url,
                'comment_id': '',
                'comment_body': ''
            })
    print(f'Data exported to {filename}')

if __name__ == '__main__':
    # repo_url = input("Enter the GitHub repository URL (e.g., https://github.com/owner/repo): ").strip()
    owner, repo = get_repo_info_from_url(REPO.strip())
    print(f"Fetching issues for repository: {owner}/{repo}")
    issues = get_issues(owner, repo)
    if issues:
        write_issues_to_csv(issues, owner, repo)
    else:
        print("No issues found or unable to fetch issues.")