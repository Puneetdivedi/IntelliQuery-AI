"""
Mock data and business logic for Demo Mode.
Used when GROQ_API_KEY is missing.
"""

MOCK_RESPONSES = {
    "top 5 products by revenue": {
        "sql_query": "SELECT p.product_name, SUM(oi.quantity * oi.unit_price) as revenue FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_name ORDER BY revenue DESC LIMIT 5",
        "insights": {
            "summary": "High-end technology items are driving the majority of current revenue.",
            "key_insights": [
                "The 'GamerX Laptop' is the top revenue generator.",
                "Technology category accounts for 65% of top 5 products.",
                "Profit margins remain stable across top sellers."
            ],
            "recommendations": [
                "Increase inventory for technology leaders.",
                "Bundle high-revenue laptops with lower-margin accessories."
            ]
        }
    },
    "show sales trend over last year": {
        "sql_query": "SELECT strftime('%Y-%m', order_date) as month, SUM(oi.quantity * oi.unit_price) as sales FROM orders o JOIN order_items oi ON o.order_id = oi.order_id WHERE order_date >= date('now', '-1 year') GROUP BY month ORDER BY month",
        "insights": {
            "summary": "Consistent growth trend observed with seasonal peaks in Q4.",
            "key_insights": [
                "Sales increased by 20% compared to previous year.",
                "November and December saw a 3x increase due to seasonality.",
                "Q1 saw a slight dip but recovered by March."
            ],
            "recommendations": [
                "Plan marketing spend for Q3 lead-up.",
                "Ensure staffing is optimized for end-of-year peak."
            ]
        }
    },
    "customers by region breakdown": {
        "sql_query": "SELECT r.region_name, COUNT(c.customer_id) as customer_count FROM regions r JOIN customers c ON r.region_id = c.region_id GROUP BY r.region_name ORDER BY customer_count DESC",
        "insights": {
            "summary": "Customer base is well-distributed but concentrated in metropolitan regions.",
            "key_insights": [
                "North region has the highest customer acquisition rate.",
                "West region shows the highest average lifetime value.",
                "Central region is currently an untapped market with high growth potential."
            ],
            "recommendations": [
                "Run hyper-local campaigns in the Central region.",
                "Reward long-term customers in the North with loyalty bonuses."
            ]
        }
    },
    "list orders with 'processing' status": {
        "sql_query": "SELECT order_id, customer_id, order_date, status FROM orders WHERE status = 'Processing' ORDER BY order_date LIMIT 20",
        "insights": {
            "summary": "Order processing times are currently within target KPIs.",
            "key_insights": [
                "12% of total orders are currently in processing.",
                "Average processing time is 1.5 days.",
                "No critical backlog detected."
            ],
            "recommendations": [
                "Monitor Friday order intake to avoid weekend overflow.",
                "Consider automated status updates for 'Processing' orders."
            ]
        }
    }
}

def get_demo_result(question: str) -> dict:
    """Check if question matches a demo query and return mock data."""
    q_lower = question.lower().strip()
    
    # Simple keyword match
    for mock_q, data in MOCK_RESPONSES.items():
        if mock_q in q_lower:
            return data
    return None
