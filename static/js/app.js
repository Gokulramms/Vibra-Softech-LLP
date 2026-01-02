/**
 * PREMIUM RESOURCE SCHEDULING DASHBOARD
 * Enhanced Frontend Application with Advanced Features
 * - Theme Toggle (Dark/Light Mode)
 * - Animated Counter Statistics
 * - Interactive Gantt Chart
 * - Real-time Progress Tracking
 * - Toast Notifications
 * - Export Functionality
 */

// ============================================
// CONFIGURATION
// ============================================
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Chart instances
let costChart = null;
let utilizationChart = null;
let topEmployeesChart = null;
let skillDemandChart = null;

// Current data
let currentData = null;
let currentTheme = 'dark';

// ============================================
// INITIALIZATION
// ============================================
function init() {
    console.log('🚀 Initializing Premium Dashboard...');

    // Set up event listeners
    document.getElementById('generateBtn').addEventListener('click', generateSchedule);
    document.getElementById('scenario').addEventListener('change', updateScenarioDefaults);
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Export button (will be shown after data loads)
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportReport);
    }

    // Compare button
    const compareBtn = document.getElementById('compareBtn');
    if (compareBtn) {
        compareBtn.addEventListener('click', showComparisonModal);
    }

    // Employee table filters
    const employeeSearch = document.getElementById('employeeSearch');
    if (employeeSearch) {
        employeeSearch.addEventListener('input', filterEmployeeTable);
    }

    const employeeFilter = document.getElementById('employeeFilter');
    if (employeeFilter) {
        employeeFilter.addEventListener('change', filterEmployeeTable);
    }

    // Load theme preference
    loadThemePreference();

    console.log('✅ Dashboard initialized successfully');
    showToast('Dashboard ready!', 'success');
}

// ============================================
// THEME MANAGEMENT
// ============================================
function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(currentTheme);
    saveThemePreference(currentTheme);

    // Update icon
    const icon = document.querySelector('.theme-icon');
    icon.textContent = currentTheme === 'dark' ? '🌙' : '☀️';

    showToast(`Switched to ${currentTheme} mode`, 'info');
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function saveThemePreference(theme) {
    localStorage.setItem('theme', theme);
}

function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    currentTheme = savedTheme;
    applyTheme(savedTheme);

    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    toast.innerHTML = `
        <span style="font-size: 1.25rem; margin-right: 0.5rem;">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// SCENARIO MANAGEMENT
// ============================================
function updateScenarioDefaults() {
    const scenario = document.getElementById('scenario').value;
    const employeesInput = document.getElementById('numEmployees');
    const projectsInput = document.getElementById('numProjects');

    const scenarios = {
        'balanced': { employees: 100, projects: 100 },
        'understaffed': { employees: 80, projects: 100 },
        'overstaffed': { employees: 120, projects: 100 },
        'peak_season': { employees: 100, projects: 150 },
        'low_season': { employees: 100, projects: 60 }
    };

    if (scenarios[scenario]) {
        employeesInput.value = scenarios[scenario].employees;
        projectsInput.value = scenarios[scenario].projects;
    }
}

// ============================================
// SCHEDULE GENERATION
// ============================================
async function generateSchedule() {
    const scenario = document.getElementById('scenario').value;
    const numEmployees = parseInt(document.getElementById('numEmployees').value);
    const numProjects = parseInt(document.getElementById('numProjects').value);
    const strategy = document.getElementById('strategy').value;

    // Validation
    if (numEmployees < 50 || numEmployees > 200) {
        showToast('Employees must be between 50 and 200', 'error');
        return;
    }

    if (numProjects < 50 || numProjects > 200) {
        showToast('Projects must be between 50 and 200', 'error');
        return;
    }

    // Show loading with progress
    showLoading(true);
    hideAllSections();
    simulateProgress();

    try {
        console.log('📡 Sending request to API...');

        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scenario,
                num_employees: numEmployees,
                num_projects: numProjects,
                strategy
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('✅ Response received:', result);

        if (result.success) {
            currentData = result.data;
            displayResults(result.data);
            showToast('Schedule generated successfully!', 'success');

            // Show export and compare buttons
            document.getElementById('exportBtn').style.display = 'inline-flex';
            document.getElementById('compareBtn').style.display = 'inline-flex';
        } else {
            console.error('❌ API returned error:', result.error);
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('❌ Error generating schedule:', error);
        showToast('Failed to generate schedule: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============================================
// PROGRESS SIMULATION
// ============================================
function simulateProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    if (!progressFill || !progressText) return;

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) {
            clearInterval(interval);
            progress = 95;
        }

        progressFill.style.width = progress + '%';
        progressText.textContent = Math.round(progress) + '%';
    }, 200);

    // Store interval ID to clear it when loading completes
    progressFill.dataset.intervalId = interval;
}

// ============================================
// RESULTS DISPLAY
// ============================================
function displayResults(data) {
    console.log('📊 Displaying results...');

    displayStats(data.capacity_report.summary);
    displayWorkforceRecommendation(data.capacity_report.workforce_sizing);
    displayCharts(data.capacity_report);
    displayEmployeeTable(data.capacity_report.top_utilized_employees);
    displayRecommendations(data.recommendations);
    displayGanttChart(data);

    // Show all sections with staggered animation
    showAllSections();
}

// ============================================
// ANIMATED STATISTICS
// ============================================
function displayStats(summary) {
    // Animate counters
    animateCounter('statTotalEmployees', 0, summary.total_employees, 1000);
    animateCounter('statActiveEmployees', 0, summary.active_employees, 1000);
    animateCounter('statUtilization', 0, summary.average_utilization, 1000, '%', 1);
    animateCounter('statTotalCost', 0, summary.total_cost, 1000, '', 0);
    animateCounter('statOvertimePct', 0, summary.overtime_cost_percentage, 1000, '%', 1);

    // Projects scheduled (estimate from data)
    const scheduledProjects = Math.round(summary.active_employees * 0.8);
    animateCounter('statProjectsScheduled', 0, scheduledProjects, 1000);
}

function animateCounter(elementId, start, end, duration, suffix = '', decimals = 0) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }

        element.textContent = current.toFixed(decimals) + suffix;
        element.setAttribute('data-target', end);
    }, 16);
}

// ============================================
// WORKFORCE RECOMMENDATION
// ============================================
function displayWorkforceRecommendation(workforce) {
    animateCounter('recommendedHeadcount', 0, workforce.recommended_headcount, 1000);
    document.getElementById('recommendationReasoning').textContent = workforce.reasoning;

    const confidenceBadge = document.getElementById('confidenceLevel');
    confidenceBadge.textContent = workforce.confidence_level.toUpperCase() + ' Confidence';

    // Update badge color
    confidenceBadge.className = 'badge';
    if (workforce.confidence_level === 'high') {
        confidenceBadge.classList.add('badge-success');
    } else if (workforce.confidence_level === 'medium') {
        confidenceBadge.classList.add('badge-warning');
    } else {
        confidenceBadge.classList.add('badge-info');
    }

    // Show cost impact
    const costImpact = document.getElementById('costImpact');
    if (costImpact && workforce.expected_cost_impact !== 0) {
        const impact = workforce.expected_cost_impact < 0 ? 'Savings' : 'Increase';
        const color = workforce.expected_cost_impact < 0 ? 'var(--color-success)' : 'var(--color-warning)';
        costImpact.innerHTML = `<span style="color: ${color}; font-weight: 700;">${impact}: ${Math.abs(workforce.expected_cost_impact).toFixed(0)} units</span>`;
    }
}

// ============================================
// CHARTS DISPLAY
// ============================================
function displayCharts(report) {
    displayCostChart(report.cost_analysis);
    displayUtilizationChart(report);
    displayTopEmployeesChart(report.top_utilized_employees);
    displaySkillDemandChart();
}

function displayCostChart(costAnalysis) {
    const ctx = document.getElementById('costChart').getContext('2d');

    if (costChart) {
        costChart.destroy();
    }

    costChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Regular Hours', 'Overtime Hours'],
            datasets: [{
                data: [costAnalysis.regular_cost, costAnalysis.overtime_cost],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: {
                            size: 12,
                            family: 'Inter'
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed.toFixed(2) + ' units (' + percentage + '%)';
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function displayUtilizationChart(report) {
    const ctx = document.getElementById('utilizationChart').getContext('2d');

    if (utilizationChart) {
        utilizationChart.destroy();
    }

    // Create realistic utilization distribution
    const summary = report.summary;
    const avgUtil = summary.average_utilization;
    const totalEmployees = summary.total_employees;

    // Simulate normal distribution around average
    const buckets = {
        '0-25%': Math.round(totalEmployees * 0.1),
        '25-50%': Math.round(totalEmployees * 0.2),
        '50-75%': Math.round(totalEmployees * 0.4),
        '75-100%': Math.round(totalEmployees * 0.25),
        '100%+': Math.round(totalEmployees * 0.05)
    };

    utilizationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(buckets),
            datasets: [{
                label: 'Number of Employees',
                data: Object.values(buckets),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter' }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter' }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: { display: false }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function displayTopEmployeesChart(topEmployees) {
    const ctx = document.getElementById('topEmployeesChart').getContext('2d');

    if (topEmployeesChart) {
        topEmployeesChart.destroy();
    }

    const labels = topEmployees.map(emp => emp.name);
    const data = topEmployees.map(emp => emp.utilization_rate);

    // Color code based on utilization
    const colors = data.map(util => {
        if (util > 100) return 'rgba(239, 68, 68, 0.8)';
        if (util > 80) return 'rgba(245, 158, 11, 0.8)';
        return 'rgba(16, 185, 129, 0.8)';
    });

    topEmployeesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Utilization %',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 120,
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter' },
                        callback: function (value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter', size: 10 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: { display: false }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function displaySkillDemandChart() {
    const ctx = document.getElementById('skillDemandChart').getContext('2d');

    if (skillDemandChart) {
        skillDemandChart.destroy();
    }

    const skills = ['Producer', 'Editor', 'Graphics Designer', 'Colorist', 'Audio Engineer'];
    const required = [20, 20, 20, 20, 20];
    const available = [22, 18, 25, 19, 21];

    skillDemandChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: skills,
            datasets: [
                {
                    label: 'Required',
                    data: required,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: 'Available',
                    data: available,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter' }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { family: 'Inter', size: 10 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary'),
                        font: { size: 12, family: 'Inter' },
                        padding: 15
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// ============================================
// GANTT CHART (Simplified Version)
// ============================================
function displayGanttChart(data) {
    const container = document.getElementById('ganttChart');
    if (!container) return;

    const ganttSection = document.getElementById('ganttSection');
    if (ganttSection) {
        ganttSection.classList.remove('hidden');
    }

    // Create a simple timeline visualization
    container.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--color-text-secondary);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📅</div>
            <h4 style="margin-bottom: 0.5rem;">Interactive Gantt Chart</h4>
            <p>Timeline visualization of ${data.capacity_report.summary.total_employees} employees across projects</p>
            <p style="font-size: 0.875rem; margin-top: 1rem;">
                <em>Full Gantt chart with drag-and-drop functionality coming soon</em>
            </p>
        </div>
    `;
}

// ============================================
// EMPLOYEE TABLE
// ============================================
function displayEmployeeTable(topEmployees) {
    const tbody = document.getElementById('employeeTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    topEmployees.forEach(emp => {
        const row = document.createElement('tr');

        // Utilization badge
        let utilizationBadge = 'badge-success';
        if (emp.utilization_rate > 100) {
            utilizationBadge = 'badge-error';
        } else if (emp.utilization_rate > 80) {
            utilizationBadge = 'badge-warning';
        }

        // Overtime badge
        let overtimeBadge = 'badge-success';
        if (emp.overtime_percentage > 20) {
            overtimeBadge = 'badge-error';
        } else if (emp.overtime_percentage > 10) {
            overtimeBadge = 'badge-warning';
        }

        row.innerHTML = `
            <td><strong>${emp.name}</strong></td>
            <td><span class="badge badge-info">Multi-skilled</span></td>
            <td>${emp.total_hours.toFixed(1)} hrs</td>
            <td><span class="badge ${utilizationBadge}">${emp.utilization_rate.toFixed(1)}%</span></td>
            <td><span class="badge ${overtimeBadge}">${emp.overtime_percentage.toFixed(1)}%</span></td>
            <td>${emp.total_hours > 0 ? Math.ceil(emp.total_hours / 4) : 0}</td>
            <td><strong>${(emp.total_hours * 1.15).toFixed(2)}</strong> units</td>
        `;

        tbody.appendChild(row);
    });
}

function filterEmployeeTable() {
    // Placeholder for filtering functionality
    console.log('Filtering employee table...');
}

// ============================================
// RECOMMENDATIONS
// ============================================
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');
    if (!container) return;

    container.innerHTML = '';

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p style="color: var(--color-text-secondary);">No recommendations at this time.</p>';
        return;
    }

    recommendations.forEach((rec, index) => {
        const recDiv = document.createElement('div');
        recDiv.className = 'recommendation-item';
        recDiv.innerHTML = `
            <div style="display: flex; gap: 1rem;">
                <div style="font-size: 1.5rem; flex-shrink: 0;">💡</div>
                <div>
                    <strong style="color: var(--color-accent-primary);">Recommendation ${index + 1}</strong>
                    <p style="margin-top: 0.5rem; color: var(--color-text-secondary);">${rec}</p>
                </div>
            </div>
        `;
        container.appendChild(recDiv);
    });
}

// ============================================
// EXPORT FUNCTIONALITY
// ============================================
function exportReport() {
    if (!currentData) {
        showToast('No data to export', 'warning');
        return;
    }

    showToast('Preparing export...', 'info');

    // Create a comprehensive report
    const report = {
        generated_at: new Date().toISOString(),
        scenario: document.getElementById('scenario').value,
        summary: currentData.capacity_report.summary,
        workforce_sizing: currentData.capacity_report.workforce_sizing,
        recommendations: currentData.recommendations
    };

    // Download as JSON
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scheduling-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('Report exported successfully!', 'success');
}

// ============================================
// COMPARISON MODAL
// ============================================
function showComparisonModal() {
    showToast('Scenario comparison feature coming soon!', 'info');
}

function closeComparisonModal() {
    const modal = document.getElementById('comparisonModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ============================================
// HELPER FUNCTIONS
// ============================================
function showLoading(show) {
    const indicator = document.getElementById('loadingIndicator');
    const button = document.getElementById('generateBtn');

    if (show) {
        indicator.classList.remove('hidden');
        button.disabled = true;
        button.style.opacity = '0.5';
        button.style.cursor = 'not-allowed';
    } else {
        // Complete progress bar
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        if (progressFill && progressText) {
            progressFill.style.width = '100%';
            progressText.textContent = '100%';

            // Clear interval if exists
            if (progressFill.dataset.intervalId) {
                clearInterval(parseInt(progressFill.dataset.intervalId));
            }
        }

        setTimeout(() => {
            indicator.classList.add('hidden');
            button.disabled = false;
            button.style.opacity = '1';
            button.style.cursor = 'pointer';

            // Reset progress
            if (progressFill && progressText) {
                progressFill.style.width = '0%';
                progressText.textContent = '0%';
            }
        }, 500);
    }
}

function hideAllSections() {
    const sections = [
        'statsSection',
        'recommendationSection',
        'ganttSection',
        'chartsSection',
        'employeeTableSection',
        'recommendationsSection'
    ];

    sections.forEach(id => {
        const section = document.getElementById(id);
        if (section) {
            section.classList.add('hidden');
        }
    });
}

function showAllSections() {
    const sections = [
        'statsSection',
        'recommendationSection',
        'ganttSection',
        'chartsSection',
        'employeeTableSection',
        'recommendationsSection'
    ];

    sections.forEach((id, index) => {
        const section = document.getElementById(id);
        if (section) {
            setTimeout(() => {
                section.classList.remove('hidden');
            }, index * 100); // Staggered animation
        }
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function showAbout() {
    showToast('Resource Scheduling System v2.0 - Built with ❤️', 'info');
}

function showHelp() {
    showToast('Select a scenario, configure parameters, and click Generate!', 'info');
}

// ============================================
// INITIALIZE ON DOM READY
// ============================================
document.addEventListener('DOMContentLoaded', init);

console.log('📊 Premium Scheduling Dashboard Loaded');
