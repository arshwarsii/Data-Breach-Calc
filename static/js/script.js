// Data Breach Impact Calculator - Frontend Logic
let breachData = null;
let costChart = null;

// DOM Elements
const companyForm = document.getElementById('company-form');
const resultsSection = document.getElementById('results-section');
const loadingSpinner = document.getElementById('loading-spinner');
const getRecommendationsBtn = document.getElementById('get-recommendations-btn');
const chatInput = document.getElementById('chat-input');
const sendMessageBtn = document.getElementById('send-message');
const chatContainer = document.getElementById('chat-container');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Form submission
    companyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateBreachImpact();
    });
    
    // Get recommendations button
    getRecommendationsBtn.addEventListener('click', function() {
        getRecommendations();
    });
    
    // Chat functionality
    sendMessageBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    // Example question buttons
    document.querySelectorAll('.example-question').forEach(button => {
        button.addEventListener('click', function() {
            chatInput.value = this.textContent;
            sendChatMessage();
        });
    });
});

// Calculate breach impact
function calculateBreachImpact() {
    // Show loading spinner and hide results
    loadingSpinner.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Get form values
    const companySize = document.getElementById('company-size').value;
    const annualRevenue = document.getElementById('annual-revenue').value;
    const industry = document.getElementById('industry').value;
    
    // Validate inputs
    if (!companySize || !annualRevenue || !industry) {
        alert('Please fill in all fields');
        loadingSpinner.style.display = 'none';
        return;
    }
    
    // Prepare data for API call
    const data = {
        company_size: companySize,
        annual_revenue: annualRevenue,
        industry: industry
    };
    
    // Make API call
    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Store the data globally
        breachData = data;
        
        // Update the UI with results
        updateBreachScenario(data.breach_scenario);
        updateFinancialImpact(data.financial_impact, data.explanation);
        updatePrevention(data.prevention);
        updateRecovery(data.recovery);
        
        // Create cost breakdown chart
        createCostChart(data.financial_impact);
        
        // Add initial AI assistant message
        addBotMessage(`I've analyzed the potential impact of a ${data.breach_scenario.severity} data breach for your ${industry} company. The total estimated cost would be ${data.financial_impact.total_cost}, affecting ${data.breach_scenario.records_affected.toLocaleString()} records. How can I help you understand these results?`);
        
        // Hide loading spinner and show results
        loadingSpinner.style.display = 'none';
        resultsSection.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        loadingSpinner.style.display = 'none';
    });
}

// Get security recommendations
function getRecommendations() {
    if (!breachData) return;
    
    const data = {
        company_size: document.getElementById('company-size').value,
        annual_revenue: document.getElementById('annual-revenue').value,
        industry: document.getElementById('industry').value,
        total_cost: breachData.financial_impact.total_cost_raw
    };
    
    // Make API call
    fetch('/get_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        updateRecommendations(data);
        
        // Add AI assistant message
        addBotMessage(`I've prepared some security recommendations tailored to your company profile. The suggested annual security budget is ${data.annual_security_budget}, which is a fraction of the potential breach cost.`);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while fetching recommendations.');
    });
}

// Update breach scenario section
function updateBreachScenario(scenario) {
    document.getElementById('breach-description').textContent = scenario.description;
    document.getElementById('breach-severity').textContent = `Severity: ${capitalizeFirstLetter(scenario.severity)}`;
    document.getElementById('records-affected').textContent = scenario.records_affected.toLocaleString();
    document.getElementById('industry-impact').textContent = scenario.industry_impact;
}

// Update financial impact section
function updateFinancialImpact(financialImpact, explanation) {
    document.getElementById('total-cost').textContent = financialImpact.total_cost;
    document.getElementById('direct-cost').textContent = financialImpact.direct_cost;
    document.getElementById('regulatory-fines').textContent = financialImpact.regulatory_fines;
    document.getElementById('revenue-loss').textContent = financialImpact.revenue_loss;
    document.getElementById('reputation-damage').textContent = financialImpact.reputation_damage;
    document.getElementById('recovery-cost').textContent = financialImpact.recovery_cost;
    
    // Explanation details
    document.getElementById('cost-per-record').textContent = explanation.cost_per_record;
    document.getElementById('gdpr-rate').textContent = explanation.gdpr_fine_rate;
    document.getElementById('churn-rate').textContent = explanation.churn_rate;
}

// Update prevention section
function updatePrevention(prevention) {
    document.getElementById('prevention-cost').textContent = prevention.estimated_prevention_cost;
    document.getElementById('prevention-roi').textContent = prevention.roi;
}

// Update recovery section
function updateRecovery(recovery) {
    document.getElementById('recovery-time').textContent = recovery.estimated_time;
}

// Update recommendations section
function updateRecommendations(data) {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';
    
    // Add annual security budget card
    const budgetCard = document.createElement('div');
    budgetCard.className = 'card bg-light mb-4';
    budgetCard.innerHTML = `
        <div class="card-body text-center">
            <h4 class="card-title">Recommended Annual Security Budget</h4>
            <h2 class="display-6 text-primary">${data.annual_security_budget}</h2>
            <p class="text-muted">Based on your company profile and potential breach impact</p>
        </div>
    `;
    container.appendChild(budgetCard);
    
    // Add recommendations
    data.recommendations.forEach(rec => {
        const effectiveness = rec.effectiveness.toLowerCase();
        let badgeClass = 'bg-info';
        
        if (effectiveness === 'high') {
            badgeClass = 'bg-primary';
        } else if (effectiveness === 'very high') {
            badgeClass = 'bg-success';
        } else if (effectiveness === 'critical') {
            badgeClass = 'bg-danger';
        }
        
        const card = document.createElement('div');
        card.className = 'card recommendation-card';
        card.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="card-title mb-0">${rec.title}</h5>
                    <span class="badge ${badgeClass} badge-effectiveness">${rec.effectiveness}</span>
                </div>
                <p class="card-text">${rec.description}</p>
                <div class="text-end">
                    <span class="recommendation-cost">${rec.cost}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
    
    // Hide the get recommendations button
    getRecommendationsBtn.style.display = 'none';
}

// Create cost breakdown chart
function createCostChart(financialImpact) {
    // Destroy existing chart if it exists
    if (costChart) {
        costChart.destroy();
    }
    
    // Prepare data for chart
    const labels = [
        'Direct Costs', 
        'Regulatory Fines', 
        'Revenue Loss',
        'Reputation Damage',
        'Recovery Cost'
    ];
    
    const data = [
        financialImpact.direct_cost_raw,
        financialImpact.regulatory_fines_raw,
        financialImpact.revenue_loss_raw,
        financialImpact.reputation_damage_raw,
        financialImpact.recovery_cost_raw
    ];
    
    // Get canvas context
    const ctx = document.getElementById('cost-chart').getContext('2d');
    
    // Create chart
    costChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cost Breakdown',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000000) {
                                return '$' + (value / 1000000).toFixed(1) + 'M';
                            } else if (value >= 1000) {
                                return '$' + (value / 1000).toFixed(1) + 'K';
                            } else {
                                return '$' + value;
                            }
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Cost Breakdown'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let value = context.raw;
                            if (value >= 1000000) {
                                return '$' + (value / 1000000).toFixed(2) + ' million';
                            } else if (value >= 1000) {
                                return '$' + (value / 1000).toFixed(2) + ' thousand';
                            } else {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        }
    });
}

// Chat functionality
function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Generate AI response based on user message
    generateAIResponse(message);
}

// Add user message to chat
function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message user clearfix';
    messageElement.innerHTML = `
        <div class="chat-avatar">
            <i class="fas fa-user text-white" style="font-size: 14px; margin: 8px;"></i>
        </div>
        ${message}
    `;
    chatContainer.appendChild(messageElement);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add bot message to chat
function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message bot clearfix';
    messageElement.innerHTML = `
        <div class="chat-avatar">
            <i class="fas fa-robot text-white" style="font-size: 14px; margin: 8px;"></i>
        </div>
        ${message}
    `;
    chatContainer.appendChild(messageElement);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Generate AI response based on predefined answers
function generateAIResponse(userMessage) {
    // Convert user message to lowercase for easier matching
    const message = userMessage.toLowerCase();
    
    // Define response patterns
    let response = "";
    
    // Check for specific questions
    if (message.includes("gdpr") || message.includes("regulatory") || message.includes("fines")) {
        response = "Regulatory fines like GDPR are calculated as a percentage of global annual revenue. For severe breaches, fines can reach up to 4% of annual revenue (or €20M, whichever is higher). The severity level determines the percentage applied.";
    } 
    else if (message.includes("churn") || message.includes("revenue loss")) {
        response = "Customer churn rate represents the percentage of customers who leave after a breach. This directly impacts revenue. In the " + (breachData ? breachData.breach_scenario.severity : "simulated") + " breach scenario, we estimated a churn rate of " + (breachData ? breachData.explanation.churn_rate : "X%") + " based on industry averages and breach severity.";
    }
    else if (message.includes("prevention") || message.includes("strategy") || message.includes("protect")) {
        response = "The most effective prevention strategy combines employee security training with robust technical measures. For your specific industry, " + (breachData ? "investing in " + (breachData.prevention.estimated_prevention_cost) + " toward cybersecurity could yield an ROI of " + breachData.prevention.roi : "investing in cybersecurity provides significant ROI") + " by preventing costlier breaches.";
    }
    else if (message.includes("cost per record") || message.includes("record cost")) {
        response = "Cost per record varies by industry. For " + (breachData ? breachData.explanation.cost_per_record : "$X") + " per compromised record in your industry, which includes notification costs, credit monitoring, legal expenses, and customer service.";
    }
    else if (message.includes("reputation") || message.includes("brand damage")) {
        response = "Reputation damage is calculated based on factors like lost future business, reduced customer trust, and brand devaluation. Though harder to quantify precisely, it often exceeds direct costs and can have long-lasting impacts on company valuation.";
    }
    else if (message.includes("recovery") || message.includes("time to recover")) {
        response = "Recovery time depends on breach severity and company preparedness. For the " + (breachData ? breachData.breach_scenario.severity : "simulated") + " breach scenario, we estimate " + (breachData ? breachData.recovery.estimated_time : "X months") + " to fully recover, including investigation, remediation, and rebuilding customer trust.";
    }
    else if (message.includes("roi") || message.includes("return on investment")) {
        response = "The cybersecurity ROI is calculated by dividing the potential breach costs by the prevention investment. For your scenario, every $1 invested in prevention could save " + (breachData ? breachData.prevention.roi.replace("x investment", "") : "several dollars") + " in breach-related expenses.";
    }
    else if (message.includes("industry") || message.includes("sector")) {
        const industry = breachData ? document.getElementById('industry').value : "your industry";
        response = `${capitalizeFirstLetter(industry)} organizations face unique cybersecurity challenges. They typically have ${industrySpecificInfo(industry)} This affects both the likelihood of breaches and the cost per record.`;
    }
    else if (message.includes("hello") || message.includes("hi ") || message === "hi") {
        response = "Hello! I'm your cybersecurity assistant. I can help explain the breach impact calculation, prevention strategies, or specific aspects of the financial impact. What would you like to know?";
    }
    else {
        response = "Thanks for your question. To better assist you with understanding data breach impacts, could you ask about specific aspects like regulatory fines, prevention strategies, recovery time, or ROI calculations? I'm here to help explain any part of the simulation.";
    }
    
    // Add bot's response with a slight delay to seem more natural
    setTimeout(() => {
        addBotMessage(response);
    }, 600);
}

// Helper functions
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function industrySpecificInfo(industry) {
    const industryInfo = {
        "healthcare": "strict regulatory requirements like HIPAA and highly sensitive personal health information.",
        "financial": "high-value financial data and stringent regulations like PCI-DSS and GLBA.",
        "retail": "customer payment information and high transaction volumes.",
        "technology": "intellectual property concerns and large volumes of user data.",
        "education": "student records and research data with varying retention requirements.",
        "manufacturing": "intellectual property, supply chain security issues, and operational technology.",
        "other": "specific data security requirements based on their operations."
    };
    
    return industryInfo[industry.toLowerCase()] || "specific security considerations unique to their operations.";
}