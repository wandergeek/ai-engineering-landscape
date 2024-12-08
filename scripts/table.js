
function renderResources(filteredResources) {
    const tbody = document.getElementById('resourcesBody');
    tbody.innerHTML = '';

    filteredResources.forEach(resource => {
        const row = document.createElement('tr');

        // Name
        const nameCell = document.createElement('td');
        nameCell.textContent = resource.name;
        row.appendChild(nameCell);

        // Description
        const descCell = document.createElement('td');
        descCell.textContent = resource.description;
        row.appendChild(descCell);

        // Tags
        const tagsCell = document.createElement('td');
        resource.tags.forEach(tag => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-secondary tag-badge';
            badge.textContent = tag;
            tagsCell.appendChild(badge);
        });
        row.appendChild(tagsCell);

        // Licensing
        const licensingCell = document.createElement('td');
        const licensingBadge = document.createElement('span');
        resource.licensing.forEach(licensing => {
            licensingBadge.className = `badge licensing-badge licensing-${licensing.toLowerCase().replace(' ', '-')}`;
            licensingBadge.textContent = licensing;
            licensingCell.appendChild(licensingBadge);
        });
        row.appendChild(licensingCell);

        // Link
        const linksCell = document.createElement('td')
        if (resource.links) {
            resource.links.forEach(item => {
                // Loop over each key-value pair in the links object
                Object.entries(item).forEach(([key, value]) => {
                    const resourceLink = document.createElement('a');
                    resourceLink.href = value; // The URL
                    resourceLink.textContent = `${key}`; // Display the key as the link text
                    resourceLink.target = '_blank';
                    resourceLink.className = 'btn btn-sm btn-link';
                    resourceLink.type = 'button';
                    linksCell.appendChild(resourceLink);
                });
            });
        } else {
            linksCell.textContent = '';
        }
        row.appendChild(linksCell);

        // Popularity
        const popularityCell = document.createElement('td');
        if (resource.links) {
            // Filter links to only include GitHub
            const githubLink = resource.links.find(link => link.github);
            if (githubLink) {
                const githubUrl = new URL(githubLink.github);
                const githubRepo = githubUrl.pathname.split('/').pop();
                const githubApiUrl = `https://api.github.com/repos${githubUrl.pathname}`;
                // Cache to reduce the number of requests to the GitHub API
                const cacheKey = `github-${githubRepo}`;
                const cachedResponse = localStorage.getItem(cacheKey);
                //Cached response contains the data from the API and the time it was cached
                if (cachedResponse && JSON.parse(cachedResponse).cachedAt > Date.now() - 3600000) {
                    console.log('Using cached response');
                    const data = JSON.parse(cachedResponse).data;
                    const stars = data.stargazers_count;
                    generateGithubPage(stars, popularityCell);
                } else {
                    console.log('Fetching from API');
                    fetch(githubApiUrl)
                        .then(response => response.json())
                        .then(data => {
                            const stars = data.stargazers_count;
                            // Convert count to smaller format
                            generateGithubPage(stars, popularityCell);
                            localStorage.setItem(cacheKey, JSON.stringify({ data, cachedAt: Date.now() }));
                        });
                }
            }
        }
        row.appendChild(popularityCell);

        tbody.appendChild(row);

    });
}

function generateGithubPage(stars, popularityCell) {
    if (stars > 999) {
        stars = (stars / 1000).toFixed(1) + 'k';
    }
    if (stars > 999999) {
        stars = (stars / 1000000).toFixed(1) + 'm';
    }
    const starsBadge = document.createElement('span');
    starsBadge.className = 'badge bg-warning';
    starsBadge.textContent = ` ${stars}`;
    // Add star icon
    const starIcon = document.createElement('i');
    starIcon.className = 'bi bi-star';
    starsBadge.prepend(starIcon);
    // Add github icon
    const githubIcon = document.createElement('i');
    githubIcon.className = 'bi bi-github';
    starsBadge.prepend(githubIcon);
    popularityCell.appendChild(starsBadge);
}


function sortTable(columnIndex) {
    const tbody = document.getElementById('resourcesBody');
    const rows = Array.from(tbody.rows);

    const isAscending = tbody.dataset.sortColumn !== columnIndex.toString();

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent;
        const bValue = b.cells[columnIndex].textContent;
        return isAscending
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));

    tbody.dataset.sortColumn = columnIndex;
}