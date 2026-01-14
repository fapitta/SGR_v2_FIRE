const DATA_YEARS = Array.from({ length: 19 }, (_, i) => String(2010 + i)); // 2010-2028

// --- GLOBAL STATE ---
let originalData = null; // Store original data from backend
let originalDataPromise = null;
let charts = {};
let userData = {
    mei: {},
    medical: {},
    cf: {},
    population: {},
    gdp: {},
    law: {},
    rv: {},
    weights: {}
};
let modifiedCells = new Set(); // Track modified cells

async function initRvTable() {
    const tbody = document.getElementById('rv-table-body');
    if (!tbody) return;

    updateTableHeader('rv-table', '종별');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const years = DATA_YEARS;

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.0001';

                const originalValue = data.rv[type]?.[year];
                const userValue = userData.rv[year]?.[type];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(4) : '';
                input.dataset.type = type;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(4) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('rv-table');
        setupColumnHighlight('rv-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">상대가치 로드 실패: ${e.message}</td></tr>`;
    }
}
function saveRvData() {
    const tbody = document.getElementById('rv-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.rv[year]) userData.rv[year] = {};
            userData.rv[year][input.dataset.type] = parseFloat(input.value);
        }
    });
    showToast('✅ 상대가치변화 데이터가 저장되었습니다.');
    initRvTable();
    triggerGlobalSimulation();
}
function resetRvData() {
    if (!confirm('상대가치변화 수정을 취소하시겠습니까?')) return;
    userData.rv = {};
    initRvTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

async function initWeightsTable() {
    const tbody = document.getElementById('weights-table-body');
    if (!tbody) return;

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';
        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const cols = ['인건비', '관리비', '재료비'];

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            cols.forEach(col => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.0001';

                const originalValue = data.weights[type]?.[col];
                const userValue = userData.weights[type]?.[col];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(4) : '';

                input.dataset.type = type;
                input.dataset.col = col;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(4) : '';

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('weights-table');
        setupColumnHighlight('weights-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--danger);">가중치 로드 실패: ${e.message}</td></tr>`;
    }
}
function saveWeightsData() {
    const tbody = document.getElementById('weights-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const type = input.dataset.type;
            const col = input.dataset.col;
            if (!userData.weights[type]) userData.weights[type] = {};
            userData.weights[type][col] = parseFloat(input.value);
        }
    });
    showToast('✅ 가중치 데이터가 저장되었습니다.');
    initWeightsTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}
function resetWeightsData() {
    if (!confirm('가중치 수정을 취소하시겠습니까?')) return;
    userData.weights = {};
    initWeightsTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.');
        triggerGlobalSimulation();
    });
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

    const tabEl = document.getElementById(tabId);
    if (tabEl) tabEl.classList.add('active');

    // Find sidebar item
    const navItems = document.querySelectorAll('.nav-menu .nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('onclick')?.includes(`'${tabId}'`)) {
            item.classList.add('active');
        }
    });

    if (tabId === 'dashboard') {
        renderCharts();
    } else if (tabId === 'raw-data-view') {
        initRawDataView();
    } else if (tabId === 'detailed-stats') {
        renderDetailTable();
    } else if (tabId === 'analysis-report') {
        renderInsightReport();
    } else if (tabId === 'data-entry') {
        initAllDataTables();
    }
}

function initApp() {
    // Check for tab query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const targetTab = urlParams.get('tab');

    // Populate year selectors
    const yearSels = ['detailYearSelector', 'dashboardYearSelector'];
    const years = (appData.history && appData.history.years) ? appData.history.years : DATA_YEARS;
    yearSels.forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        sel.innerHTML = '';
        years.forEach(y => {
            const opt = document.createElement('option');
            opt.value = y; opt.textContent = `${y}년`;
            if (y === 2025) opt.selected = true;
            sel.appendChild(opt);
        });
    });

    if (targetTab) {
        switchTab(targetTab);
    } else {
        // Only load if current tab is data-entry
        const activeItem = document.querySelector('.nav-item.active');
        if (activeItem && activeItem.getAttribute('onclick')?.includes('data-entry')) {
            initAllDataTables();
        } else {
            renderCharts();
        }
    }

    // Add event listener for dashboard year selector
    const dashboardYearSelector = document.getElementById('dashboardYearSelector');
    if (dashboardYearSelector) {
        dashboardYearSelector.addEventListener('change', function () {
            renderCharts();
            renderInsightReport();
        });
    }

    renderCharts();
}

function initAllDataTables() {
    // Lazy: Only init the sub-tab that is currently active within data-entry
    const activeSubTab = document.querySelector('.category-tab.active');
    if (!activeSubTab) {
        initMedicalTable(); // Default fallback
        return;
    }

    const onclickStr = activeSubTab.getAttribute('onclick') || '';
    if (onclickStr.includes("'mei'")) initMeiTable();
    else if (onclickStr.includes("'medical'")) initMedicalTable();
    else if (onclickStr.includes("'cf'")) initCfTable();
    else if (onclickStr.includes("'population'")) initPopTable();
    else if (onclickStr.includes("'gdp'")) initGdpTable();
    else if (onclickStr.includes("'law'")) initLawTable();
    else if (onclickStr.includes("'rv'")) initRvTable();
    else if (onclickStr.includes("'weights'")) initWeightsTable();
}

const typeColors = {
    '병원(계)': '#6366f1', // Indigo
    '의원(계)': '#10b981', // Emerald
    '치과(계)': '#f59e0b', // Amber
    '한방(계)': '#ec4899', // Pink
    '약국(계)': '#8b5cf6', // Violet (Changed for clarity)
    '전체': '#94a3b8'
};

function updateTableHeader(tableId, firstColName) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const thead = table.querySelector('thead');
    if (!thead) return;

    let html = `<tr><th>${firstColName}</th>`;
    DATA_YEARS.forEach(y => html += `<th>${y}년</th>`);
    html += '</tr>';
    thead.innerHTML = html;
}

// Register DataLabels globally
Chart.register(ChartDataLabels);

// Global State for selections
if (typeof appData.selectedType === 'undefined') appData.selectedType = null;

function updateModelSelection() {
    renderCharts();
    renderInsightReport();
}


function renderCharts() {
    const selectedYear = parseInt(document.getElementById('dashboardYearSelector')?.value || 2025);
    const selectedModelKey = document.getElementById('dashboardModelSelector')?.value || 'S2';

    // Update labels
    const labelEl = document.getElementById('trendModelLabel');
    if (labelEl) {
        const modelNames = { 'S1': '현행 SGR(S1)', 'S2': '개선 SGR(S2)', 'GDP': 'GDP 모형', 'MEI': 'MEI 모형', 'Link': '거시지표 연계' };
        labelEl.textContent = modelNames[selectedModelKey] || selectedModelKey;
    }

    // Render comparison table first
    renderDashboardComparison();

    const years = appData.history.years;
    const history = appData.history;

    const baseWidth = 2.5;
    const clickedWidth = 6.5;

    const applyLineStyles = (chart) => {
        if (!chart || !chart.data) return;
        chart.data.datasets.forEach((ds) => {
            const color = typeColors[ds.label] || ds.borderColor;
            if (appData.selectedType) {
                const isSelected = ds.label === appData.selectedType;
                // 선택된 라인은 매우 굵게, 선택되지 않은 라인은 매우 얇게
                ds.borderWidth = isSelected ? clickedWidth : 1.5;
                // Use substring to strip any existing alpha then add transparency
                const baseColor = color.length > 7 ? color.substring(0, 7) : color;
                // 선택된 라인은 원래 색상, 선택되지 않은 라인은 매우 투명하게
                ds.borderColor = isSelected ? baseColor : baseColor + '25';
                // 포인트도 동일하게 처리
                ds.pointBackgroundColor = isSelected ? baseColor : baseColor + '25';
                ds.pointBorderColor = isSelected ? baseColor : baseColor + '25';
            } else {
                const baseColor = color.length > 7 ? color.substring(0, 7) : color;
                // 선택된 유형이 없을 때는 기본 스타일
                ds.borderWidth = (ds.label === '전체' ? 4 : (ds.label.includes('평균') ? 2 : baseWidth));
                ds.borderColor = baseColor;
                ds.pointBackgroundColor = baseColor;
                ds.pointBorderColor = baseColor;
            }
        });
        chart.update('none');
    };

    // Helper function to apply year highlighting to point styles
    const applyYearHighlight = (chart) => {
        if (!chart || !chart.data) return;
        const selectedYearIndex = years.indexOf(selectedYear);

        chart.data.datasets.forEach((ds) => {
            // Create arrays for point radius and point border width
            ds.pointRadius = years.map((year, idx) => {
                if (idx === selectedYearIndex) {
                    // 선택된 연도의 포인트를 더 크게
                    return appData.selectedType && ds.label !== appData.selectedType ? 7 : 10;
                }
                // 다른 연도의 포인트는 작게
                return appData.selectedType && ds.label !== appData.selectedType ? 2 : 4;
            });

            ds.pointBorderWidth = years.map((year, idx) => {
                // 선택된 연도는 테두리를 더 굵게
                return idx === selectedYearIndex ? 4 : 2;
            });

            ds.pointBorderColor = years.map((year, idx) => {
                if (idx === selectedYearIndex) {
                    // 선택된 연도는 흰색 테두리로 강조
                    return '#ffffff';
                }
                // 다른 연도는 라인 색상과 동일하게
                return ds.borderColor;
            });

            ds.pointBackgroundColor = years.map((year, idx) => {
                const color = typeColors[ds.label] || ds.borderColor;
                const baseColor = color.length > 7 ? color.substring(0, 7) : color;

                if (idx === selectedYearIndex) {
                    // 선택된 연도는 원래 색상 그대로
                    return baseColor;
                }
                // 다른 연도는 약간 투명하게
                return appData.selectedType && ds.label !== appData.selectedType
                    ? baseColor + '60'
                    : baseColor + 'CC';
            });
        });

        chart.update('none');
    };



    // 1. Main Trends
    const ctxTrends = document.getElementById('mainTrendsChart').getContext('2d');
    if (charts.trends) charts.trends.destroy();

    let trendDatasets = [];
    const mainGroups = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)'];

    // Build Category Lines
    mainGroups.forEach(g => {
        trendDatasets.push({
            label: g,
            data: years.map(y => history[selectedModelKey][y][g]),
            borderColor: typeColors[g],
            backgroundColor: typeColors[g] + '20',
            fill: false,
            tension: 0.35,
            borderWidth: baseWidth,
            pointStyle: 'rectRounded'
        });
    });

    if (!['GDP', 'MEI', 'Link'].includes(selectedModelKey)) {
        trendDatasets.push({
            label: '전체',
            data: years.map(y => history[selectedModelKey][y]['전체']),
            borderColor: '#94a3b8',
            borderWidth: 4,
            pointStyle: 'rectRounded'
        });
    }

    charts.trends = new Chart(ctxTrends, {
        type: 'line',
        data: { labels: years, datasets: trendDatasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            onClick: (event, elements, chart) => {
                // Use 'nearest' mode to find the specific line clicked, even if interaction mode is 'index'
                const preciseElements = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
                if (preciseElements.length > 0) {
                    const label = chart.data.datasets[preciseElements[0].datasetIndex].label;
                    appData.selectedType = (appData.selectedType === label) ? null : label;
                    renderCharts();
                }
            },

            onHover: (event, el) => { event.native.target.style.cursor = el.length > 0 ? 'pointer' : 'default'; },
            plugins: {
                datalabels: { display: false },
                legend: {
                    position: 'bottom',
                    onClick: (e, legendItem, legend) => {
                        const label = legendItem.text;
                        appData.selectedType = (appData.selectedType === label) ? null : label;
                        renderCharts();
                    },
                    labels: {
                        color: '#94a3b8',
                        usePointStyle: true,
                        pointStyle: 'rectRounded',
                        font: { size: 11, weight: '600' }
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            return `${context[0].label} (${appData.selectedType || '전체 보기'})`;
                        },
                        label: function (context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y.toFixed(2);
                            const isSelected = appData.selectedType === label;
                            return `${isSelected ? '★ ' : ''}${label}: ${value}%`;
                        }
                    }
                }
            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8', callback: v => v + '%' } },
                x: { ticks: { color: '#94a3b8' } }
            }
        }
    });

    // 2. Rank Chart
    const ctxRank = document.getElementById('rankStreamChart').getContext('2d');
    if (charts.rank) charts.rank.destroy();

    charts.rank = new Chart(ctxRank, {
        type: 'line',
        data: {
            labels: years,
            datasets: mainGroups.map((g) => ({
                label: g,
                data: years.map(y => {
                    const sorted = mainGroups
                        .map(gn => ({ name: gn, val: history[selectedModelKey][y][gn] }))
                        .sort((a, b) => b.val - a.val);
                    return sorted.findIndex(item => item.name === g) + 1;
                }),
                borderColor: typeColors[g],
                backgroundColor: typeColors[g],
                tension: 0.2,
                borderWidth: baseWidth,
                pointStyle: 'rectRounded'
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            onClick: (event, elements, chart) => {
                const preciseElements = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
                if (preciseElements.length > 0) {
                    const label = chart.data.datasets[preciseElements[0].datasetIndex].label;
                    appData.selectedType = (appData.selectedType === label) ? null : label;
                    renderCharts();
                }
            },

            onHover: (event, el) => { event.native.target.style.cursor = el.length > 0 ? 'pointer' : 'default'; },
            scales: {
                y: { reverse: true, min: 1, max: 5, ticks: { stepSize: 1, color: '#94a3b8' } },
                x: { ticks: { color: '#94a3b8' } }
            },
            plugins: {
                datalabels: { display: false },
                legend: {
                    position: 'bottom',
                    onClick: (e, legendItem, legend) => {
                        const label = legendItem.text;
                        appData.selectedType = (appData.selectedType === label) ? null : label;
                        renderCharts();
                    },
                    labels: {
                        color: '#94a3b8',
                        usePointStyle: true,
                        pointStyle: 'rectRounded',
                        font: { size: 11, weight: '600' }
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            return `${context[0].label} (${appData.selectedType || '전체 보기'})`;
                        },
                        label: function (context) {
                            const label = context.dataset.label || '';
                            const rank = context.parsed.y;
                            const isSelected = appData.selectedType === label;
                            return `${isSelected ? '★ ' : ''}${label}: ${rank}위`;
                        }
                    }
                }
            }
        }
    });


    applyLineStyles(charts.trends);
    applyYearHighlight(charts.trends);
    applyLineStyles(charts.rank);
    applyYearHighlight(charts.rank);







    // 3. Type Comparison (Selected Model & Year)
    const ctxType = document.getElementById('typeCompareChart').getContext('2d');
    if (charts.type) charts.type.destroy();

    const compareGroups = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)'];
    let compareDatasets = [];

    if (selectedModelKey === 'Link') {
        compareDatasets = [
            { label: 'GDP', data: compareGroups.map(g => history.GDP[selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g] + '44') },
            { label: 'MEI', data: compareGroups.map(g => history.MEI[selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g] + '88') },
            { label: '거시연계', data: compareGroups.map(g => history.Link[selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g]) }
        ];
    } else if (selectedModelKey === 'GDP' || selectedModelKey === 'MEI') {
        compareDatasets = [
            { label: selectedModelKey + ' 모형', data: compareGroups.map(g => history[selectedModelKey][selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g]) }
        ];
    } else {
        const otherModel = selectedModelKey === 'S1' ? 'S2' : 'S1';
        compareDatasets = [
            { label: selectedModelKey === 'S1' ? 'SGR(S1)' : 'SGR(S2)', data: compareGroups.map(g => history[selectedModelKey][selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g]) },
            { label: otherModel === 'S1' ? 'SGR(S1)' : 'SGR(S2)', data: compareGroups.map(g => history[otherModel][selectedYear][g]), backgroundColor: compareGroups.map(g => typeColors[g] + '44') }
        ];
    }


    charts.type = new Chart(ctxType, {
        type: 'bar',
        data: { labels: compareGroups, datasets: compareDatasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } },

                datalabels: {
                    display: true,
                    color: '#fff',
                    anchor: 'end',
                    align: 'top',
                    offset: 2,
                    font: { size: 10, weight: 'bold' },
                    formatter: (v) => v.toFixed(2) + '%'
                }

            },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' }, grace: '15%' },
                x: { ticks: { color: '#94a3b8' } }
            }
        }
    });
}







function renderDetailTable() {
    const type = document.getElementById('detailTableSelector').value;
    const yearSel = document.getElementById('detailYearSelector');
    const year = yearSel.value;
    const container = document.getElementById('detailTableContainer');
    if (!container) return;
    container.innerHTML = ''; // Clear container

    // Hide year selector for EXCEL_RAW as it shows all years/sheets
    if (type === 'EXCEL_RAW' || type === 'SGR_S1' || type === 'SGR_S2' || type === 'UAF_BOTH' || type === 'SGR_INDEX' || type === 'TARGET_EXP' || type === 'BULK_RAW') {
        if (yearSel) yearSel.style.display = 'none';
        // Some of these might benefit from year sel, but user asked for "All years" in some views.
        // Actually, most of them show year-ranges or all years. 
        // Only SGR_COMP and MEI_SCENARIO strictly need a specific year.
    } else {
        yearSel.style.display = 'block';
    }

    const createTable = (id, headHtml, bodyHtml, title = "") => {
        return `
            <div class="glass" style="margin-bottom: 2rem; overflow-x: auto;">
                ${title ? `<h3 style="padding: 1.2rem; border-bottom: 1px solid var(--border-glass); background: rgba(255,255,255,0.02);">${title}</h3>` : ''}
                <table id="${id}" class="detail-display-table">
                    <thead>${headHtml}</thead>
                    <tbody>${bodyHtml}</tbody>
                </table>
            </div>
        `;
    };

    if (type === 'UAF_BOTH') {
        // Table 1: S1 UAF
        let headS1 = `<tr><th>연도</th>${appData.groups.map(g => `<th>${g}</th>`).join('')}</tr>`;
        let bodyS1 = appData.history.years.map(y => {
            return `<tr><td>${y}년 (S1)</td>${appData.groups.map(g => `<td>${parseFloat(appData.history.UAF_S1[y][g] || 0).toFixed(3)}%</td>`).join('')}</tr>`;
        }).join('');

        // Table 2: S2 UAF
        let headS2 = `<tr><th>연도</th>${appData.groups.map(g => `<th>${g}</th>`).join('')}</tr>`;
        let bodyS2 = appData.history.years.map(y => {
            return `<tr><td>${y}년 (S2)</td>${appData.groups.map(g => `<td>${parseFloat(appData.history.UAF_S2[y][g] || 0).toFixed(3)}%</td>`).join('')}</tr>`;
        }).join('');

        container.innerHTML = createTable('uaf-s1-table', headS1, bodyS1, "📈 (현행 SGR 모형) UAF(PAF) 산출 추이") +
            createTable('uaf-s2-table', headS2, bodyS2, "📈 (개선 SGR 모형) UAF(PAF) 산출 추이");


    } else if (type === 'SGR_S1' || type === 'SGR_S2') {
        const modelKey = type === 'SGR_S1' ? 'S1' : 'S2';
        const modelLabel = type === 'SGR_S1' ? '현행 SGR 모형(S1)' : '개선 SGR 모형(S2)';

        let head = `<tr><th>유형</th>${appData.history.years.filter(y => y <= 2026).map(y => `<th>${y}년</th>`).join('')}</tr>`;
        let body = appData.groups.map(g => {
            let rowCols = `<td>${g}</td>`;
            appData.history.years.filter(y => y <= 2026).forEach(y => {
                const val = appData.history[modelKey][y]?.[g] || 0;
                rowCols += `<td style="font-weight:700;">${parseFloat(val).toFixed(2)}</td>`;
            });
            return `<tr>${rowCols}</tr>`;
        }).join('');

        container.innerHTML = createTable('sgr-result-table', head, body, `🏆 ${modelLabel} 조정률_MEI_평균 기준(%)`);

    } else if (type === 'MEI_SCENARIO') {
        const yearData = appData.components.mei_raw[year];
        if (!yearData) {
            container.innerHTML = `<div class="glass" style="padding: 2rem;">해당 연도(${year}년)의 시나리오 데이터가 없습니다.</div>`;
            return;
        }
        // Ensure specific order: Avg, Min, Max, Median, then others
        const priorities = ['평균', '최소', '최대', '중위수'];
        const allKeys = Object.keys(yearData);
        const scenarios = [
            ...priorities.filter(k => allKeys.includes(k)),
            ...allKeys.filter(k => !priorities.includes(k) && !['평균', '최소', '최대', '중위수'].includes(k)).sort()
        ];

        let head = `<tr><th>종별</th>${scenarios.map(s => `<th>${s}</th>`).join('')}</tr>`;
        let body = appData.groups.filter(g => !g.includes('(계)') && g !== '전체').map(ht => {
            let row = `<td style="font-weight:600;">${ht}</td>`;
            scenarios.forEach(sc => {
                const rowData = yearData[sc] || {};
                // Look for key exactly, or trimmed version
                let val = rowData[ht];
                if (val === undefined) {
                    val = rowData[ht.trim()];
                }

                // If still undefined, default to 1.0
                if (val === undefined || val === null) {
                    val = 1.0;
                }
                row += `<td>${parseFloat(val).toFixed(4)}</td>`;
            });
            return `<tr>${row}</tr>`;
        }).join('');
        container.innerHTML = createTable('mei-scen-table', head, body, `📊 CF_${year}에 사용될  MEI _${parseInt(year) - 2}년 시나리오 (12종 + 통계)`);

    } else if (type === 'CF_SCENARIO_S1' || type === 'CF_SCENARIO_S2') {
        const scenData = appData.bulk_sgr.scenario_adjustments[year];
        const modelKey = type === 'CF_SCENARIO_S1' ? 'S1' : 'S2';
        const modelLabel = type === 'CF_SCENARIO_S1' ? '현행모형(S1)' : '개선모형(S2)';

        if (!scenData) {
            container.innerHTML = `<div class="glass" style="padding: 2rem;">해당 연도의 조정률 시나리오 데이터가 아직 생성되지 않았습니다.</div>`;
            return;
        }

        // Ensure specific order: Avg, Min, Max, Median, then others
        const priorities = ['평균', '최소', '최대', '중위수'];
        const allKeys = Object.keys(scenData);
        const scenarios = [
            ...priorities.filter(k => allKeys.includes(k)),
            ...allKeys.filter(k => !priorities.includes(k)).sort()
        ];

        let head = `<tr><th>유형</th>${scenarios.map(s => `<th>${s}</th>`).join('')}</tr>`;
        let body = appData.groups.map(g => {
            let row = `<td style="font-weight:600;">${g}</td>`;
            scenarios.forEach(sc => {
                const val = scenData[sc][modelKey][g] || 0;
                row += `<td>${parseFloat(val).toFixed(2)}%</td>`;
            });
            return `<tr>${row}</tr>`;
        }).join('');
        container.innerHTML = createTable('cf-scen-table', head, body, `📉 ${year}년도 유형별 환산지수 조정률 (시나리오별, ${modelLabel} 기준)`);


    } else if (type === 'MACRO_MODELS') {
        // 거시지표 모형: GDP, MEI, Link 모형의 계산 과정 표시
        const individualTypes = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const groupTypes = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'];
        const allTypes = [...individualTypes, ...groupTypes];

        // 계산에 사용되는 연도: 2025년 조정률 = 2023년 데이터 사용
        const calcYear = year - 2;

        // 1. GDP 증가율 모형
        // 공식: GDP 증가율 - 상대가치 변화율
        let gdpHead = `<tr><th>종별</th><th>실질GDP 증가율 (%)<br/>(${calcYear}년)</th><th>상대가치 변화율 (%)<br/>(${calcYear}년)</th><th>최종 조정률 (%)<br/>(${year}년 적용)</th></tr>`;
        let gdpBody = allTypes.map(type => {
            const gdpGrowth = appData.bulk_sgr.gdp_growth[calcYear]?.total || 0;
            const revalGrowth = appData.bulk_sgr.reval_growth[calcYear]?.[type] || 0;
            const finalRate = appData.history.GDP[year]?.[type] || 0;

            return `<tr>
                <td style="font-weight:600; text-align:left; padding-left:1rem;">${type}</td>
                <td style="font-family: monospace; font-weight: 600;">${gdpGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 600;">${revalGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 700; color: var(--accent-primary);">${finalRate.toFixed(2)}</td>
            </tr>`;
        }).join('');

        // 2. MEI 증가율 모형
        // 공식: MEI 증가율 - 상대가치 변화율
        let meiHead = `<tr><th>종별</th><th>MEI 증가율 (%)<br/>(${calcYear}년)</th><th>상대가치 변화율 (%)<br/>(${calcYear}년)</th><th>최종 조정률 (%)<br/>(${year}년 적용)</th></tr>`;
        let meiBody = allTypes.map(type => {
            const meiGrowth = appData.bulk_sgr.mei_growth[calcYear]?.[type] || 0;
            const revalGrowth = appData.bulk_sgr.reval_growth[calcYear]?.[type] || 0;
            const finalRate = appData.history.MEI[year]?.[type] || 0;

            return `<tr>
                <td style="font-weight:600; text-align:left; padding-left:1rem;">${type}</td>
                <td style="font-family: monospace; font-weight: 600;">${meiGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 600;">${revalGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 700; color: var(--accent-primary);">${finalRate.toFixed(2)}</td>
            </tr>`;
        }).join('');

        // 3. 거시지표 연계 모형
        // 공식: [GDP + 1/3*(MEI-GDP) if MEI>GDP else GDP] - 상대가치 변화율
        let linkHead = `<tr><th>종별</th><th>실질GDP 증가율 (%)<br/>(${calcYear}년)</th><th>MEI 증가율 (%)<br/>(${calcYear}년)</th><th>연계 조정률 (%)<br/>(계산값)</th><th>상대가치 변화율 (%)<br/>(${calcYear}년)</th><th>최종 조정률 (%)<br/>(${year}년 적용)</th></tr>`;
        let linkBody = allTypes.map(type => {
            const gdpGrowth = appData.bulk_sgr.gdp_growth[calcYear]?.total || 0;
            const meiGrowth = appData.bulk_sgr.mei_growth[calcYear]?.[type] || 0;

            // 거시지표 연계 계산: GDP + (1/3 * (MEI - GDP)) if MEI > GDP, else GDP
            let linkCalc = gdpGrowth;
            if (meiGrowth > gdpGrowth) {
                linkCalc = gdpGrowth + (1 / 3 * (meiGrowth - gdpGrowth));
            }

            const revalGrowth = appData.bulk_sgr.reval_growth[calcYear]?.[type] || 0;
            const finalRate = appData.history.Link[year]?.[type] || 0;

            return `<tr>
                <td style="font-weight:600; text-align:left; padding-left:1rem;">${type}</td>
                <td style="font-family: monospace; font-weight: 600;">${gdpGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 600;">${meiGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 600; color: var(--accent-secondary);">${linkCalc.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 600;">${revalGrowth.toFixed(2)}</td>
                <td style="font-family: monospace; font-weight: 700; color: var(--accent-primary);">${finalRate.toFixed(2)}</td>
            </tr>`;
        }).join('');

        container.innerHTML =
            createTable('macro-gdp-table', gdpHead, gdpBody, `📊 1. GDP 증가율 모형 (${year}년도 환산지수 조정률)<br/><small style="color: var(--text-secondary);">공식: 실질GDP 증가율 - 상대가치 변화율</small>`) +
            createTable('macro-mei-table', meiHead, meiBody, `📈 2. MEI 증가율 모형<br/><small style="color: var(--text-secondary);">공식: MEI 증가율 - 상대가치 변화율</small>`) +
            createTable('macro-link-table', linkHead, linkBody, `🔗 3. 거시지표 연계 모형 (${year}년도 환산지수 조정률)<br/><small style="color: var(--text-secondary);">공식: [GDP + 1/3×(MEI-GDP) if MEI>GDP else GDP] - 상대가치 변화율</small>`);

    } else if (type === 'FINAL_SCENARIO') {
        const models = [
            { key: 'S1', label: 'SGR 현행(S1)' },
            { key: 'S2', label: 'SGR 개선(S2)' },
            { key: 'GDP', label: 'GDP 모형' },
            { key: 'MEI', label: 'MEI 모형' },
            { key: 'Link', label: '거시지표연계' }
        ];

        let headHtml = `<tr><th>구분 (유형/종별)</th>${models.map(m => `<th>${m.label}</th>`).join('')}</tr>`;

        // 1. Individual Types (10 types)
        const individualTypes = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        let body = `<tr><td colspan="${models.length + 1}" style="background: rgba(255,255,255,0.05); font-weight: 800; text-align: left; padding-left: 1rem;">[ 10대 유형별 결과 ]</td></tr>`;
        body += individualTypes.map(ht => {
            let rowCols = `<td style="font-weight:600;">${ht}</td>`;
            models.forEach(m => {
                const val = appData.history[m.key][year]?.[ht];
                const displayVal = val !== undefined ? `${parseFloat(val).toFixed(2)}%` : '-';
                rowCols += `<td style="color: var(--accent-primary); font-weight: 700;">${displayVal}</td>`;
            });
            return `<tr>${rowCols}</tr>`;
        }).join('');

        // 2. Groups (5 groups)
        const groupTypes = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'];
        body += `<tr><td colspan="${models.length + 1}" style="background: rgba(255,255,255,0.05); font-weight: 800; text-align: left; padding-left: 1rem;">[ 5대 종별 및 전체 ]</td></tr>`;
        body += groupTypes.map(gt => {
            let rowCols = `<td style="font-weight:600; color: var(--accent-secondary);">${gt}</td>`;
            models.forEach(m => {
                const val = appData.history[m.key][year]?.[gt];
                const displayVal = val !== undefined ? `${parseFloat(val).toFixed(2)}%` : '-';
                rowCols += `<td style="font-weight: 700;">${displayVal}</td>`;
            });
            return `<tr>${rowCols}</tr>`;
        }).join('');

        container.innerHTML = createTable('final-scen-table', headHtml, body, `💎 ${year}년도 최종 결과 종합 (5대 모형 비교)`);

    } else if (type === 'BULK_RAW') {
        const years = appData.history.years;

        // 1. 생산요소_물가증가율 (%)
        let factorHead = `<tr><th>생산요소별</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;
        const factorFields = [
            { key: '인건비_1', label: '인건비 (1) - 3년평균' }, { key: '인건비_2', label: '인건비 (2) - 3년평균' }, { key: '인건비_3', label: '인건비 (3) - 3년평균' },
            { key: '관리비_1', label: '관리비 (1) - 전년비' }, { key: '관리비_2', label: '관리비 (2) - 전년비' },
            { key: '재료비_1', label: '재료비 (1) - 전년비' }, { key: '재료비_2', label: '재료비 (2) - 전년비' }
        ];
        let factorBody = factorFields.map(f => {
            return `<tr><td style="text-align:left; padding-left:1rem;">${f.label}</td>${years.map(y => `<td>${(appData.bulk_sgr.factor_growth[y]?.[f.key] !== undefined ? appData.bulk_sgr.factor_growth[y][f.key].toFixed(2) : '- ')}</td>`).join('')}</tr>`;
        }).join('');

        // 2. 건강보험대상인구_증가율 (%)
        let popHead = `<tr><th>항목</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;
        let popBody = [
            `<tr><td style="text-align:left; padding-left:1rem;">1. 건보대상 인구 증가율 (S1)</td>${years.map(y => `<td>${(appData.bulk_sgr.pop_growth[y]?.s1 || 0).toFixed(2)}</td>`).join('')}</tr>`,
            `<tr><td style="text-align:left; padding-left:1rem;">2. 건보대상 인구 증가율 (고령화반영, S2)</td>${years.map(y => {
                const idx = appData.bulk_sgr.pop_growth[y]?.s2_index || 1.0;
                const rate = (idx - 1) * 100;
                return `<td>${rate.toFixed(2)}</td>`;
            }).join('')}</tr>`
        ].join('');

        // 3. 1인당실질GDP_증가율 (%)
        let gdpHead = `<tr><th>항목</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;
        let gdpBody = [
            `<tr><td style="text-align:left; padding-left:1rem;">1. 1인당 실질 GDP 증가율 (S1)</td>${years.map(y => `<td>${(appData.bulk_sgr.gdp_growth[y]?.s1 || 0).toFixed(2)}</td>`).join('')}</tr>`,
            `<tr><td style="text-align:left; padding-left:1rem;">2. 1인당 실질 GDP 증가율 (S2: *0.8)</td>${years.map(y => `<td>${(appData.bulk_sgr.gdp_growth[y]?.s2 || 0).toFixed(2)}</td>`).join('')}</tr>`,
            `<tr><td style="text-align:left; padding-left:1rem;">3. 실질GDP 증가율 (총액)</td>${years.map(y => `<td>${(appData.bulk_sgr.gdp_growth[y]?.total || 0).toFixed(2)}</td>`).join('')}</tr>`
        ].join('');

        // 4. 연도별 환산지수_증가율 (%)
        let revalHead = `<tr><th>종별</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;
        let revalBody = appData.groups.map(g => {
            return `<tr><td style="text-align:left; padding-left:1rem;">${g}</td>${years.map(y => `<td style="font-weight:700;">${(appData.bulk_sgr.reval_rates[y]?.[g] || 0).toFixed(2)}</td>`).join('')}</tr>`;
        }).join('');

        // 5. 법과 제도 변화지수 (Index)
        let lawHead = `<tr><th>종별</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;
        let lawBody = appData.groups.filter(g => g !== '전체').map(ht => {
            return `<tr><td style="text-align:left; padding-left:1rem;">${ht}</td>${years.map(y => `<td>${(appData.bulk_sgr.law_changes[y]?.[ht] || 1.0).toFixed(4)}</td>`).join('')}</tr>`;
        }).join('');

        container.innerHTML =
            createTable('bulk-factor-table', factorHead, factorBody, "📊 1. 생산요소_물가 증가율 (%)") +
            createTable('bulk-pop-table', popHead, popBody, "👥 2. 건강보험대상인구_증가율 (%)") +
            createTable('bulk-gdp-table', gdpHead, gdpBody, "📈 3. 1인당실질GDP_증가율 (%)") +
            createTable('bulk-reval-table', revalHead, revalBody, "💰 4. 연도별 환산지수_증가율 (전년비, %)") +
            createTable('bulk-law-table', lawHead, lawBody, "⚖️ 5. 법과 제도 변화지수 (Index, 1.xxxx)");

    } else if (type === 'SGR_INDEX') {
        const years = appData.history.years; // Use analysis years 2014-2028
        const groups = appData.groups.filter(g => !g.includes('(계)'));

        const createSgrIndexBody = (modelKey) => {
            return groups.map(g => {
                let row = `<td>${g}</td>`;
                years.forEach(y => {
                    const val = appData.history[modelKey][y]?.[g];
                    row += `<td>${val !== undefined ? val.toFixed(4) : '-'}</td>`;
                });
                return `<tr>${row}</tr>`;
            }).join('');
        };

        let header = `<tr><th>종별</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;

        container.innerHTML =
            createTable('sgr-idx-s1', header, createSgrIndexBody('SGR_S1_INDEX'), "📊 SGR 산출내역 (현행모형, 지수)") +
            createTable('sgr-idx-s2', header, createSgrIndexBody('SGR_S2_INDEX'), "📊 SGR 산출내역 (개선모형, 지수)");

    } else if (type === 'TARGET_EXP') {
        const years = appData.history.years.filter(y => y <= 2026);
        const groups = appData.groups.filter(g => !g.includes('(계)'));

        const createTargetPopBody = (modelKey) => {
            return groups.map(g => {
                let row = `<td>${g}</td>`;
                years.forEach(y => {
                    const val = appData.history[modelKey][y]?.[g];
                    row += `<td>${val !== undefined ? Math.round(val).toLocaleString() : '-'}</td>`;
                });
                return `<tr>${row}</tr>`;
            }).join('');
        };

        let header = `<tr><th>종별</th>${years.map(y => `<th>${y}년</th>`).join('')}</tr>`;

        container.innerHTML =
            createTable('target-s1', header, createTargetPopBody('Target_S1'), "💰 연도별 목표진료비 (Target V, 현행모형, 단위:원)") +
            createTable('target-s2', header, createTargetPopBody('Target_S2'), "💰 연도별 목표진료비 (Target V, 개선모형, 단위:원)");

    } else if (type === 'SGR_COMP') {
        // Display all years from 2014 to 2028
        const years = appData.history.years || [];
        const displayYears = years.filter(y => y >= 2014 && y <= 2028);

        const FactorMap = {
            'g_s1': { label: '1인당 실질 GDP 증가율 (S1)', type: 'macro' },
            'g_s2': { label: '1인당 실질 GDP 증가율 (S2: *0.8)', type: 'macro' },
            'p_s1': { label: '건보대상 인구 증가율 (S1)', type: 'macro' },
            'p_s2': { label: '건보대상 인구(고령화반영) 증가율 (S2)', type: 'macro' },
            'l': { label: '법제도 변화 지수', type: 'type-specific' },
            'r': { label: '환산지수 재평가(Reval) 지수', type: 'type-specific' }
        };

        // Create table header with years
        let head = `<tr><th style="min-width: 250px;">거시 경제 지표</th>`;
        displayYears.forEach(y => {
            head += `<th>${y}년</th>`;
        });
        head += `</tr>`;

        // Create table body with factor values for each year
        let body = "";
        Object.entries(FactorMap).forEach(([k, info]) => {
            body += `<tr><td style="font-weight: 600; color: var(--text-primary); text-align:left; padding-left:1.5rem;">${info.label}</td>`;

            displayYears.forEach(y => {
                const factors = appData.components.sgr_factors[y] || {};
                const v = factors[k];
                let displayVal = '-';

                if (v !== undefined && v !== null) {
                    displayVal = typeof v === 'number' ? v.toFixed(4) : v;
                }

                body += `<td style="font-family: monospace; font-weight: 600;">${displayVal}</td>`;
            });

            body += `</tr>`;
        });

        container.innerHTML = createTable('sgr-comp-table', head, body, `⚙️ SGR 구성요소 연도별 상세 (2014-2028)`);

        // Enable column highlight on hover
        setTimeout(() => setupColumnHighlight('sgr-comp-table'), 100);
    } else if (type === 'AR_SCENARIO') {
        const arData = appData.bulk_sgr.ar_analysis[year];
        if (!arData || arData.length === 0) {
            container.innerHTML = `<div class="glass" style="padding: 2rem;">해당 연도(${year}년)의 AR모형 시나리오 데이터가 없습니다. (2020-2028년 제공)</div>`;
            return;
        }

        const columns = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국', '병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'];
        const baseRates = ['GDP', 'MEI', 'Link'];

        let fullHtml = `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="font-weight: 800; color: var(--accent-primary);">📌 AR모형 시나리오 분석 (${year}년)</h2>
            <button class="primary" onclick="exportArExcel(${year})">📥 AR 시나리오 엑셀 다운로드</button>
        </div>`;

        baseRates.forEach(br => {
            const filtered = arData.filter(d => d.base_rate === br);
            if (filtered.length === 0) return;

            let head = `<tr><th style="background: rgba(99, 102, 241, 0.2);">거시지표(B)</th><th>MEI(S)</th><th>적용률(r)</th>${columns.map(c => `<th>${c}<br/>(%)</th>`).join('')}</tr>`;
            let body = filtered.map(d => {
                let row = `<td style="font-weight:800; color: var(--accent-primary);">${d.base_rate}</td>`;
                row += `<td style="font-size:0.85rem; color: var(--text-secondary);">${d.mei_scenario}</td>`;
                row += `<td style="font-weight:800; color:var(--accent-secondary); background: rgba(16, 185, 129, 0.05);">${d.r}</td>`;
                columns.forEach(c => {
                    const val = d.rates[c];
                    row += `<td style="font-family: 'Outfit', monospace; font-weight:600;">${val !== undefined ? val.toFixed(2) : '-'}</td>`;
                });
                return `<tr>${row}</tr>`;
            }).join('');

            fullHtml += createTable(`ar-scen-table-${br}`, head, body, `[기본증가율: ${br} 모형] 시나리오 분석 결과`);
        });

        container.innerHTML = fullHtml;

    } else if (type === 'EXCEL_RAW') {
        renderExcelRawView(container);
    }
}

async function renderExcelRawView(container) {
    container.innerHTML = '<div class="glass" style="padding: 3rem; text-align: center;"><div class="spinner"></div><p style="margin-top: 1rem;">Excel 시트 데이터를 로드하고 있습니다...</p></div>';

    try {
        const response = await fetch('/get_excel_raw_data');
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<div class="glass" style="padding: 2rem; color: var(--danger);">오류: ${data.error}</div>`;
            return;
        }

        // Requested Order
        const requestedOrder = ['진료비_실제', '종별비용구조', '생산요소_물가', '1인당GDP', '건보대상', '연도별환산지수', '법과제도', '상대가치변화'];
        const apiSheetNames = Object.keys(data);
        const sheetNames = requestedOrder.filter(name => apiSheetNames.includes(name));

        if (sheetNames.length === 0) {
            container.innerHTML = '<div class="glass" style="padding: 2rem;">데이터가 없습니다.</div>';
            return;
        }

        let html = `
            <div style="margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <div>
                        <h2 style="font-size: 1.5rem; color: var(--accent-primary); font-weight: 800;">📊 기초 데이터 원본 확인 (2010-2028)</h2>
                        <p style="color: var(--text-secondary);">엑셀 파일에서 직접 읽어온 원시자료입니다. 분석(2014-2028)의 기초가 됩니다.</p>
                    </div>
                </div>
                <div class="sheet-tabs glass" style="display: flex; gap: 0.5rem; overflow-x: auto; padding: 0.8rem; border-radius: 12px; background: rgba(255,255,255,0.03);">
                    ${sheetNames.map((name, idx) => `
                        <button class="category-tab ${idx === 0 ? 'active' : ''}" onclick="switchSheetTab('${name}')" id="btn-sheet-${idx}" style="white-space: nowrap;">
                            ${name}
                        </button>
                    `).join('')}
                </div>
            </div>
            <div id="sheetContentContainer" style="min-height: 400px;"></div>
        `;

        container.innerHTML = html;
        window.rawExcelData = data;
        window.rawSheetNames = sheetNames;

        window.switchSheetTab = (sheetName) => {
            const tabs = document.querySelectorAll('.sheet-tabs .category-tab');
            tabs.forEach(t => t.classList.remove('active'));
            const idx = window.rawSheetNames.indexOf(sheetName);
            const activeTab = document.getElementById(`btn-sheet-${idx}`);
            if (activeTab) activeTab.classList.add('active');

            const contentArea = document.getElementById('sheetContentContainer');
            const sheetData = window.rawExcelData[sheetName];

            if (!sheetData) {
                contentArea.innerHTML = '<div class="glass" style="padding: 2rem;">데이터를 찾을 수 없습니다.</div>';
                return;
            }

            // Enhanced Table Rendering
            const integerSheets = ['진료비_실제', '1인당GDP', '건보대상'];
            const decimalSheets = {
                '생산요소_물가': 4,
                '법과제도': 4,
                '상대가치변화': 4,
                '종별비용구조': 4,
                '연도별환산지수': 2
            };
            const isIntegerSheet = integerSheets.includes(sheetName);

            let headHtml = `<tr>${sheetData.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
            let bodyHtml = sheetData.rows.map(row => {
                let rowCols = row.map((cell, cellIdx) => {
                    let displayVal = cell;

                    if (cell === null || cell === undefined) displayVal = '-';
                    else if (typeof cell === 'number') {
                        // Years/Index columns should be integers
                        if (cellIdx === 0) {
                            displayVal = Math.round(cell).toString();
                        } else if (isIntegerSheet) {
                            displayVal = Math.round(cell).toLocaleString();
                        } else if (decimalSheets[sheetName]) {
                            displayVal = cell.toLocaleString(undefined, {
                                minimumFractionDigits: decimalSheets[sheetName],
                                maximumFractionDigits: decimalSheets[sheetName]
                            });
                        } else {
                            // Default behavior
                            if (Number.isInteger(cell)) displayVal = cell.toLocaleString();
                            else displayVal = cell.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 4 });
                        }
                    }
                    return `<td style="text-align: center; font-family: monospace; min-width: 80px;">${displayVal}</td>`;
                }).join('');
                return `<tr>${rowCols}</tr>`;
            }).join('');

            contentArea.innerHTML = `
                <div class="glass" style="overflow-x: auto; border-radius: 12px; border: 1px solid var(--border-glass); animation: slideUp 0.4s ease-out;">
                    <div style="background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent); padding: 1.5rem; border-bottom: 1px solid var(--border-glass); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="font-weight: 800; color: var(--accent-primary); margin: 0;">📋 시트명: ${sheetName}</h3>
                        <span style="font-size: 0.8rem; background: rgba(255,255,255,0.05); padding: 0.3rem 0.8rem; border-radius: 20px;">Rows: ${sheetData.rows.length}</span>
                    </div>
                    <div style="max-height: 600px; overflow-y: auto;">
                        <table class="detail-display-table" style="width: 100%; border-collapse: separate; border-spacing: 0;">
                            <thead style="position: sticky; top: 0; z-index: 10; background: var(--bg-dark);">${headHtml}</thead>
                            <tbody>${bodyHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        };

        window.switchSheetTab(sheetNames[0]);

    } catch (err) {
        console.error("Excel raw load failed:", err);
        container.innerHTML = '<div class="glass" style="padding: 2rem; color: var(--danger);">데이터를 불러오는 중 오류가 발생했습니다.</div>';
    }
}

async function saveAllToExcelFile(mode = 'final') {
    if (mode === 'final') {
        if (!confirm('현재까지의 모든 수정사항을 원본 엑셀 파일(SGR_data.xlsx)에 저장하시겠습니까?')) return;
        if (!confirm('정말로 저장하시겠습니까?\n이 작업은 원본 데이터가 영구적으로 업데이트되며 원본 파일이 직접 수정됩니다.')) return;
    }

    // Collect all data similar to triggerGlobalSimulation
    const allOverrides = {};

    function getMeiCode(field) {
        const typeChar = field.startsWith('인건비') ? 'I' : field.startsWith('관리비') ? 'M' : 'Z';
        return typeChar + field.split('_')[1];
    }

    // MEI
    for (const year in userData.mei) {
        for (const field in userData.mei[year]) {
            // field in userData.mei should already be English codes like I1
            allOverrides[`${field}_${year}`] = userData.mei[year][field];
        }
    }
    // GDP
    for (const year in userData.gdp) {
        if (userData.gdp[year].value !== undefined) allOverrides[`GDP_${year}`] = userData.gdp[year].value;
        if (userData.gdp[year].pop !== undefined) allOverrides[`POP_${year}`] = userData.gdp[year].pop;
    }
    // Population
    for (const year in userData.population) {
        if (userData.population[year].basic !== undefined) allOverrides[`NHI_POP_${year}`] = userData.population[year].basic;
    }
    // Law
    for (const year in userData.law) {
        for (const type in userData.law[year]) {
            allOverrides[`LAW_${type}_${year}`] = userData.law[year][type];
        }
    }
    // RV
    for (const year in userData.rv) {
        for (const type in userData.rv[year]) {
            allOverrides[`RV_${type}_${year}`] = userData.rv[year][type];
        }
    }
    // Medical
    for (const year in userData.medical) {
        for (const type in userData.medical[year]) {
            allOverrides[`${type}_${year}`] = userData.medical[year][type];
        }
    }
    // CF
    for (const year in userData.cf) {
        for (const type in userData.cf[year]) {
            allOverrides[`CF_${type}_${year}`] = userData.cf[year][type];
        }
    }
    // Weights
    for (const type in userData.weights) {
        for (const col in userData.weights[type]) {
            allOverrides[`WEIGHT_${type}_${col}`] = userData.weights[type][col];
        }
    }

    try {
        const response = await fetch('/save_to_excel_file', {
            method: 'POST',
            body: JSON.stringify({ overrides: allOverrides, mode: mode }),
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();

        if (result.success) {
            if (mode === 'final') {
                alert('✅ 저장되었습니다. 원본 엑셀 파일이 갱신되었습니다.');
                resetAllData();
            } else {
                showToast(`📂 임시 엑셀 저장 완료: ${result.message.split(': ')[1]}`);
            }
        } else {
            console.error('Save failed:', result.error);
            if (mode === 'final') alert('❌ 저장 실패: ' + result.error);
        }
    } catch (e) {
        console.error(e);
        if (mode === 'final') alert('저장 중 오류가 발생했습니다.');
    }
}

function resetAllData() {
    originalData = null; // Clear cache
    userData = { mei: {}, medical: {}, cf: {}, population: {}, gdp: {}, law: {}, rv: {}, weights: {} };
    initAllDataTables();
    triggerGlobalSimulation(); // Re-run sim with clear overrides (which means using loaded excel data)
}

async function updateSimulation() {
    // Legacy function, might not be needed if we use triggerGlobalSimulation
    // But keeping it just in case
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}



function exportArExcel(year) {
    if (!year) year = document.getElementById('detailYearSelector')?.value || 2025;
    window.location.href = `/download_ar/${year}`;
}

function exportExcel() {
    const year = document.getElementById('detailYearSelector')?.value || 2025;
    window.location.href = `/download/${year}`;
}

/**
 * 대시보드 상단에 모든 모형의 조정률을 비교하는 테이블 렌더링
 */
function renderDashboardComparison() {
    const year = parseInt(document.getElementById('dashboardYearSelector')?.value || 2025);
    const container = document.getElementById('dashboardComparisonContainer');
    if (!container) return;

    const models = [
        { key: 'S1', label: '현행 SGR (S1)', color: '#6366f1' },
        { key: 'S2', label: '개선 SGR (S2)', color: '#10b981' },
        { key: 'GDP', label: 'GDP 모형', color: '#f59e0b' },
        { key: 'MEI', label: 'MEI 모형', color: '#ec4899' },
        { key: 'Link', label: '거시연계', color: '#8b5cf6' }
    ];

    const groups = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'];

    let html = `<table class="detail-display-table" style="font-size: 0.9rem;">
        <thead>
            <tr>
                <th>분석 대상 (종별)</th>`;
    models.forEach(m => {
        html += `<th style="color: ${m.color}; background: rgba(255,255,255,0.03);">${m.label}</th>`;
    });
    html += `</tr>
        </thead>
        <tbody>`;

    groups.forEach(g => {
        const isTotal = g === '전체';
        html += `<tr style="${isTotal ? 'background: rgba(99, 102, 241, 0.1);' : ''}">
            <td style="font-weight: 800; text-align: left; padding-left: 1.5rem;">${g}</td>`;
        models.forEach(m => {
            const val = appData.history[m.key][year]?.[g];
            const displayVal = val !== undefined ? `${parseFloat(val).toFixed(2)}%` : '-';
            html += `<td style="font-weight: 800; color: ${m.color}; font-size: 1.1rem;">${displayVal}</td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

/**
 * 원시자료 확인 탭 초기화
 */
function initRawDataView() {
    const container = document.getElementById('rawDataContainer');
    if (container) {
        renderExcelRawView(container);
    }
}

// Data Category Switching
function switchDataCategory(category, el) {
    console.log("Switching to data category:", category);

    // Update tabs
    document.querySelectorAll('.category-tab').forEach(tab => tab.classList.remove('active'));

    if (el) {
        el.classList.add('active');
    } else {
        // Find by text or target if el is not provided
        document.querySelectorAll('.category-tab').forEach(tab => {
            if (tab.getAttribute('onclick')?.includes(`'${category}'`)) {
                tab.classList.add('active');
            }
        });
    }

    // Update content visibility
    document.querySelectorAll('.data-category-content').forEach(content => content.classList.remove('active'));
    const contentEl = document.getElementById(`data-${category}`);
    if (contentEl) contentEl.classList.add('active');

    // Initialize the table for the selected category
    try {
        switch (category) {
            case 'mei': initMeiTable(); break;
            case 'medical': initMedicalTable(); break;
            case 'cf': initCfTable(); break;
            case 'population': initPopTable(); break;
            case 'gdp': initGdpTable(); break;
            case 'law': initLawTable(); break;
            case 'rv': initRvTable(); break;
            case 'weights': initWeightsTable(); break;
        }
    } catch (err) {
        console.error(`Error loading category ${category}:`, err);
    }
}



function renderInsightReport() {
    const selectedYear = document.getElementById('dashboardYearSelector')?.value || 2025;
    const insightBox = document.getElementById('aiInsight');
    const summaryBox = document.getElementById('summaryDashboard');
    const modelKey = appData.model_name_map[appData.selected_model] || 'S2';
    const modelDisplayName = appData.selected_model;

    const cfSelected = appData.history[modelKey][selectedYear];
    const targetGroups = ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)'];
    const topGroup = [...targetGroups].sort((a, b) => cfSelected[b] - cfSelected[a])[0];
    const bottomGroup = [...targetGroups].sort((a, b) => cfSelected[a] - cfSelected[b])[0];
    const avgVal = cfSelected['전체'];

    if (!insightBox || !summaryBox) return;

    insightBox.innerHTML = `
        <div style="background: rgba(99, 102, 241, 0.1); padding: 1.5rem; border-radius: 12px; border-left: 4px solid var(--accent-primary);">
            <p><b>[${selectedYear}년 ${modelDisplayName} 전망 요약]</b></p>
            <p style="margin-top: 0.5rem;">선택하신 <b>${modelDisplayName}</b> 기준, 전체 평균 조정률은 <b>${parseFloat(avgVal).toFixed(2)}%</b>로 산출되었습니다.</p>
        </div>
        <p style="margin-top: 1.5rem;">유형별로는 <b>${topGroup}</b>이 가장 높은 인상 압력을 받고 있으며, <b>${bottomGroup}</b>은 상대적으로 낮은 수준을 유지하고 있습니다.</p>
        <p style="margin-top: 1rem;">이 결과는 입력된 최신 기초자료와 선택된 분석 모성을 바탕으로 실시간 계산된 값입니다.</p>
    `;

    summaryBox.innerHTML = '';
    const mainGroups = ['전체', '병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)'];
    mainGroups.forEach(g => {
        const val = cfSelected[g];
        summaryBox.innerHTML += `
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 12px; border: 1px solid var(--border-glass);">
                <span style="font-weight: 500;">${g}</span>
                <span style="font-weight: 800; font-size: 1.2rem; color: ${val >= 0 ? 'var(--success)' : 'var(--danger)'}">${parseFloat(val).toFixed(1)}%</span>
            </div>
        `;
    });
}

// Model Selection Sync
function syncModelSelection(model) {
    if (document.getElementById('dashboardModelSelector')) {
        document.getElementById('dashboardModelSelector').value = model;
    }
    if (document.getElementById('dataEntryModelSelector')) {
        document.getElementById('dataEntryModelSelector').value = model;
    }
    if (typeof updateModelSelection === 'function') {
        updateModelSelection();
    }
}

// Column Highlight Helper
function setupColumnHighlight(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    table.addEventListener('mouseover', (e) => {
        const cell = e.target.closest('td, th');
        if (!cell) return;
        const colIndex = cell.cellIndex;
        if (colIndex === undefined || colIndex < 0) return;

        table.querySelectorAll(`tr > *:nth-child(${colIndex + 1})`).forEach(el => {
            el.classList.add('col-highlight');
        });
    });

    table.addEventListener('mouseout', (e) => {
        const cell = e.target.closest('td, th');
        if (!cell) return;
        table.querySelectorAll('.col-highlight').forEach(el => {
            el.classList.remove('col-highlight');
        });
    });
}

// Fetch original data from backend
async function fetchOriginalData() {
    if (originalData) return originalData;
    if (originalDataPromise) return originalDataPromise;

    console.log("Fetching original data...");
    originalDataPromise = fetch('/get_original_data')
        .then(async response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            originalData = data;
            return originalData;
        })
        .catch(err => {
            console.error('Error fetching original data:', err);
            originalDataPromise = null; // Allow retry
            throw err;
        });

    return originalDataPromise;
}

// Initialize MEI table
async function initMeiTable() {
    const tbody = document.getElementById('mei-table-body');
    if (!tbody) return;

    // Show loading state
    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const fields = [
            { key: '인건비_1', label: '인건비_1 (원)', type: 'number' },
            { key: '인건비_2', label: '인건비_2 (원)', type: 'number' },
            { key: '인건비_3', label: '인건비_3 (원)', type: 'number' },
            { key: '관리비_1', label: '관리비_1 (지수)', type: 'number', step: '0.0001' },
            { key: '관리비_2', label: '관리비_2 (지수)', type: 'number', step: '0.0001' },
            { key: '재료비_1', label: '재료비_1 (지수)', type: 'number', step: '0.0001' },
            { key: '재료비_2', label: '재료비_2 (지수)', type: 'number', step: '0.0001' }
        ];

        const years = DATA_YEARS;
        updateTableHeader('mei-table', '항목');

        function getMeiCode(fieldKey) {
            const parts = fieldKey.split('_');
            const typeChar = parts[0] === '인건비' ? 'I' : parts[0] === '관리비' ? 'M' : 'Z';
            return typeChar + parts[1];
        }

        fields.forEach(field => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="white-space:nowrap; text-align:left; font-weight:600;">${field.label}</td>`;

            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = field.type;
                if (field.step) input.step = field.step;

                const originalValue = data.mei[field.key]?.[year];
                const meiCode = getMeiCode(field.key);
                const userValue = userData.mei[year]?.[meiCode];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(4) : '';
                input.dataset.field = field.key;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(4) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });

                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('mei-table');
        setupColumnHighlight('mei-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">데이터 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveMeiData() {
    const tbody = document.getElementById('mei-table-body');
    const rows = tbody.querySelectorAll('tr');
    const years = DATA_YEARS;

    let savedCount = 0;

    rows.forEach(row => {
        const cells = row.querySelectorAll('td:not(:first-child)');
        cells.forEach((cell, index) => {
            const input = cell.querySelector('input');
            if (input && input.value) {
                const year = years[index];
                const field = input.dataset.field;
                const parts = field.split('_');
                const typeChar = parts[0] === '인건비' ? 'I' : parts[0] === '관리비' ? 'M' : 'Z';
                const fieldCode = typeChar + parts[1];

                if (!userData.mei[year]) userData.mei[year] = {};
                userData.mei[year][fieldCode] = parseFloat(input.value);
                savedCount++;
            }
        });
    });

    showToast(`✅ MEI 데이터 ${savedCount}개 항목이 저장되었습니다.`);
    modifiedCells.clear();

    // Remove modified highlights
    tbody.querySelectorAll('td.modified').forEach(td => td.classList.remove('modified'));
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetMeiData() {
    if (!confirm('모든 수정사항을 취소하고 원본 데이터로 복원하시겠습니까?')) return;

    // Clear user data for MEI
    userData.mei = {};
    modifiedCells.clear();

    // Reload table
    initMeiTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

function triggerGlobalSimulation() {
    // Collect all user data and send to simulate
    const allOverrides = {};

    // MEI
    for (const year in userData.mei) {
        for (const field in userData.mei[year]) {
            allOverrides[`${field}_${year}`] = userData.mei[year][field];
        }
    }
    // GDP
    for (const year in userData.gdp) {
        if (userData.gdp[year].value !== undefined) allOverrides[`GDP_${year}`] = userData.gdp[year].value;
        if (userData.gdp[year].pop !== undefined) allOverrides[`POP_${year}`] = userData.gdp[year].pop;
    }
    // Population
    for (const year in userData.population) {
        if (userData.population[year].basic !== undefined) allOverrides[`NHI_POP_${year}`] = userData.population[year].basic;
    }
    // Law
    for (const year in userData.law) {
        for (const type in userData.law[year]) {
            allOverrides[`LAW_${type}_${year}`] = userData.law[year][type];
        }
    }
    // RV
    for (const year in userData.rv) {
        for (const type in userData.rv[year]) {
            allOverrides[`RV_${type}_${year}`] = userData.rv[year][type];
        }
    }
    // Medical
    for (const year in userData.medical) {
        for (const type in userData.medical[year]) {
            allOverrides[`${type}_${year}`] = userData.medical[year][type];
        }
    }
    // CF
    for (const year in userData.cf) {
        for (const type in userData.cf[year]) {
            allOverrides[`CF_${type}_${year}`] = userData.cf[year][type];
        }
    }
    // Weights
    for (const type in userData.weights) {
        for (const col in userData.weights[type]) {
            // Override format for weights: WEIGHT_{TYPE}_{COL} (e.g. WEIGHT_병원_인건비)
            // But python apply_overrides usually expects FIELD_YEAR.
            // Wait, Python code for 'weights' is usually static. 
            // My Python `_apply_overrides` does NOT have a case for `WEIGHTS`.
            // I need to update Python code to handle weights override too!
            // I'll assume I will add `WEIGHT_{TYPE}_{COL}` handling in Python.
            // Or use a dummy year like 9999?
            // Let's use generic key and update Python later: WEIGHT_{TYPE}_{COL}
            allOverrides[`WEIGHT_${type}_${col}`] = userData.weights[type][col];
        }
    }

    // Weights
    for (const type in userData.weights) {
        for (const col in userData.weights[type]) {
            allOverrides[`WEIGHT_${type}_${col}`] = userData.weights[type][col];
        }
    }

    updateSimulationWithData(allOverrides);
}

async function updateSimulationWithData(overrides) {
    try {
        const response = await fetch('/simulate', {
            method: 'POST',
            body: JSON.stringify(overrides),
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (result.success) {
            appData = result.analysis_data;
            renderAllViews();
        }
    } catch (e) {
        console.error(e);
    }
}

function renderAllViews() {
    renderCharts();
    renderDetailTable();
    renderInsightReport();
}

// --- Medical Data (실제진료비) ---
async function initMedicalTable() {
    const tbody = document.getElementById('medical-table-body');
    if (!tbody) return;

    updateTableHeader('medical-table', '종별');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const years = DATA_YEARS;

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.1';

                const originalValue = data.medical[type]?.[year];
                const userValue = userData.medical[year]?.[type];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                // Using toFixed(1) for consistent 1 decimal place as requested
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(1) : '';
                input.dataset.type = type;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(1) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('medical-table');
        setupColumnHighlight('medical-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">진료비 데이터 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveMedicalData() {
    const tbody = document.getElementById('medical-table-body');
    const inputs = tbody.querySelectorAll('input');
    inputs.forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.medical[year]) userData.medical[year] = {};
            userData.medical[year][input.dataset.type] = parseFloat(input.value);
        }
    });
    showToast('✅ 실제진료비 데이터가 저장되었습니다.');
    initMedicalTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetMedicalData() {
    if (!confirm('실제진료비 수정을 취소하시겠습니까?')) return;
    userData.medical = {};
    initMedicalTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- CF Data (환산지수) ---
async function initCfTable() {
    const tbody = document.getElementById('cf-table-body');
    if (!tbody) return;

    updateTableHeader('cf-table', '종별');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const years = DATA_YEARS;

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.01';

                const originalValue = data.cf[type]?.[year];
                const userValue = userData.cf[year]?.[type];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(2) : '';
                input.dataset.type = type;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(2) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('cf-table');
        setupColumnHighlight('cf-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">환산지수 데이터 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveCfData() {
    const tbody = document.getElementById('cf-table-body');
    const inputs = tbody.querySelectorAll('input');
    inputs.forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.cf[year]) userData.cf[year] = {};
            userData.cf[year][input.dataset.type] = parseFloat(input.value);
        }
    });
    showToast('✅ 환산지수 데이터가 저장되었습니다.');
    initCfTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetCfData() {
    if (!confirm('환산지수 수정을 취소하시겠습니까?')) return;
    userData.cf = {};
    initCfTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- Population Data (건보대상자수) ---
async function initPopTable() {
    const tbody = document.getElementById('pop-table-body');
    if (!tbody) return;

    updateTableHeader('pop-table', '항목');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const items = [{ key: 'basic', label: '건보대상자수 (기본)' }, { key: 'aged', label: '건보대상자수 (고령화 반영)' }];
        const years = DATA_YEARS;

        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${item.label}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '1';

                const valObj = data.population[year] || {};
                const originalValue = (item.key === 'basic') ? valObj.basic : valObj.aged;
                const userValue = userData.population[year]?.[item.key];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(0) : '';
                input.dataset.key = item.key;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(0) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('pop-table');
        setupColumnHighlight('pop-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">건보대상자 로드 실패: ${e.message}</td></tr>`;
    }
}

function savePopData() {
    const tbody = document.getElementById('pop-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.population[year]) userData.population[year] = {};
            userData.population[year][input.dataset.key] = parseFloat(input.value);
        }
    });
    showToast('✅ 건보대상자수 데이터가 저장되었습니다.');
    initPopTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetPopData() {
    if (!confirm('건보대상자수 수정을 취소하시겠습니까?')) return;
    userData.population = {};
    initPopTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- GDP Data (1인당 실질GDP) ---
async function initGdpTable() {
    const tbody = document.getElementById('gdp-table-body');
    if (!tbody) return;

    updateTableHeader('gdp-table', '항목');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const items = [{ key: '실질GDP', label: '실질GDP (십억원)' }, { key: '영안인구', label: '영안인구 (명)' }];
        const years = DATA_YEARS;

        items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${item.label}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';

                const originalValue = data.gdp[year]?.[item.key];
                const userValue = userData.gdp[year]?.[item.key === '실질GDP' ? 'value' : 'pop'];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toLocaleString(undefined, { maximumFractionDigits: 1 }).replace(/,/g, '') : '';
                input.dataset.key = item.key;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(1) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('gdp-table');
        setupColumnHighlight('gdp-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">GDP 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveGdpData() {
    const tbody = document.getElementById('gdp-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.gdp[year]) userData.gdp[year] = {};
            const key = input.dataset.key === '실질GDP' ? 'value' : 'pop';
            userData.gdp[year][key] = parseFloat(input.value);
        }
    });
    showToast('✅ GDP 데이터가 저장되었습니다.');
    initGdpTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetGdpData() {
    if (!confirm('GDP 수정을 취소하시겠습니까?')) return;
    userData.gdp = {};
    initGdpTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- Law Data (법과제도변화) ---
async function initLawTable() {
    const tbody = document.getElementById('law-table-body');
    if (!tbody) return;

    updateTableHeader('law-table', '종별');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const years = DATA_YEARS;

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.0001';

                const originalValue = data.law[type]?.[year];
                const userValue = userData.law[year]?.[type];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(4) : '';
                input.dataset.type = type;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(4) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('law-table');
        setupColumnHighlight('law-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">법자료 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveLawData() {
    const tbody = document.getElementById('law-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.law[year]) userData.law[year] = {};
            userData.law[year][input.dataset.type] = parseFloat(input.value);
        }
    });
    showToast('✅ 법과제도변화 데이터가 저장되었습니다.');
    initLawTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetLawData() {
    if (!confirm('법과제도 수정을 취소하시겠습니까?')) return;
    userData.law = {};
    initLawTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- RV Data (상대가치변화율) ---
async function initRvTable() {
    const tbody = document.getElementById('rv-table-body');
    if (!tbody) return;

    updateTableHeader('rv-table', '종별');

    if (tbody.children.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" style="text-align:center; padding: 2rem;">데이터를 불러오는 중입니다...</td></tr>';
    }

    try {
        const data = await fetchOriginalData();
        tbody.innerHTML = '';

        const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
        const years = DATA_YEARS;

        types.forEach(type => {
            const row = document.createElement('tr');
            row.innerHTML = `<td style="font-weight:600; text-align:left;">${type}</td>`;
            years.forEach(year => {
                const td = document.createElement('td');
                const input = document.createElement('input');
                input.className = 'editable-input';
                input.type = 'number';
                input.step = '0.0001';

                const originalValue = data.rv[type]?.[year];
                const userValue = userData.rv[year]?.[type];

                const displayValue = userValue !== undefined ? userValue : originalValue;
                input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(4) : '';
                input.dataset.type = type;
                input.dataset.year = year;
                input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(4) : '';

                if (parseInt(year) < 2022) {
                    input.disabled = true;
                    input.style.backgroundColor = 'rgba(255,255,255,0.05)';
                    input.style.color = 'var(--text-secondary)';
                    input.style.cursor = 'not-allowed';
                }

                if (userValue !== undefined && parseFloat(userValue) !== parseFloat(originalValue)) {
                    td.classList.add('modified');
                }

                input.addEventListener('input', function () {
                    const newValue = parseFloat(this.value);
                    const origValue = parseFloat(this.dataset.original);
                    if (this.value && newValue !== origValue) {
                        td.classList.add('modified');
                    } else {
                        td.classList.remove('modified');
                    }
                });
                td.appendChild(input);
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
        setupTableNavigation('rv-table');
        setupColumnHighlight('rv-table');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="20" style="text-align:center; padding: 2rem; color: var(--danger);">상대가치 로드 실패: ${e.message}</td></tr>`;
    }
}

function saveRvData() {
    const tbody = document.getElementById('rv-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const year = input.dataset.year;
            if (!userData.rv[year]) userData.rv[year] = {};
            userData.rv[year][input.dataset.type] = parseFloat(input.value);
        }
    });
    showToast('✅ 상대가치변화율 데이터가 저장되었습니다.');
    initRvTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetRvData() {
    if (!confirm('상대가치변화율 수정을 취소하시겠습니까?')) return;
    userData.rv = {};
    initRvTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// --- Weights Data (종별비용구조) ---
async function initWeightsTable() {
    const data = await fetchOriginalData();
    if (!data || !data.weights) return;
    const tbody = document.getElementById('weights-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국'];
    const cols = ['인건비', '관리비', '재료비'];

    types.forEach(type => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${type}</td>`;
        cols.forEach(col => {
            const td = document.createElement('td');
            const input = document.createElement('input');
            input.type = 'number';
            input.step = '0.01';

            const originalValue = data.weights[type]?.[col];
            const userValue = userData.weights[type]?.[col];

            const displayValue = userValue !== undefined ? userValue : originalValue;
            input.value = (displayValue !== undefined && displayValue !== null) ? parseFloat(displayValue).toFixed(2) : '';
            input.dataset.type = type;
            input.dataset.col = col;
            input.dataset.original = (originalValue !== undefined && originalValue !== null) ? parseFloat(originalValue).toFixed(2) : '';

            if (userValue !== undefined && userValue != originalValue) td.classList.add('modified');

            input.addEventListener('input', function () {
                if (this.value && parseFloat(this.value) != parseFloat(this.dataset.original)) td.classList.add('modified');
                else td.classList.remove('modified');
            });
            td.appendChild(input);
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });
    setupTableNavigation('weights-table');
    setupColumnHighlight('weights-table');
}

function saveWeightsData() {
    const tbody = document.getElementById('weights-table-body');
    tbody.querySelectorAll('input').forEach(input => {
        if (input.value) {
            const type = input.dataset.type;
            const col = input.dataset.col;
            if (!userData.weights[type]) userData.weights[type] = {};
            userData.weights[type][col] = parseFloat(input.value);
        }
    });
    showToast('✅ 종별비용구조 데이터가 저장되었습니다.');
    initWeightsTable();
    triggerGlobalSimulation();
    saveAllToExcelFile('temp');
}

function resetWeightsData() {
    if (!confirm('종별비용구조 수정을 취소하시겠습니까?')) return;
    userData.weights = {};
    initWeightsTable().then(() => {
        showToast('✅ 원본 데이터로 복원되었습니다.', 'success');
        triggerGlobalSimulation();
    });
}

// Toast notification helper
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'glass';
    const bgColor = type === 'success' ? 'var(--success)' : type === 'warning' ? 'var(--warning)' : 'var(--accent-primary)';
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        padding: 1.2rem 2rem;
        background: ${bgColor};
        color: white;
        border-radius: 12px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles if not already present
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// View All Data Functions are now integrated into the editable tables
// Removed: viewAllMeiData, viewAllMedicalData, viewAllCfData, viewAllPopData, viewAllGdpData, viewAllLawData, viewAllRvData


// Modal Display Function
function showModal(title, content) {
    // Remove existing modal if any
    const existingModal = document.getElementById('dataModal');
    if (existingModal) existingModal.remove();

    const modal = document.createElement('div');
    modal.id = 'dataModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;

    const modalContent = document.createElement('div');
    modalContent.className = 'glass';
    modalContent.style.cssText = `
        max-width: 90%;
        max-height: 85%;
        overflow: auto;
        padding: 2rem;
        border-radius: 16px;
        background: var(--bg-surface);
    `;

    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: var(--accent-primary);">${title}</h2>
            <button onclick="closeModal()" style="background: var(--danger); color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 600;">✕ 닫기</button>
        </div>
        <div style="overflow-x: auto;">
            ${content}
        </div>
    `;

    modal.appendChild(modalContent);
    document.body.appendChild(modal);

    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
}

function closeModal() {
    const modal = document.getElementById('dataModal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    }
}

// Add modal animation styles
if (!document.getElementById('modal-animations')) {
    const style = document.createElement('style');
    style.id = 'modal-animations';
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        #dataModal table th,
        #dataModal table td {
            padding: 0.75rem;
            text-align: center;
            border: 1px solid var(--border-glass);
        }
        #dataModal table th {
            background: rgba(99, 102, 241, 0.2);
            color: var(--accent-primary);
            font-weight: 700;
        }
        #dataModal table tr:hover td {
            background: rgba(255, 255, 255, 0.05);
        }
    `;
    document.head.appendChild(style);
}

// Helper for table navigation
function setupTableNavigation(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    table.addEventListener('keydown', function (e) {
        const input = e.target;
        if (input.tagName !== 'INPUT') return;

        const td = input.parentElement;
        const tr = td.parentElement;
        const columnIndex = Array.from(tr.children).indexOf(td);

        let nextRow = null;
        let nextTd = null;

        if (e.key === 'Enter') {
            e.preventDefault();
            nextRow = tr.nextElementSibling;
            if (nextRow) {
                nextTd = nextRow.children[columnIndex];
                if (nextTd && nextTd.querySelector('input')) {
                    nextTd.querySelector('input').focus();
                    nextTd.querySelector('input').select();
                }
            }
        } else if (e.key === 'ArrowDown') {
            nextRow = tr.nextElementSibling;
            if (nextRow) {
                nextTd = nextRow.children[columnIndex];
                if (nextTd && nextTd.querySelector('input')) nextTd.querySelector('input').focus();
            }
        } else if (e.key === 'ArrowUp') {
            nextRow = tr.previousElementSibling;
            if (nextRow) {
                nextTd = nextRow.children[columnIndex];
                if (nextTd && nextTd.querySelector('input')) nextTd.querySelector('input').focus();
            }
        } else if (e.key === 'ArrowRight' && input.selectionEnd === input.value.length) {
            nextTd = td.nextElementSibling;
            if (nextTd && nextTd.querySelector('input')) nextTd.querySelector('input').focus();
        } else if (e.key === 'ArrowLeft' && input.selectionStart === 0) {
            nextTd = td.previousElementSibling;
            if (nextTd && nextTd.querySelector('input')) nextTd.querySelector('input').focus();
        }
    });
}

// Show detailed macro/factor breakdown modal
function showMacroDetail(key, highlightYear) {
    const years = [2020, 2021, 2022, 2023, 2024, 2025, 2026];
    let title = "";
    let content = "";

    const formatVal = (v, digits = 4) => (typeof v === 'number' ? v.toFixed(digits) : v || '0');
    const getYearStyle = (y) => (parseInt(y) === parseInt(highlightYear) ? 'background: rgba(99, 102, 241, 0.4); font-weight: 800; color: #fff; border: 2px solid var(--accent-primary) !important;' : '');

    if (key === 'g_s1' || key === 'g_s2') {
        title = key === 'g_s1' ? "1인당 실질 GDP 증가율 (S1)" : "1인당 실질 GDP 증가율 (S2: *0.8)";
        const variant = key === 'g_s1' ? 's1' : 's2';
        content = `<div class="glass" style="padding: 1rem; border-radius: 12px;">
            <table style="width: 100%; border-collapse: collapse;">
            <thead><tr>${years.map(y => `<th style="${getYearStyle(y)}">${y}년</th>`).join('')}</tr></thead>
            <tbody><tr>${years.map(y => `<td style="${getYearStyle(y)}">${formatVal(appData.bulk_sgr.gdp_growth[y]?.[variant] / 100 + 1)}</td>`).join('')}</tr>
            <tr style="font-size: 0.8rem; color: var(--text-secondary);">
                ${years.map(y => `<td style="border: none; ${getYearStyle(y)}">(${formatVal(appData.bulk_sgr.gdp_growth[y]?.[variant], 2)}%)</td>`).join('')}
            </tr>
            </tbody></table></div>`;
    }
    else if (key === 'p_s1' || key === 'p_s2') {
        title = key === 'p_s1' ? "건보대상 인구 증가율 (S1)" : "건보대상 인구 증가율 (S2: 고령화)";
        const variant = key === 'p_s1' ? 's1' : 's2';
        content = `<div class="glass" style="padding: 1rem; border-radius: 12px;">
            <table style="width: 100%; border-collapse: collapse;">
            <thead><tr>${years.map(y => `<th style="${getYearStyle(y)}">${y}년</th>`).join('')}</tr></thead>
            <tbody><tr>${years.map(y => {
            let idxVal = 0;
            if (variant === 's2') {
                // Use explicit index if available
                idxVal = appData.bulk_sgr.pop_growth[y]?.s2_index || ((appData.bulk_sgr.pop_growth[y]?.s2 || 0) / 100 + 1);
            } else {
                // S1 is stored as growth rate (%)
                idxVal = (appData.bulk_sgr.pop_growth[y]?.s1 || 0) / 100 + 1;
            }
            return `<td style="${getYearStyle(y)}">${formatVal(idxVal, 4)}</td>`;
        }).join('')}</tr>
            <tr style="font-size: 0.8rem; color: var(--text-secondary);">
                ${years.map(y => {
            let rateVal = 0;
            if (variant === 's2') {
                const idx = appData.bulk_sgr.pop_growth[y]?.s2_index || ((appData.bulk_sgr.pop_growth[y]?.s2 || 0) / 100 + 1);
                rateVal = (idx - 1) * 100;
            } else {
                rateVal = appData.bulk_sgr.pop_growth[y]?.s1 || 0;
            }
            return `<td style="border: none; ${getYearStyle(y)}">(${formatVal(rateVal, 3)}%)</td>`;
        }).join('')}
            </tr>
            </tbody></table></div>`;
    }
    else if (key === 'l' || key === 'r') {
        title = key === 'l' ? "법제도 변화 지수 상세" : "환산지수 재평가(Reval) 지수 상세";
        const dataMap = key === 'l' ? appData.bulk_sgr.law_changes : appData.bulk_sgr.reval_rates;
        const types = appData.groups.filter(g => g !== '전체');

        let rows = "";
        types.forEach(ht => {
            rows += `<tr><td style="font-weight: 700; text-align: left; background: rgba(255,255,255,0.03);">${ht}</td>`;
            years.forEach(y => {
                let val = dataMap[y]?.[ht] || 0;
                let displayVal = 0;
                let pctVal = 0;

                if (key === 'l') {
                    // Law: stored as Index (e.g. 1.0101)
                    displayVal = val;
                    pctVal = (val - 1) * 100;
                } else {
                    // Reval: stored as Percentage (e.g. 1.98) via get_combined
                    displayVal = val / 100 + 1;
                    pctVal = val;
                }

                rows += `<td style="${getYearStyle(y)}">${formatVal(displayVal)}<br><span style="font-size: 0.75rem; opacity: 0.7;">(${formatVal(pctVal, 2)}%)</span></td>`;
            });
            rows += `</tr>`;
        });

        content = `<div style="max-height: 60vh; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
            <thead><tr><th style="position: sticky; top: 0; z-index: 10; background: var(--bg-surface);">구분</th>${years.map(y => `<th style="position: sticky; top: 0; z-index: 10; background: var(--bg-surface); ${getYearStyle(y)}">${y}년</th>`).join('')}</tr></thead>
            <tbody>${rows}</tbody></table></div>`;
    }

    showModal(title, content);
}

// Global variable for modal chart
let modalChart = null;

function expandChart(sourceChartId, title) {
    // Determine the source chart object from our global 'charts' registry
    let sourceChart = null;
    if (sourceChartId === 'mainTrendsChart') sourceChart = charts.trends;
    else if (sourceChartId === 'rankStreamChart') sourceChart = charts.rank;
    else if (sourceChartId === 'typeCompareChart') sourceChart = charts.type;

    if (!sourceChart) {
        console.warn("Source chart not found:", sourceChartId);
        return;
    }

    const overlay = document.getElementById('chartModalOverlay');
    const titleEl = document.getElementById('chartModalTitle');
    const canvas = document.getElementById('expandedChartCanvas');

    if (!overlay || !canvas) {
        console.warn("Modal elements not found");
        return;
    }

    titleEl.textContent = title;
    overlay.classList.add('active');

    // Destroy existing modal chart if any to prevent canvas reuse issues
    if (modalChart) {
        modalChart.destroy();
        modalChart = null;
    }

    // Construct a new configuration for the expanded view by deep copying critical parts
    // We avoid standard JSON.stringify to keep potential function references in options
    const newConfig = {
        type: sourceChart.config.type,
        data: {
            ...sourceChart.config.data,
            datasets: sourceChart.config.data.datasets.map(ds => ({
                ...ds,
                // Ensure array data is copied to avoid observer issues
                data: Array.isArray(ds.data) ? [...ds.data] : ds.data
            }))
        },
        options: {
            ...sourceChart.config.options,
            maintainAspectRatio: false,
            responsive: true,
            // Enhanced layout/padding for expanded view
            layout: {
                padding: { top: 20, right: 30, bottom: 20, left: 10 }
            }
        }
    };

    // Apply modal-specific styling overrides for better visibility
    if (newConfig.options.plugins) {
        if (newConfig.options.plugins.legend) {
            newConfig.options.plugins.legend.labels = {
                ...newConfig.options.plugins.legend.labels,
                font: { size: 14, weight: '700' },
                padding: 20
            };
        }

        if (newConfig.options.plugins.datalabels) {
            newConfig.options.plugins.datalabels.font = {
                ...newConfig.options.plugins.datalabels.font,
                size: 13,
                weight: 'bold'
            };
        }
    }

    // Larger fonts for scales in expanded view
    if (newConfig.options.scales) {
        Object.keys(newConfig.options.scales).forEach(axis => {
            const scale = newConfig.options.scales[axis];
            if (scale.ticks) {
                scale.ticks.font = { size: 14, weight: '500' };
                scale.ticks.color = '#94a3b8';
            }
            if (scale.title) {
                scale.title.font = { size: 16, weight: '700' };
                scale.title.color = '#f8fafc';
                scale.title.display = true;
            }
        });
    }

    // Wait for the modal transition to complete or stabilize before rendering
    // This solves the 'blurry/invisible' issue caused by rendering on an uninitialized/transitioning canvas
    setTimeout(() => {
        try {
            modalChart = new Chart(canvas, newConfig);
            console.log("Modal chart initialized successfully");
        } catch (err) {
            console.error("Failed to initialize modal chart:", err);
            // Fallback: simple text if chart fails
            canvas.parentElement.innerHTML += `<div style="color:var(--danger); padding:2rem;">차트 로드 중 오류가 발생했습니다: ${err.message}</div>`;
        }
    }, 200); // 200ms is safer for transition overlap
}

function closeChartModal(event) {
    const overlay = document.getElementById('chartModalOverlay');
    overlay.classList.remove('active');

    // Optional: Clean up modal chart after transition
    setTimeout(() => {
        if (modalChart) {
            modalChart.destroy();
            modalChart = null;
        }
    }, 400);
}
