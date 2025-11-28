document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results-container');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');
    const statusMessage = document.getElementById('status-message');
    const autocompleteList = document.getElementById('autocomplete-list');
    
    let debounceTimer;

    // --- Core Functions ---

    function copyToClipboard(text) {
        if (!text || text === 'null' || text === 'undefined') return;
        
        // Modern Clipboard API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text.trim()).then(() => {
                showToast('Copied to clipboard!');
            }).catch(err => {
                console.error('Clipboard API failed: ', err);
                fallbackCopy(text);
            });
        } else {
            fallbackCopy(text);
        }
    }

    function fallbackCopy(text) {
        const tempInput = document.createElement('input');
        tempInput.value = text.trim();
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        showToast('Copied to clipboard!');
    }
    
    window.copyToClipboard = copyToClipboard;

    function showToast(message) {
        let toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '1050';
        toast.innerHTML = `
            <div class="toast show align-items-center text-white bg-success border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fa-solid fa-check-circle me-2"></i> ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => { toast.remove(); }, 3000);
    }

    // --- Autocomplete Functions ---

    if (searchInput && autocompleteList) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            const val = this.value;
            
            if (!val || val.length < 2) {
                closeAllLists();
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/autocomplete?q=${encodeURIComponent(val)}`)
                    .then(response => response.json())
                    .then(data => {
                        closeAllLists();
                        if (data.length > 0) {
                            autocompleteList.style.display = 'block';
                            data.forEach(item => {
                                const div = document.createElement('div');
                                div.className = 'autocomplete-item';
                                // Highlight logic could go here
                                div.innerHTML = `
                                    <span>${item.label}</span>
                                    <span class="badge bg-light text-secondary border float-end small">${item.category}</span>
                                `;
                                div.addEventListener('click', function() {
                                    searchInput.value = item.label;
                                    closeAllLists();
                                    performSearch();
                                });
                                autocompleteList.appendChild(div);
                            });
                        }
                    });
            }, 300);
        });

        // Close list on click outside
        document.addEventListener('click', function(e) {
            if (e.target !== searchInput) {
                closeAllLists();
            }
        });
    }

    function closeAllLists() {
        if (autocompleteList) {
            autocompleteList.innerHTML = '';
            autocompleteList.style.display = 'none';
        }
    }

    // --- Search Functions ---

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            alert("Please enter a search term.");
            return;
        }

        resultsContainer.style.display = 'block';
        statusMessage.innerHTML = `
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <p class="lead text-muted">Searching database for "<strong>${query}</strong>"...</p>
        `;
        statusMessage.style.display = 'block';
        resultsTable.style.display = 'none';
        closeAllLists(); // Close dropdown if open

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsBody.innerHTML = ''; 
                if (data.length === 0) {
                    statusMessage.innerHTML = `<div class="text-danger"><i class="fa-regular fa-face-frown fa-2x mb-2"></i><p>No carriers found matching "${query}".</p></div>`;
                } else {
                    statusMessage.style.display = 'none';
                    resultsTable.style.display = 'table';

                    data.forEach(carrier => {
                        const row = document.createElement('tr');
                        const name = carrier.legal_name || 'N/A';
                        const state = carrier.state_domicile ? `<span class="badge bg-light text-dark border ms-2">${carrier.state_domicile}</span>` : '';
                        const naic = carrier.naic_code || 'N/A';
                        const payer = carrier.payer_id || 'N/A';
                        const detailsBtn = naic !== 'N/A' ? 
                            `<a href="/carrier/${naic}" class="btn btn-sm btn-primary rounded-pill px-3">Details <i class="fa-solid fa-arrow-right ms-1"></i></a>` : 
                            '<span class="text-muted">-</span>';

                        const createCopyCell = (val) => {
                            if(val === 'N/A') return `<span class="text-muted">N/A</span>`;
                            return `
                                <div class="d-flex align-items-center">
                                    <span class="me-2">${val}</span>
                                    <button class="copy-btn" onclick="window.copyToClipboard('${val}')"><i class="fa-regular fa-copy"></i></button>
                                </div>
                            `;
                        };

                        row.innerHTML = `
                            <td class="ps-4 fw-bold text-primary">${name} ${state}</td>
                            <td>${createCopyCell(naic)}</td>
                            <td>${createCopyCell(payer)}</td>
                            <td class="pe-4 text-end">${detailsBtn}</td>
                        `;
                        resultsBody.appendChild(row);
                    });
                    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statusMessage.innerHTML = `<div class="text-danger">Search failed. Please try again.</div>`;
            });
    }

    if(searchButton) {
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    }
});