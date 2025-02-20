
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
        resource.licensing.forEach(licensing => {
            const licensingBadge = document.createElement('span');
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
                        .then(response => {
                            if (!response.ok) {
                                if (cachedResponse) {
                                    console.log('API call failed, using cached response');
                                    //Unable to fetch data from GitHub API, fallback to cached data
                                    return JSON.parse(cachedResponse).data.stargazers_count;
                                }
                                // Unable to fetch cached data fallback to default
                                console.log('API call failed, using default');
                                return {stargazers_count : resource.stars}
                            } else {
                                data = response.json();
                                // Cache the response
                                localStorage.setItem(cacheKey, JSON.stringify({ data, cachedAt: Date.now() }));
                                return data;
                            }
                        })
                        .then(data => {
                            const stars = data.stargazers_count;
                            // Convert count to smaller format
                            generateGithubPage(stars, popularityCell);
                        })
                        .catch(error => {
                            console.error(error);
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
        const aValue = parseValue(a.cells[columnIndex].textContent);
        const bValue = parseValue(b.cells[columnIndex].textContent);
        
        // If both values are numbers, do numeric comparison
        if (typeof aValue === 'number' && typeof bValue === 'number') {
            return isAscending ? aValue - bValue : bValue - aValue;
        }
        
        // Otherwise, do string comparison
        return isAscending
            ? String(aValue).localeCompare(String(bValue))
            : String(bValue).localeCompare(String(aValue));
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));

    tbody.dataset.sortColumn = columnIndex;
}

function parseValue(value) {
    value = value.trim().toLowerCase();
    let numericValue = parseFloat(value);
    if (isNaN(numericValue)) {
        return value; // Return original value for text sorting
    }
    
    // Handle suffixes
    if (value.endsWith('k')) {
        numericValue = parseFloat(value.slice(0, -1)) * 1000;
    } else if (value.endsWith('m')) {
        numericValue = parseFloat(value.slice(0, -1)) * 1000000;
    }
    return numericValue;
}