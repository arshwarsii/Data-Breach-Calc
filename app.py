from flask import Flask, render_template, request, jsonify
import json
import math
import requests  # Added for OpenRouter API calls

app = Flask(__name__)

# Constants for breach cost calculations
COST_PER_RECORD = {
    "healthcare": {"min": 350, "max": 450},
    "financial": {"min": 300, "max": 400},
    "retail": {"min": 150, "max": 250},
    "technology": {"min": 200, "max": 300},
    "education": {"min": 175, "max": 225},
    "manufacturing": {"min": 150, "max": 200},
    "other": {"min": 150, "max": 200}
}

GDPR_FINE_PERCENTAGE = {
    "severe": 0.04,
    "moderate": 0.02,
    "minor": 0.01
}

CUSTOMER_CHURN_RATES = {
    "healthcare": {"min": 0.05, "max": 0.15},
    "financial": {"min": 0.07, "max": 0.20},
    "retail": {"min": 0.02, "max": 0.10},
    "technology": {"min": 0.03, "max": 0.12},
    "education": {"min": 0.01, "max": 0.08},
    "manufacturing": {"min": 0.01, "max": 0.05},
    "other": {"min": 0.02, "max": 0.10}
}

# OpenRouter API configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def generate_breach_scenario(company_size, annual_revenue, records_compromised, industry):
    records_affected = max(1, int(records_compromised))
    if company_size <= 50:
        severity = "minor"
    elif company_size <= 250:
        severity = "moderate"
    else:
        severity = "severe"
    
    return {
        "records_affected": records_affected,
        "severity": severity
    }

def calculate_breach_impact(data):
    company_size = int(data.get("company_size", 500))
    annual_revenue = float(data.get("annual_revenue", 10000000))
    industry = data.get("industry", "other").lower()
    records_compromised = float(data.get("records_compromised", 100))
    
    scenario = generate_breach_scenario(company_size, annual_revenue, records_compromised, industry)
    records_affected = scenario["records_affected"]
    severity = scenario["severity"]
    
    cost_per_record = (
        COST_PER_RECORD.get(industry, COST_PER_RECORD["other"])["min"] +
        COST_PER_RECORD.get(industry, COST_PER_RECORD["other"])["max"]
    ) / 2
    direct_cost = records_affected * cost_per_record
    direct_cost = min(direct_cost, annual_revenue / 3)
    
    gdpr_fine_percentage = GDPR_FINE_PERCENTAGE.get(severity, 0.01)
    regulatory_fines = annual_revenue * gdpr_fine_percentage
    
    churn_rate = (
        CUSTOMER_CHURN_RATES.get(industry, CUSTOMER_CHURN_RATES["other"])["min"] +
        CUSTOMER_CHURN_RATES.get(industry, CUSTOMER_CHURN_RATES["other"])["max"]
    ) / 2
    if severity == "severe":
        churn_rate *= 1.5
    elif severity == "minor":
        churn_rate *= 0.7
    revenue_loss = annual_revenue * churn_rate
    
    reputation_multiplier = 0.5 if annual_revenue < 100000 else 1.0
    reputation_damage = direct_cost * reputation_multiplier
    reputation_damage = min(reputation_damage, annual_revenue / 3)
    
    recovery_multiplier = 0.8 if annual_revenue < 100000 else 1.6
    recovery_cost = direct_cost * recovery_multiplier
    recovery_cost = min(recovery_cost, annual_revenue / 3)
    
    preventive_cost = direct_cost * 0.2
    
    roi = (direct_cost + regulatory_fines + revenue_loss + reputation_damage + recovery_cost) / preventive_cost
    
    if severity == "minor":
        recovery_time = 3
    elif severity == "moderate":
        recovery_time = 12
    else:
        recovery_time = 24
    
    breach_type = "customer data exposure"
    
    industry_specific_impacts = {
        "healthcare": "Potential HIPAA violations and patient trust violation",
        "financial": "Financial fraud risk and banking regulation penalties",
        "retail": "Customer payment information exposure risk",
        "technology": "Intellectual property theft and competitive disadvantage",
        "education": "Student data protection concerns and academic integrity",
        "manufacturing": "Supply chain disruption and trade secret exposure",
        "other": "Business continuity challenges and stakeholder trust erosion"
    }
    
    def format_currency(amount):
        if amount >= 1000000:
            return f"${amount/1000000:.2f}M"
        elif amount >= 1000:
            return f"${amount/1000:.2f}K"
        else:
            return f"${amount:.2f}"
    
    result = {
        "breach_scenario": {
            "description": f"{breach_type.title()} affecting {records_affected:,} records",
            "severity": severity,
            "records_affected": records_affected,
            "industry_impact": industry_specific_impacts.get(industry, industry_specific_impacts["other"])
        },
        "financial_impact": {
            "direct_cost": format_currency(direct_cost),
            "direct_cost_raw": direct_cost,
            "regulatory_fines": format_currency(regulatory_fines),
            "regulatory_fines_raw": regulatory_fines,
            "revenue_loss": format_currency(revenue_loss),
            "revenue_loss_raw": revenue_loss,
            "reputation_damage": format_currency(reputation_damage),
            "reputation_damage_raw": reputation_damage,
            "recovery_cost": format_currency(recovery_cost),
            "recovery_cost_raw": recovery_cost,
            "total_cost": format_currency(direct_cost + regulatory_fines + revenue_loss + reputation_damage + recovery_cost),
            "total_cost_raw": direct_cost + regulatory_fines + revenue_loss + reputation_damage + recovery_cost
        },
        "prevention": {
            "estimated_prevention_cost": format_currency(preventive_cost),
            "prevention_cost_raw": preventive_cost,
            "roi": f"{roi:.2f}x investment",
            "roi_raw": roi
        },
        "recovery": {
            "estimated_time": f"{recovery_time} months",
            "recovery_time_raw": recovery_time
        },
        "explanation": {
            "cost_per_record": f"${cost_per_record:.2f}",
            "churn_rate": f"{churn_rate*100:.2f}%",
            "gdpr_fine_rate": f"{gdpr_fine_percentage*100:.2f}%"
        }
    }
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    result = calculate_breach_impact(data)
    return jsonify(result)

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    data = request.json
    company_size = int(data.get("company_size", 500))
    annual_revenue = float(data.get("annual_revenue", 10000000))
    industry = data.get("industry", "other").lower()
    total_cost = float(data.get("total_cost", 1000000))
    
    security_measures = []
    
    security_measures.append({
        "title": "Employee Security Training",
        "description": "Regular cybersecurity awareness training for all staff",
        "cost": format_currency(company_size * 200),
        "effectiveness": "High"
    })
    
    security_measures.append({
        "title": "Data Encryption",
        "description": "Implement end-to-end encryption for sensitive data",
        "cost": format_currency(company_size * 100),
        "effectiveness": "Very High"
    })
    
    if company_size <= 50:
        security_measures.append({
            "title": "Cloud Security Services",
            "description": "Managed security services for small teams",
            "cost": format_currency(10000),
            "effectiveness": "High"
        })
    elif company_size <= 250:
        security_measures.append({
            "title": "Security Information Management System",
            "description": "SIEM solution for monitoring and alerting",
            "cost": format_currency(50000),
            "effectiveness": "High"
        })
    else:
        security_measures.append({
            "title": "Dedicated Security Team",
            "description": "In-house cybersecurity experts",
            "cost": format_currency(375000),
            "effectiveness": "Very High"
        })
    
    if industry == "healthcare":
        security_measures.append({
            "title": "HIPAA Compliance Tools",
            "description": "Specialized healthcare data protection",
            "cost": format_currency(company_size * 350),
            "effectiveness": "Critical"
        })
    elif industry == "financial":
        security_measures.append({
            "title": "Financial Transaction Monitoring",
            "description": "Real-time fraud detection systems",
            "cost": format_currency(annual_revenue * 0.002),
            "effectiveness": "Critical"
        })
    elif industry == "retail":
        security_measures.append({
            "title": "PCI DSS Compliance Suite",
            "description": "Payment card industry security standards tools",
            "cost": format_currency(annual_revenue * 0.00125),
            "effectiveness": "High"
        })
    
    return jsonify({
        "recommendations": security_measures,
        "annual_security_budget": format_currency(total_cost * 0.1)
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Prepare OpenRouter API request
    try:
        response = requests.post(
            url=OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:5000",  # Replace with your site URL if needed
                "X-Title": "Data Breach Calculator",      # Replace with your site title if needed
            },
            data=json.dumps({
                "model": "openai/gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            return jsonify({'response': bot_response})
        else:
            return jsonify({'error': f"OpenRouter API error: {response.status_code} - {response.text}"}), response.status_code
    
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500

def format_currency(amount):
    if amount >= 1000000:
        return f"${amount/1000000:.2f}M"
    elif amount >= 1000:
        return f"${amount/1000:.2f}K"
    else:
        return f"${amount:.2f}"

if __name__ == '__main__':
    app.run(debug=True)
