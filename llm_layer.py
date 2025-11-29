def llm_decision(prompt):
    text = prompt.lower()

    risk = 0.4

    if "sos" in text:
        risk = 0.95
    if "1 women and 2 men" in text:
        risk = 0.85
    if "men" in text and "women" in text:
        risk = max(risk, 0.6)

    decision = f"Estimated danger at {risk}. Stay alert."

    return decision, risk
