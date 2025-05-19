from flask import Flask, render_template, request, jsonify
import random
import json
import math

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
    "severe": 0.04,  # 4% of global revenue
    "moderate": 0.02,  # 2% of global revenue
    "minor": 0.01  # 1% of global revenue
}

# Based on industry averages
CUSTOMER_CHURN_RATES = {
    "healthcare": {"min": 0.05, "max": 0.15},
    "financial": {"min": 0.07, "max": 0.20},
    "retail": {"min": 0.02, "max": 0.10},
    "technology": {"min": 0.03, "max": 0.12},
    "education": {"min": 0.01, "max": 0.08},
    "manufacturing": {"min": 0.01, "max": 0.05},
    "other": {"min": 0.02, "max": 0.10}
}

# Breach scenarios based on company size
def generate_breach_scenario(company_size, industry):
    # Define record counts based on company size
    if company_size <= 50:  # Small
        records_affected = random.randint(100, 5000)
        severity = random.choice(["minor", "moderate"])
    elif company_size <= 250:  # Medium
        records_affected = random.randint(3000, 25000)
        severity = random.choice(["minor", "moderate", "severe"])
    else:  # Large
        records_affected = random.randint(15000, 100000)
        severity = random.choice(["moderate", "severe"])
    
    # Adjust based on industry risk profile
    if industry in ["healthcare", "financial"]:
        records_affected = int(records_affected * random.uniform(1.2, 1.5))
    
    return {
        "records_affected": records_affected,
        "severity": severity
    }

def calculate_breach_impact(data):
    company_size = int(data.get("company_size", 500))
    annual_revenue = float(data.get("annual_revenue", 10000000))
    industry = data.get("industry", "other").lower()
    
    # Generate breach scenario
    scenario = generate_breach_scenario(company_size, industry)
    records_affected = scenario["records_affected"]
    severity = scenario["severity"]
    
    # Calculate direct costs
    cost_per_record = random.uniform(
        COST_PER_RECORD.get(industry, COST_PER_RECORD["other"])["min"],
        COST_PER_RECORD.get(industry, COST_PER_RECORD["other"])["max"]
    )
    direct_cost = records_affected * cost_per_record
    
    # Calculate regulatory fines
    gdpr_fine_percentage = GDPR_FINE_PERCENTAGE.get(severity, 0.01)
    regulatory_fines = annual_revenue * gdpr_fine_percentage
    
    # Calculate revenue loss due to customer churn
    churn_rate = random.uniform(
        CUSTOMER_CHURN_RATES.get(industry, CUSTOMER_CHURN_RATES["other"])["min"],
        CUSTOMER_CHURN_RATES.get(industry, CUSTOMER_CHURN_RATES["other"])["max"]
    )
    # Adjust churn rate based on severity
    if severity == "severe":
        churn_rate *= 1.5
    elif severity == "minor":
        churn_rate *= 0.7
    
    revenue_loss = annual_revenue * churn_rate
    
    # Calculate PR and reputation damage (more abstract)
    reputation_damage = direct_cost * random.uniform(0.5, 1.5)
    
    # Calculate recovery costs
    recovery_cost = direct_cost * random.uniform(1.2, 2.0)
    
    # Calculate preventive measures cost (what it would have cost to prevent)
    preventive_cost = direct_cost * random.uniform(0.1, 0.3)
    
    # Protection ROI
    roi = (direct_cost + regulatory_fines + revenue_loss + reputation_damage) / preventive_cost
    
    # Time to recovery
    if severity == "minor":
        recovery_time = random.randint(1, 6)  # 1-6 months
    elif severity == "moderate":
        recovery_time = random.randint(6, 18)  # 6-18 months
    else:
        recovery_time = random.randint(12, 36)  # 1-3 years
    
    # Create breach description
    breach_type = random.choice([
        "customer data exposure", 
        "employee data breach",
        "financial information leak", 
        "healthcare records compromise",
        "intellectual property theft",
        "ransomware attack"
    ])
    
    # Additional impact based on industry
    industry_specific_impacts = {
        "healthcare": "Potential HIPAA violations and patient trust violation",
        "financial": "Financial fraud risk and banking regulation penalties",
        "retail": "Customer payment information exposure risk",
        "technology": "Intellectual property theft and competitive disadvantage",
        "education": "Student data protection concerns and academic integrity",
        "manufacturing": "Supply chain disruption and trade secret exposure",
        "other": "Business continuity challenges and stakeholder trust erosion"
    }
    
    # Format numbers for better readability
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
    
    # Basic recommendations based on company size and industry
    security_measures = []
    
    # Core recommendations for all businesses
    security_measures.append({
        "title": "Employee Security Training",
        "description": "Regular cybersecurity awareness training for all staff",
        "cost": format_currency(company_size * random.uniform(100, 300)),
        "effectiveness": "High"
    })
    
    security_measures.append({
        "title": "Data Encryption",
        "description": "Implement end-to-end encryption for sensitive data",
        "cost": format_currency(company_size * random.uniform(50, 150)),
        "effectiveness": "Very High"
    })
    
    # Size-specific recommendations
    if company_size <= 50:  # Small
        security_measures.append({
            "title": "Cloud Security Services",
            "description": "Managed security services for small teams",
            "cost": format_currency(random.uniform(5000, 15000)),
            "effectiveness": "High"
        })
    elif company_size <= 250:  # Medium
        security_measures.append({
            "title": "Security Information Management System",
            "description": "SIEM solution for monitoring and alerting",
            "cost": format_currency(random.uniform(25000, 75000)),
            "effectiveness": "High"
        })
    else:  # Large
        security_measures.append({
            "title": "Dedicated Security Team",
            "description": "In-house cybersecurity experts",
            "cost": format_currency(random.uniform(250000, 500000)),
            "effectiveness": "Very High"
        })
    
    # Industry-specific recommendations
    if industry == "healthcare":
        security_measures.append({
            "title": "HIPAA Compliance Tools",
            "description": "Specialized healthcare data protection",
            "cost": format_currency(company_size * random.uniform(200, 500)),
            "effectiveness": "Critical"
        })
    elif industry == "financial":
        security_measures.append({
            "title": "Financial Transaction Monitoring",
            "description": "Real-time fraud detection systems",
            "cost": format_currency(annual_revenue * random.uniform(0.001, 0.003)),
            "effectiveness": "Critical"
        })
    elif industry == "retail":
        security_measures.append({
            "title": "PCI DSS Compliance Suite",
            "description": "Payment card industry security standards tools",
            "cost": format_currency(annual_revenue * random.uniform(0.0005, 0.002)),
            "effectiveness": "High"
        })
    
    return jsonify({
        "recommendations": security_measures,
        "annual_security_budget": format_currency(total_cost * random.uniform(0.05, 0.15))
    })

def format_currency(amount):
    if amount >= 1000000:
        return f"${amount/1000000:.2f}M"
    elif amount >= 1000:
        return f"${amount/1000:.2f}K"
    else:
        return f"${amount:.2f}"

if __name__ == '__main__':
    app.run(debug=True)