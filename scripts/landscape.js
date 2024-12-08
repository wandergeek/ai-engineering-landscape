function renderResourceLandscape(resources) {
    const container = document.getElementById('resourceLandscape');
    container.innerHTML = ''; // Clear existing content

    // Group resources by tag
    const categorizedResources = resources.reduce((acc, resource) => {
        // For each tag, push the resource into the corresponding array
        resource.tags.forEach(tag => {
            if (!acc[tag]) {
                acc[tag] = [];
            }
            acc[tag].push(resource);
        });
        // Sort acc by the number of resources in each category
        return Object.fromEntries(
            Object.entries(acc).sort(([, a], [, b]) => b.length - a.length)
        );

    }, {});
    // Render categories and resources
    Object.entries(categorizedResources).forEach(([tag, tagResources]) => {
        const tagBox = document.createElement('div');
        tagBox.className = 'tag-box';
        // Dynamic tag data attribute will bu used for css styling
        // data-tag attribute is the order of the tag in the list
        tagBox.dataset.tag = 'tag-' + Object.keys(categorizedResources).indexOf(tag);

        const tagTitle = document.createElement('div');
        tagTitle.className = 'tag-title';
        tagTitle.textContent = tag;
        tagBox.appendChild(tagTitle);

        const resourcesContainer = document.createElement('div');
        resourcesContainer.className = 'resources-container';

        tagResources.forEach(resource => {
            const resourceItem = document.createElement('div');
            resourceItem.className = 'resource-item';
            const resourceLink = document.createElement('a');
            resourceLink.href = Object.values(resource.links[0])[0];
            // Add name on hover
            resourceLink.title = resource.name;
            resourceLink.target = '_blank';
            // Use logo
            if (resource.logo) {
                const logo = document.createElement('img');
                logo.src = resource.logo;
                logo.alt = resource.name;
                logo.className = 'logo';
                resourceLink.appendChild(logo);
                // If logo link is broken
                logo.onerror = function () {
                    logo.src = '';
                }
            }
            // Use name if no logo
            else {
                resourceLink.textContent = resource.name;
            }
            resourceItem.appendChild(resourceLink);
            resourcesContainer.appendChild(resourceItem);
        });

        tagBox.appendChild(resourcesContainer);
        container.appendChild(tagBox);
    });
}