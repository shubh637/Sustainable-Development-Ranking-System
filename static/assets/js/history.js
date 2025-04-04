document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const table = document.querySelector('.history-table');
    const filterBtn = document.querySelector('.filter-btn');
    const exportBtn = document.querySelector('.export-btn');
    const sortableHeaders = document.querySelectorAll('.sortable');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Sort functionality
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const columnIndex = header.cellIndex;
            const sortDirection = header.classList.contains('asc') ? 'desc' : 'asc';
            const icon = header.querySelector('i');
            
            // Reset all headers
            sortableHeaders.forEach(h => {
                h.classList.remove('asc', 'desc');
                const hIcon = h.querySelector('i');
                if (hIcon) hIcon.className = 'fas fa-sort';
            });
            
            // Set current header state
            header.classList.add(sortDirection);
            if (icon) {
                icon.className = sortDirection === 'asc' 
                    ? 'fas fa-sort-up' 
                    : 'fas fa-sort-down';
            }
            
            sortTable(columnIndex, sortDirection);
        });
    });

    function sortTable(columnIndex, sortDirection) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = getCellValue(a, columnIndex);
            const bValue = getCellValue(b, columnIndex);
            
            // Handle numeric values
            if (!isNaN(aValue)){
                return sortDirection === 'asc'? parseFloat(aValue) - parseFloat(bValue) : parseFloat(bValue) - parseFloat(aValue);
            }

            // Handle dates
            if (columnIndex === 0) {
                const aDate = new Date(aValue);
                const bDate = new Date(bValue);
                return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
            }
            
            // Default string comparison
            return sortDirection === 'asc'? aValue.localeCompare(bValue): bValue.localeCompare(aValue);
        });
        
        // Rebuild table
        rows.forEach(row => tbody.appendChild(row));
    }

    function getCellValue(row, columnIndex) {
        const cell = row.cells[columnIndex];
        return cell.textContent.trim();
    }

    // Filter functionality
    filterBtn.addEventListener('click', function() {
        const filterModal = new bootstrap.Modal(document.getElementById('filterModal'));
        filterModal.show();
    });

    // Export functionality
    exportBtn.addEventListener('click', function() {
        exportToCSV();
    });

    function exportToCSV() {
        const rows = table.querySelectorAll('tr');
        const csvContent = [];
        
        // Add headers
        const headers = Array.from(rows[0].querySelectorAll('th'))
            .map(th => th.textContent.trim())
            .filter(header => header !== 'Actions');
        csvContent.push(headers.join(','));
        
        // Add data rows
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cols = Array.from(row.querySelectorAll('td'));
            
            const rowData = cols.map((col, index) => {
                // Skip actions column
                if (index === cols.length - 1) return null;
                
                // Handle score badges
                const badge = col.querySelector('.score-badge');
                if (badge) return badge.textContent.trim();
                
                // Handle metric values
                const metric = col.querySelector('.metric-value');
                if (metric) return metric.textContent.trim();
                
                return col.textContent.trim();
            }).filter(val => val !== null);
            
            csvContent.push(rowData.join(','));
        }
        
        // Download CSV
        const csvString = csvContent.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `sustainability_history_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // Add filter modal HTML dynamically
    if (!document.getElementById('filterModal')) {
        const modalHTML = `
        <div class="modal fade" id="filterModal" tabindex="-1" aria-labelledby="filterModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="filterModalLabel">Filter History</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="dateFrom" class="form-label">From Date</label>
                            <input type="date" class="form-control" id="dateFrom">
                        </div>
                        <div class="mb-3">
                            <label for="dateTo" class="form-label">To Date</label>
                            <input type="date" class="form-control" id="dateTo">
                        </div>
                        <div class="mb-3">
                            <label for="scoreRange" class="form-label">Sustainability Score</label>
                            <select class="form-select" id="scoreRange">
                                <option value="all">All Scores</option>
                                <option value="excellent">Excellent (80-100%)</option>
                                <option value="good">Good (50-79%)</option>
                                <option value="poor">Poor (0-49%)</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="applyFilters">Apply Filters</button>
                    </div>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add filter functionality
        document.getElementById('applyFilters')?.addEventListener('click', function() {
            applyFilters();
            bootstrap.Modal.getInstance(document.getElementById('filterModal')).hide();
        });
    }

    function applyFilters() {
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;
        const scoreRange = document.getElementById('scoreRange').value;
        
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const dateCell = row.cells[0].textContent.trim();
            const date = new Date(dateCell);
            
            // Date filter
            let dateMatch = true;
            if (dateFrom) {
                const fromDate = new Date(dateFrom);
                dateMatch = dateMatch && date >= fromDate;
            }
            if (dateTo) {
                const toDate = new Date(dateTo);
                dateMatch = dateMatch && date <= toDate;
            }
            
            // Score filter
            let scoreMatch = true;
            if (scoreRange !== 'all') {
                const scoreBadge = row.querySelector('.score-badge');
                if (scoreBadge) {
                    const score = parseInt(scoreBadge.textContent);
                    if (scoreRange === 'excellent') scoreMatch = score >= 80;
                    if (scoreRange === 'good') scoreMatch = score >= 50 && score < 80;
                    if (scoreRange === 'poor') scoreMatch = score < 50;
                }
            }
            
            // Show/hide row based on filters
            row.style.display = (dateMatch && scoreMatch) ? '' : 'none';
        });
    }
});