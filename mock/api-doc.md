# 面试总结平台 - API 接口文档（测试专用）

> **版本**: v2.0
> **基础URL**: `http://{host}:{port}`
> **文档日期**: 2026-08-08
> **适用角色**: 测试人员

---

## 目录

- [1. 通用说明](#1-通用说明)
- [2. 认证模块 -](#2-认证模块---apiauth) [`/api/auth`](#2-认证模块---apiauth)
- [3. 学生端 -](#3-学生端---apistudent) [`/api/student`](#3-学生端---apistudent)
- [4. 教师端 -](#4-教师端---apiteacher) [`/api/teacher`](#4-教师端---apiteacher)
- [5. 个人信息 -](#5-个人信息---apiuser) [`/api/user`](#5-个人信息---apiuser)
- [6. 通知 -](#6-通知---apinotifications) [`/api/notifications`](#6-通知---apinotifications)
- [7. 字典管理 -](#7-字典管理---apiteacherdict) [`/api/teacher/dict`](#7-字典管理---apiteacherdict)
- [8. 公共接口 -](#8-公共接口---apicommon) [`/api/common`](#8-公共接口---apicommon)
- [9. 附录：枚举值说明](#9-附录枚举值说明)
- [10. 附录：数据模型完整字段](#10-附录数据模型完整字段)

---

## 1. 通用说明

### 1.1 响应格式

所有接口返回 JSON，有两种包装格式：

**格式一：Map 包装（大部分接口）**

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... },
  "total": 100,
  "page": 0,
  "size": 10
}
```

**格式二：ApiResponse 包装（Auth 模块）**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": { ... }
}
```

### 1.2 状态码说明

| code | 含义           |
| ---- | -------------- |
| 200  | 请求成功       |
| 403  | 权限不足       |
| 404  | 资源不存在     |
| 500  | 服务器内部错误 |

### 1.3 认证方式（JWT Token）—— 非常重要

本系统使用 **JWT（JSON Web Token）** 进行身份认证。除登录/注册/公共接口外，**所有接口都必须携带 Token**，否则返回 401 未授权。

#### 1.3.1 获取 Token

首先调用登录接口获取 Token（详见 [2.1 登录](#21-登录)），响应中的 `data.token` 字段即为 JWT Token：

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJURUFDSEVSIiwiaWF0IjoxNzU1Mjg2MDAwLCJleHAiOjE3NTUzNzI0MDB9.xxx",
    "username": "admin",
    "name": "管理员",
    "role": "TEACHER",
    "userId": 1
  }
}
```

#### 1.3.2 携带 Token 的方式

在 HTTP 请求头中添加 `Authorization` 字段，格式为 `Bearer ` + 空格 + Token：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJURUFDSEVSIiwiaWF0IjoxNzU1Mjg2MDAwLCJleHAiOjE3NTUzNzI0MDB9.xxx
```

> **注意**：`Bearer` 后面有一个空格，Token 不需要用引号包裹。

#### 1.3.3 curl 示例

**步骤1：获取Token**

```bash
# 登录获取Token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

**步骤2：使用Token调用需要认证的接口**

```bash
# 将 {token} 替换为步骤1获取到的实际Token
curl -X GET http://localhost:8080/api/student/questions?page=0&size=10 \
  -H "Authorization: Bearer {token}"
```

#### 1.3.4 Postman 配置

1. 先调用 `POST /api/auth/login` 登录
2. 从响应中复制 `data.token` 的值
3. 在后续请求的 **Headers** 标签页中添加：
   - **Key**: `Authorization`
   - **Value**: `Bearer eyJhbGciOiJIUzI1NiJ9...`（粘贴你的Token）
4. 也可以在 Postman 的 **Collection** 级别设置 **Authorization** 为 `Bearer Token` 类型，自动在所有请求中携带

![Postman设置] 在 Authorization 标签页选择 Type = "Bearer Token"，右侧输入框中粘贴 Token 值即可

#### 1.3.5 Token 过期

- Token 有过期时间，过期后请求会返回 401
- 过期后需要重新调用登录接口获取新 Token
- 过期响应示例：

```json
{
  "code": 401,
  "message": "Token已过期，请重新登录"
}
```

#### 1.3.6 不同角色的 Token 权限

| 接口模块                 | 所需角色              | 使用哪种Token       |
| ------------------------ | --------------------- | ------------------- |
| `/api/auth/*`          | 无限制                | 不需要Token         |
| `/api/student/*`       | STUDENT               | 学生账号的Token     |
| `/api/teacher/*`       | TEACHER / SUPER_ADMIN | 教师账号的Token     |
| `/api/user/*`          | 任意登录用户          | 学生或教师Token均可 |
| `/api/notifications/*` | 任意登录用户          | 学生或教师Token均可 |
| `/api/common/*`        | 无限制                | 不需要Token         |

> **测试提示**：学生用学生Token调用教师接口（如 `/api/teacher/users`）会返回 403 权限不足，这是正常的。

#### 1.3.7 未携带Token时的响应

```json
{
  "code": 401,
  "message": "未登录，请先登录"
}
```

### 1.4 分页参数

支持分页的接口使用以下查询参数：

| 参数 | 类型 | 默认值 | 说明            |
| ---- | ---- | ------ | --------------- |
| page | int  | 0      | 页码，从 0 开始 |
| size | int  | 10     | 每页条数        |

分页响应中额外包含：

- `total`: 总记录数（Long 类型）
- `page`: 当前页码
- `size`: 每页条数

---

### 1.5 快速开始（Quick Start）

以下是一个完整的测试流程示例，使用 curl 命令：

```bash
# ========== 步骤1：登录获取Token ==========
# 假设服务运行在 http://localhost:8080
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

echo "获取到的Token: $TOKEN"

# ========== 步骤2：验证Token是否有效（携带Token调用需要认证的接口）==========
curl -X GET "http://localhost:8080/api/student/questions?page=0&size=5" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# ========== 步骤3：不带Token测试（预期返回401）==========
curl -X GET "http://localhost:8080/api/student/questions?page=0&size=5" \
  -H "Content-Type: application/json"

# ========== 步骤4：权限越权测试（学生Token调用教师接口，预期返回403）==========
STUDENT_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student_a","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

curl -X GET "http://localhost:8080/api/teacher/users?page=0&size=5" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json"
```

**Windows PowerShell 等效命令**：

```powershell
# 步骤1：登录获取Token
$response = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"123456"}'
$TOKEN = $response.data.token
Write-Host "获取到的Token: $TOKEN"

# 步骤2：携带Token调用接口
Invoke-RestMethod -Uri "http://localhost:8080/api/student/questions?page=0&size=5" -Method GET -Headers @{Authorization="Bearer $TOKEN"}

# 步骤3：不带Token测试（预期401）
Invoke-RestMethod -Uri "http://localhost:8080/api/student/questions?page=0&size=5" -Method GET

# 步骤4：权限越权测试（预期403）
$studentResp = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"student_a","password":"123456"}'
$STUDENT_TOKEN = $studentResp.data.token
Invoke-RestMethod -Uri "http://localhost:8080/api/teacher/users?page=0&size=5" -Method GET -Headers @{Authorization="Bearer $STUDENT_TOKEN"}
```

### 1.6 接口权限速查表

| 接口模块                 | 需要Token    | 需要角色 | 不需要Token的例外 |
| ------------------------ | ------------ | -------- | ----------------- |
| `/api/auth/login`      | **否** | 无       | -                 |
| `/api/auth/register`   | **否** | 无       | -                 |
| `/api/student/*`       | **是** | STUDENT  | -                 |
| `/api/teacher/*`       | **是** | TEACHER  | -                 |
| `/api/user/*`          | **是** | 任意角色 | -                 |
| `/api/notifications/*` | **是** | 任意角色 | -                 |
| `/api/common/*`        | **否** | 无       | 全部公开          |

---

## 2. 认证模块 - `/api/auth`

> **权限说明**: 此模块所有接口**不需要**携带 Token，直接调用即可。

### 2.1 登录

> **POST** `/api/auth/login`

**请求头**

```
Content-Type: application/json
```

**请求体**

```JSON
{
  "username": "admin",
  "password": "123456"
}
```

**请求参数说明**

| 字段     | 类型   | 必填 | 说明   |
| -------- | ------ | ---- | ------ |
| username | String | 是   | 用户名 |
| password | String | 是   | 密码   |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "username": "admin",
    "name": "管理员",
    "role": "TEACHER",
    "userId": 1
  }
}
```

**响应字段说明**

| 字段     | 类型   | 说明                                   |
| -------- | ------ | -------------------------------------- |
| token    | String | JWT Token，后续请求需携带              |
| username | String | 用户名                                 |
| name     | String | 显示姓名                               |
| role     | String | 角色：TEACHER / STUDENT / SUPER\_ADMIN |
| userId   | Long   | 用户ID                                 |

**curl 示例**

```bash
# 教师登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 学生登录
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student_a","password":"123456"}'
```

**Windows PowerShell**

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"123456"}'
```

**错误响应**

```json
{
  "code": 500,
  "message": "用户名或密码错误",
  "data": null
}
```

---

### 2.2 注册

> **POST** `/api/auth/register`

**请求体**

```json
{
  "username": "student001",
  "password": "123456",
  "name": "张三",
  "role": "STUDENT",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "classId": 1
}
```

**请求参数说明**

| 字段     | 类型   | 必填 | 说明                     |
| -------- | ------ | ---- | ------------------------ |
| username | String | 是   | 用户名，需唯一           |
| password | String | 是   | 密码                     |
| name     | String | 是   | 姓名                     |
| role     | String | 是   | 角色：TEACHER 或 STUDENT |
| email    | String | 否   | 邮箱                     |
| phone    | String | 否   | 电话                     |
| classId  | Long   | 否   | 班级ID（学生角色时使用） |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "username": "student001",
    "name": "张三",
    "role": "STUDENT",
    "userId": 10
  }
}
```

---

## 3. 学生端 - `/api/student`

> **权限要求**: 需要 STUDENT 角色，携带 Token
> **请求头**: `Authorization: Bearer {token}`（必须）
> **Token获取**: 先调用 `POST /api/auth/login`，用学生账号登录获取Token

**curl 示例（先登录获取Token，再调用接口）**：

```bash
# 步骤1：学生登录获取Token
STUDENT_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student_a","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 步骤2：携带Token调用学生端接口
curl -X GET "http://localhost:8080/api/student/questions?page=0&size=10" \
  -H "Authorization: Bearer $STUDENT_TOKEN"
```

**Windows PowerShell**：

```powershell
$resp = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"student_a","password":"123456"}'
$TOKEN = $resp.data.token
Invoke-RestMethod -Uri "http://localhost:8080/api/student/questions?page=0&size=10" -Method GET -Headers @{Authorization="Bearer $TOKEN"}
```

### 3.1 面试记录

#### 3.1.1 获取我的面试记录（平铺列表）

> **GET** `/api/student/my-records`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "student": { "id": 10, "username": "...", "name": "张三", ... },
      "company": { "id": 1, "name": "腾讯", "industry": "互联网", ... },
      "recordQuestions": [
        {
          "id": 1,
          "question": { "id": 1, "title": "Java中HashMap的实现原理", ... },
          "sortOrder": 0
        }
      ],
      "interviewDate": "2026-08-01T10:00:00",
      "position": "Java开发工程师",
      "result": "PASS",
      "interviewerComment": "面试官评语",
      "teacherComment": "老师评语",
      "examPoints": "考试重点",
      "isPublic": false,
      "status": "APPROVED",
      "salaryRange": "15K-25K",
      "interviewRound": 1,
      "interviewType": "技术面",
      "hrContact": "HR小王",
      "workLocation": "深圳",
      "parentRecordId": null,
      "interviewSessionId": "uuid-xxx-xxx",
      "creatorId": 10,
      "creatorName": "student001",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ]
}
```

---

#### 3.1.2 获取我的面试记录（按会话分组）

> **GET** `/api/student/my-records/grouped`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "sessionId": "uuid-xxx-xxx",
      "companyId": 1,
      "companyName": "腾讯",
      "companyIndustry": "互联网",
      "position": "Java开发工程师",
      "rounds": [
        {
          "id": 1,
          "interviewRound": 1,
          "interviewType": "技术面",
          "result": "PASS",
          "interviewDate": "2026-08-01T10:00:00",
          ...
        },
        {
          "id": 2,
          "interviewRound": 2,
          "interviewType": "HR面",
          "result": "PENDING_RESULT",
          ...
        }
      ]
    }
  ]
}
```

**说明**: 同一家公司同一职位的多轮面试通过 `interviewSessionId` 关联，按 round 排序。无 `interviewSessionId` 的旧数据会以 `legacy-{id}` 作为 sessionId 单独展示。

---

#### 3.1.3 获取面试会话详情

> **GET** `/api/student/my-records/session/{sessionId}`

**路径参数**

| 参数      | 类型   | 说明       |
| --------- | ------ | ---------- |
| sessionId | String | 面试会话ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": {
    "sessionId": "uuid-xxx-xxx",
    "companyId": 1,
    "companyName": "腾讯",
    "companyIndustry": "互联网",
    "position": "Java开发工程师",
    "rounds": [ ... ]
  }
}
```

**错误响应**

```json
{
  "code": 404,
  "message": "会话不存在"
}
```

---

#### 3.1.4 创建面试记录

> **POST** `/api/student/my-records`

**请求体**

```json
{
  "companyId": 1,
  "questionIds": [1, 2, 3],
  "interviewDate": "2026-08-01 10:00:00",
  "position": "Java开发工程师",
  "result": "PASS",
  "interviewerComment": "面试官觉得基础扎实",
  "examPoints": "多线程、集合框架",
  "isPublic": false,
  "status": "APPROVED",
  "salaryRange": "15K-25K",
  "interviewRound": 1,
  "interviewType": "技术面",
  "hrContact": "HR小王",
  "workLocation": "深圳",
  "parentRecordId": null,
  "interviewSessionId": null
}
```

**请求参数说明**

| 字段               | 类型        | 必填 | 说明                                       |
| ------------------ | ----------- | ---- | ------------------------------------------ |
| companyId          | Long        | 建议 | 公司ID                                     |
| questionIds        | List\<Long> | 否   | 关联的题目ID列表                           |
| interviewDate      | String      | 否   | 面试日期时间，格式 `yyyy-MM-dd HH:mm:ss` |
| position           | String      | 否   | 面试职位                                   |
| result             | String      | 否   | 面试结果，见枚举值                         |
| interviewerComment | String      | 否   | 面试官评语                                 |
| examPoints         | String      | 否   | 考试重点                                   |
| isPublic           | Boolean     | 否   | 是否公开，默认 false                       |
| status             | String      | 否   | 记录状态，见枚举值                         |
| salaryRange        | String      | 否   | 薪资范围                                   |
| interviewRound     | Integer     | 否   | 面试轮次，如 1, 2, 3                       |
| interviewType      | String      | 否   | 面试类型，如"技术面"、"HR面"               |
| hrContact          | String      | 否   | HR联系人                                   |
| workLocation       | String      | 否   | 工作地点                                   |
| parentRecordId     | Long        | 否   | 父记录ID（指向首轮记录）                   |
| interviewSessionId | String      | 否   | 面试会话ID（UUID），同一次面试多轮共享     |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "录入成功，该记录仅自己可见",
  "data": { ... }
}
```

---

#### 3.1.5 提交审核

> **POST** `/api/student/submit-review`

**请求体**: 同 3.1.4 创建面试记录

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "已提交审核，等待老师审批",
  "data": { ... }
}
```

---

#### 3.1.6 追加下一轮面试

> **POST** `/api/student/my-records/{id}/append`

**路径参数**

| 参数 | 类型 | 说明           |
| ---- | ---- | -------------- |
| id   | Long | 已有面试记录ID |

**请求体**: 同 3.1.4

**说明**: 基于已有记录自动创建下一轮面试，自动继承 companyId、sessionId 等信息，interviewRound 自动 +1。

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "已追加第2轮面试",
  "data": { ... }
}
```

---

#### 3.1.7 更新面试结果

> **PUT** `/api/student/my-records/{id}/result`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**请求体**

```json
{
  "result": "PASS"
}
```

**请求参数说明**

| 字段   | 类型   | 必填 | 说明           |
| ------ | ------ | ---- | -------------- |
| result | String | 是   | 面试结果枚举值 |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "结果已更新",
  "data": { ... }
}
```

---

### 3.2 收藏功能

#### 3.2.1 切换收藏状态

> **POST** `/api/student/favorites/{recordId}`

**路径参数**

| 参数     | 类型 | 说明       |
| -------- | ---- | ---------- |
| recordId | Long | 面试记录ID |

**说明**: 如果已收藏则取消收藏，未收藏则添加收藏。同一用户对同一记录只能收藏一次。

**成功响应 (200)**

```json
// 收藏成功
{ "code": 200, "message": "收藏成功" }
// 取消收藏
{ "code": 200, "message": "已取消收藏" }
```

---

#### 3.2.2 获取我的收藏列表

> **GET** `/api/student/favorites`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

返回收藏的面试记录完整对象列表。

---

#### 3.2.3 检查是否已收藏

> **GET** `/api/student/favorites/check/{recordId}`

**路径参数**

| 参数     | 类型 | 说明       |
| -------- | ---- | ---------- |
| recordId | Long | 面试记录ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": true
}
```

`data` 为 `true` 表示已收藏，`false` 表示未收藏。

---

### 3.3 随机刷题

> **GET** `/api/student/practice`

**查询参数**

| 参数  | 类型 | 默认值 | 说明               |
| ----- | ---- | ------ | ------------------ |
| count | int  | 5      | 随机抽取的题目数量 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "title": "Java中HashMap的实现原理",
      "content": "请简述Java中HashMap的底层实现原理",
      "difficulty": "MEDIUM",
      "category": "Java基础",
      "tags": "集合,HashMap,数据结构",
      "referenceAnswer": "HashMap基于数组+链表+红黑树实现...",
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ]
}
```

---

### 3.4 题库管理

#### 3.4.1 获取分类列表

> **GET** `/api/student/categories`

**请求参数**: 无

**说明**: 返回题库分类下拉选项，仅返回启用状态的数据。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "dictTypeCode": "question_category",
      "label": "Java基础",
      "value": "JAVA_BASIC",
      "sortOrder": 0,
      "status": "1",
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ]
}
```

---

#### 3.4.2 获取题目列表（分页）

> **GET** `/api/student/questions`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 100,
  "page": 0,
  "size": 10
}
```

---

#### 3.4.3 搜索题目

> **GET** `/api/student/questions/search`

**查询参数**

| 参数       | 类型   | 必填 | 说明                           |
| ---------- | ------ | ---- | ------------------------------ |
| keyword    | String | 否   | 搜索关键词（匹配标题和内容）   |
| difficulty | String | 否   | 难度筛选：EASY / MEDIUM / HARD |
| category   | String | 否   | 分类筛选                       |
| page       | int    | 否   | 页码，默认 0                   |
| size       | int    | 否   | 每页条数，默认 10              |

**注意**: keyword、difficulty、category 三者只能同时使用一个（优先级：keyword > difficulty > category）。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 50,
  "page": 0,
  "size": 10
}
```

---

#### 3.4.4 新增题目

> **POST** `/api/student/questions`

**请求体**

```json
{
  "title": "Spring Boot自动配置原理",
  "content": "请简述Spring Boot的自动配置原理",
  "difficulty": "MEDIUM",
  "category": "Java基础",
  "tags": "Spring,自动配置",
  "referenceAnswer": "Spring Boot通过@EnableAutoConfiguration..."
}
```

**请求参数说明**

| 字段            | 类型   | 必填 | 说明                       |
| --------------- | ------ | ---- | -------------------------- |
| title           | String | 是   | 题目标题                   |
| content         | String | 否   | 题目内容/描述              |
| difficulty      | String | 否   | 难度：EASY / MEDIUM / HARD |
| category        | String | 否   | 分类名称                   |
| tags            | String | 否   | 标签，逗号分隔             |
| referenceAnswer | String | 否   | 参考答案                   |

**说明**: 创建者自动设置为当前登录用户。学生只能编辑自己创建的题目。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": {
    "id": 101,
    "title": "Spring Boot自动配置原理",
    "creatorName": "student001",
    ...
  }
}
```

---

#### 3.4.5 编辑题目

> **PUT** `/api/student/questions/{id}`

**权限说明**: 只能编辑自己创建的题目（`creatorName` 必须等于当前用户名），否则返回 403。

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 题目ID |

**请求体**: 同 3.4.4 新增题目

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

**权限不足响应**

```json
{
  "code": 403,
  "message": "只能编辑自己创建的题目"
}
```

---

## 4. 教师端 - `/api/teacher`

> **权限要求**: 需要 TEACHER 或 SUPER\_ADMIN 角色，携带 Token
> **请求头**: `Authorization: Bearer {token}`（必须）
> **Token获取**: 先调用 `POST /api/auth/login`，用教师账号登录获取Token

**curl 示例（先登录获取Token，再调用接口）**：

```bash
# 步骤1：教师登录获取Token
TEACHER_TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 步骤2：携带Token调用教师端接口
curl -X GET "http://localhost:8080/api/teacher/users?page=0&size=10" \
  -H "Authorization: Bearer $TEACHER_TOKEN"
```

**Windows PowerShell**：

```powershell
$resp = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"123456"}'
$TOKEN = $resp.data.token
Invoke-RestMethod -Uri "http://localhost:8080/api/teacher/users?page=0&size=10" -Method GET -Headers @{Authorization="Bearer $TOKEN"}
```

### 4.1 用户管理

#### 4.1.1 获取用户列表（分页+筛选）

> **GET** `/api/teacher/users`

**查询参数**

| 参数    | 类型   | 默认值 | 说明                          |
| ------- | ------ | ------ | ----------------------------- |
| page    | int    | 0      | 页码                          |
| size    | int    | 10     | 每页条数                      |
| classId | Long   | 否     | 按班级ID筛选                  |
| name    | String | 否     | 按姓名模糊搜索                |
| role    | String | 否     | 按角色筛选：TEACHER / STUDENT |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 10,
      "username": "student001",
      "name": "张三",
      "role": "STUDENT",
      "email": "zhangsan@example.com",
      "phone": "13800138000",
      "schoolClass": { "id": 1, "name": "Java一班", ... },
      "frozen": false,
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00"
    }
  ],
  "total": 50,
  "page": 0,
  "size": 10
}
```

**注意**: 响应中不包含 `password` 字段（通过 `@JsonIgnore` 排除）。

---

#### 4.1.2 创建用户

> **POST** `/api/teacher/users`

**请求体**

```json
{
  "username": "student002",
  "password": "123456",
  "name": "李四",
  "role": "STUDENT",
  "email": "lisi@example.com",
  "phone": "13800138001",
  "classId": 1
}
```

**请求参数说明**

| 字段     | 类型   | 必填 | 说明                    |
| -------- | ------ | ---- | ----------------------- |
| username | String | 是   | 用户名，需唯一          |
| password | String | 是   | 密码                    |
| name     | String | 是   | 姓名                    |
| role     | String | 是   | 角色：TEACHER / STUDENT |
| email    | String | 否   | 邮箱                    |
| phone    | String | 否   | 电话                    |
| classId  | Long   | 否   | 班级ID                  |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": { ... }
}
```

---

#### 4.1.3 编辑用户

> **PUT** `/api/teacher/users/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 用户ID |

**请求体**: 同 4.1.2 创建用户

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "用户更新成功",
  "data": { ... }
}
```

---

#### 4.1.4 删除用户

> **DELETE** `/api/teacher/users/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 用户ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "用户删除成功"
}
```

---

#### 4.1.5 冻结用户

> **PUT** `/api/teacher/users/{id}/freeze`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 用户ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "用户已冻结"
}
```

---

#### 4.1.6 解冻用户

> **PUT** `/api/teacher/users/{id}/unfreeze`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 用户ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "用户已解冻"
}
```

---

#### 4.1.7 批量删除用户

> **DELETE** `/api/teacher/users/batch`

**请求体**

```json
[1, 2, 3]
```

请求体是一个 Long 类型的 ID 数组。

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "成功删除 3 个用户"
}
```

---

#### 4.1.8 获取所有学生（下拉列表）

> **GET** `/api/teacher/users/students`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    { "id": 10, "username": "student001", "name": "张三", "role": "STUDENT", ... }
  ]
}
```

---

### 4.2 班级管理

#### 4.2.1 获取班级列表（分页）

> **GET** `/api/teacher/classes`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "Java一班",
      "description": "2026级Java开发方向",
      "students": [ ... ],
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ],
  "total": 5,
  "page": 0,
  "size": 10
}
```

---

#### 4.2.2 创建班级

> **POST** `/api/teacher/classes`

**请求体**

```json
{
  "name": "Java二班",
  "description": "2026级Java开发方向二班"
}
```

**请求参数说明**

| 字段        | 类型   | 必填 | 说明     |
| ----------- | ------ | ---- | -------- |
| name        | String | 是   | 班级名称 |
| description | String | 否   | 班级描述 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.2.3 编辑班级

> **PUT** `/api/teacher/classes/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 班级ID |

**请求体**: 同 4.2.2

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.2.4 删除班级

> **DELETE** `/api/teacher/classes/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 班级ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

#### 4.2.5 获取所有班级（下拉列表）

> **GET** `/api/teacher/classes/all`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

### 4.3 公司管理

#### 4.3.1 获取公司列表（分页）

> **GET** `/api/teacher/companies`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "腾讯",
      "industry": "互联网",
      "description": "中国领先的互联网科技公司",
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00"
    }
  ],
  "total": 20,
  "page": 0,
  "size": 10
}
```

---

#### 4.3.2 创建公司

> **POST** `/api/teacher/companies`

**请求体**

```json
{
  "name": "阿里巴巴",
  "industry": "互联网/电商",
  "description": "中国最大的电商平台"
}
```

**请求参数说明**

| 字段        | 类型   | 必填 | 说明     |
| ----------- | ------ | ---- | -------- |
| name        | String | 是   | 公司名称 |
| industry    | String | 否   | 所属行业 |
| description | String | 否   | 公司描述 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.3.3 编辑公司

> **PUT** `/api/teacher/companies/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 公司ID |

**请求体**: 同 4.3.2

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.3.4 删除公司

> **DELETE** `/api/teacher/companies/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 公司ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

#### 4.3.5 搜索公司

> **GET** `/api/teacher/companies/search`

**查询参数**

| 参数    | 类型   | 必填 | 说明       |
| ------- | ------ | ---- | ---------- |
| keyword | String | 是   | 搜索关键词 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

### 4.4 题库管理

#### 4.4.1 获取题目列表（分页）

> **GET** `/api/teacher/questions`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 100,
  "page": 0,
  "size": 10
}
```

---

#### 4.4.2 创建题目

> **POST** `/api/teacher/questions`

**请求体**: 同 3.4.4 学生新增题目

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.4.3 编辑题目

> **PUT** `/api/teacher/questions/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 题目ID |

**请求体**: 同 3.4.4

**说明**: 教师端无权限限制，可编辑任意题目。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.4.4 删除题目

> **DELETE** `/api/teacher/questions/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 题目ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

#### 4.4.5 搜索题目

> **GET** `/api/teacher/questions/search`

**查询参数**

| 参数       | 类型   | 必填 | 说明                 |
| ---------- | ------ | ---- | -------------------- |
| keyword    | String | 否   | 搜索关键词           |
| difficulty | String | 否   | 难度筛选             |
| category   | String | 否   | 分类筛选             |
| tags       | String | 否   | 标签筛选（模糊匹配） |
| page       | int    | 否   | 页码，默认 0         |
| size       | int    | 否   | 每页条数，默认 10    |

**注意**: keyword、difficulty、category、tags 四者只能同时使用一个（优先级：keyword > difficulty > category > tags）。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 50,
  "page": 0,
  "size": 10
}
```

---

#### 4.4.6 批量删除题目

> **DELETE** `/api/teacher/questions/batch`

**请求体**

```json
[1, 2, 3]
```

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "成功删除 3 道题目"
}
```

---

#### 4.4.7 获取所有题目（下拉列表）

> **GET** `/api/teacher/questions/all`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

### 4.5 面试记录管理

#### 4.5.1 获取所有面试记录（分页+多条件筛选）

> **GET** `/api/teacher/records`

**查询参数**

| 参数        | 类型   | 默认值 | 说明                          |
| ----------- | ------ | ------ | ----------------------------- |
| page        | int    | 0      | 页码                          |
| size        | int    | 10     | 每页条数                      |
| startDate   | String | 否     | 开始日期，格式 `yyyy-MM-dd` |
| endDate     | String | 否     | 结束日期，格式 `yyyy-MM-dd` |
| studentId   | Long   | 否     | 学生ID                        |
| studentName | String | 否     | 学生姓名（模糊匹配）          |
| companyId   | Long   | 否     | 公司ID                        |
| classId     | Long   | 否     | 班级ID                        |
| result      | String | 否     | 面试结果                      |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 200,
  "page": 0,
  "size": 10
}
```

---

#### 4.5.2 创建面试记录

> **POST** `/api/teacher/records`

**请求头**: 必须携带 `Authorization: Bearer {token}`

**请求体**: 同 3.1.4

**说明**: 教师代为创建面试记录，需指定 `studentId`。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.5.3 编辑面试记录

> **PUT** `/api/teacher/records/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**请求体**: 同 3.1.4

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.5.4 删除面试记录

> **DELETE** `/api/teacher/records/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "删除成功"
}
```

---

#### 4.5.5 批量删除面试记录

> **DELETE** `/api/teacher/records/batch`

**请求体**

```json
[1, 2, 3]
```

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "成功删除 3 条记录"
}
```

---

#### 4.5.6 获取待审核记录

> **GET** `/api/teacher/records/pending`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 10,
  "page": 0,
  "size": 10
}
```

---

#### 4.5.7 评价面试记录

> **PUT** `/api/teacher/records/{id}/evaluate`

**记录操作日志**: 是（`@Auditable(action = "老师评价", target = "面试记录")`）

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**请求体**

```json
{
  "teacherComment": "该生基础扎实，表达清晰",
  "result": "PASS"
}
```

**请求参数说明**

| 字段           | 类型   | 必填 | 说明                 |
| -------------- | ------ | ---- | -------------------- |
| teacherComment | String | 是   | 老师评语             |
| result         | String | 否   | 更新面试结果（可选） |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "评价成功",
  "data": { ... }
}
```

---

#### 4.5.8 审核通过

> **PUT** `/api/teacher/records/{id}/approve`

**记录操作日志**: 是（`@Auditable(action = "审核通过", target = "面试记录")`）

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.5.9 审核驳回

> **PUT** `/api/teacher/records/{id}/reject`

**记录操作日志**: 是（`@Auditable(action = "审核驳回", target = "面试记录")`）

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 4.5.10 按公司查询记录

> **GET** `/api/teacher/records/company/{companyId}`

**路径参数**

| 参数      | 类型 | 说明   |
| --------- | ---- | ------ |
| companyId | Long | 公司ID |

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ],
  "total": 15,
  "page": 0,
  "size": 10
}
```

---

### 4.6 导出功能

#### 4.6.1 导出公司面试题（Markdown）

> **GET** `/api/teacher/export/company/{companyId}`

**路径参数**

| 参数      | 类型 | 说明   |
| --------- | ---- | ------ |
| companyId | Long | 公司ID |

**响应**: 文件下载，`Content-Type: text/markdown; charset=UTF-8`，文件名 `interview_questions.md`

---

#### 4.6.2 导出全部面试题（Markdown）

> **GET** `/api/teacher/export/all`

**请求参数**: 无

**响应**: 文件下载，`Content-Type: text/markdown; charset=UTF-8`，文件名 `all_interview_questions.md`

---

### 4.7 数据统计

> **GET** `/api/teacher/statistics`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": {
    "totalRecords": 200,
    "totalUsers": 50,
    "totalQuestions": 100,
    "totalCompanies": 20,
    "passCount": 80,
    "failCount": 30,
    "notInterviewedCount": 50,
    "pendingResultCount": 25,
    "pendingReviewCount": 10,
    "approvedCount": 180,
    "passRate": 40.0,
    "difficultyStats": {
      "EASY": 30,
      "MEDIUM": 50,
      "HARD": 20
    },
    "companyStats": [
      { "companyId": 1, "companyName": "腾讯", "count": 15 },
      { "companyId": 2, "companyName": "阿里巴巴", "count": 12 }
    ],
    "recentRecords": 25
  }
}
```

**响应字段说明**

| 字段                | 类型   | 说明                          |
| ------------------- | ------ | ----------------------------- |
| totalRecords        | long   | 总记录数                      |
| totalUsers          | long   | 总用户数                      |
| totalQuestions      | long   | 总题目数                      |
| totalCompanies      | long   | 总公司数                      |
| passCount           | long   | 通过数                        |
| failCount           | long   | 未通过数                      |
| notInterviewedCount | long   | 未面试数                      |
| pendingResultCount  | long   | 等待结果数                    |
| pendingReviewCount  | long   | 待审核记录数                  |
| approvedCount       | long   | 已审核通过数                  |
| passRate            | double | 通过率（百分比，保留1位小数） |
| difficultyStats     | Map    | 各难度题目数量                |
| companyStats        | List   | 各公司面试记录数              |
| recentRecords       | long   | 最近7天新增记录数             |

---

### 4.8 批量导入

#### 4.8.1 下载题库导入模板

> **GET** `/api/teacher/import/template`

**请求参数**: 无

**模板列说明**:

| 列                     | 必填 | 说明              |
| ---------------------- | ---- | ----------------- |
| 题目\*                 | 是   | 题目标题          |
| 题目内容               | 否   | 题目详细内容      |
| 难度(EASY/MEDIUM/HARD) | 否   | 难度，默认 MEDIUM |
| 分类                   | 否   | 分类名称          |
| 标签(逗号分隔)         | 否   | 标签              |
| 参考答案               | 否   | 参考答案          |

**响应**: 文件下载，`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`，文件名 `题库导入模板.xlsx`

---

#### 4.8.2 导入题库

> **POST** `/api/teacher/import/questions`

**Content-Type**: `multipart/form-data`

**表单参数**

| 参数 | 类型 | 必填 | 说明                |
| ---- | ---- | ---- | ------------------- |
| file | File | 是   | Excel 文件（.xlsx） |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "成功导入 10 道题目"
}
```

**错误响应**

```json
{
  "code": 500,
  "message": "导入失败: 错误详情"
}
```

---

#### 4.8.3 下载用户导入模板

> **GET** `/api/teacher/import/users-template`

**请求参数**: 无

**模板列说明**:

| 列                      | 必填 | 说明       |
| ----------------------- | ---- | ---------- |
| 用户名\*                | 是   | 登录用户名 |
| 姓名\*                  | 是   | 显示姓名   |
| 密码\*                  | 是   | 登录密码   |
| 角色(TEACHER/STUDENT)\* | 是   | 角色       |
| 邮箱                    | 否   | 邮箱       |
| 电话                    | 否   | 电话       |
| 班级ID\*                | 是   | 所属班级ID |

**响应**: 文件下载，文件名 `用户导入模板.xlsx`

---

#### 4.8.4 导入用户

> **POST** `/api/teacher/import/users`

**Content-Type**: `multipart/form-data`

**表单参数**

| 参数 | 类型 | 必填 | 说明                |
| ---- | ---- | ---- | ------------------- |
| file | File | 是   | Excel 文件（.xlsx） |

**注意**:

- 已存在的用户名会被跳过
- 缺少班级ID或班级ID不存在会跳过并记录警告
- 密码会被 BCrypt 加密存储

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "成功导入 50 个用户",
  "warnings": ["第3行缺少班级ID", "第5行班级ID 99 不存在"]
}
```

`warnings` 字段仅在存在警告时出现。

---

### 4.9 操作日志

> **GET** `/api/teacher/audit-logs`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 10     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "userId": 1,
      "username": "admin",
      "action": "老师评价",
      "target": "面试记录",
      "targetId": 5,
      "detail": null,
      "createdAt": "2026-08-08T10:30:00"
    }
  ],
  "total": 100,
  "page": 0,
  "size": 10
}
```

---

## 5. 个人信息 - `/api/user`

> **权限要求**: 需要登录，携带 Token（学生或教师Token均可）
> **请求头**: `Authorization: Bearer {token}`（必须）

**curl 示例**：

```bash
# 使用任意角色的Token
curl -X POST http://localhost:8080/api/user/profile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name":"新名字","email":"new@email.com"}'
```

### 5.1 更新个人资料

> **POST** `/api/user/profile`

**请求体**

```json
{
  "name": "张三",
  "email": "zhangsan@newemail.com",
  "phone": "13900139000"
}
```

**请求参数说明**

| 字段  | 类型   | 必填 | 说明 |
| ----- | ------ | ---- | ---- |
| name  | String | 否   | 姓名 |
| email | String | 否   | 邮箱 |
| phone | String | 否   | 电话 |

**说明**: 只更新请求中提供的字段，未提供的字段保持不变。

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "个人信息更新成功",
  "data": {
    "id": 10,
    "username": "student001",
    "name": "张三",
    "email": "zhangsan@newemail.com",
    "phone": "13900139000",
    ...
  }
}
```

---

### 5.2 修改密码

> **POST** `/api/user/change-password`

**请求体**

```json
{
  "oldPassword": "123456",
  "newPassword": "654321"
}
```

**请求参数说明**

| 字段        | 类型   | 必填 | 说明   |
| ----------- | ------ | ---- | ------ |
| oldPassword | String | 是   | 旧密码 |
| newPassword | String | 是   | 新密码 |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

**错误响应**

```json
{
  "code": 500,
  "message": "旧密码不正确"
}
```

---

## 6. 通知 - `/api/notifications`

> **权限要求**: 需要登录，携带 Token（学生或教师Token均可）
> **请求头**: `Authorization: Bearer {token}`（必须）

**curl 示例**：

```bash
curl -X GET "http://localhost:8080/api/notifications?page=0&size=20" \
  -H "Authorization: Bearer {token}"
```

### 6.1 获取通知列表

> **GET** `/api/notifications`

**查询参数**

| 参数 | 类型 | 默认值 | 说明     |
| ---- | ---- | ------ | -------- |
| page | int  | 0      | 页码     |
| size | int  | 20     | 每页条数 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "userId": 10,
      "title": "面试记录已审核",
      "content": "您的面试记录已被老师审核通过",
      "type": "REVIEW",
      "isRead": false,
      "createdAt": "2026-08-08T10:00:00"
    }
  ],
  "total": 5,
  "page": 0,
  "size": 20
}
```

---

### 6.2 标记单条已读

> **PUT** `/api/notifications/{id}/read`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 通知ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "已读"
}
```

---

### 6.3 全部标记已读

> **PUT** `/api/notifications/read-all`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "全部已读"
}
```

---

### 6.4 获取未读数量

> **GET** `/api/notifications/unread-count`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": 3
}
```

`data` 为未读通知数量（Long 类型）。

---

## 7. 字典管理 - `/api/teacher/dict`

> **权限要求**: 需要 TEACHER 角色，携带 Token
> **请求头**: `Authorization: Bearer {token}`（必须，使用教师Token）

**curl 示例**：

```bash
curl -X GET http://localhost:8080/api/teacher/dict/types \
  -H "Authorization: Bearer {token}"
```

### 7.1 字典类型

#### 7.1.1 获取字典类型列表

> **GET** `/api/teacher/dict/types`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "typeName": "题库分类",
      "typeCode": "question_category",
      "description": "用于题库分类管理",
      "status": "1",
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ]
}
```

---

#### 7.1.2 创建字典类型

> **POST** `/api/teacher/dict/types`

**请求体**

```json
{
  "typeName": "面试结果",
  "typeCode": "interview_result",
  "description": "面试结果选项"
}
```

**请求参数说明**

| 字段        | 类型   | 必填 | 说明             |
| ----------- | ------ | ---- | ---------------- |
| typeName    | String | 是   | 类型名称         |
| typeCode    | String | 是   | 类型编码，需唯一 |
| description | String | 否   | 类型描述         |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典类型创建成功",
  "data": { ... }
}
```

---

#### 7.1.3 编辑字典类型

> **PUT** `/api/teacher/dict/types/{id}`

**路径参数**

| 参数 | 类型 | 说明       |
| ---- | ---- | ---------- |
| id   | Long | 字典类型ID |

**请求体**: 同 7.1.2

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典类型更新成功",
  "data": { ... }
}
```

---

#### 7.1.4 删除字典类型

> **DELETE** `/api/teacher/dict/types/{id}`

**路径参数**

| 参数 | 类型 | 说明       |
| ---- | ---- | ---------- |
| id   | Long | 字典类型ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典类型删除成功"
}
```

---

### 7.2 字典数据

#### 7.2.1 根据类型编码获取字典数据

> **GET** `/api/teacher/dict/data/{typeCode}`

**路径参数**

| 参数     | 类型   | 说明                                   |
| -------- | ------ | -------------------------------------- |
| typeCode | String | 字典类型编码，如 `question_category` |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "dictTypeCode": "question_category",
      "label": "Java基础",
      "value": "JAVA_BASIC",
      "sortOrder": 0,
      "status": "1",
      "creatorName": "admin",
      "createdAt": "2026-08-01T10:00:00",
      "updatedAt": "2026-08-01T10:00:00"
    }
  ]
}
```

---

#### 7.2.2 创建字典数据

> **POST** `/api/teacher/dict/data`

**请求体**

```json
{
  "dictTypeCode": "question_category",
  "label": "前端开发",
  "value": "FRONTEND",
  "sortOrder": 1,
  "status": "1"
}
```

**请求参数说明**

| 字段         | 类型    | 必填 | 说明                             |
| ------------ | ------- | ---- | -------------------------------- |
| dictTypeCode | String  | 是   | 所属字典类型编码                 |
| label        | String  | 是   | 显示标签                         |
| value        | String  | 是   | 数据值                           |
| sortOrder    | Integer | 否   | 排序序号，默认 0                 |
| status       | String  | 否   | 状态："1"启用，"0"禁用，默认 "1" |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典数据创建成功",
  "data": { ... }
}
```

---

#### 7.2.3 编辑字典数据

> **PUT** `/api/teacher/dict/data/{id}`

**路径参数**

| 参数 | 类型 | 说明       |
| ---- | ---- | ---------- |
| id   | Long | 字典数据ID |

**请求体**: 同 7.2.2

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典数据更新成功",
  "data": { ... }
}
```

---

#### 7.2.4 删除字典数据

> **DELETE** `/api/teacher/dict/data/{id}`

**路径参数**

| 参数 | 类型 | 说明       |
| ---- | ---- | ---------- |
| id   | Long | 字典数据ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "字典数据删除成功"
}
```

---

#### 7.2.5 获取题库分类（下拉选项）

> **GET** `/api/teacher/dict/categories`

**请求参数**: 无

**说明**: 返回 `question_category` 类型下所有启用状态（status="1"）的字典数据。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

## 8. 公共接口 - `/api/common`

> **权限要求**: 无需登录认证，**不需要携带 Token**

**curl 示例（直接调用，无需Token）**：

```bash
# 获取所有公司
curl -X GET http://localhost:8080/api/common/companies

# 搜索公司
curl -X GET "http://localhost:8080/api/common/companies/search?keyword=腾讯"

# 获取公开记录
curl -X GET http://localhost:8080/api/common/records/public
```

### 8.1 公司

#### 8.1.1 获取所有公司列表

> **GET** `/api/common/companies`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

#### 8.1.2 搜索公司

> **GET** `/api/common/companies/search`

**查询参数**

| 参数    | 类型   | 必填 | 说明       |
| ------- | ------ | ---- | ---------- |
| keyword | String | 是   | 搜索关键词 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

#### 8.1.3 获取公司详情

> **GET** `/api/common/companies/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 公司ID |

**注意**: 路径使用正则 `{id:\d+}` 匹配纯数字ID。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

### 8.2 题目

#### 8.2.1 获取所有题目列表

> **GET** `/api/common/questions`

**请求参数**: 无

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

#### 8.2.2 获取题目详情

> **GET** `/api/common/questions/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 题目ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

#### 8.2.3 搜索题目

> **GET** `/api/common/questions/search`

**查询参数**

| 参数    | 类型   | 必填 | 说明       |
| ------- | ------ | ---- | ---------- |
| keyword | String | 是   | 搜索关键词 |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

### 8.3 面试记录

#### 8.3.1 获取公开记录列表

> **GET** `/api/common/records/public`

**请求参数**: 无

**说明**: 返回所有 `isPublic = true` 且状态为 `APPROVED` 的面试记录。

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

#### 8.3.2 按公司获取公开记录

> **GET** `/api/common/records/company/{companyId}`

**路径参数**

| 参数      | 类型 | 说明   |
| --------- | ---- | ------ |
| companyId | Long | 公司ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": [ ... ]
}
```

---

#### 8.3.3 获取面试记录详情

> **GET** `/api/common/records/{id}`

**路径参数**

| 参数 | 类型 | 说明   |
| ---- | ---- | ------ |
| id   | Long | 记录ID |

**成功响应 (200)**

```json
{
  "code": 200,
  "data": { ... }
}
```

---

## 9. 附录：枚举值说明

### 9.1 用户角色 (User.Role)

| 枚举值       | 说明       |
| ------------ | ---------- |
| STUDENT      | 学生       |
| TEACHER      | 老师       |
| SUPER\_ADMIN | 超级管理员 |

### 9.2 面试结果 (result)

| 常量                     | 枚举值           | 说明       |
| ------------------------ | ---------------- | ---------- |
| RESULT\_NOT\_INTERVIEWED | NOT\_INTERVIEWED | 未面试     |
| RESULT\_PENDING          | PENDING\_RESULT  | 等待结果   |
| RESULT\_PASS             | PASS             | 面试通过   |
| RESULT\_FAIL             | FAIL             | 面试未通过 |

### 9.3 记录状态 (RecordStatus)

| 枚举值   | 说明       |
| -------- | ---------- |
| PENDING  | 待审核     |
| APPROVED | 已审核通过 |
| REJECTED | 已驳回     |

### 9.4 题目难度 (difficulty)

| 枚举值 | 说明 |
| ------ | ---- |
| EASY   | 简单 |
| MEDIUM | 中等 |
| HARD   | 困难 |

### 9.5 字典数据状态 (status)

| 值  | 说明 |
| --- | ---- |
| "1" | 启用 |
| "0" | 禁用 |

---

## 10. 附录：数据模型完整字段

### 10.1 User（用户）

| 字段        | 数据库列      | 类型                    | 说明                                 |
| ----------- | ------------- | ----------------------- | ------------------------------------ |
| id          | id            | Long (自增)             | 主键                                 |
| username    | username      | String(50)              | 用户名，唯一                         |
| password    | password      | String                  | 密码（BCrypt加密，JSON序列化时排除） |
| name        | name          | String(50)              | 姓名                                 |
| role        | role          | Enum(Role)              | 角色                                 |
| email       | email         | String(100)             | 邮箱                                 |
| phone       | phone         | String(20)              | 电话                                 |
| schoolClass | class\_id     | SchoolClass (ManyToOne) | 所属班级                             |
| frozen      | frozen        | Boolean                 | 是否冻结，默认 false                 |
| creatorName | creator\_name | String(50)              | 创建者用户名                         |
| createdAt   | created\_at   | LocalDateTime           | 创建时间                             |

### 10.2 Question（题目）

| 字段            | 数据库列          | 类型          | 说明                   |
| --------------- | ----------------- | ------------- | ---------------------- |
| id              | id                | Long (自增)   | 主键                   |
| title           | title             | TEXT          | 题目标题               |
| content         | content           | TEXT          | 题目内容               |
| difficulty      | difficulty        | String(50)    | 难度：EASY/MEDIUM/HARD |
| category        | category          | String(100)   | 分类                   |
| tags            | tags              | String(100)   | 标签，逗号分隔         |
| referenceAnswer | reference\_answer | TEXT          | 参考答案               |
| creatorName     | creator\_name     | String(50)    | 创建者用户名           |
| createdAt       | created\_at       | LocalDateTime | 创建时间               |
| updatedAt       | updated\_at       | LocalDateTime | 更新时间               |

### 10.3 InterviewRecord（面试记录）

| 字段               | 数据库列               | 类型                                       | 说明                 |
| ------------------ | ---------------------- | ------------------------------------------ | -------------------- |
| id                 | id                     | Long (自增)                                | 主键                 |
| student            | student\_id            | User (ManyToOne)                           | 学生                 |
| company            | company\_id            | Company (ManyToOne)                        | 公司                 |
| recordQuestions    | -                      | List\<InterviewRecordQuestion> (OneToMany) | 关联题目列表         |
| interviewDate      | interview\_date        | LocalDateTime                              | 面试日期时间         |
| position           | position               | String(50)                                 | 面试职位             |
| result             | result                 | String(20)                                 | 面试结果             |
| interviewerComment | interviewer\_comment   | TEXT                                       | 面试官评语           |
| teacherComment     | teacher\_comment       | TEXT                                       | 老师评语             |
| examPoints         | exam\_points           | TEXT                                       | 考试重点             |
| isPublic           | is\_public             | Boolean                                    | 是否公开，默认 false |
| status             | status                 | Enum(RecordStatus)                         | 记录状态             |
| creatorId          | creator\_id            | Long                                       | 创建者ID             |
| creatorName        | creator\_name          | String(50)                                 | 创建者用户名         |
| salaryRange        | salary\_range          | String(50)                                 | 薪资范围             |
| interviewRound     | interview\_round       | Integer                                    | 面试轮次             |
| interviewType      | interview\_type        | String(20)                                 | 面试类型             |
| hrContact          | hr\_contact            | String(100)                                | HR联系人             |
| workLocation       | work\_location         | String(100)                                | 工作地点             |
| parentRecordId     | parent\_record\_id     | Long                                       | 父记录ID             |
| interviewSessionId | interview\_session\_id | String(64)                                 | 面试会话ID（UUID）   |
| createdAt          | created\_at            | LocalDateTime                              | 创建时间             |
| updatedAt          | updated\_at            | LocalDateTime                              | 更新时间             |

### 10.4 InterviewRecordQuestion（记录-题目关联）

| 字段            | 数据库列     | 类型                        | 说明             |
| --------------- | ------------ | --------------------------- | ---------------- |
| id              | id           | Long (自增)                 | 主键             |
| interviewRecord | record\_id   | InterviewRecord (ManyToOne) | 所属面试记录     |
| question        | question\_id | Question (ManyToOne)        | 关联题目         |
| sortOrder       | sort\_order  | Integer                     | 排序序号，默认 0 |

### 10.5 Company（公司）

| 字段        | 数据库列      | 类型          | 说明         |
| ----------- | ------------- | ------------- | ------------ |
| id          | id            | Long (自增)   | 主键         |
| name        | name          | String(100)   | 公司名称     |
| industry    | industry      | String(50)    | 行业         |
| description | description   | TEXT          | 公司描述     |
| creatorName | creator\_name | String(50)    | 创建者用户名 |
| createdAt   | created\_at   | LocalDateTime | 创建时间     |

### 10.6 SchoolClass（班级）

| 字段        | 数据库列      | 类型                          | 说明         |
| ----------- | ------------- | ----------------------------- | ------------ |
| id          | id            | Long (自增)                   | 主键         |
| name        | name          | String                        | 班级名称     |
| description | description   | TEXT                          | 班级描述     |
| students    | -             | List\<User> (OneToMany, LAZY) | 学生列表     |
| creatorName | creator\_name | String(50)                    | 创建者用户名 |
| createdAt   | created\_at   | LocalDateTime                 | 创建时间     |
| updatedAt   | updated\_at   | LocalDateTime                 | 更新时间     |

### 10.7 FavoriteRecord（收藏记录）

| 字段      | 数据库列    | 类型          | 说明       |
| --------- | ----------- | ------------- | ---------- |
| id        | id          | Long (自增)   | 主键       |
| userId    | user\_id    | Long          | 用户ID     |
| recordId  | record\_id  | Long          | 面试记录ID |
| createdAt | created\_at | LocalDateTime | 创建时间   |

**唯一约束**: (user\_id, record\_id)

### 10.8 Notification（通知）

| 字段      | 数据库列    | 类型          | 说明                 |
| --------- | ----------- | ------------- | -------------------- |
| id        | id          | Long (自增)   | 主键                 |
| userId    | user\_id    | Long          | 接收用户ID           |
| title     | title       | String(200)   | 通知标题             |
| content   | content     | TEXT          | 通知内容             |
| type      | type        | String(50)    | 通知类型             |
| isRead    | is\_read    | Boolean       | 是否已读，默认 false |
| createdAt | created\_at | LocalDateTime | 创建时间             |

### 10.9 DictType（字典类型）

| 字段        | 数据库列      | 类型          | 说明                   |
| ----------- | ------------- | ------------- | ---------------------- |
| id          | id            | Long (自增)   | 主键                   |
| typeName    | type\_name    | String(100)   | 类型名称               |
| typeCode    | type\_code    | String(100)   | 类型编码，唯一         |
| description | description   | String(255)   | 类型描述               |
| status      | status        | String(1)     | 状态："1"启用，"0"禁用 |
| creatorName | creator\_name | String(50)    | 创建者用户名           |
| createdAt   | created\_at   | LocalDateTime | 创建时间               |
| updatedAt   | updated\_at   | LocalDateTime | 更新时间               |

### 10.10 DictData（字典数据）

| 字段         | 数据库列         | 类型          | 说明                   |
| ------------ | ---------------- | ------------- | ---------------------- |
| id           | id               | Long (自增)   | 主键                   |
| dictTypeCode | dict\_type\_code | String(100)   | 所属字典类型编码       |
| label        | label            | String(100)   | 显示标签               |
| value        | value            | String(100)   | 数据值                 |
| sortOrder    | sort\_order      | Integer       | 排序序号，默认 0       |
| status       | status           | String(1)     | 状态："1"启用，"0"禁用 |
| creatorName  | creator\_name    | String(50)    | 创建者用户名           |
| createdAt    | created\_at      | LocalDateTime | 创建时间               |
| updatedAt    | updated\_at      | LocalDateTime | 更新时间               |

### 10.11 AuditLog（操作日志）

| 字段      | 数据库列    | 类型          | 说明       |
| --------- | ----------- | ------------- | ---------- |
| id        | id          | Long (自增)   | 主键       |
| userId    | user\_id    | Long          | 操作用户ID |
| username  | username    | String(50)    | 操作用户名 |
| action    | action      | String(100)   | 操作类型   |
| target    | target      | String(100)   | 操作目标   |
| targetId  | target\_id  | Long          | 目标ID     |
| detail    | detail      | TEXT          | 操作详情   |
| createdAt | created\_at | LocalDateTime | 操作时间   |

---

## 接口索引总表

| 序号 | 方法   | 路径                                        | 说明                     | 权限     |
| ---- | ------ | ------------------------------------------- | ------------------------ | -------- |
| 1    | POST   | /api/auth/login                             | 登录                     | 公开     |
| 2    | POST   | /api/auth/register                          | 注册                     | 公开     |
| 3    | GET    | /api/student/my-records                     | 获取我的面试记录         | STUDENT  |
| 4    | GET    | /api/student/my-records/grouped             | 获取按会话分组的记录     | STUDENT  |
| 5    | GET    | /api/student/my-records/session/{sessionId} | 获取会话详情             | STUDENT  |
| 6    | POST   | /api/student/my-records                     | 创建面试记录             | STUDENT  |
| 7    | POST   | /api/student/submit-review                  | 提交审核                 | STUDENT  |
| 8    | POST   | /api/student/my-records/{id}/append         | 追加下一轮面试           | STUDENT  |
| 9    | PUT    | /api/student/my-records/{id}/result         | 更新面试结果             | STUDENT  |
| 10   | POST   | /api/student/favorites/{recordId}           | 切换收藏状态             | STUDENT  |
| 11   | GET    | /api/student/favorites                      | 获取收藏列表             | STUDENT  |
| 12   | GET    | /api/student/favorites/check/{recordId}     | 检查是否已收藏           | STUDENT  |
| 13   | GET    | /api/student/practice                       | 随机刷题                 | STUDENT  |
| 14   | GET    | /api/student/categories                     | 获取分类列表             | STUDENT  |
| 15   | GET    | /api/student/questions                      | 获取题目列表（分页）     | STUDENT  |
| 16   | GET    | /api/student/questions/search               | 搜索题目                 | STUDENT  |
| 17   | POST   | /api/student/questions                      | 新增题目                 | STUDENT  |
| 18   | PUT    | /api/student/questions/{id}                 | 编辑题目（仅限自己创建） | STUDENT  |
| 19   | GET    | /api/teacher/users                          | 获取用户列表             | TEACHER  |
| 20   | POST   | /api/teacher/users                          | 创建用户                 | TEACHER  |
| 21   | PUT    | /api/teacher/users/{id}                     | 编辑用户                 | TEACHER  |
| 22   | DELETE | /api/teacher/users/{id}                     | 删除用户                 | TEACHER  |
| 23   | PUT    | /api/teacher/users/{id}/freeze              | 冻结用户                 | TEACHER  |
| 24   | PUT    | /api/teacher/users/{id}/unfreeze            | 解冻用户                 | TEACHER  |
| 25   | DELETE | /api/teacher/users/batch                    | 批量删除用户             | TEACHER  |
| 26   | GET    | /api/teacher/users/students                 | 获取所有学生             | TEACHER  |
| 27   | GET    | /api/teacher/classes                        | 获取班级列表（分页）     | TEACHER  |
| 28   | POST   | /api/teacher/classes                        | 创建班级                 | TEACHER  |
| 29   | PUT    | /api/teacher/classes/{id}                   | 编辑班级                 | TEACHER  |
| 30   | DELETE | /api/teacher/classes/{id}                   | 删除班级                 | TEACHER  |
| 31   | GET    | /api/teacher/classes/all                    | 获取所有班级             | TEACHER  |
| 32   | GET    | /api/teacher/companies                      | 获取公司列表（分页）     | TEACHER  |
| 33   | POST   | /api/teacher/companies                      | 创建公司                 | TEACHER  |
| 34   | PUT    | /api/teacher/companies/{id}                 | 编辑公司                 | TEACHER  |
| 35   | DELETE | /api/teacher/companies/{id}                 | 删除公司                 | TEACHER  |
| 36   | GET    | /api/teacher/companies/search               | 搜索公司                 | TEACHER  |
| 37   | GET    | /api/teacher/questions                      | 获取题目列表（分页）     | TEACHER  |
| 38   | POST   | /api/teacher/questions                      | 创建题目                 | TEACHER  |
| 39   | PUT    | /api/teacher/questions/{id}                 | 编辑题目                 | TEACHER  |
| 40   | DELETE | /api/teacher/questions/{id}                 | 删除题目                 | TEACHER  |
| 41   | GET    | /api/teacher/questions/search               | 搜索题目                 | TEACHER  |
| 42   | DELETE | /api/teacher/questions/batch                | 批量删除题目             | TEACHER  |
| 43   | GET    | /api/teacher/questions/all                  | 获取所有题目             | TEACHER  |
| 44   | GET    | /api/teacher/records                        | 获取所有面试记录         | TEACHER  |
| 45   | POST   | /api/teacher/records                        | 创建面试记录             | TEACHER  |
| 46   | PUT    | /api/teacher/records/{id}                   | 编辑面试记录             | TEACHER  |
| 47   | DELETE | /api/teacher/records/{id}                   | 删除面试记录             | TEACHER  |
| 48   | DELETE | /api/teacher/records/batch                  | 批量删除面试记录         | TEACHER  |
| 49   | GET    | /api/teacher/records/pending                | 获取待审核记录           | TEACHER  |
| 50   | PUT    | /api/teacher/records/{id}/evaluate          | 评价面试记录             | TEACHER  |
| 51   | PUT    | /api/teacher/records/{id}/approve           | 审核通过                 | TEACHER  |
| 52   | PUT    | /api/teacher/records/{id}/reject            | 审核驳回                 | TEACHER  |
| 53   | GET    | /api/teacher/records/company/{companyId}    | 按公司查询记录           | TEACHER  |
| 54   | GET    | /api/teacher/export/company/{companyId}     | 导出公司面试题           | TEACHER  |
| 55   | GET    | /api/teacher/export/all                     | 导出全部面试题           | TEACHER  |
| 56   | GET    | /api/teacher/statistics                     | 数据统计                 | TEACHER  |
| 57   | GET    | /api/teacher/import/template                | 下载题库导入模板         | TEACHER  |
| 58   | POST   | /api/teacher/import/questions               | 导入题库                 | TEACHER  |
| 59   | GET    | /api/teacher/import/users-template          | 下载用户导入模板         | TEACHER  |
| 60   | POST   | /api/teacher/import/users                   | 导入用户                 | TEACHER  |
| 61   | GET    | /api/teacher/audit-logs                     | 获取操作日志             | TEACHER  |
| 62   | POST   | /api/user/profile                           | 更新个人资料             | 登录用户 |
| 63   | POST   | /api/user/change-password                   | 修改密码                 | 登录用户 |
| 64   | GET    | /api/notifications                          | 获取通知列表             | 登录用户 |
| 65   | PUT    | /api/notifications/{id}/read                | 标记单条已读             | 登录用户 |
| 66   | PUT    | /api/notifications/read-all                 | 全部标记已读             | 登录用户 |
| 67   | GET    | /api/notifications/unread-count             | 获取未读数量             | 登录用户 |
| 68   | GET    | /api/teacher/dict/types                     | 获取字典类型列表         | TEACHER  |
| 69   | POST   | /api/teacher/dict/types                     | 创建字典类型             | TEACHER  |
| 70   | PUT    | /api/teacher/dict/types/{id}                | 编辑字典类型             | TEACHER  |
| 71   | DELETE | /api/teacher/dict/types/{id}                | 删除字典类型             | TEACHER  |
| 72   | GET    | /api/teacher/dict/data/{typeCode}           | 获取字典数据             | TEACHER  |
| 73   | POST   | /api/teacher/dict/data                      | 创建字典数据             | TEACHER  |
| 74   | PUT    | /api/teacher/dict/data/{id}                 | 编辑字典数据             | TEACHER  |
| 75   | DELETE | /api/teacher/dict/data/{id}                 | 删除字典数据             | TEACHER  |
| 76   | GET    | /api/teacher/dict/categories                | 获取题库分类             | TEACHER  |
| 77   | GET    | /api/common/companies                       | 获取所有公司             | 公开     |
| 78   | GET    | /api/common/companies/search                | 搜索公司                 | 公开     |
| 79   | GET    | /api/common/companies/{id}                  | 获取公司详情             | 公开     |
| 80   | GET    | /api/common/questions                       | 获取所有题目             | 公开     |
| 81   | GET    | /api/common/questions/{id}                  | 获取题目详情             | 公开     |
| 82   | GET    | /api/common/questions/search                | 搜索题目                 | 公开     |
| 83   | GET    | /api/common/records/public                  | 获取公开记录             | 公开     |
| 84   | GET    | /api/common/records/company/{companyId}     | 按公司获取公开记录       | 公开     |
| 85   | GET    | /api/common/records/{id}                    | 获取记录详情             | 公开     |

---

> **文档结束** - 共 85 个接口，覆盖 8 个模块。如有疑问请联系开发团队。
