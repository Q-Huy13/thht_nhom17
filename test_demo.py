"""Kiểm thử tự động: chạy 3 dịch vụ, thử thành công / 404 / 400 / Finance sập / POST."""
import subprocess, sys, time, requests

def start(f): return subprocess.Popen([sys.executable, f])
procs = {n: start(n + ".py") for n in ("academic_api", "finance_api", "portal")}
time.sleep(2)
P = "http://127.0.0.1:5000/api/portal/"
results = []
def check(name, cond, detail=""):
    results.append(bool(cond)); print(("PASS" if cond else "FAIL"), "-", name, detail)
try:
    r = requests.get(P + "SV002"); check("TC01 Thành công (200, status ok)", r.status_code == 200 and r.json()["status"] == "ok", r.text[:80])
    r = requests.get(P + "SV999"); check("TC02 Không tìm thấy (404)", r.status_code == 404)
    r = requests.get(P + "abc");   check("TC03 Mã không hợp lệ (400)", r.status_code == 400)
    r = requests.get(P + "SV008"); check("TC04 Có SV nhưng chưa có phí (partial)", r.status_code == 200 and r.json()["status"] == "partial")
    r = requests.post("http://127.0.0.1:5002/api/fees/SV006", json={"term": "HK1-2026", "amount": 9000000}); check("TC05 POST tạo phí (201)", r.status_code == 201)
    r = requests.post("http://127.0.0.1:5002/api/fees/SV006", json={"amount": -1}); check("TC06 POST body sai (400)", r.status_code == 400)
    procs["finance_api"].terminate(); time.sleep(1)
    r = requests.get(P + "SV001"); check("TC07 Finance sập -> partial, vẫn có thông tin SV", r.status_code == 200 and r.json()["status"] == "partial" and r.json()["student"])
    procs["academic_api"].terminate(); time.sleep(1)
    r = requests.get(P + "SV001"); check("TC08 Cả hai sập (503)", r.status_code == 503)
finally:
    for p in procs.values(): p.terminate()
print(f"\n{sum(results)}/{len(results)} test đạt")
