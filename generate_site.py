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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def generate_webpage_screenshot(html_path):
    # Setup Selenium with specific window size
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--force-device-scale-factor=1")

    print("Starting screenshot process...")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print(f"Chrome version: {driver.capabilities['browserVersion']}")

    try:
        # Set a fixed window size
        driver.set_window_size(1600, 1600)
        file_url = f"file://{os.path.abspath(html_path)}"
        driver.get(file_url)

        # Wait for initial page load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Wait for JS to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script(
                """
                return typeof resources !== 'undefined' && 
                        document.querySelector('script[src="scripts/landscape.js"]') !== null
            """
            )
        )

        # Wait for element to be visible and have dimensions
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "landscape-container"))
        )

        # Print the number of sub elements
        print(
            f"Number of sub elements: {len(element.find_elements(By.CSS_SELECTOR, '*'))}"
        )

        dimensions = driver.execute_script(
            """
            const element = document.querySelector('.landscape-container');
            const rect = element.getBoundingClientRect();
            return {
                left: Math.max(0, rect.left),
                top: rect.top,
                width: rect.width,
                height: rect.height,
                devicePixelRatio: window.devicePixelRatio
            };
        """
        )

        print(f"Element dimensions: {dimensions}")

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

        print("Screenshot cropped and saved successfully!")

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

def initialize_github_stars(resource, token=None):
    if (resource.links and 'github' in resource.links):
        githubLink = resource.links.get('github');
        if githubLink:
            githubRepo = githubLink.split('/').pop();
            githubApiUrl = f'https://api.github.com/repos/{githubRepo}';
            headers = {"Accept": "application/vnd.github.v3+json"}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            response = requests.get(githubApiUrl, headers=headers);
            if response.status_code == 200:
                resource.stars = response.json().get("stargazers_count", 0);
            else : 
                print(f"Failed to fetch stars for {resource.link}");
            



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


def generate_sitemap():
    timestamp = datetime.now().strftime("%Y-%m-%d")
    screenshot_path = "img/ai_engineering_landscape.png"
    owner, repo = get_repo_info_from_github_env()
    url = f"https://{owner}.github.io/{repo}"

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
       xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
   <url>
       <loc>{url}</loc>
       <lastmod>{timestamp}</lastmod>
       <image:image>
           <image:loc>{url}/{screenshot_path}</image:loc>
           <image:title>AI Engineering Landscape</image:title>
           <image:caption>AI Engineering Landscape</image:caption>
       </image:image>
   </url>
</urlset>"""

    with open("dist/sitemap.xml", "w") as f:
        f.write(sitemap_content)


def generate_html(resources):
    # Prepare Jinja2 environment
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")

    # Get repository information
    owner, repo = get_repo_info_from_github_env()

    # Get contributors
    contributors = get_github_contributors(token=os.environ.get("GITHUB_TOKEN"))

    # Get all github stars and store them as backup
    for resource in resources:
        if "github" in resource.get("links", {}):
            response = requests.get(resource.get("links").get("github"))
            if response.status_code == 200:
                resource.stars = response.json().get("stargazers_count", 0)
            else:
                print(f"Failed to fetch stars for {resource.link}")


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

    # Generate sitemap
    generate_sitemap()


def main():
    import os
    import shutil

    os.makedirs("dist", exist_ok=True)
    resources = load_resources()

    shutil.copy("styles.css", "dist/styles.css")
    shutil.copytree("scripts", "dist/scripts/", dirs_exist_ok=True)
    shutil.copytree("logos", "dist/logos/", dirs_exist_ok=True)

    generate_html(resources)


if __name__ == "__main__":
    main()
