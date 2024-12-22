from datetime import datetime
import yaml
from jinja2 import Environment, FileSystemLoader
import json
import os
import requests
from dotenv import load_dotenv
load_dotenv()

def get_repo_info_from_github_env():
    # GITHUB_REPOSITORY is in format "owner/repo"
    repository = os.environ.get('GITHUB_REPOSITORY', '')
    if '/' in repository:
        owner, repo = repository.split('/')
        return owner, repo
    return None, None

def get_github_contributors(token=None):
    owner, repo = get_repo_info_from_github_env()
    if not owner or not repo:
        print("Could not determine repository information")
        return []
    
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f'https://api.github.com/repos/{owner}/{repo}/contributors'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        contributors = response.json()
        return [
            {
                'username': contributor['login'],
                'avatar_url': contributor['avatar_url'],
                'contributions': contributor['contributions'],
                'profile_url': contributor['html_url']
            }
            for contributor in contributors
        ]
    else:
        print(f"Failed to fetch contributors: {response.status_code}")
        print(response.text)
    return []

def load_resources():
    with open("resources.yaml", "r") as file:
        return yaml.safe_load(file)["resources"]


def generate_html(resources):
    # Prepare Jinja2 environment
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")

    # Get repository information
    owner, repo = get_repo_info_from_github_env()

    # Get contributors
    contributors = get_github_contributors(
        token=os.environ.get('GITHUB_TOKEN')
    )

    # Render the template
    html_output = template.render(
        resources=resources,
        resources_json=json.dumps(resources),
        generation_date=datetime.now(),
        repo_name=repo,
        repo_owner=owner,
        contributors=contributors
    )

    # Write the output
    with open("dist/index.html", "w") as file:
        file.write(html_output)


def main():
    import os
    import shutil

    os.makedirs("dist", exist_ok=True)
    resources = load_resources()
    generate_html(resources)
    # Copy the styles file to the dist directory
    shutil.copy("styles.css", "dist/styles.css")
    shutil.copytree("scripts", "dist/scripts/", dirs_exist_ok=True)
    shutil.copytree("logos", "dist/logos/", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
