"""Academic API (cổng 5001) - nguồn dữ liệu sinh viên."""
import re
from flask import Flask, jsonify

app = Flask(__name__)
STUDENTS = {f"SV{i:03d}": {"student_id": f"SV{i:03d}", "full_name": n, "major": m,
            "email": f"sv{i:03d}@student.edu.vn", "gpa": g}
            for i, (n, m, g) in enumerate([
    ("Nguyễn Văn An", "Công nghệ thông tin", 3.2), ("Trần Thị Bình", "Hệ thống thông tin", 3.5),
    ("Lê Hoàng Cường", "Công nghệ thông tin", 2.9), ("Phạm Thu Dung", "Kinh tế số", 3.7),
    ("Võ Minh Đức", "An toàn thông tin", 3.0), ("Đặng Ngọc Hà", "Hệ thống thông tin", 3.4),
    ("Bùi Quốc Huy", "Công nghệ thông tin", 2.8), ("Ngô Thanh Lan", "Kinh tế số", 3.9),
    ("Phan Gia Minh", "An toàn thông tin", 3.1), ("Hoàng Yến Nhi", "Công nghệ thông tin", 3.6)], 1)}
ID_RE = re.compile(r"^SV\d{3}$")

@app.get("/health")
def health():
    return jsonify(service="academic", status="UP")

@app.get("/api/students")
def list_students():
    return jsonify(count=len(STUDENTS), data=list(STUDENTS.values()))

@app.get("/api/students/<sid>")
def get_student(sid):
    if not ID_RE.match(sid):
        return jsonify(error="INVALID_ID", message="Mã SV phải dạng SV + 3 chữ số, vd SV001"), 400
    s = STUDENTS.get(sid)
    if not s:
        return jsonify(error="NOT_FOUND", message=f"Không có sinh viên {sid}"), 404
    return jsonify(s), 200

if __name__ == "__main__":
    app.run(port=5001)
