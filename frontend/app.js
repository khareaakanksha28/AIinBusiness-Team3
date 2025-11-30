// FactoryTwin AI Frontend
const API_URL = 'http://localhost:5001/query';

let currentChart = null;

// Initialize
let selectedSimulationId = null;
let availableSimulations = [];

// Auto-select first simulation when available
function autoSelectSimulation(simulations) {
    if (simulations && simulations.length > 0 && !selectedSimulationId) {
        selectedSimulationId = simulations[0].identifier;
        console.log('Auto-selected simulation:', selectedSimulationId);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('FactoryTwin AI Frontend initialized');
    checkServerHealth();
    // Don't auto-send greeting - wait for user to say hello
});

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch('http://localhost:5001/health');
        const data = await response.json();
        console.log('Server health:', data);
    } catch (error) {
        console.error('Server not reachable:', error);
        showError('Cannot connect to server. Make sure the local server is running on port 5001.');
    }
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendQuestion();
    }
}

// Ask question from example button
function askQuestion(question) {
    document.getElementById('questionInput').value = question;
    sendQuestion();
}

// Handle greeting - now part of sendQuestion

// Simulation selection removed - automatically uses first available simulation

// Send question to API
async function sendQuestion() {
    const input = document.getElementById('questionInput');
    const question = input.value.trim();
    const sendButton = document.getElementById('sendButton');

    if (!question) {
        return;
    }

    // Disable input
    input.disabled = true;
    sendButton.disabled = true;

    // Add user message
    addMessage('user', question);
    input.value = '';

    // Hide welcome message
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }

    // Show loading
    const loadingId = addLoadingMessage();

    try {
        const requestBody = { question };
        // Include simulation_id if selected, or use default
        if (selectedSimulationId) {
            requestBody.simulation_id = selectedSimulationId;
        }

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            // Try to get error message from response body
            let errorMessage = `Server error: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.message) {
                    errorMessage = errorData.message;
                } else if (errorData.error) {
                    errorMessage = errorData.error;
                }
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || `Server error: ${response.status}`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();

        // Remove loading
        removeMessage(loadingId);

        // Handle greeting response
        if (data.type === 'greeting') {
            addMessage('assistant', data.message);
        } else if (data.type === 'acknowledgment') {
            // Handle acknowledgment (thank you, etc.) - no visualization needed
            addMessage('assistant', data.answer);
            hideVisualization();
        } else {
            // Regular question response
            addMessage('assistant', data.answer);

            // Show visualization if chart data exists (agentic decision)
            if (data.chart_data && data.visualization_type) {
                showVisualization(data.chart_data, data.visualization_type, data.endpoint);
                
                // Show agentic decision reasoning if available
                if (data.agentic_decision) {
                    console.log('🤖 Agentic Decision:', data.agentic_decision);
                }
            } else {
                hideVisualization();
            }
        }

    } catch (error) {
        console.error('Error:', error);
        removeMessage(loadingId);
        addMessage('assistant', `Sorry, I encountered an error: ${error.message}`, true);
    } finally {
        // Re-enable input
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
    }
}

// Add message to chat
function addMessage(sender, text, isError = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageId = 'msg-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.id = messageId;

    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isError ? 'error-message' : ''}`;
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    bubble.appendChild(textDiv);

    messageDiv.appendChild(bubble);

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.textContent = new Date().toLocaleTimeString();
    messageDiv.appendChild(meta);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return messageId;
}

// Add loading message
function addLoadingMessage() {
    const messagesContainer = document.getElementById('chatMessages');
    const loadingId = 'loading-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = loadingId;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble loading';
    
    bubble.innerHTML = `
        <span>Thinking</span>
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;

    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return loadingId;
}

// Remove message
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Show visualization
function showVisualization(chartData, visualizationType, endpoint) {
    const section = document.getElementById('visualizationSection');
    section.style.display = 'flex';

    const canvas = document.getElementById('chartCanvas');
    const ctx = canvas.getContext('2d');

    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }

    // Prepare data based on visualization type
    let chartConfig = {};
    let orderedData = []; // Store for center text plugin

    if (visualizationType === 'donut' || visualizationType === 'donut-chart') {
        // Donut chart - match the reference design
        const stackData = chartData.stackDataList || [];
        
        // Ensure we have all three categories (even if value is 0)
        const categoryMap = {
            "Firm Order": { name: "Firm Order", value: 0, quantity: 0 },
            "Overdue": { name: "Overdue", value: 0, quantity: 0 },
            "Forecasted": { name: "Forecasted", value: 0, quantity: 0 }
        };
        
        stackData.forEach(item => {
            if (item.name in categoryMap) {
                categoryMap[item.name] = item;
            }
        });
        
        // Always show all three categories in order: Firm Order, Overdue, Forecasted
        orderedData = [
            categoryMap["Firm Order"],
            categoryMap["Overdue"],
            categoryMap["Forecasted"]
        ];
        
        // Filter out zero values - don't show categories with zero value/quantity
        orderedData = orderedData.filter(item => (item.value || 0) > 0 || (item.quantity || 0) > 0);
        
        const labels = orderedData.map(item => item.name);
        const quantities = orderedData.map(item => item.quantity || 0);
        
        // Colors matching the reference: medium blue, dark blue, gray
        const categoryColors = {
            "Firm Order": "#3b82f6",      // Medium blue
            "Overdue": "#1e40af",         // Dark blue  
            "Forecasted": "#9ca3af"       // Gray
        };
        const colors = labels.map(label => categoryColors[label] || "#3b82f6");
        
        // Calculate total for center display (sum of all quantities)
        const totalQuantity = quantities.reduce((sum, qty) => sum + qty, 0);
        
        // Store orderedData and quantities for plugin access
        const chartDataStore = {
            orderedData: orderedData,
            quantities: quantities,
            totalQuantity: totalQuantity
        };

        chartConfig = {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: quantities,  // Use quantity instead of value
                    backgroundColor: colors,
                    borderWidth: 0,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Total Aggregate Demand',
                        font: {
                            size: 18,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 14
                            },
                            usePointStyle: true,
                            pointStyle: 'rect',
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: label,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].borderColor,
                                            lineWidth: data.datasets[0].borderWidth,
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0, 0, 0, 0.85)',
                        padding: 14,
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        titleFont: {
                            size: 16,
                            weight: 'bold',
                            family: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
                        },
                        bodyFont: {
                            size: 14,
                            family: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
                        },
                        footerFont: {
                            size: 13,
                            weight: 'bold',
                            family: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif'
                        },
                        callbacks: {
                            title: function(context) {
                                return context[0].label || '';
                            },
                            label: function(context) {
                                const label = context.label || '';
                                const quantity = context.parsed || 0;
                                const index = context.dataIndex;
                                
                                // Get quantities and totals from chart data store
                                const dataStore = chart.config._dataStore || {};
                                const quantities = dataStore.quantities || [];
                                const totalQuantity = dataStore.totalQuantity || 0;
                                
                                const qty = quantities[index] || 0;
                                const percentage = totalQuantity > 0 ? ((quantity / totalQuantity) * 100).toFixed(1) : 0;
                                return [
                                    `Quantity: ${qty.toLocaleString()} units`,
                                    `Percentage: ${percentage}% of total`
                                ];
                            },
                            footer: function(context) {
                                const dataStore = chart.config._dataStore || {};
                                const totalQuantity = dataStore.totalQuantity || 0;
                                return `Total: ${totalQuantity.toLocaleString()} units`;
                            },
                            labelColor: function(context) {
                                return {
                                    borderColor: context.dataset.backgroundColor[context.dataIndex],
                                    backgroundColor: context.dataset.backgroundColor[context.dataIndex]
                                };
                            }
                        }
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    const ctx = chart.ctx;
                    const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                    const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;
                    
                    // Get total quantity from stored data
                    const totalQty = chartDataStore.totalQuantity || 0;
                    const totalVal = chartDataStore.totalValue || 0;
                    
                    ctx.save();
                    ctx.font = 'bold 32px -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif';
                    ctx.fillStyle = '#1d1d1f';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    // Display total quantity in center
                    if (totalQty > 0) {
                        ctx.fillText(totalQty.toLocaleString(), centerX, centerY - 10);
                        ctx.font = '14px -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif';
                        ctx.fillStyle = '#6b7280';
                        ctx.fillText('units', centerX, centerY + 20);
                    } else {
                        ctx.fillText('0', centerX, centerY);
                    }
                    
                    ctx.restore();
                }
            }]
        };
        
        // Store data reference in chart config for plugin access
        chartConfig._dataStore = chartDataStore;
    } else if (visualizationType === 'stacked-bar' || visualizationType === 'histogram') {
        // Stacked bar chart (histogram)
        const periods = Array.isArray(chartData) ? chartData : [chartData];
        const allNames = new Set();
        
        // Safely collect all category names
        periods.forEach(period => {
            if (period && period.stackDataList && Array.isArray(period.stackDataList)) {
                period.stackDataList.forEach(item => {
                    if (item && item.name) {
                        allNames.add(item.name);
                    }
                });
            }
        });

        const labels = periods.map(period => {
            if (!period || !period.startDate) {
                return 'Unknown';
            }
            try {
                const date = new Date(period.startDate);
                if (isNaN(date.getTime())) {
                    return 'Invalid Date';
                }
                return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            } catch (e) {
                return 'Invalid Date';
            }
        });

        const names = Array.from(allNames);
        const colors = generateColors(names.length);
        const datasets = names.map((name, index) => {
            // For histogram charts, rename "Firm Order" to "Forecasted" when displaying
            const displayLabel = name === "Firm Order" ? "Forecasted" : name;
            return {
                label: displayLabel,
                data: periods.map(period => {
                    // Safely handle empty or missing stackDataList
                    if (!period || !period.stackDataList || !Array.isArray(period.stackDataList)) {
                        return 0;
                    }
                    const item = period.stackDataList.find(i => i && i.name === name);
                    return item ? (item.quantity || 0) : 0;  // Use quantity instead of value
                }),
                backgroundColor: colors[index],
                borderColor: colors[index],
                borderWidth: 1
            };
        });

        chartConfig = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString() + ' units';  // Format as quantity instead of currency
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 14
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const quantity = context.parsed.y || 0;
                                return `${label}: ${quantity.toLocaleString()} units`;
                            }
                        }
                    }
                }
            }
        };
    }

    // Create chart
    currentChart = new Chart(ctx, chartConfig);
}

// Hide visualization
function hideVisualization() {
    const section = document.getElementById('visualizationSection');
    section.style.display = 'none';
    
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}

// Generate colors for charts
function generateColors(count) {
    const colors = [
        '#3b82f6', // blue
        '#10b981', // green
        '#f59e0b', // amber
        '#ef4444', // red
        '#8b5cf6', // purple
        '#ec4899', // pink
        '#06b6d4', // cyan
        '#84cc16', // lime
    ];
    
    // Repeat colors if needed
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Show error message
function showError(message) {
    const messagesContainer = document.getElementById('chatMessages');
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
    addMessage('assistant', message, null, true);
}

