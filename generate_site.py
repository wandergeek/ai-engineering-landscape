from datetime import datetime
import yaml
from jinja2 import Environment, FileSystemLoader
import json


def load_resources():
    with open("resources.yaml", "r") as file:
        return yaml.safe_load(file)["resources"]


def generate_html(resources):
    # Prepare Jinja2 environment
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")

    # Render the template
    html_output = template.render(
        resources=resources,
        resources_json=json.dumps(resources),
        generation_date=datetime.now(),
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
