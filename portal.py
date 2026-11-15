"""Portal (cổng 5000) - tích hợp dữ liệu từ Academic API + Finance API."""
import logging, os, re, time, requests
from flask import Flask, jsonify, render_template_string

ACADEMIC_URL = "http://127.0.0.1:5001"   
FINANCE_URL = "http://127.0.0.1:5002"
TIMEOUT = 2  # giây
ID_RE = re.compile(r"^SV\d{3}$")

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/portal.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
app = Flask(__name__)

def call(name, url):
    t = time.time()
    try:
        r = requests.get(url, timeout=TIMEOUT)
        logging.info("%s GET %s -> %s (%.0f ms)", name, url, r.status_code, (time.time() - t) * 1000)
        return r.status_code, r.json()
    except requests.RequestException as e:
        logging.error("%s GET %s FAILED: %s", name, url, type(e).__name__)
        return None, {"error": "SERVICE_UNAVAILABLE", "message": f"{name} không phản hồi"}

@app.get("/api/portal/<sid>")
def portal(sid):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV phải dạng SV001"), 400
    a_code, a = call("Academic", f"{ACADEMIC_URL}/api/students/{sid}")
    f_code, f = call("Finance", f"{FINANCE_URL}/api/fees/{sid}")
    if a_code is None and f_code is None:
        return jsonify(error="ALL_DOWN", message="Cả hai dịch vụ không phản hồi"), 503
    if a_code == 404:
        return jsonify(error="NOT_FOUND", message=f"Không có sinh viên {sid}"), 404
    warnings = []
    student = a if a_code == 200 else None
    fees = f if f_code == 200 else None
    if a_code != 200: warnings.append("Không lấy được thông tin sinh viên (Academic)")
    if f_code == 404: warnings.append("Sinh viên chưa có khoản học phí")
    elif f_code != 200: warnings.append("Không lấy được học phí (Finance)")
    return jsonify(status="partial" if warnings else "ok", student=student, finance=fees, warnings=warnings)

PAGE = """<!doctype html><meta charset=utf-8><title>Portal sinh viên</title>
<style>body{font-family:sans-serif;max-width:640px;margin:40px auto}input,button{padding:8px;font-size:16px}
.card{border:1px solid #ccc;border-radius:8px;padding:12px;margin:10px 0}.warn{color:#b45309}.err{color:#b91c1c}</style>
<h2>Cổng thông tin sinh viên</h2>
<input id=sid placeholder="Nhập mã SV, vd SV001"><button onclick=go()>Tra cứu</button><div id=out></div>
<script>
async function go(){const id=document.getElementById('sid').value.trim();
const r=await fetch('/api/portal/'+encodeURIComponent(id));const d=await r.json();const o=document.getElementById('out');
if(!r.ok){o.innerHTML='<p class=err>['+r.status+'] '+d.message+'</p>';return}
let h='';if(d.student)h+='<div class=card><b>'+d.student.full_name+'</b><br>Ngành: '+d.student.major+'<br>Email: '+d.student.email+'</div>';
if(d.finance)h+='<div class=card>Tổng phí: '+d.finance.total.toLocaleString()+' đ<br>Đã nộp: '+d.finance.paid.toLocaleString()+' đ<br><b>Còn nợ: '+d.finance.balance.toLocaleString()+' đ</b></div>';
(d.warnings||[]).forEach(w=>h+='<p class=warn>⚠ '+w+'</p>');o.innerHTML=h}
</script>"""

@app.get("/")
def index():
    return render_template_string(PAGE)

if __name__ == "__main__":
    app.run(port=5000)
