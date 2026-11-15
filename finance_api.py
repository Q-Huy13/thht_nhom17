"""Finance API (cổng 5002) - khoản học phí."""
import re
from flask import Flask, jsonify, request

app = Flask(__name__)
FEES = {
    "SV001": [{"fee_id": "F001", "term": "HK1-2026", "amount": 12500000, "paid": 12500000}],
    "SV002": [{"fee_id": "F002", "term": "HK1-2026", "amount": 12500000, "paid": 5000000}],
    "SV003": [{"fee_id": "F003", "term": "HK1-2026", "amount": 11000000, "paid": 0}],
    "SV004": [{"fee_id": "F004", "term": "HK1-2026", "amount": 13000000, "paid": 13000000}],
    "SV005": [{"fee_id": "F005", "term": "HK1-2026", "amount": 12500000, "paid": 2500000}],
}
ID_RE = re.compile(r"^SV\d{3}$")

@app.get("/health")
def health():
    return jsonify(service="finance", status="UP")

@app.get("/api/fees/<sid>")
def get_fees(sid):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    fees = FEES.get(sid)
    if fees is None:
        return jsonify(error="NOT_FOUND", message=f"Chưa có khoản phí cho {sid}"), 404
    total = sum(f["amount"] for f in fees); paid = sum(f["paid"] for f in fees)
    return jsonify(student_id=sid, fees=fees, total=total, paid=paid, balance=total - paid)

@app.post("/api/fees/<sid>")
def create_fee(sid):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    body = request.get_json(silent=True) or {}
    if not isinstance(body.get("amount"), (int, float)) or body["amount"] <= 0 or not body.get("term"):
        return jsonify(error="INVALID_BODY", message="Cần term (chuỗi) và amount > 0"), 400
    lst = FEES.setdefault(sid, [])
    fee = {"fee_id": f"F{sum(len(v) for v in FEES.values()) + 1:03d}", "term": body["term"],
           "amount": body["amount"], "paid": 0}
    lst.append(fee)
    return jsonify(fee), 201

if __name__ == "__main__":
    app.run(port=5002)
