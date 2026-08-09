def _is(payload, key, value):
    return str(payload.get(key, "")).lower() == value.lower()


def build_recommendations(payload: dict, probability: float) -> list:
    recs = []
    p = probability
    raw = {k: str(v).lower() for k, v in payload.items()}

    if _is(payload, "Contract", "Month-to-month"):
        recs.append(
            {
                "title": "Offer annual contract",
                "reason": "Month-to-month contracts carry the highest churn risk.",
                "impact": "Reduce churn probability by up to 0.20",
                "priority": "high",
                "category": "contract",
            }
        )
    if _is(payload, "InternetService", "Fiber optic") and float(payload.get("MonthlyCharges") or 0) > 75:
        recs.append(
            {
                "title": "Right-size fiber plan",
                "reason": "High fiber charges with high churn signal price sensitivity.",
                "impact": "Lower spend pressure; reduce churn probability",
                "priority": "high",
                "category": "pricing",
            }
        )
    if not _is(payload, "OnlineSecurity", "Yes") and not _is(payload, "InternetService", "No"):
        recs.append(
            {
                "title": "Upsell online security",
                "reason": "Customers without online security churn more often.",
                "impact": "Improve stickiness and account security",
                "priority": "medium",
                "category": "upsell",
            }
        )
    if not _is(payload, "TechSupport", "Yes") and not _is(payload, "InternetService", "No"):
        recs.append(
            {
                "title": "Add tech support",
                "reason": "No support coverage increases frustration and churn.",
                "impact": "Boost support satisfaction and retention",
                "priority": "medium",
                "category": "upsell",
            }
        )
    if float(payload.get("tenure") or 0) < 6:
        recs.append(
            {
                "title": "Onboarding & loyalty program",
                "reason": "New customers in the first 6 months are high-risk.",
                "impact": "Increase early engagement and tenure",
                "priority": "high",
                "category": "retention",
            }
        )
    if _is(payload, "PaymentMethod", "Electronic check"):
        recs.append(
            {
                "title": "Switch to automatic billing",
                "reason": "Electronic check payments correlate with higher churn.",
                "impact": "Streamline billing; add discount incentive",
                "priority": "low",
                "category": "billing",
            }
        )
    if _is(payload, "PaperlessBilling", "Yes"):
        recs.append(
            {
                "title": "Win-back / personalized offer",
                "reason": "Paperless billing users in high-risk cohorts need proactive outreach.",
                "impact": "Prevent churn with targeted discount",
                "priority": "medium",
                "category": "retention",
            }
        )
    if _is(payload, "StreamingTV", "Yes") or _is(payload, "StreamingMovies", "Yes"):
        recs.append(
            {
                "title": "Entertainment bundle discount",
                "reason": "Streaming-heavy users respond well to bundled pricing.",
                "impact": "Increase ARPU while reducing churn",
                "priority": "low",
                "category": "pricing",
            }
        )
    if not _is(payload, "Partner", "Yes") and not _is(payload, "Dependents", "Yes"):
        recs.append(
            {
                "title": "Family & multi-line offers",
                "reason": "Single-line customers without household ties churn more.",
                "impact": "Deepen account relationship",
                "priority": "low",
                "category": "upsell",
            }
        )

    for rec in recs:
        if p >= 0.7 and rec["priority"] == "medium":
            rec["priority"] = "high"
        elif p < 0.3 and rec["priority"] == "high":
            rec["priority"] = "medium"

    order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: order[r["priority"]])
    return recs[:6]


def risk_category(probability: float) -> str:
    if probability >= 0.7:
        return "Very High"
    if probability >= 0.5:
        return "High"
    if probability >= 0.3:
        return "Medium"
    return "Low"
