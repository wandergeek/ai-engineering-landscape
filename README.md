# AI Engineering Landscape

This repository maintains a curated list of resources for AI Engineering.
It is deployed [here](https://malywut.github.io/ai-engineering-landscape/).

## Contributing Resources

We welcome contributions! To add or update resources:

1. Fork the repository
2. Create a new branch for your changes
3. Edit the `resources.yaml` file
4. Commit your changes
5. Open a Pull Request

### Guidelines for Contributions

- Ensure your resource is unique and valuable
- Follow the existing YAML structure
- Include comprehensive details
- Verify all links are active
- Be respectful and professional in descriptions

### Resource Structure

Each resource should include:
- Name
- Description
- Links (website, github...)
- Tags
- Logo (preferably a file in logos/)


### Pull Request Process

1. Describe the resources you're adding/updating
2. Ensure the YAML is valid and well-formatted
3. Your PR will be reviewed by maintainers
4. Once approved, changes will be merged and automatically deployed

## Technical Details

- Automatically generated static site using GitHub Actions
- Searchable and sortable resources
- Hosted on GitHub Pages

## Local Development

1. Ensure Python 3.9+ is installed
2. Install dependencies: `pip install pyyaml jinja2 requests python-dotenv selenium webdriver-manager`
3. Run site generation: `python generate_site.py`

## Code of Conduct

Be kind, be constructive, and help us build a valuable resource collection.