# 8 步全链测试场景设计文档

> 工具：Apifox 自动化测试场景（此文档为场景的手工整理版；执行证据见 `../baseline-report/baseline-report-20261123.html`，8 步 53 断言全绿）
> 设计原则：跨接口数据流用**变量提取**打通，不硬编码；每个交接点验证"下游接住的是不是我交出去的那条"。

## 场景流程

```
①教师登录 ─┐
②学生登录 ─┤（双角色 token，各自管各自的数据可见性）
           │
③学生创建面试记录 ──提取──> student_a_record_id（录入语义）
④学生提交审核     ──提取──> submitted_record_id（送审语义）
⑤教师查待审列表  <──断言── 列表中存在 submitted_record_id（下游可见性）
⑥教师审核通过（路径参数引用 submitted_record_id）
⑦教师查审计日志  <──断言── 存在 targetId=submitted_record_id 的审核事件
⑧学生复查我的记录 <──断言── 该记录 status 已变 APPROVED（端到端状态流转）
```

## 步骤明细

| # | 用例编号 | 请求 | 关键断言 | 变量 |
| --- | --- | --- | --- | --- |
| 1 | TC-AUTH-001 | `POST /api/auth/login`（admin/TEACHER） | 协议层 200 + Content-Type；业务层 code/message/token 非空/name/role | → `teacher_token` |
| 2 | TC-AUTH-002 | `POST /api/auth/login`（student_a/STUDENT） | 同上 | → `student_token` |
| 3 | TC-STU-014 | `POST /api/student/my-records` | 创建成功、响应契约；**提取返回 id** | → `student_a_record_id` |
| 4 | TC-STU-019 | `POST /api/student/submit-review` | 提交成功；**提取返回 id** | → `submitted_record_id` |
| 5 | TC-TCH-080 | `GET /api/teacher/records/pending` | 列表非空（`isinstance list && len>0`，禁用固定下标）；filter 存在性断言定位 `submitted_record_id` | 引用 ④ |
| 6 | TC-TCH-083 | `PUT /api/teacher/records/{submitted_record_id}/approve` | 审核通过、status=APPROVED | 引用 ④ |
| 7 | TC-TCH-104 | `GET /api/teacher/audit-logs` | 日志中存在 targetId=`submitted_record_id` 的「审核通过」事件（下游验证哲学："提交成功"由教师端看见算） | 引用 ④ |
| 8 | TC-STU-015 | `GET /api/student/my-records` | 该记录 status=APPROVED（状态流转端到端确认） | 引用 ④ |

## 断言分层（53 条断言的组织方式）

1. **协议层**（目录级公共断言，全部接口共享）：HTTP 状态码、Content-Type 值校验、响应耗时基线（`<2s`，失败消息附实测值）
2. **结构层**：响应体契约校验（字段存在、类型正确；防"data 从数组变对象"类结构变化，用 `isinstance` + `len()` 而非 `!= ''`）
3. **业务层**：业务码、关键字段取值、状态流转、跨接口数据一致性

## 可重复执行设计

- 全部接口引用走变量提取，**零硬编码 id**：2026-11-23 重启 mock 清场后 id 序列从初始值重新开始，场景照跑全绿（见基线报告）
- 正式跑场景前重启 mock 清场，避免试验数据污染报告

## 已知设计取舍（非缺陷）

创建接口（my-records）只做"仅自己可见的录入"；按接口文档 §3.1.5，submit-review 是"提交审核申请（新建待审记录）"，请求体同创建接口、无 id 参数——接口清单中不存在"按 id 送审"的能力。因此 ③ 创建的记录与 ④ 提交审核生成的记录是两条数据，场景通过**两条变量各管一段业务语义**（`student_a_record_id` 管录入、`submitted_record_id` 管送审→审核）保持链路完整。该脱节定性为设计取舍（文档=实现一致，非缺陷），详见 `defect-management-report.md` 第五节。

