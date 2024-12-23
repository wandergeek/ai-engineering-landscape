from datetime import datetime
import yaml
from jinja2 import Environment, FileSystemLoader
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
from pathlib import Path


def generate_webpage_screenshot(html_path):
    # Setup Selenium with specific window size
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--force-device-scale-factor=1")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Set a fixed window size
        driver.set_window_size(1600, 1600)
        file_url = f"file://{os.path.abspath(html_path)}"
        driver.get(file_url)

        # Wait for the element to be fully rendered
        driver.implicitly_wait(4)

        # Get element dimensions with JavaScript
        dimensions = driver.execute_script(
            """
            const element = document.querySelector('.landscape-container');
            const rect = element.getBoundingClientRect();
            return {
                left: rect.left,
                top: rect.top,
                width: rect.width,
                height: rect.height,
                devicePixelRatio: window.devicePixelRatio
            };
        """
        )

        # Take full page screenshot
        driver.save_screenshot("temp_screenshot.png")
        im = Image.open("temp_screenshot.png")

        # Calculate dimensions accounting for device pixel ratio, with 5px margin
        dpr = dimensions["devicePixelRatio"]
        left = int(dimensions["left"] * dpr) - 5
        top = int(dimensions["top"] * dpr) - 5
        right = int((dimensions["left"] + dimensions["width"]) * dpr) + 5
        bottom = int((dimensions["top"] + dimensions["height"]) * dpr) + 5

        # Crop the image
        im = im.crop((left, top, right, bottom))
        Path("dist/img").mkdir(parents=True, exist_ok=True)
        im.save("dist/img/ai_engineering_landscape.png")

        # Remove the temporary screenshot
        os.remove("temp_screenshot.png")

    finally:
        driver.quit()


def get_repo_info_from_github_env():
    # GITHUB_REPOSITORY is in format "owner/repo"
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" in repository:
        owner, repo = repository.split("/")
        return owner, repo
    return None, None


def get_github_contributors(token=None):
    owner, repo = get_repo_info_from_github_env()
    if not owner or not repo:
        print("Could not determine repository information")
        return []

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        contributors = response.json()
        return [
            {
                "username": contributor["login"],
                "avatar_url": contributor["avatar_url"],
                "contributions": contributor["contributions"],
                "profile_url": contributor["html_url"],
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
    contributors = get_github_contributors(token=os.environ.get("GITHUB_TOKEN"))

    # Render the template
    html_output = template.render(
        resources=resources,
        resources_json=json.dumps(resources),
        generation_date=datetime.now(),
        repo_name=repo,
        repo_owner=owner,
        contributors=contributors,
    )

    # Write the output
    html_path = "dist/index.html"
    with open(html_path, "w") as file:
        file.write(html_output)

    # Generate a screenshot of the webpage
    generate_webpage_screenshot(html_path=html_path)


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
