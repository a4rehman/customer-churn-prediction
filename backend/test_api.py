from fastapi.testclient import TestClient

from app.main import app


def run_tests():
    with TestClient(app) as client:
        test_health(client)
        test_login_and_predict(client)
        test_search(client)
        test_admin_stats(client)
        test_admin_reports(client)
    print("\nALL BACKEND TESTS PASSED")


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    print("health:", body)


def test_login_and_predict(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "customer_id": "TEST001",
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 2,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 89.9,
        "TotalCharges": 179.8,
    }
    r = client.post("/api/predict", headers=headers, json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert 0.0 <= body["probability"] <= 1.0
    assert body["contributions"], "no SHAP contributions"
    assert body["recommendations"], "no recommendations"
    print("predict:", {k: body[k] for k in ("customer_id", "probability", "churn_prediction", "risk_category", "model_version")})
    print("top contrib:", [(c["feature"], round(c["value"], 3)) for c in body["top_contributors"][:4]])
    print("recs:", [(c["priority"], c["title"]) for c in body["recommendations"][:3]])


def test_search(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/customers/search?q=&limit=5", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] > 0
    print("search total:", body["total"], "first risk:", body["customers"][0].get("risk"))


def test_admin_stats(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/admin/stats", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    print("admin stats:", {k: body[k] for k in ("total_customers", "churn_rate", "predictions_today", "model_roc_auc", "model_name")})


def test_admin_reports(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/admin/model", headers=headers)
    assert r.status_code == 200, r.text
    assert "best" in r.json()
    r = client.get("/api/admin/reports/shap_summary.png", headers=headers)
    assert r.status_code in (200, 404), r.text
    print("admin model + report images test passed")


if __name__ == "__main__":
    run_tests()
