// Search
document.getElementById('searchInput').addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const filteredResources = resources.filter(resource =>
        resource.name.toLowerCase().includes(searchTerm) ||
        resource.description.toLowerCase().includes(searchTerm) ||
        resource.tags.some(tag => tag.toLowerCase().includes(searchTerm)) ||
        resource.licensing.some(licensing => licensing.toLowerCase().includes(searchTerm))
    );
    renderResourceLandscape(filteredResources);
    renderResources(filteredResources);
});



// Initial render
renderResourceLandscape(resources);
renderResources(resources);