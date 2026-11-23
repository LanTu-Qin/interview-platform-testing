# -*- coding: utf-8 -*-
"""
面试总结平台 - 本地 Mock 服务（仅用 Python 标准库，无需 pip install）

用途：后端源码 / Java 环境缺失时，用它练习接口测试：
  登录取 Token、401 未登录、403 越权、分页、状态流转、端到端流程串联

启动：python mock_interview_api.py
地址：http://127.0.0.1:8080

说明：这是按《接口文档.md》模拟的假后端，数据存在内存里，重启即重置。
     它的行为特意做得"和文档不完全一致"，留出几个 bug 供你练习发现。
"""

import json
import base64
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = 8080

# ---------------- 内置账号 ----------------
USERS = {
    "admin":     {"password": "123456", "userId": 1,  "name": "管理员", "role": "TEACHER"},
    "teacher_b": {"password": "123456", "userId": 2,  "name": "王老师", "role": "TEACHER"},
    "student_a": {"password": "123456", "userId": 10, "name": "张三",   "role": "STUDENT"},
    "student_b": {"password": "123456", "userId": 11, "name": "李四",   "role": "STUDENT"},
}

COMPANIES = [
    {"id": 1, "name": "腾讯", "industry": "互联网", "description": "中国领先的互联网科技公司", "creatorName": "admin"},
    {"id": 2, "name": "阿里巴巴", "industry": "互联网/电商", "description": "中国最大的电商平台", "creatorName": "admin"},
    {"id": 3, "name": "字节跳动", "industry": "互联网", "description": "字节跳动科技有限公司", "creatorName": "admin"},
]

QUESTIONS = [
    {"id": 1, "title": "Java中HashMap的实现原理", "content": "请简述Java中HashMap的底层实现原理",
     "difficulty": "MEDIUM", "category": "Java基础", "tags": "集合,HashMap,数据结构",
     "referenceAnswer": "HashMap基于数组+链表+红黑树实现...", "creatorName": "admin"},
    {"id": 2, "title": "Spring Boot自动配置原理", "content": "请简述Spring Boot的自动配置原理",
     "difficulty": "MEDIUM", "category": "Java基础", "tags": "Spring,自动配置",
     "referenceAnswer": "Spring Boot通过@EnableAutoConfiguration...", "creatorName": "admin"},
    {"id": 3, "title": "MySQL索引失效的场景", "content": "列举MySQL索引失效的常见场景",
     "difficulty": "HARD", "category": "数据库", "tags": "MySQL,索引",
     "referenceAnswer": "隐式类型转换、使用函数、like前导%...", "creatorName": "admin"},
    {"id": 4, "title": "TCP三次握手过程", "content": "描述TCP三次握手的流程",
     "difficulty": "EASY", "category": "计算机网络", "tags": "TCP,网络",
     "referenceAnswer": "SYN -> SYN+ACK -> ACK", "creatorName": "admin"},
]

CATEGORIES = [
    {"id": 1, "dictTypeCode": "question_category", "label": "Java基础", "value": "JAVA_BASIC", "sortOrder": 0, "status": "1"},
    {"id": 2, "dictTypeCode": "question_category", "label": "数据库", "value": "DATABASE", "sortOrder": 1, "status": "1"},
    {"id": 3, "dictTypeCode": "question_category", "label": "计算机网络", "value": "NETWORK", "sortOrder": 2, "status": "1"},
]

# 内存"数据库"
DB = {
    "records": [
        {"id": 1, "studentId": 10, "studentName": "张三", "companyId": 1, "companyName": "腾讯",
         "position": "Java开发工程师", "result": "PASS", "status": "PENDING",
         "interviewRound": 1, "interviewType": "技术面", "isPublic": False,
         "creatorId": 10, "creatorName": "student_a", "interviewSessionId": "sess-001",
         "interviewerComment": "基础扎实", "teacherComment": None},
        {"id": 2, "studentId": 11, "studentName": "李四", "companyId": 2, "companyName": "阿里巴巴",
         "position": "后端开发", "result": "PENDING_RESULT", "status": "APPROVED",
         "interviewRound": 1, "interviewType": "技术面", "isPublic": True,
         "creatorId": 11, "creatorName": "student_b", "interviewSessionId": "sess-002",
         "interviewerComment": "表达清晰", "teacherComment": "不错"},
    ],
    "next_record_id": 3,
    "favorites": [],           # {"userId": .., "recordId": ..}
    "audit_logs": [],          # 操作日志
    "next_log_id": 1,
    "notifications": [
        {"id": 1, "userId": 10, "title": "面试记录已审核", "content": "您的面试记录已被老师审核通过",
         "type": "REVIEW", "isRead": False},
        {"id": 2, "userId": 10, "title": "系统通知", "content": "欢迎使用面试总结平台",
         "type": "SYSTEM", "isRead": False},
    ],
}


# ---------------- Token（模拟 JWT） ----------------
def make_token(user):
    payload = {"sub": user, "role": USERS[user]["role"], "userId": USERS[user]["userId"],
               "iat": int(time.time()), "exp": int(time.time()) + 3600}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=") + ".signature"


def parse_token(token):
    try:
        raw = token.split(".")[0]
        raw += "=" * (-len(raw) % 4)
        return json.loads(base64.urlsafe_b64decode(raw).decode())
    except Exception:
        return None


def add_log(username, user_id, action, target, target_id):
    DB["audit_logs"].append({"id": DB["next_log_id"], "userId": user_id, "username": username,
                             "action": action, "target": target, "targetId": target_id,
                             "detail": None, "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S")})
    DB["next_log_id"] += 1


def paginate(items, page, size):
    start = page * size
    return items[start:start + size]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    # ---------- 工具 ----------
    def _send(self, code, body, http_status=200):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(http_status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _ok(self, data=None, message="操作成功", **extra):
        body = {"code": 200, "message": message, "data": data}
        body.update(extra)
        self._send(200, body)

    def _fail(self, code, message, http_status=200):
        self._send(http_status, {"code": code, "message": message, "data": None})

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def _auth(self):
        """返回 (payload, error_response)"""
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None, (401, "未登录，请先登录")
        payload = parse_token(header[7:].strip())
        if not payload:
            return None, (401, "Token无效，请重新登录")
        if payload.get("exp", 0) < time.time():
            return None, (401, "Token已过期，请重新登录")
        return payload, None

    # ---------- 路由 ----------
    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        self._route("POST")

    def do_PUT(self):
        self._route("PUT")

    def do_DELETE(self):
        self._route("DELETE")

    def _route(self, method):
        u = urlparse(self.path)
        path, query = u.path.rstrip("/"), parse_qs(u.query)
        page = int(query.get("page", ["0"])[0])
        size = int(query.get("size", ["10"])[0])
        body = self._body() if method in ("POST", "PUT", "DELETE") else {}

        # ---- 公开：认证模块 ----
        if path == "/api/auth/login" and method == "POST":
            return self._login(body)
        if path == "/api/auth/register" and method == "POST":
            return self._register(body)

        # ---- 公开：公共接口 ----
        if path.startswith("/api/common"):
            return self._common(method, path, query)

        # ---- 需登录 ----
        payload, err = self._auth()
        if err:
            return self._fail(err[0], err[1])
        role, username, user_id = payload["role"], payload["sub"], payload["userId"]

        if path.startswith("/api/student"):
            if role != "STUDENT":
                return self._fail(403, "权限不足，仅学生可访问")
            return self._student(method, path, query, body, username, user_id, page, size)

        if path.startswith("/api/teacher"):
            if role not in ("TEACHER", "SUPER_ADMIN"):
                return self._fail(403, "权限不足，仅教师可访问")
            return self._teacher(method, path, query, body, username, user_id, page, size)

        if path.startswith("/api/user"):
            return self._user(method, path, body, username, user_id)

        if path.startswith("/api/notifications"):
            return self._notifications(method, path, user_id, page, size)

        return self._fail(404, "接口不存在: %s" % path)

    # ---------- 认证 ----------
    def _login(self, body):
        username = body.get("username")
        password = body.get("password")
        if not username or not password:
            return self._fail(400, "用户名和密码不能为空")
        user = USERS.get(username)
        if not user or user["password"] != password:
            # 注意：这里沿用文档里的 500，实际不合理，可作为一个可提的"改进建议"
            return self._fail(500, "用户名或密码错误")
        return self._ok({"token": make_token(username), "username": username,
                         "name": user["name"], "role": user["role"], "userId": user["userId"]},
                        message="登录成功")

    def _register(self, body):
        username = body.get("username")
        if not username or not body.get("password"):
            return self._fail(400, "用户名和密码不能为空")
        if username in USERS:
            return self._fail(500, "用户名已存在")
        USERS[username] = {"password": body["password"], "userId": len(USERS) + 100,
                           "name": body.get("name", username), "role": body.get("role", "STUDENT")}
        return self._ok({"token": make_token(username), "username": username,
                         "name": USERS[username]["name"], "role": USERS[username]["role"],
                         "userId": USERS[username]["userId"]}, message="注册成功")

    # ---------- 公共接口 ----------
    def _common(self, method, path, query):
        if path == "/api/common/companies":
            return self._ok(COMPANIES)
        if path == "/api/common/companies/search":
            kw = query.get("keyword", [""])[0]
            return self._ok([c for c in COMPANIES if kw in c["name"]])
        if path.startswith("/api/common/companies/"):
            cid = path.split("/")[-1]
            if not cid.isdigit():
                return self._fail(404, "资源不存在")
            for c in COMPANIES:
                if str(c["id"]) == cid:
                    return self._ok(c)
            return self._fail(404, "公司不存在")
        if path == "/api/common/questions":
            return self._ok(QUESTIONS)
        if path.startswith("/api/common/questions/"):
            qid = path.split("/")[-1]
            for q in QUESTIONS:
                if str(q["id"]) == qid:
                    return self._ok(q)
            return self._fail(404, "题目不存在")
        if path == "/api/common/records/public":
            return self._ok([r for r in DB["records"] if r["isPublic"] and r["status"] == "APPROVED"])
        return self._fail(404, "接口不存在")

    # ---------- 学生端 ----------
    def _student(self, method, path, query, body, username, user_id, page, size):
        if path == "/api/student/my-records" and method == "GET":
            return self._ok([r for r in DB["records"] if r["creatorName"] == username])
        if path == "/api/student/my-records" and method == "POST":
            rec = {"id": DB["next_record_id"], "studentId": user_id, "studentName": USERS[username]["name"],
                   "companyId": body.get("companyId"), "companyName": self._company_name(body.get("companyId")),
                   "position": body.get("position"), "result": body.get("result", "PENDING_RESULT"),
                   "status": "PENDING", "interviewRound": body.get("interviewRound", 1),
                   "interviewType": body.get("interviewType"), "isPublic": body.get("isPublic", False),
                   "creatorId": user_id, "creatorName": username,
                   "interviewSessionId": body.get("interviewSessionId") or str(uuid.uuid4()),
                   "interviewerComment": body.get("interviewerComment"), "teacherComment": None}
            DB["records"].append(rec)
            DB["next_record_id"] += 1
            return self._ok(rec, message="录入成功，该记录仅自己可见")
        if path == "/api/student/submit-review" and method == "POST":
            rec = {"id": DB["next_record_id"], "studentId": user_id, "studentName": USERS[username]["name"],
                   "companyId": body.get("companyId"), "companyName": self._company_name(body.get("companyId")),
                   "position": body.get("position"), "result": body.get("result", "PENDING_RESULT"),
                   "status": "PENDING", "interviewRound": body.get("interviewRound", 1),
                   "interviewType": body.get("interviewType"), "isPublic": body.get("isPublic", False),
                   "creatorId": user_id, "creatorName": username,
                   "interviewSessionId": body.get("interviewSessionId") or str(uuid.uuid4()),
                   "interviewerComment": body.get("interviewerComment"), "teacherComment": None}
            DB["records"].append(rec)
            DB["next_record_id"] += 1
            return self._ok(rec, message="已提交审核，等待老师审批")
        if path == "/api/student/questions" and method == "GET":
            return self._ok(paginate(QUESTIONS, page, size), total=len(QUESTIONS), page=page, size=size)
        if path == "/api/student/questions/search" and method == "GET":
            kw = query.get("keyword", [""])[0]
            return self._ok([q for q in QUESTIONS if kw in q["title"] or kw in q["content"]],
                            total=len(QUESTIONS), page=page, size=size)
        if path == "/api/student/categories":
            return self._ok(CATEGORIES)
        if path == "/api/student/practice":
            count = int(query.get("count", ["5"])[0])
            return self._ok(QUESTIONS[:max(0, count)])
        if path == "/api/student/favorites" and method == "GET":
            ids = [f["recordId"] for f in DB["favorites"] if f["userId"] == user_id]
            return self._ok([r for r in DB["records"] if r["id"] in ids])
        if path.startswith("/api/student/favorites/") and method == "POST":
            rid = path.split("/")[-1]
            if not rid.isdigit():
                return self._fail(404, "资源不存在")
            rid = int(rid)
            for f in DB["favorites"]:
                if f["userId"] == user_id and f["recordId"] == rid:
                    DB["favorites"].remove(f)
                    return self._ok(None, message="已取消收藏")
            DB["favorites"].append({"userId": user_id, "recordId": rid})
            return self._ok(None, message="收藏成功")
        return self._fail(404, "接口不存在: %s" % path)

    @staticmethod
    def _company_name(cid):
        for c in COMPANIES:
            if c["id"] == cid:
                return c["name"]
        return None

    # ---------- 教师端 ----------
    def _teacher(self, method, path, query, body, username, user_id, page, size):
        if path == "/api/teacher/users" and method == "GET":
            users = [{"id": v["userId"], "username": k, "name": v["name"], "role": v["role"]}
                     for k, v in USERS.items()]
            return self._ok(paginate(users, page, size), total=len(users), page=page, size=size)
        if path == "/api/teacher/records" and method == "GET":
            recs = DB["records"]
            status = query.get("status")
            if status:
                recs = [r for r in recs if r["status"] == status[0]]
            return self._ok(paginate(recs, page, size), total=len(recs), page=page, size=size)
        if path == "/api/teacher/records/pending" and method == "GET":
            pending = [r for r in DB["records"] if r["status"] == "PENDING"]
            return self._ok(paginate(pending, page, size), total=len(pending), page=page, size=size)
        if path.startswith("/api/teacher/records/") and method == "PUT":
            parts = path.split("/")
            rid = parts[-2] if parts[-1] in ("approve", "reject") else parts[-1]
            if not rid.isdigit():
                return self._fail(404, "资源不存在")
            rec = next((r for r in DB["records"] if str(r["id"]) == rid), None)
            if not rec:
                return self._fail(404, "记录不存在")
            action = parts[-1]
            if action == "approve":
                rec["status"] = "APPROVED"
                add_log(username, user_id, "审核通过", "面试记录", rec["id"])
                return self._ok(rec, message="审核通过")
            if action == "reject":
                rec["status"] = "REJECTED"
                add_log(username, user_id, "审核驳回", "面试记录", rec["id"])
                return self._ok(rec, message="审核驳回")
            if action == "evaluate":
                rec["teacherComment"] = body.get("teacherComment")
                if body.get("result"):
                    rec["result"] = body["result"]
                add_log(username, user_id, "老师评价", "面试记录", rec["id"])
                return self._ok(rec, message="评价成功")
        if path == "/api/teacher/statistics":
            recs = DB["records"]
            return self._ok({"totalRecords": len(recs), "totalUsers": len(USERS),
                             "totalQuestions": len(QUESTIONS), "totalCompanies": len(COMPANIES),
                             "passCount": len([r for r in recs if r["result"] == "PASS"]),
                             "pendingReviewCount": len([r for r in recs if r["status"] == "PENDING"]),
                             "approvedCount": len([r for r in recs if r["status"] == "APPROVED"])})
        if path == "/api/teacher/audit-logs":
            logs = DB["audit_logs"]
            return self._ok(paginate(logs, page, size), total=len(logs), page=page, size=size)
        if path == "/api/teacher/companies":
            return self._ok(paginate(COMPANIES, page, size), total=len(COMPANIES), page=page, size=size)
        if path == "/api/teacher/questions":
            return self._ok(paginate(QUESTIONS, page, size), total=len(QUESTIONS), page=page, size=size)
        return self._fail(404, "接口不存在: %s" % path)

    # ---------- 个人信息 ----------
    def _user(self, method, path, body, username, user_id):
        if path == "/api/user/profile" and method == "POST":
            u = USERS[username]
            for k in ("name", "email", "phone"):
                if k in body:
                    u[k] = body[k]
            return self._ok({"id": u["userId"], "username": username, "name": u["name"],
                             "email": u.get("email"), "phone": u.get("phone"), "role": u["role"]},
                            message="个人信息更新成功")
        if path == "/api/user/change-password" and method == "POST":
            u = USERS[username]
            if body.get("oldPassword") != u["password"]:
                return self._fail(500, "旧密码不正确")
            u["password"] = body.get("newPassword")
            return self._ok(None, message="密码修改成功")
        return self._fail(404, "接口不存在")

    # ---------- 通知 ----------
    def _notifications(self, method, path, user_id, page, size):
        notes = [n for n in DB["notifications"] if n["userId"] == user_id]
        if path == "/api/notifications" and method == "GET":
            return self._ok(paginate(notes, page, size), total=len(notes), page=page, size=size)
        if path == "/api/notifications/unread-count":
            return self._ok(len([n for n in notes if not n["isRead"]]))
        if path == "/api/notifications/read-all" and method == "PUT":
            for n in notes:
                n["isRead"] = True
            return self._ok(None, message="全部已读")
        if path.startswith("/api/notifications/") and path.endswith("/read") and method == "PUT":
            nid = path.split("/")[-2]
            for n in notes:
                if str(n["id"]) == nid:
                    n["isRead"] = True
                    return self._ok(None, message="已读")
            return self._fail(404, "通知不存在")
        return self._fail(404, "接口不存在")


if __name__ == "__main__":
    print("Mock 服务已启动: http://127.0.0.1:%d" % PORT)
    print("测试账号: admin/123456(TEACHER)  student_a/123456(STUDENT)  student_b/123456(STUDENT)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
