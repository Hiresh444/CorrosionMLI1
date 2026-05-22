// Simplified Corrosion ML Dashboard Controller

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial Data Setup Validation
    if (typeof dashboardData === 'undefined') {
        console.error("Dashboard data not loaded. Make sure data.js is generated.");
        return;
    }

    // Populate header stats
    document.getElementById('dataset-size-badge').textContent = 
        dashboardData.dataset_summary.total_records.toLocaleString() + ' Rows';

    let charts = {}; // Chart.js instances cache
    let currentScatterSplit = 'val';

    // Helper: Create horizontal linear gradient
    function getHorizontalGradient(ctx, colorStart, colorEnd) {
        const gradient = ctx.createLinearGradient(0, 0, 400, 0);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
    }

    // Initialize all visualizations on startup
    renderFeatureImportanceChart();
    renderScatterPlot();
    renderCoatingPerformanceChart();
    renderMaintenanceStrategyChart();
    renderCorrelationHeatmap();
    renderAreaBinsByMaterialChart();
    renderEnvironmentSeverityChart();
    renderMaterialCorrRateChart();
    renderExposureScatterChart();

    // 2. feature importance chart
    function renderFeatureImportanceChart() {
        const importanceData = dashboardData.feature_importances.slice(0, 15); // Top 15
        const ctx = document.getElementById('chart-final-importance').getContext('2d');
        const grad = getHorizontalGradient(ctx, 'rgba(6, 182, 212, 0.85)', 'rgba(139, 92, 246, 0.35)');
        
        charts['importance'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: importanceData.map(d => d.feature.replace('environment_', 'Env: ').replace('material_', 'Mat: ').replace('coating_', 'Coat: ').replace('maintenance_', 'Maint: ')),
                datasets: [{
                    label: 'Feature Importance (Gain)',
                    data: importanceData.map(d => d.importance),
                    backgroundColor: grad,
                    borderColor: 'rgba(6, 182, 212, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { color: '#22314d' }, ticks: { color: '#94a3b8' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } } }
                }
            }
        });
    }

    // 3. actual vs. predicted scatter plot
    function renderScatterPlot() {
        const ctx = document.getElementById('chart-eval-scatter').getContext('2d');
        const points = dashboardData.predictions[currentScatterSplit];
        const maxVal = Math.max(...points.map(p => Math.max(p.actual, p.predicted))) * 1.05;

        charts['scatter'] = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Predictions',
                        data: points.map(p => ({ x: p.actual, y: p.predicted })),
                        backgroundColor: 'rgba(6, 182, 212, 0.65)',
                        borderColor: 'rgba(6, 182, 212, 0.9)',
                        borderWidth: 1,
                        radius: 4,
                        hoverRadius: 6
                    },
                    {
                        label: 'Ideal Fit (Actual = Predicted)',
                        data: [{ x: 0, y: 0 }, { x: maxVal, y: maxVal }],
                        type: 'line',
                        borderColor: 'rgba(245, 158, 11, 0.7)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Actual: ${context.parsed.x.toFixed(3)} | Predicted: ${context.parsed.y.toFixed(3)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Actual Corrosion Rate (MPY)', color: '#94a3b8' }, grid: { color: '#22314d' }, ticks: { color: '#94a3b8' }, min: 0, max: maxVal },
                    y: { title: { display: true, text: 'Predicted Corrosion Rate (MPY)', color: '#94a3b8' }, grid: { color: '#22314d' }, ticks: { color: '#94a3b8' }, min: 0, max: maxVal }
                }
            }
        });

        // Scatter toggle buttons
        document.getElementById('btn-toggle-scatter-val').addEventListener('click', (e) => {
            toggleScatter('val', e.target);
        });
        document.getElementById('btn-toggle-scatter-test').addEventListener('click', (e) => {
            toggleScatter('test', e.target);
        });
    }

    function toggleScatter(split, activeBtn) {
        if (split === currentScatterSplit) return;
        currentScatterSplit = split;

        document.getElementById('btn-toggle-scatter-val').classList.remove('active');
        document.getElementById('btn-toggle-scatter-test').classList.remove('active');
        activeBtn.classList.add('active');

        const points = dashboardData.predictions[split];
        charts['scatter'].data.datasets[0].data = points.map(p => ({ x: p.actual, y: p.predicted }));
        charts['scatter'].update();
    }

    // 4. coating performance chart
    function renderCoatingPerformanceChart() {
        const coatingData = dashboardData.insights.coating;
        const ctx = document.getElementById('chart-insights-coating').getContext('2d');
        
        const noneRate = coatingData.find(d => d.name === 'None').avg_mpy;
        const sortedCoats = coatingData.filter(d => d.name !== 'None').sort((a,b) => b.avg_mpy - a.avg_mpy);
        
        charts['coating'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Untreated (None)', ...sortedCoats.map(c => c.name)],
                datasets: [{
                    label: 'Avg Corrosion Rate (MPY)',
                    data: [noneRate, ...sortedCoats.map(c => c.avg_mpy)],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.75)', // Red baseline
                        ...sortedCoats.map(() => 'rgba(6, 182, 212, 0.75)') // Cyan coatings
                    ],
                    borderColor: [
                        'rgba(239, 68, 68, 1)',
                        ...sortedCoats.map(() => 'rgba(6, 182, 212, 1)')
                    ],
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            footer: function(items) {
                                const val = items[0].parsed.y;
                                if (items[0].dataIndex > 0) {
                                    const pct = ((noneRate - val) / noneRate * 100).toFixed(1);
                                    return `Corrosion Reduction: -${pct}%`;
                                }
                                return '';
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#22314d' } }
                }
            }
        });
    }

    // 5. maintenance strategies chart
    function renderMaintenanceStrategyChart() {
        const maintData = dashboardData.insights.maintenance;
        const ctx = document.getElementById('chart-insights-maintenance').getContext('2d');
        
        const noneRate = maintData.find(d => d.name === 'None').avg_mpy;
        const sortedMaint = maintData.filter(d => d.name !== 'None').sort((a,b) => b.avg_mpy - a.avg_mpy);

        charts['maintenance'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['No Maintenance (None)', ...sortedMaint.map(m => m.name)],
                datasets: [{
                    label: 'Avg Corrosion Rate (MPY)',
                    data: [noneRate, ...sortedMaint.map(m => m.avg_mpy)],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.75)',
                        ...sortedMaint.map(() => 'rgba(16, 185, 129, 0.75)') // Emerald active maintenance
                    ],
                    borderColor: [
                        'rgba(239, 68, 68, 1)',
                        ...sortedMaint.map(() => 'rgba(16, 185, 129, 1)')
                    ],
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            footer: function(items) {
                                const val = items[0].parsed.y;
                                if (items[0].dataIndex > 0) {
                                    const pct = ((noneRate - val) / noneRate * 100).toFixed(1);
                                    return `Corrosion Reduction: -${pct}%`;
                                }
                                return '';
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#22314d' } }
                }
            }
        });
    }

    // 6. Custom correlation matrix heatmap grid
    function renderCorrelationHeatmap() {
        const container = document.getElementById('correlation-heatmap');
        if (!container) return;

        const data = dashboardData.correlation_matrix;
        const columns = [];
        data.forEach(d => {
            if (!columns.includes(d.x)) columns.push(d.x);
        });

        // Abbreviate names for header cells
        const nameMap = {
            'corrosion_rate_mpy': 'Rate',
            'base_aggressiveness': 'Aggres',
            'temperature_c': 'Temp',
            'ph': 'pH',
            'chloride_g_per_l': 'Chlor',
            'oxygen_ppm': 'Oxy',
            'flow_m_per_s': 'Flow',
            'humidity_pct': 'Humid',
            'material_resistance_index': 'MatRes',
            'coating_efficiency': 'CoatEff',
            'inhibitor_ppm': 'Inhib',
            'wall_thickness_mm': 'WallThk',
            'pressure_bar': 'Press',
            'exposed_area_m2': 'Area',
            'exposure_days': 'Days',
            'safety_risk_score': 'Risk',
            'total_cost_usd': 'Cost'
        };

        // Header spacer
        const spacer = document.createElement('div');
        spacer.className = 'heatmap-label-row';
        spacer.style.gridColumn = '1';
        spacer.style.gridRow = '1';
        container.appendChild(spacer);

        // Header Row labels
        columns.forEach((col, idx) => {
            const header = document.createElement('div');
            header.className = 'heatmap-label-row';
            header.style.gridColumn = `${idx + 2}`;
            header.style.gridRow = '1';
            header.textContent = nameMap[col] || col;
            header.title = col;
            container.appendChild(header);
        });

        // Rows
        columns.forEach((rowCol, rIdx) => {
            // Col Label
            const label = document.createElement('div');
            label.className = 'heatmap-label-col';
            label.style.gridColumn = '1';
            label.style.gridRow = `${rIdx + 2}`;
            label.textContent = nameMap[rowCol] || rowCol;
            label.title = rowCol;
            container.appendChild(label);

            // Cells
            columns.forEach((cCol, cIdx) => {
                const pair = data.find(d => d.x === rowCol && d.y === cCol);
                const val = pair ? pair.value : 0;

                const cell = document.createElement('div');
                cell.className = 'heatmap-cell';
                cell.style.gridColumn = `${cIdx + 2}`;
                cell.style.gridRow = `${rIdx + 2}`;
                
                let bg;
                if (val > 0) {
                    bg = `rgba(16, 185, 129, ${val})`; // Emerald for positive correlation
                } else if (val < 0) {
                    bg = `rgba(239, 68, 68, ${Math.abs(val)})`; // Red for negative correlation
                } else {
                    bg = 'rgba(255,255,255,0.02)';
                }
                
                if (rowCol === cCol) {
                    bg = 'rgba(6, 182, 212, 0.9)'; // Diagonal is cyan
                }

                cell.style.backgroundColor = bg;
                cell.setAttribute('data-tooltip', `${rowCol} x ${cCol}: ${val.toFixed(3)}`);
                container.appendChild(cell);
            });
        });
    }

    // 7. Area Bins by Material Performance Chart
    function renderAreaBinsByMaterialChart() {
        const data = dashboardData.area_bins_by_material;
        if (!data) return;

        const ctx = document.getElementById('chart-area-bins-material').getContext('2d');
        const bins = ['Small', 'Medium', 'Large', 'Very Large'];
        const materials = Object.keys(data);
        const palette = [
            'rgba(6, 182, 212, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
        ];

        const datasets = materials.map((mat, idx) => ({
            label: mat,
            data: bins.map(bin => data[mat][bin] || 0),
            backgroundColor: palette[idx % palette.length],
            borderColor: palette[idx % palette.length].replace('0.8', '1'),
            borderWidth: 1,
            borderRadius: 3
        }));

        charts['areaBins'] = new Chart(ctx, {
            type: 'bar',
            data: { labels: bins, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { size: 10 } } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: {
                        title: { display: true, text: 'Mean Corrosion Rate (MPY)', color: '#94a3b8' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#22314d' }
                    }
                }
            }
        });
    }

    // 8. Environment Severity Chart
    function renderEnvironmentSeverityChart() {
        const data = dashboardData.environment_analysis;
        if (!data) return;

        const ctx = document.getElementById('chart-environment-severity').getContext('2d');
        const envs = Object.keys(data.mean_corr_rate);
        const rates = envs.map(e => data.mean_corr_rate[e]);

        // Generate gradient colors: highest rate = red, lowest = green
        const maxRate = Math.max(...rates);
        const colors = rates.map(r => {
            const ratio = r / maxRate;
            if (ratio > 0.7) return 'rgba(239, 68, 68, 0.8)';
            if (ratio > 0.4) return 'rgba(245, 158, 11, 0.8)';
            return 'rgba(16, 185, 129, 0.8)';
        });

        charts['envSeverity'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: envs,
                datasets: [{
                    label: 'Mean Corrosion Rate (MPY)',
                    data: rates,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        title: { display: true, text: 'Mean Corrosion Rate (MPY)', color: '#94a3b8' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#22314d' }
                    },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } } }
                }
            }
        });
    }

    // 9. Material Mean Corrosion Rate Chart
    function renderMaterialCorrRateChart() {
        const data = dashboardData.material_mean_corr_rate;
        if (!data) return;

        const ctx = document.getElementById('chart-material-corr-rate').getContext('2d');

        // Sort by value ascending
        const entries = Object.entries(data).sort((a, b) => a[1] - b[1]);
        const labels = entries.map(e => e[0]);
        const values = entries.map(e => e[1]);

        const maxVal = Math.max(...values);
        const colors = values.map(v => {
            const ratio = v / maxVal;
            if (ratio > 0.75) return 'rgba(239, 68, 68, 0.8)';
            if (ratio > 0.5) return 'rgba(245, 158, 11, 0.8)';
            if (ratio > 0.25) return 'rgba(6, 182, 212, 0.8)';
            return 'rgba(16, 185, 129, 0.8)';
        });

        charts['materialRate'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Mean Corrosion Rate (MPY)',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.8', '1')),
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Mean Rate: ${context.parsed.x.toFixed(4)} MPY`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Mean Corrosion Rate (MPY)', color: '#94a3b8' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#22314d' }
                    },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } } }
                }
            }
        });
    }

    // 10. Exposure Time vs Corrosion Rate Scatter Chart
    function renderExposureScatterChart() {
        const data = dashboardData.exposure_scatter;
        if (!data) return;

        const ctx = document.getElementById('chart-exposure-scatter').getContext('2d');

        // Group by environment
        const envGroups = {};
        data.forEach(point => {
            if (!envGroups[point.env]) envGroups[point.env] = [];
            envGroups[point.env].push({ x: point.days, y: point.rate });
        });

        const envColors = {
            'CO2 Pipeline Wet': 'rgba(239, 68, 68, 0.7)',
            'Process Brine': 'rgba(245, 158, 11, 0.7)',
            'Marine Splash': 'rgba(6, 182, 212, 0.7)',
            'Industrial Urban': 'rgba(139, 92, 246, 0.7)',
            'Marine Immersed': 'rgba(59, 130, 246, 0.7)',
            'Soil Clay': 'rgba(16, 185, 129, 0.7)',
            'Soil Sandy': 'rgba(168, 162, 158, 0.7)',
            'Rural': 'rgba(101, 163, 13, 0.7)'
        };

        const datasets = Object.entries(envGroups).map(([env, points]) => ({
            label: env,
            data: points,
            backgroundColor: envColors[env] || 'rgba(148, 163, 184, 0.7)',
            borderColor: (envColors[env] || 'rgba(148, 163, 184, 0.7)').replace('0.7', '1'),
            borderWidth: 1,
            radius: 4,
            hoverRadius: 6
        }));

        charts['exposureScatter'] = new Chart(ctx, {
            type: 'scatter',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { size: 9 } },
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.x} days, ${context.parsed.y.toFixed(3)} MPY`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Exposure Days', color: '#94a3b8' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#22314d' }
                    },
                    y: {
                        title: { display: true, text: 'Corrosion Rate (MPY)', color: '#94a3b8' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: '#22314d' }
                    }
                }
            }
        });
    }
});
