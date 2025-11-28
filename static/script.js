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
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text.trim()).then(() => showToast('Copied!')).catch(err => fallbackCopy(text));
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
        showToast('Copied!');
    }
    
    window.copyToClipboard = copyToClipboard;

    function showToast(message) {
        let toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '1050';
        toast.innerHTML = `<div class="toast show text-white bg-success border-0"><div class="toast-body">${message}</div></div>`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
    }

    // --- Autocomplete ---
    if (searchInput && autocompleteList) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            const val = this.value;
            if (!val || val.length < 2) { closeAllLists(); return; }

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
                                div.innerHTML = `<span>${item.label}</span><span class="badge bg-light text-secondary border float-end small">${item.category}</span>`;
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

        document.addEventListener('click', function(e) {
            if (e.target !== searchInput) closeAllLists();
        });
    }

    function closeAllLists() {
        if (autocompleteList) { autocompleteList.innerHTML = ''; autocompleteList.style.display = 'none'; }
    }

    // --- Search Logic ---
    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) { alert("Please enter a search term."); return; }

        resultsContainer.style.display = 'block';
        statusMessage.innerHTML = `<div class="spinner-border text-primary mb-3"></div><p>Searching...</p>`;
        statusMessage.style.display = 'block';
        resultsTable.style.display = 'none';
        closeAllLists();

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsBody.innerHTML = ''; 
                if (data.length === 0) {
                    statusMessage.innerHTML = `<div class="text-danger"><p>No results found for "${query}".</p></div>`;
                } else {
                    statusMessage.style.display = 'none';
                    resultsTable.style.display = 'table';

                    data.forEach(item => {
                        const row = document.createElement('tr');
                        const payerName = item.payer_name || 'N/A';
                        const payerId = item.payer_code || 'N/A';
                        const naicCode = item.cocode || '-';
                        const carrierId = item.carrier_id;

                        const createCopyCell = (val) => {
                            if(val === 'N/A' || val === '-') return `<span class="text-muted">${val}</span>`;
                            return `<div class="d-flex align-items-center"><span class="me-2">${val}</span><button class="copy-btn" onclick="window.copyToClipboard('${val}')"><i class="fa-regular fa-copy"></i></button></div>`;
                        };

                        row.innerHTML = `
                            <td class="ps-4 fw-bold text-primary">${payerName}</td>
                            <td>${createCopyCell(payerId)}</td>
                            <td>${createCopyCell(naicCode)}</td>
                            <td class="pe-4 text-end">
                                <a href="/carrier/${carrierId}" class="btn btn-sm btn-outline-primary">
                                    <i class="fa-solid fa-circle-info me-1"></i> Details
                                </a>
                            </td>
                        `;
                        resultsBody.appendChild(row);
                    });
                    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statusMessage.innerHTML = `<div class="text-danger">Search failed.</div>`;
            });
    }

    if(searchButton) {
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    }
});