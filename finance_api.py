import re
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

FEES = {
    "SV001": [{"fee_id": "F001", "term": "HK1-2026", "amount": 12500000, "paid": 12500000}],
    "SV002": [{"fee_id": "F002", "term": "HK1-2026", "amount": 12500000, "paid": 5000000}],
    "SV003": [{"fee_id": "F003", "term": "HK1-2026", "amount": 11000000, "paid": 0}],
    "SV004": [{"fee_id": "F004", "term": "HK1-2026", "amount": 13000000, "paid": 13000000}],
    "SV005": [{"fee_id": "F005", "term": "HK1-2026", "amount": 12500000, "paid": 2500000}],
}
NEXT_FEE_ID = 6
ID_RE = re.compile(r"^SV\d{3}$")


@app.get("/health")
def health():
    return jsonify(service="finance", status="UP")


@app.get("/api/fees/<sid>")
def get_fees(sid):
    delay = request.args.get("delay", type=float)
    if delay and delay > 0:
        time.sleep(min(delay, 10))
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    fees = FEES.get(sid)
    if not fees:
        return jsonify(error="NOT_FOUND", message=f"Chưa có khoản phí cho {sid}"), 404
    total = sum(f["amount"] for f in fees)
    paid = sum(f["paid"] for f in fees)
    return jsonify(student_id=sid, fees=fees, total=total, paid=paid, balance=total - paid), 200


@app.post("/api/fees/<sid>")
def create_fee(sid):
    global NEXT_FEE_ID
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    body = request.get_json(silent=True) or {}
    if not isinstance(body.get("amount"), (int, float)) or body["amount"] <= 0 or not body.get("term"):
        return jsonify(error="INVALID_BODY", message="Cần term (chuỗi) và amount > 0"), 400
    lst = FEES.setdefault(sid, [])
    fee = {
        "fee_id": f"F{NEXT_FEE_ID:03d}",
        "term": body["term"],
        "amount": body["amount"],
        "paid": 0,
    }
    NEXT_FEE_ID += 1
    lst.append(fee)
    return jsonify(fee), 201


@app.put("/api/fees/<sid>/<fee_id>")
def update_fee(sid, fee_id):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    fees = FEES.get(sid, [])
    target = next((f for f in fees if f["fee_id"] == fee_id), None)
    if not target:
        return jsonify(error="NOT_FOUND", message=f"Không tìm thấy khoản phí {fee_id} của {sid}"), 404
    body = request.get_json(silent=True) or {}
    if not body:
        return jsonify(error="INVALID_BODY", message="Body JSON không được rỗng"), 400

    new_amount = body.get("amount", target["amount"])
    new_paid = body.get("paid", target["paid"])
    new_term = body.get("term", target["term"])

    if not isinstance(new_amount, (int, float)) or new_amount <= 0:
        return jsonify(error="INVALID_BODY", message="amount phải > 0"), 400
    if not isinstance(new_paid, (int, float)) or new_paid < 0 or new_paid > new_amount:
        return jsonify(error="INVALID_BODY", message="paid phải nằm trong khoảng [0, amount]"), 400
    if not isinstance(new_term, str) or not new_term.strip():
        return jsonify(error="INVALID_BODY", message="term không hợp lệ"), 400

    target["amount"] = new_amount
    target["paid"] = new_paid
    target["term"] = new_term.strip()
    return jsonify(target), 200


@app.delete("/api/fees/<sid>/<fee_id>")
def delete_fee(sid, fee_id):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV không hợp lệ"), 400
    fees = FEES.get(sid, [])
    target = next((f for f in fees if f["fee_id"] == fee_id), None)
    if not target:
        return jsonify(error="NOT_FOUND", message=f"Không tìm thấy khoản phí {fee_id} của {sid}"), 404
    fees.remove(target)
    if not fees:
        del FEES[sid]
    return jsonify(message=f"Đã xóa khoản phí {fee_id}", deleted=target), 200


if __name__ == "__main__":
    app.run(port=5002)