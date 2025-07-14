/**
 * Main JavaScript file for Gas Mais Barato Dashboard
 */

// Global variables
let currentFilters = {};
let searchTimeout = null;
let currentData = []; // Armazena os dados atuais da tabela
let currentSort = { column: null, direction: 'asc' }; // Armazena o estado da ordenação

// Variável global para armazenar instâncias de Chart.js por KPI
window.kpiCharts = window.kpiCharts || {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Gas Mais Barato Dashboard initialized');
    
    // Add fade-in animation to cards
    addFadeInAnimation();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add smooth scrolling
    addSmoothScrolling();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    // Initialize report price functionality
    initializeReportPrice();

    // Initialize table sorting
    initializeTableSorting();

    // Handler do botão Buscar
    const searchBtn = document.getElementById('searchBtn') || document.querySelector('button[type="submit"]');
    if (searchBtn) {
        searchBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const state = document.getElementById('stateSelect') ? document.getElementById('stateSelect').value : '';
            const city = document.getElementById('citySelect') ? document.getElementById('citySelect').value : '';
            const filters = { state, city };
            fetchAndRenderKpis(filters);
            loadResults(filters);
        });
    }

    // Handler do botão Limpar Filtros
    const clearBtn = document.getElementById('clearFilters');
    if (clearBtn) {
        clearBtn.addEventListener('click', function(e) {
            setTimeout(() => {
                fetchAndRenderKpis({});
                loadResults({});
            }, 100);
        });
    }
});

/**
 * Add fade-in animation to cards
 */
function addFadeInAnimation() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease-in-out, transform 0.5s ease-in-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Add smooth scrolling to anchor links
 */
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Add keyboard shortcuts
 */
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('citySelect');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to clear filters
        if (e.key === 'Escape') {
            const clearBtn = document.getElementById('clearFilters');
            if (clearBtn) {
                clearBtn.click();
            }
        }
    });
}

/**
 * Initialize report price functionality
 */
function initializeReportPrice() {
    const reportButton = document.querySelector('a[href^="mailto:renan.de.moraes777@gmail.com"]');
    
    if (reportButton) {
        // Add tooltip to the button
        reportButton.setAttribute('data-bs-toggle', 'tooltip');
        reportButton.setAttribute('data-bs-placement', 'top');
        reportButton.setAttribute('title', 'Clique para enviar um e-mail reportando preços diferentes');
        
        // Add click event to show confirmation
        reportButton.addEventListener('click', function(e) {
            // Show a brief notification
            showNotification('Abrindo seu cliente de e-mail...', 'info');
            
            // Add a small delay to show the notification
            setTimeout(() => {
                // The mailto link will open automatically
            }, 500);
        });
        
        // Reinitialize tooltips after adding new ones
        initializeTooltips();
    }
}

/**
 * Format price with Brazilian currency
 */
function formatPrice(price) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(price);
}

/**
 * Format date to Brazilian format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(searchTimeout);
            func(...args);
        };
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Texto copiado para a área de transferência!', 'success');
        }).catch(() => {
            showNotification('Erro ao copiar texto', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('Texto copiado para a área de transferência!', 'success');
        } catch (err) {
            showNotification('Erro ao copiar texto', 'danger');
        }
        document.body.removeChild(textArea);
    }
}

/**
 * Export data to CSV
 */
function exportToCSV(data, filename = 'glp_prices.csv') {
    if (!data || data.length === 0) {
        showNotification('Nenhum dado para exportar', 'warning');
        return;
    }
    
    // Create CSV content
    const headers = ['Cidade', 'Estado', 'Empresa', 'Preço (R$)', 'Endereço', 'Data Coleta', 'Bandeira'];
    const csvContent = [
        headers.join(','),
        ...data.map(item => [
            `"${item.municipio}"`,
            `"${item.estado}"`,
            `"${item.revenda}"`,
            item.preco.toFixed(2),
            `"${item.endereco}"`,
            `"${item.data_coleta}"`,
            `"${item.bandeira}"`
        ].join(','))
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Dados exportados com sucesso!', 'success');
}

/**
 * Get current timestamp
 */
function getCurrentTimestamp() {
    return new Date().toISOString();
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Format phone number
 */
function formatPhoneNumber(phone) {
    // Remove all non-digits
    const cleaned = phone.replace(/\D/g, '');
    
    // Format Brazilian phone number
    if (cleaned.length === 11) {
        return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 7)}-${cleaned.slice(7)}`;
    } else if (cleaned.length === 10) {
        return `(${cleaned.slice(0, 2)}) ${cleaned.slice(2, 6)}-${cleaned.slice(6)}`;
    }
    
    return phone;
}

/**
 * Add loading state to button
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Carregando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Buscar';
    }
}

/**
 * Save filters to localStorage
 */
function saveFilters(filters) {
    try {
        localStorage.setItem('glp_filters', JSON.stringify(filters));
    } catch (e) {
        console.warn('Could not save filters to localStorage:', e);
    }
}

/**
 * Load filters from localStorage
 */
function loadFilters() {
    try {
        const saved = localStorage.getItem('glp_filters');
        return saved ? JSON.parse(saved) : {};
    } catch (e) {
        console.warn('Could not load filters from localStorage:', e);
        return {};
    }
}

/**
 * Clear saved filters
 */
function clearSavedFilters() {
    try {
        localStorage.removeItem('glp_filters');
    } catch (e) {
        console.warn('Could not clear filters from localStorage:', e);
    }
}

function renderKpiCard(kpi, data, label, prefix = '', suffix = '') {
  // Valor atual
  let value = data.current;
  document.getElementById(`kpi-${kpi}-value`).textContent =
    value !== null && value !== undefined ? `${prefix}${(kpi === 'avg_price' ? value.toFixed(2) : value)}${suffix}` : '--';

  // Variação
  let varText = '--';
  let varColor = '#888';
  if (data.variation && data.variation.pct !== null && data.variation.pct !== undefined) {
    const arrow = data.variation.pct > 0 ? '▲' : (data.variation.pct < 0 ? '▼' : '→');
    varColor = data.variation.pct > 0 ? '#28a745' : (data.variation.pct < 0 ? '#b48a78' : '#888'); // tom terroso suave para negativo
    let absVal = data.variation.abs !== null && data.variation.abs !== undefined ? (kpi === 'avg_price' ? data.variation.abs.toFixed(2) : data.variation.abs) : '--';
    varText = `${arrow} ${Math.abs(data.variation.pct).toFixed(1)}% (${data.variation.abs > 0 ? '+' : ''}${absVal})`;
  }
  const varDiv = document.getElementById(`kpi-${kpi}-variation`);
  varDiv.textContent = varText;
  varDiv.style.color = varColor;

  // Sparkline
  const ctx = document.getElementById(`kpi-${kpi}-sparkline`).getContext('2d');
  // Destroi o Chart antigo se existir
  if (window.kpiCharts[kpi]) {
    window.kpiCharts[kpi].destroy();
  }
  window.kpiCharts[kpi] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.history && window.kpiDates ? window.kpiDates : [],
      datasets: [{
        data: data.history || [],
        borderColor: '#4a90e2',
        backgroundColor: 'rgba(74,144,226,0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { display: false } },
      elements: { line: { borderWidth: 2 } },
      responsive: false,
      maintainAspectRatio: false
    }
  });
}

function renderKpisContextual(kpis) {
  // Esconde todos os cards primeiro
  document.getElementById('kpi-avg_price-card').style.display = 'none';
  document.getElementById('kpi-total_cities-card').style.display = 'none';
  document.getElementById('kpi-total_companies-card').style.display = 'none';
  document.getElementById('kpi-min_price-card').style.display = 'none';
  document.getElementById('kpi-max_price-card').style.display = 'none';

  // Sempre mostra preço médio
  document.getElementById('kpi-avg_price-card').style.display = '';
  renderKpiCard('avg_price', kpis.avg_price, 'Preço Médio', 'R$ ');

  if (kpis.kpi_type === 'global' || kpis.kpi_type === 'state') {
    document.getElementById('kpi-total_cities-card').style.display = '';
    document.getElementById('kpi-total_companies-card').style.display = '';
    renderKpiCard('total_cities', kpis.total_cities, 'Cidades');
    renderKpiCard('total_companies', kpis.total_companies, 'Empresas');
  }
  if (kpis.kpi_type === 'city') {
    document.getElementById('kpi-total_companies-card').style.display = '';
    renderKpiCard('total_companies', kpis.total_companies, 'Empresas');
    // Min/max preço
    document.getElementById('kpi-min_price-card').style.display = '';
    document.getElementById('kpi-max_price-card').style.display = '';
    document.getElementById('kpi-min_price-value').textContent = kpis.min_price !== null && kpis.min_price !== undefined ? `R$ ${kpis.min_price.toFixed(2)}` : '--';
    document.getElementById('kpi-max_price-value').textContent = kpis.max_price !== null && kpis.max_price !== undefined ? `R$ ${kpis.max_price.toFixed(2)}` : '--';

    // Sparkline para Preço Mínimo
    const minCtx = document.getElementById('kpi-min_price-sparkline').getContext('2d');
    if (window.kpiCharts['min_price']) window.kpiCharts['min_price'].destroy();
    window.kpiCharts['min_price'] = new Chart(minCtx, {
        type: 'line',
        data: {
            labels: kpis.dates || [],
            datasets: [{
                data: kpis.min_price_history || [],
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74,144,226,0.08)',
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } },
            elements: { line: { borderWidth: 2 } },
            responsive: false,
            maintainAspectRatio: false
        }
    });

    // Sparkline para Preço Máximo
    const maxCtx = document.getElementById('kpi-max_price-sparkline').getContext('2d');
    if (window.kpiCharts['max_price']) window.kpiCharts['max_price'].destroy();
    window.kpiCharts['max_price'] = new Chart(maxCtx, {
        type: 'line',
        data: {
            labels: kpis.dates || [],
            datasets: [{
                data: kpis.max_price_history || [],
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74,144,226,0.08)',
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { x: { display: false }, y: { display: false } },
            elements: { line: { borderWidth: 2 } },
            responsive: false,
            maintainAspectRatio: false
        }
    });
  }
}

function fetchAndRenderKpis(filters) {
  const params = new URLSearchParams();
  if (filters && filters.state) params.append('state', filters.state);
  if (filters && filters.city) params.append('city', filters.city);
  fetch('/api/stats?' + params.toString())
    .then(res => res.json())
    .then(json => {
      if (json.success) {
        const kpis = json.data;
        window.kpiDates = kpis.dates;
        renderKpisContextual(kpis);
      }
    });
}

function loadResults(filters = {}) {
    const state = filters.state || '';
    const city = filters.city || '';
    const limit = document.getElementById('limitSelect') ? document.getElementById('limitSelect').value : 50;
    let url = `/api/search?limit=${limit}`;
    if (state) url += `&state=${encodeURIComponent(state)}`;
    if (city) url += `&city=${encodeURIComponent(city)}`;
    fetch(url)
        .then(res => res.json())
        .then(json => {
            renderResultsTable(json.data);
        });
}

function renderResultsTable(data) {
    // Armazena os dados atuais
    currentData = data || [];
    
    const tableDiv = document.getElementById('resultsTable');
    if (!tableDiv) return;

    if (!data || data.length === 0) {
        tableDiv.innerHTML = '<div class="text-center text-muted py-4">Nenhum resultado encontrado.</div>';
        return;
    }

    // Aplica ordenação se houver
    let sortedData = [...data];
    if (currentSort.column) {
        sortedData = sortData(data, currentSort.column, currentSort.direction);
    }

    let html = `
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th class="sortable" data-sort="municipio">
                        <span>Cidade</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable" data-sort="estado">
                        <span>Estado</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable data-coleta-col" data-sort="data_coleta">
                        <span>Data Coleta</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable" data-sort="revenda">
                        <span>Empresa</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable" data-sort="preco">
                        <span>Preço (R$)</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable" data-sort="endereco">
                        <span>Endereço</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                    <th class="sortable" data-sort="bandeira">
                        <span>Bandeira</span>
                        <i class="bi bi-arrow-down-up sort-icon"></i>
                    </th>
                </tr>
            </thead>
            <tbody>
    `;
    
    sortedData.forEach(item => {
        html += `
            <tr>
                <td><strong>${item.municipio}</strong></td>
                <td><span class="badge bg-secondary">${item.estado}</span></td>
                <td class="data-coleta-col">${item.data_coleta}</td>
                <td>${item.revenda}</td>
                <td><span class="badge bg-success">R$ ${item.preco.toFixed(2)}</span></td>
                <td><small>${item.endereco}</small></td>
                <td><span class="badge bg-info">${item.bandeira}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    tableDiv.innerHTML = html;
    
    // Reaplica os event listeners de ordenação
    initializeTableSorting();
}

/**
 * Initialize table sorting functionality
 */
function initializeTableSorting() {
    const sortableHeaders = document.querySelectorAll('th.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            handleSort(column);
        });
    });
}

/**
 * Handle sorting when header is clicked
 */
function handleSort(column) {
    // Remove previous sort indicators
    document.querySelectorAll('th.sortable').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Determine sort direction
    let direction = 'asc';
    if (currentSort.column === column && currentSort.direction === 'asc') {
        direction = 'desc';
    }
    
    // Update current sort state
    currentSort.column = column;
    currentSort.direction = direction;
    
    // Add sort indicator to clicked header
    const clickedHeader = document.querySelector(`th[data-sort="${column}"]`);
    if (clickedHeader) {
        clickedHeader.classList.add(`sort-${direction}`);
    }
    
    // Re-render table with sorted data
    renderResultsTable(currentData);
}

/**
 * Sort data by column and direction
 */
function sortData(data, column, direction) {
    return [...data].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle different data types
        if (column === 'preco') {
            aVal = parseFloat(aVal);
            bVal = parseFloat(bVal);
        } else if (column === 'data_coleta') {
            // Convert date string to Date object for comparison
            aVal = new Date(aVal.split('/').reverse().join('-'));
            bVal = new Date(bVal.split('/').reverse().join('-'));
        } else {
            // String comparison
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
        }
        
        // Compare values
        if (aVal < bVal) {
            return direction === 'asc' ? -1 : 1;
        }
        if (aVal > bVal) {
            return direction === 'asc' ? 1 : -1;
        }
        return 0;
    });
}

// Exemplo de uso inicial
fetchAndRenderKpis({});

// Atualize para chamar fetchAndRenderKpis(filters) ao buscar/filtrar
// (adicione isso no handler do botão Buscar e ao limpar filtros) 