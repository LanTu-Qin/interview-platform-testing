# 面试总结平台 - 测试用例（模板格式）

> \\\\\\\*\\\\\\\*版本\\\\\\\*\\\\\\\*: v1.0  
> \\\\\\\*\\\\\\\*日期\\\\\\\*\\\\\\\*: 2026-08-08  
> \\\\\\\*\\\\\\\*环境\\\\\\\*\\\\\\\*: 测试环境 (http://localhost:8080, 数据库 127.0.0.1:3306, root/root)  
> \\\\\\\*\\\\\\\*说明\\\\\\\*\\\\\\\*: "实际结果"列由测试人员执行后填写

\---

## 测试准备

### 测试账号

|账号|用户名|密码|角色|Token用途|
|-|-|-|-|-|
|管理员|admin|123456|TEACHER|教师端接口测试|
|学生A|student\_a|123456|STUDENT|学生端接口测试|

### Token获取方式

```
POST /api/auth/login
请求体: {"username":"admin","password":"123456"}
响应: data.token 即为 JWT Token
```

### 请求头说明

|接口类型|需要Token|请求头|
|-|-|-|
|认证接口|否|`Content-Type: application/json`|
|公共接口|否|无特殊要求|
|学生端|是|`Authorization: Bearer {学生Token}` + `Content-Type: application/json`|
|教师端|是|`Authorization: Bearer {教师Token}` + `Content-Type: application/json`|
|个人信息|是|`Authorization: Bearer {任意Token}` + `Content-Type: application/json`|
|通知|是|`Authorization: Bearer {任意Token}` + `Content-Type: application/json`|

### 优先级定义

|级别|说明|
|-|-|
|P0|核心功能，阻塞性问题|
|P1|重要功能，影响体验|
|P2|边界场景，建议覆盖|

\---

## 一、认证模块

### 1.1 登录

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-AUTH-001|教师正常登录|P0|账号admin存在|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"admin","password":"123456"}`|code=200, message="登录成功", data含token/username/name/role/userId, role="TEACHER"||
|TC-AUTH-002|学生正常登录|P0|账号student\_a存在|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"student\\\\\\\_a","password":"123456"}`|code=200, role="STUDENT"||
|TC-AUTH-003|密码错误|P0|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"admin","password":"wrong"}`|code=500, message含"用户名或密码错误"||
|TC-AUTH-004|用户名不存在|P0|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"notexist","password":"123456"}`|code=500, 登录失败||
|TC-AUTH-005|用户名为空|P1|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"","password":"123456"}`|返回错误提示||
|TC-AUTH-006|密码为空|P1|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"admin","password":""}`|返回错误提示||
|TC-AUTH-007|请求体为空|P1|无|登录|POST|/api/auth/login|Content-Type: application/json|`{}`|返回参数校验错误||
|TC-AUTH-008|缺少username字段|P1|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"password":"123456"}`|返回参数校验错误||
|TC-AUTH-009|缺少password字段|P1|无|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"admin"}`|返回参数校验错误||
|TC-AUTH-010|冻结用户登录|P0|存在被冻结的账号|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"frozen\\\\\\\_user","password":"123456"}`|返回错误，提示账号已被冻结||
|TC-AUTH-011|登录后Token可用于认证|P0|已登录获取token|登录|POST|/api/auth/login|Content-Type: application/json|`{"username":"admin","password":"123456"}`|获取token后，用该token访问需认证接口应返回200||

### 1.2 注册

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-AUTH-012|正常注册学生|P0|用户名不重复|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t1","password":"123","name":"测试","role":"STUDENT","classId":1}`|code=200, message="注册成功", 返回token和用户信息||
|TC-AUTH-013|正常注册教师|P0|用户名不重复|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t2","password":"123","name":"李老师","role":"TEACHER"}`|code=200, role="TEACHER"||
|TC-AUTH-014|用户名重复注册|P0|admin已存在|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"admin","password":"123","name":"重复","role":"STUDENT"}`|返回错误，提示用户名已存在||
|TC-AUTH-015|缺username|P1|无|注册|POST|/api/auth/register|Content-Type: application/json|`{"password":"123","name":"test","role":"STUDENT"}`|返回参数校验错误||
|TC-AUTH-016|缺password|P1|无|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t3","name":"test","role":"STUDENT"}`|返回参数校验错误||
|TC-AUTH-017|缺name|P1|无|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t4","password":"123","role":"STUDENT"}`|返回参数校验错误||
|TC-AUTH-018|缺role|P1|无|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t5","password":"123","name":"test"}`|返回参数校验错误||
|TC-AUTH-019|role无效值|P1|无|注册|POST|/api/auth/register|Content-Type: application/json|`{"username":"t6","password":"123","name":"test","role":"INVALID"}`|返回参数校验错误||
|TC-AUTH-020|注册后立即登录|P0|刚注册成功|注册→登录|POST|/api/auth/register → /api/auth/login|Content-Type: application/json|用注册的账号密码登录|登录成功，返回token||

\---

## 二、学生端

### 2.1 获取我的面试记录

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-001|正常获取记录|P0|学生已登录，有面试记录|获取我的面试记录|GET|/api/student/my-records|Authorization: Bearer {学生Token}|无|code=200, data为数组，所有记录student.id=当前学生ID||
|TC-STU-002|无记录时获取|P0|学生已登录，无记录|获取我的面试记录|GET|/api/student/my-records|Authorization: Bearer {学生Token}|无|code=200, data为空数组\[]||
|TC-STU-003|未登录访问|P0|无Token|获取我的面试记录|GET|/api/student/my-records|无|无|返回401未授权||
|TC-STU-004|教师角色访问|P1|用教师Token|获取我的面试记录|GET|/api/student/my-records|Authorization: Bearer {教师Token}|无|返回403权限不足||

### 2.2 获取面试记录（按会话分组）

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-005|正常分组返回|P0|学生有多轮面试记录（同一sessionId）|获取分组记录|GET|/api/student/my-records/grouped|Authorization: Bearer {学生Token}|无|code=200, data按sessionId分组，每组含sessionId/companyName/position/rounds||
|TC-STU-006|单轮记录分组|P0|学生只有单轮记录|获取分组记录|GET|/api/student/my-records/grouped|Authorization: Bearer {学生Token}|无|每组rounds数组只有1条记录||
|TC-STU-007|多轮排序|P1|同一sessionId有3轮记录|获取分组记录|GET|/api/student/my-records/grouped|Authorization: Bearer {学生Token}|无|rounds按interviewRound升序排列||
|TC-STU-008|无记录时|P0|学生无任何记录|获取分组记录|GET|/api/student/my-records/grouped|Authorization: Bearer {学生Token}|无|code=200, data为空数组\[]||
|TC-STU-009|未登录访问|P0|无Token|获取分组记录|GET|/api/student/my-records/grouped|无|无|返回401||

### 2.3 获取会话详情

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-010|正常获取会话详情|P0|有效的sessionId|获取会话详情|GET|/api/student/my-records/session/{validSessionId}|Authorization: Bearer {学生Token}|无|code=200, data包含sessionId/companyName/position/rounds||
|TC-STU-011|不存在的sessionId|P0|无|获取会话详情|GET|/api/student/my-records/session/nonexist-uuid|Authorization: Bearer {学生Token}|无|code=404, message="会话不存在"||
|TC-STU-012|获取他人会话|P0|学生A登录，sessionId属于学生B|获取会话详情|GET|/api/student/my-records/session/{他人sessionId}|Authorization: Bearer {学生Token}|无|返回404||
|TC-STU-013|未登录访问|P0|无Token|获取会话详情|GET|/api/student/my-records/session/test|无|无|返回401||

### 2.4 创建面试记录

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-014|创建完整记录|P0|学生已登录|创建面试记录|POST|/api/student/my-records|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1,"questionIds":\\\\\\\[1,2],"interviewDate":"2026-08-08 10:00:00","position":"Java开发","result":"PASS","interviewerComment":"评语","examPoints":"重点","isPublic":false,"status":"APPROVED","salaryRange":"15K-25K","interviewRound":1,"interviewType":"技术面","hrContact":"HR小王","workLocation":"深圳"}`|code=200, message="录入成功，该记录仅自己可见"||
|TC-STU-015|创建最小记录|P0|学生已登录|创建面试记录|POST|/api/student/my-records|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1}`|code=200, 创建成功||
|TC-STU-016|关联不存在的题目|P1|学生已登录|创建面试记录|POST|/api/student/my-records|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1,"questionIds":\\\\\\\[9999]}`|创建成功或忽略不存在的题目ID||
|TC-STU-017|未登录创建|P0|无Token|创建面试记录|POST|/api/student/my-records|Content-Type: application/json|`{"companyId":1}`|返回401||
|TC-STU-018|创建后其他学生不可见|P0|学生A创建记录|创建面试记录|POST|/api/student/my-records|Authorization: Bearer {学生A Token}<br>Content-Type: application/json|`{"companyId":1}`|学生B登录后看不到该记录||

### 2.5 提交审核

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-019|正常提交审核|P0|学生已登录|提交审核|POST|/api/student/submit-review|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1,"position":"Java开发","interviewDate":"2026-08-08 10:00:00"}`|code=200, message="已提交审核，等待老师审批", status=PENDING||
|TC-STU-020|提交后教师可见|P0|提交审核后|提交审核|POST|/api/student/submit-review|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1}`|教师登录查看待审核列表，能看到该记录||
|TC-STU-021|未登录提交|P0|无Token|提交审核|POST|/api/student/submit-review|Content-Type: application/json|`{"companyId":1}`|返回401||

### 2.6 追加下一轮面试

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-022|正常追加|P0|已有第1轮记录|追加下一轮|POST|/api/student/my-records/{id}/append|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1,"position":"Java开发","interviewType":"HR面"}`|code=200, message含"已追加第2轮面试", interviewRound=2, sessionId继承||
|TC-STU-023|追加不存在的记录|P0|无|追加下一轮|POST|/api/student/my-records/9999/append|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1}`|返回错误||
|TC-STU-024|追加他人记录|P0|学生A登录，记录属于学生B|追加下一轮|POST|/api/student/my-records/{他人记录id}/append|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1}`|返回错误或403||
|TC-STU-025|连续追加多轮|P1|已有第1轮|追加下一轮|POST|/api/student/my-records/{id}/append|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"companyId":1}`|追加第2轮→第3轮，每轮interviewRound递增，sessionId相同||
|TC-STU-026|未登录追加|P0|无Token|追加下一轮|POST|/api/student/my-records/1/append|Content-Type: application/json|`{"companyId":1}`|返回401||

### 2.7 更新面试结果

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-027|正常更新结果|P0|学生有记录|更新面试结果|PUT|/api/student/my-records/{id}/result|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"result":"PASS"}`|code=200, message="结果已更新", data.result="PASS"||
|TC-STU-028|更新为各枚举值|P1|学生有记录|更新面试结果|PUT|/api/student/my-records/{id}/result|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"result":"FAIL"}`|更新成功||
|TC-STU-029|更新不存在的记录|P1|无|更新面试结果|PUT|/api/student/my-records/9999/result|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"result":"PASS"}`|返回错误||
|TC-STU-030|空请求体|P1|学生有记录|更新面试结果|PUT|/api/student/my-records/{id}/result|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{}`|可能报错（result为null）||
|TC-STU-031|未登录|P0|无Token|更新面试结果|PUT|/api/student/my-records/1/result|Content-Type: application/json|`{"result":"PASS"}`|返回401||

### 2.8 收藏功能

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-032|收藏记录|P0|学生已登录，记录未收藏|收藏/取消收藏|POST|/api/student/favorites/{recordId}|Authorization: Bearer {学生Token}|无|code=200, message="收藏成功"||
|TC-STU-033|取消收藏|P0|记录已收藏|收藏/取消收藏|POST|/api/student/favorites/{recordId}|Authorization: Bearer {学生Token}|无|code=200, message="已取消收藏"||
|TC-STU-034|重复收藏（toggle）|P0|记录已收藏|收藏/取消收藏|POST|/api/student/favorites/{recordId}|Authorization: Bearer {学生Token}|无|第一次收藏成功，第二次取消收藏||
|TC-STU-035|获取收藏列表（有收藏）|P0|已收藏多条记录|获取收藏列表|GET|/api/student/favorites|Authorization: Bearer {学生Token}|无|code=200, data为收藏的记录列表||
|TC-STU-036|获取收藏列表（无收藏）|P0|无收藏|获取收藏列表|GET|/api/student/favorites|Authorization: Bearer {学生Token}|无|code=200, data为空数组\[]||
|TC-STU-037|检查已收藏|P0|记录已收藏|检查是否已收藏|GET|/api/student/favorites/check/{recordId}|Authorization: Bearer {学生Token}|无|code=200, data=true||
|TC-STU-038|检查未收藏|P0|记录未收藏|检查是否已收藏|GET|/api/student/favorites/check/{recordId}|Authorization: Bearer {学生Token}|无|code=200, data=false||
|TC-STU-039|未登录收藏|P0|无Token|收藏/取消收藏|POST|/api/student/favorites/1|无|无|返回401||

### 2.9 随机刷题

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-040|默认5题|P0|题库有题目|随机刷题|GET|/api/student/practice|Authorization: Bearer {学生Token}|无|code=200, data长度为5（或<=5如果题库不足）||
|TC-STU-041|指定抽取3题|P1|题库有足够题目|随机刷题|GET|/api/student/practice?count=3|Authorization: Bearer {学生Token}|无|data长度为3||
|TC-STU-042|count=0|P1|题库有题目|随机刷题|GET|/api/student/practice?count=0|Authorization: Bearer {学生Token}|无|data为空数组\[]||
|TC-STU-043|count>题库总数|P1|题库有10题|随机刷题|GET|/api/student/practice?count=20|Authorization: Bearer {学生Token}|无|data长度为10（全部题目）||
|TC-STU-044|未登录|P0|无Token|随机刷题|GET|/api/student/practice|无|无|返回401||

### 2.10 获取分类列表

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-045|正常获取分类|P0|学生已登录，有分类数据|获取分类列表|GET|/api/student/categories|Authorization: Bearer {学生Token}|无|code=200, data为分类数组，只含status="1"的||
|TC-STU-046|无分类数据|P1|无分类数据|获取分类列表|GET|/api/student/categories|Authorization: Bearer {学生Token}|无|code=200, data为空数组\[]||
|TC-STU-047|未登录|P0|无Token|获取分类列表|GET|/api/student/categories|无|无|返回401||

### 2.11 获取题目列表（分页）

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-048|正常分页page=0|P0|学生已登录|获取题目列表|GET|/api/student/questions?page=0\&size=10|Authorization: Bearer {学生Token}|无|code=200, data长度<=10, total为总数||
|TC-STU-049|默认分页参数|P0|学生已登录|获取题目列表|GET|/api/student/questions|Authorization: Bearer {学生Token}|无|默认page=0, size=10||
|TC-STU-050|第二页page=1|P0|题库有>10题|获取题目列表|GET|/api/student/questions?page=1\&size=10|Authorization: Bearer {学生Token}|无|total不变, page=1, data为第2页数据||
|TC-STU-051|超出范围page=100|P1|题库有10题|获取题目列表|GET|/api/student/questions?page=100\&size=10|Authorization: Bearer {学生Token}|无|data为空数组\[]||
|TC-STU-052|未登录|P0|无Token|获取题目列表|GET|/api/student/questions|无|无|返回401||

### 2.12 搜索题目

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-053|关键词搜索|P0|学生已登录|搜索题目|GET|/api/student/questions/search?keyword=Java|Authorization: Bearer {学生Token}|无|返回标题或内容包含"Java"的题目||
|TC-STU-054|难度筛选|P0|学生已登录|搜索题目|GET|/api/student/questions/search?difficulty=EASY|Authorization: Bearer {学生Token}|无|返回难度为EASY的题目||
|TC-STU-055|分类筛选|P0|学生已登录|搜索题目|GET|/api/student/questions/search?category=Java基础|Authorization: Bearer {学生Token}|无|返回分类为"Java基础"的题目||
|TC-STU-056|搜索无结果|P1|学生已登录|搜索题目|GET|/api/student/questions/search?keyword=不存在的关键词xyz|Authorization: Bearer {学生Token}|无|code=200, data为空数组\[], total=0||
|TC-STU-057|keyword+分页|P1|学生已登录|搜索题目|GET|/api/student/questions/search?keyword=Java\&page=0\&size=5|Authorization: Bearer {学生Token}|无|返回分页后的搜索结果||
|TC-STU-058|未登录|P0|无Token|搜索题目|GET|/api/student/questions/search?keyword=Java|无|无|返回401||

### 2.13 新增题目

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-059|正常新增完整题目|P0|学生已登录|新增题目|POST|/api/student/questions|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"Spring Boot原理","content":"简述自动配置","difficulty":"MEDIUM","category":"Java基础","tags":"Spring,自动配置","referenceAnswer":"略"}`|code=200, creatorName=当前学生用户名||
|TC-STU-060|只填title|P0|学生已登录|新增题目|POST|/api/student/questions|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"测试题目"}`|code=200, 创建成功，其他字段为null||
|TC-STU-061|空title|P0|学生已登录|新增题目|POST|/api/student/questions|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":""}`|创建成功（title为空）或返回错误||
|TC-STU-062|无title字段|P1|学生已登录|新增题目|POST|/api/student/questions|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{}`|创建成功或返回错误||
|TC-STU-063|未登录|P0|无Token|新增题目|POST|/api/student/questions|Content-Type: application/json|`{"title":"test"}`|返回401||
|TC-STU-064|创建后可在列表看到|P0|刚创建题目|新增题目→获取列表|POST→GET|/api/student/questions → /api/student/questions|Authorization: Bearer {学生Token}|新增后查询列表|列表中包含刚创建的题目||

### 2.14 编辑题目

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-STU-065|编辑自己的题目|P0|学生创建了题目|编辑题目|PUT|/api/student/questions/{自己创建的题目id}|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"修改后的标题"}`|code=200, 更新成功||
|TC-STU-066|编辑他人题目|P0|题目由他人创建|编辑题目|PUT|/api/student/questions/{他人题目id}|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"尝试修改"}`|code=403, message="只能编辑自己创建的题目"||
|TC-STU-067|编辑教师创建的题目|P0|题目由教师创建|编辑题目|PUT|/api/student/questions/{教师创建题目id}|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"尝试修改"}`|code=403||
|TC-STU-068|编辑不存在的题目|P1|无|编辑题目|PUT|/api/student/questions/9999|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"title":"test"}`|返回错误||
|TC-STU-069|未登录|P0|无Token|编辑题目|PUT|/api/student/questions/1|Content-Type: application/json|`{"title":"test"}`|返回401||

\---

## 三、教师端

### 3.1 用户管理 - 获取用户列表

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-001|正常分页获取|P0|教师已登录|获取用户列表|GET|/api/teacher/users?page=0\&size=10|Authorization: Bearer {教师Token}|无|code=200, data长度<=10, total>=1, 不含password字段||
|TC-TCH-002|按班级筛选|P1|有班级数据|获取用户列表|GET|/api/teacher/users?classId=1|Authorization: Bearer {教师Token}|无|返回该班级的用户||
|TC-TCH-003|按姓名模糊搜索|P1|有用户|获取用户列表|GET|/api/teacher/users ?name=张三|Authorization: Bearer {教师Token}|无|返回姓名包含"张三"的用户||
|TC-TCH-004|按角色筛选|P1|有多种角色|获取用户列表|GET|/api/teacher/users?role=STUDENT|Authorization: Bearer {教师Token}|无|只返回STUDENT角色用户||
|TC-TCH-005|组合筛选|P1|有数据|获取用户列表|GET|/api/teacher/users?classId=1\&role=STUDENT\&name=张|Authorization: Bearer {教师Token}|无|返回同时满足条件的用户||
|TC-TCH-006|筛选无结果|P1|有数据|获取用户列表|GET|/api/teacher/users?name=不存在的人|Authorization: Bearer {教师Token}|无|data为空数组\[], total=0||
|TC-TCH-007|学生角色访问|P0|学生Token|获取用户列表|GET|/api/teacher/users|Authorization: Bearer {学生Token}|无|返回403||
|TC-TCH-008|未登录|P0|无Token|获取用户列表|GET|/api/teacher/users|无|无|返回401||

### 3.2 用户管理 - 创建用户

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-009|创建学生|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"stu\\\\\\\_new","password":"123456","name":"新生","role":"STUDENT","classId":1}`|code=200, message="用户创建成功"||
|TC-TCH-010|创建教师|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"tch\\\\\\\_new","password":"123456","name":"新老师","role":"TEACHER"}`|code=200, role="TEACHER"||
|TC-TCH-011|重复用户名|P0|用户名已存在|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"admin","password":"123","name":"重复","role":"STUDENT"}`|返回错误，提示用户名已存在||
|TC-TCH-012|缺username|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"password":"123","name":"test","role":"STUDENT"}`|返回参数校验错误||
|TC-TCH-013|缺password|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"test","name":"test","role":"STUDENT"}`|返回参数校验错误||
|TC-TCH-014|缺name|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"test","password":"123","role":"STUDENT"}`|返回参数校验错误||
|TC-TCH-015|缺role|P0|教师已登录|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"test","password":"123","name":"test"}`|返回参数校验错误||
|TC-TCH-016|创建后密码加密|P0|刚创建用户|创建用户|POST|/api/teacher/users|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"pwd\\\\\\\_test","password":"123456","name":"密码测试","role":"STUDENT"}`|查数据库password字段以$2a$开头（BCrypt加密）||
|TC-TCH-017|创建后可用新账号登录|P0|刚创建用户|创建用户→登录|POST→POST|/api/teacher/users → /api/auth/login|Authorization: Bearer {教师Token}|用新账号登录|登录成功||
|TC-TCH-018|学生角色访问|P0|学生Token|创建用户|POST|/api/teacher/users|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"username":"test","password":"123","name":"test","role":"STUDENT"}`|返回403||
|TC-TCH-019|未登录|P0|无Token|创建用户|POST|/api/teacher/users|Content-Type: application/json|`{"username":"test","password":"123","name":"test","role":"STUDENT"}`|返回401||

### 3.3 用户管理 - 编辑用户

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-020|正常编辑|P0|教师已登录，用户存在|编辑用户|PUT|/api/teacher/users/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"user1","password":"123","name":"新名字","role":"STUDENT"}`|code=200, message="用户更新成功"||
|TC-TCH-021|编辑不存在的用户|P0|无|编辑用户|PUT|/api/teacher/users/9999|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"test","password":"123","name":"test","role":"STUDENT"}`|返回错误||
|TC-TCH-022|修改为已存在的用户名|P1|有其他用户|编辑用户|PUT|/api/teacher/users/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"username":"admin","password":"123","name":"test","role":"STUDENT"}`|返回错误（唯一约束）||
|TC-TCH-023|学生角色访问|P0|学生Token|编辑用户|PUT|/api/teacher/users/1|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`{"name":"test"}`|返回403||
|TC-TCH-024|未登录|P0|无Token|编辑用户|PUT|/api/teacher/users/1|Content-Type: application/json|`{"name":"test"}`|返回401||

### 3.4 用户管理 - 删除用户

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-025|正常删除|P0|教师已登录|删除用户|DELETE|/api/teacher/users/{id}|Authorization: Bearer {教师Token}|无|code=200, message="用户删除成功"||
|TC-TCH-026|删除不存在的用户|P0|无|删除用户|DELETE|/api/teacher/users/9999|Authorization: Bearer {教师Token}|无|返回错误||
|TC-TCH-027|删除后不可见|P0|刚删除用户|删除→查询|DELETE→GET|/api/teacher/users/{id} → /api/teacher/users|Authorization: Bearer {教师Token}|无|列表中不再包含该用户||
|TC-TCH-028|删除后无法登录|P0|刚删除用户|删除→登录|DELETE→POST|/api/teacher/users/{id} → /api/auth/login|Authorization: Bearer {教师Token}|用被删除的账号登录|登录失败||
|TC-TCH-029|学生角色访问|P0|学生Token|删除用户|DELETE|/api/teacher/users/1|Authorization: Bearer {学生Token}|无|返回403||
|TC-TCH-030|未登录|P0|无Token|删除用户|DELETE|/api/teacher/users/1|无|无|返回401||

### 3.5 用户管理 - 冻结/解冻

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-031|冻结用户|P0|用户frozen=false|冻结用户|PUT|/api/teacher/users/{id}/freeze|Authorization: Bearer {教师Token}|无|code=200, message="用户已冻结"||
|TC-TCH-032|冻结后不可登录|P0|用户被冻结|冻结→登录|PUT→POST|/api/teacher/users/{id}/freeze → /api/auth/login|Authorization: Bearer {教师Token}|用被冻结账号登录|登录失败，提示账号已冻结||
|TC-TCH-033|解冻用户|P0|用户frozen=true|解冻用户|PUT|/api/teacher/users/{id}/unfreeze|Authorization: Bearer {教师Token}|无|code=200, message="用户已解冻"||
|TC-TCH-034|解冻后可登录|P0|刚解冻用户|解冻→登录|PUT→POST|/api/teacher/users/{id}/unfreeze → /api/auth/login|Authorization: Bearer {教师Token}|用解冻账号登录|登录成功||
|TC-TCH-035|冻结不存在的用户|P1|无|冻结用户|PUT|/api/teacher/users/9999/freeze|Authorization: Bearer {教师Token}|无|返回错误||
|TC-TCH-036|学生角色访问|P0|学生Token|冻结用户|PUT|/api/teacher/users/1/freeze|Authorization: Bearer {学生Token}|无|返回403||

### 3.6 用户管理 - 批量删除/获取所有学生

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-037|批量删除|P0|教师已登录|批量删除用户|DELETE|/api/teacher/users/batch|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`\\\\\\\[10, 11, 12]`|code=200, message="成功删除 3 个用户"||
|TC-TCH-038|批量删除空数组|P1|教师已登录|批量删除用户|DELETE|/api/teacher/users/batch|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`\\\\\\\[]`|message="成功删除 0 个用户"||
|TC-TCH-039|获取所有学生|P0|教师已登录|获取所有学生|GET|/api/teacher/users/students|Authorization: Bearer {教师Token}|无|code=200, data中所有用户role=STUDENT||
|TC-TCH-040|学生角色访问批量删除|P0|学生Token|批量删除用户|DELETE|/api/teacher/users/batch|Authorization: Bearer {学生Token}<br>Content-Type: application/json|`\\\\\\\[1]`|返回403||

### 3.7 班级管理

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-041|获取班级列表|P0|教师已登录|获取班级列表|GET|/api/teacher/classes?page=0\&size=10|Authorization: Bearer {教师Token}|无|code=200, data包含班级列表||
|TC-TCH-042|创建班级|P0|教师已登录|创建班级|POST|/api/teacher/classes|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"Python一班","description":"测试班"}`|code=200, 创建成功||
|TC-TCH-043|创建班级空name|P0|教师已登录|创建班级|POST|/api/teacher/classes|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":""}`|创建成功或返回错误||
|TC-TCH-044|编辑班级|P0|教师已登录，班级存在|编辑班级|PUT|/api/teacher/classes/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"修改后的班级名"}`|code=200, 更新成功||
|TC-TCH-045|编辑不存在的班级|P0|无|编辑班级|PUT|/api/teacher/classes/9999|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"test"}`|返回错误||
|TC-TCH-046|删除班级|P0|教师已登录|删除班级|DELETE|/api/teacher/classes/{id}|Authorization: Bearer {教师Token}|无|code=200, message="删除成功"||
|TC-TCH-047|删除不存在的班级|P0|无|删除班级|DELETE|/api/teacher/classes/9999|Authorization: Bearer {教师Token}|无|返回错误||
|TC-TCH-048|获取所有班级|P0|教师已登录|获取所有班级|GET|/api/teacher/classes/all|Authorization: Bearer {教师Token}|无|code=200, data为全部班级||
|TC-TCH-049|学生角色访问班级|P0|学生Token|获取班级列表|GET|/api/teacher/classes|Authorization: Bearer {学生Token}|无|返回403||

### 3.8 公司管理

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-050|获取公司列表|P0|教师已登录|获取公司列表|GET|/api/teacher/companies?page=0\&size=10|Authorization: Bearer {教师Token}|无|code=200, data包含公司列表||
|TC-TCH-051|创建公司|P0|教师已登录|创建公司|POST|/api/teacher/companies|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"新公司","industry":"互联网","description":"描述"}`|code=200, 创建成功||
|TC-TCH-052|创建公司只填name|P0|教师已登录|创建公司|POST|/api/teacher/companies|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"新公司"}`|code=200, 创建成功||
|TC-TCH-053|创建公司空name|P0|教师已登录|创建公司|POST|/api/teacher/companies|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":""}`|创建成功或返回错误||
|TC-TCH-054|编辑公司|P0|教师已登录|编辑公司|PUT|/api/teacher/companies/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"name":"修改后公司名"}`|code=200, 更新成功||
|TC-TCH-055|删除公司|P0|教师已登录|删除公司|DELETE|/api/teacher/companies/{id}|Authorization: Bearer {教师Token}|无|code=200, message="删除成功"||
|TC-TCH-056|搜索公司|P0|教师已登录|搜索公司|GET|/api/teacher/companies/search?keyword=腾讯|Authorization: Bearer {教师Token}|无|返回包含"腾讯"的公司||
|TC-TCH-057|搜索无结果|P1|教师已登录|搜索公司|GET|/api/teacher/companies/search?keyword=不存在|Authorization: Bearer {教师Token}|无|data为空数组\[]||
|TC-TCH-058|学生角色访问公司|P0|学生Token|获取公司列表|GET|/api/teacher/companies|Authorization: Bearer {学生Token}|无|返回403||

### 3.9 题库管理

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-059|获取题目列表|P0|教师已登录|获取题目列表|GET|/api/teacher/questions?page=0\&size=10|Authorization: Bearer {教师Token}|无|code=200, data长度<=10, total为总数||
|TC-TCH-060|创建题目|P0|教师已登录|创建题目|POST|/api/teacher/questions|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"title":"教师创建题目","content":"内容","difficulty":"MEDIUM","category":"Java基础","tags":"Java","referenceAnswer":"答案"}`|code=200, creatorName为教师用户名||
|TC-TCH-061|编辑题目|P0|教师已登录|编辑题目|PUT|/api/teacher/questions/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"title":"修改后的标题"}`|code=200, 更新成功（教师无权限限制）||
|TC-TCH-062|编辑学生创建的题目|P0|题目由学生创建|编辑题目|PUT|/api/teacher/questions/{学生题目id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"title":"教师修改"}`|code=200, 更新成功||
|TC-TCH-063|删除题目|P0|教师已登录|删除题目|DELETE|/api/teacher/questions/{id}|Authorization: Bearer {教师Token}|无|code=200, message="删除成功"||
|TC-TCH-064|搜索题目（关键词）|P0|教师已登录|搜索题目|GET|/api/teacher/questions/search?keyword=Java|Authorization: Bearer {教师Token}|无|返回匹配的题目||
|TC-TCH-065|搜索题目（难度）|P0|教师已登录|搜索题目|GET|/api/teacher/questions/search?difficulty=HARD|Authorization: Bearer {教师Token}|无|只返回HARD难度题目||
|TC-TCH-066|搜索题目（分类+分页）|P1|教师已登录|搜索题目|GET|/api/teacher/questions/search?category=Java基础\&page=0\&size=5|Authorization: Bearer {教师Token}|无|返回分页后的分类搜索结果||
|TC-TCH-067|批量删除题目|P0|教师已登录|批量删除题目|DELETE|/api/teacher/questions/batch|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`\\\\\\\[1,2,3]`|code=200, message="成功删除 3 道题目"||
|TC-TCH-068|获取所有题目|P0|教师已登录|获取所有题目|GET|/api/teacher/questions/all|Authorization: Bearer {教师Token}|无|code=200, data为全部题目||
|TC-TCH-069|学生角色访问题库|P0|学生Token|获取题目列表|GET|/api/teacher/questions|Authorization: Bearer {学生Token}|无|返回403||

### 3.10 面试记录管理

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-070|获取所有记录（分页）|P0|教师已登录|获取所有记录|GET|/api/teacher/records?page=0\&size=10|Authorization: Bearer {教师Token}|无|code=200, data包含记录列表||
|TC-TCH-071|日期范围筛选|P1|有记录|获取所有记录|GET|/api/teacher/records?startDate=2026-08-01\&endDate=2026-08-08|Authorization: Bearer {教师Token}|无|返回该日期范围内的记录||
|TC-TCH-072|按学生ID筛选|P1|有记录|获取所有记录|GET|/api/teacher/records?studentId=10|Authorization: Bearer {教师Token}|无|只返回该学生的记录||
|TC-TCH-073|按公司ID筛选|P1|有记录|获取所有记录|GET|/api/teacher/records?companyId=1|Authorization: Bearer {教师Token}|无|只返回该公司的记录||
|TC-TCH-074|按结果筛选|P1|有记录|获取所有记录|GET|/api/teacher/records?result=PASS|Authorization: Bearer {教师Token}|无|只返回PASS的记录||
|TC-TCH-075|多条件组合|P1|有记录|获取所有记录|GET|/api/teacher/records?startDate=2026-01-01\&companyId=1\&result=PASS|Authorization: Bearer {教师Token}|无|返回满足所有条件的记录||
|TC-TCH-076|创建面试记录|P0|教师已登录|创建面试记录|POST|/api/teacher/records|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"studentId":10,"companyId":1,"position":"Java开发","interviewDate":"2026-08-08 10:00:00"}`|code=200, 创建成功||
|TC-TCH-077|编辑面试记录|P0|教师已登录|编辑面试记录|PUT|/api/teacher/records/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"position":"修改后的职位"}`|code=200, 更新成功||
|TC-TCH-078|删除面试记录|P0|教师已登录|删除面试记录|DELETE|/api/teacher/records/{id}|Authorization: Bearer {教师Token}|无|code=200, message="删除成功"||
|TC-TCH-079|批量删除记录|P0|教师已登录|批量删除记录|DELETE|/api/teacher/records/batch|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`\\\\\\\[1,2,3]`|code=200, message="成功删除 3 条记录"||
|TC-TCH-080|获取待审核记录|P0|教师已登录，有PENDING记录|获取待审核记录|GET|/api/teacher/records/pending|Authorization: Bearer {教师Token}|无|code=200, data中所有记录status=PENDING||
|TC-TCH-081|无待审核记录|P0|无PENDING记录|获取待审核记录|GET|/api/teacher/records/pending|Authorization: Bearer {教师Token}|无|code=200, data为空数组\[]||
|TC-TCH-082|评价面试记录|P0|教师已登录|评价面试记录|PUT|/api/teacher/records/{id}/evaluate|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"teacherComment":"表现优秀","result":"PASS"}`|code=200, message="评价成功"||
|TC-TCH-083|审核通过|P0|教师已登录，记录PENDING|审核通过|PUT|/api/teacher/records/{id}/approve|Authorization: Bearer {教师Token}|无|code=200, status变为APPROVED||
|TC-TCH-084|审核驳回|P0|教师已登录，记录PENDING|审核驳回|PUT|/api/teacher/records/{id}/reject|Authorization: Bearer {教师Token}|无|code=200, status变为REJECTED||
|TC-TCH-085|按公司查询记录|P0|教师已登录|按公司查询记录|GET|/api/teacher/records/company/1|Authorization: Bearer {教师Token}|无|code=200, data中所有记录company.id=1||
|TC-TCH-086|学生角色访问记录|P0|学生Token|获取所有记录|GET|/api/teacher/records|Authorization: Bearer {学生Token}|无|返回403||

### 3.11 导出功能

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-087|导出公司面试题|P0|教师已登录，公司有记录|导出公司面试题|GET|/api/teacher/export/company/1|Authorization: Bearer {教师Token}|无|返回文件，Content-Type=text/markdown，文件名 interview\_questions.md||
|TC-TCH-088|导出全部面试题|P0|教师已登录|导出全部面试题|GET|/api/teacher/export/all|Authorization: Bearer {教师Token}|无|返回文件，文件名 all\_interview\_questions.md||
|TC-TCH-089|导出公司无记录|P1|公司无记录|导出公司面试题|GET|/api/teacher/export/company/9999|Authorization: Bearer {教师Token}|无|返回空文件或报错||
|TC-TCH-090|学生角色访问导出|P0|学生Token|导出全部面试题|GET|/api/teacher/export/all|Authorization: Bearer {学生Token}|无|返回403||

### 3.12 数据统计

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-091|正常获取统计|P0|教师已登录|数据统计|GET|/api/teacher/statistics|Authorization: Bearer {教师Token}|无|code=200, data包含totalRecords/totalUsers/totalQuestions/passRate等所有统计字段||
|TC-TCH-092|字段完整性|P0|教师已登录|数据统计|GET|/api/teacher/statistics|Authorization: Bearer {教师Token}|无|包含totalRecords/totalUsers/totalQuestions/totalCompanies/passCount/failCount/notInterviewedCount/pendingResultCount/pendingReviewCount/approvedCount/passRate/difficultyStats/companyStats/recentRecords||
|TC-TCH-093|学生角色访问|P0|学生Token|数据统计|GET|/api/teacher/statistics|Authorization: Bearer {学生Token}|无|返回403||

### 3.13 批量导入

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-094|下载题库导入模板|P0|教师已登录|下载题库模板|GET|/api/teacher/import/template|Authorization: Bearer {教师Token}|无|返回xlsx文件，文件名含"题库导入模板"||
|TC-TCH-095|导入题库|P0|教师已登录，准备xlsx文件|导入题库|POST|/api/teacher/import/questions|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=题库文件.xlsx|code=200, message含导入题目数量||
|TC-TCH-096|导入空文件|P1|教师已登录|导入题库|POST|/api/teacher/import/questions|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=空文件（只有表头）.xlsx|导入0道题目||
|TC-TCH-097|不传文件|P1|教师已登录|导入题库|POST|/api/teacher/import/questions|Authorization: Bearer {教师Token}|无file参数|返回错误||
|TC-TCH-098|下载用户导入模板|P0|教师已登录|下载用户模板|GET|/api/teacher/import/users-template|Authorization: Bearer {教师Token}|无|返回xlsx文件，文件名含"用户导入模板"||
|TC-TCH-099|导入用户|P0|教师已登录，准备xlsx文件|导入用户|POST|/api/teacher/import/users|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=用户文件.xlsx|code=200, message含导入用户数量||
|TC-TCH-100|导入重复用户名|P0|文件中有已存在的用户名|导入用户|POST|/api/teacher/import/users|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=含重复用户名的文件.xlsx|已存在的用户名被跳过||
|TC-TCH-101|导入缺少班级ID|P1|文件中某行无班级ID|导入用户|POST|/api/teacher/import/users|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=含缺少班级ID的文件.xlsx|该行跳过，warnings包含警告||
|TC-TCH-102|导入后密码加密|P0|导入成功|导入用户|POST|/api/teacher/import/users|Authorization: Bearer {教师Token}<br>Content-Type: multipart/form-data|form-data: file=用户文件.xlsx|查数据库password以BCrypt加密存储||
|TC-TCH-103|学生角色访问导入|P0|学生Token|导入题库|POST|/api/teacher/import/questions|Authorization: Bearer {学生Token}|form-data: file=xxx.xlsx|返回403||

### 3.14 操作日志

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-TCH-104|正常获取日志|P0|教师已登录|获取操作日志|GET|/api/teacher/audit-logs|Authorization: Bearer {教师Token}|无|code=200, data为日志列表，含userId/username/action/target/createdAt||
|TC-TCH-105|评价操作产生日志|P0|教师执行评价|评价→查日志|PUT→GET|/api/teacher/records/{id}/evaluate → /api/teacher/audit-logs|Authorization: Bearer {教师Token}|评价后查看日志|日志中有"老师评价"记录||
|TC-TCH-106|审核操作产生日志|P0|教师执行审核|审核→查日志|PUT→GET|/api/teacher/records/{id}/approve → /api/teacher/audit-logs|Authorization: Bearer {教师Token}|审核后查看日志|日志中有"审核通过"记录||
|TC-TCH-107|学生角色访问|P0|学生Token|获取操作日志|GET|/api/teacher/audit-logs|Authorization: Bearer {学生Token}|无|返回403||

\---

## 四、个人信息

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-USR-001|更新姓名|P0|已登录|更新个人资料|POST|/api/user/profile|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"name":"新名字"}`|code=200, message="个人信息更新成功", name="新名字"||
|TC-USR-002|更新邮箱|P0|已登录|更新个人资料|POST|/api/user/profile|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"email":"new@email.com"}`|code=200, email更新||
|TC-USR-003|更新电话|P0|已登录|更新个人资料|POST|/api/user/profile|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"phone":"13900139000"}`|code=200, phone更新||
|TC-USR-004|同时更新多字段|P0|已登录|更新个人资料|POST|/api/user/profile|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"name":"新","email":"e@e.com","phone":"123"}`|所有字段更新成功||
|TC-USR-005|空请求体|P1|已登录|更新个人资料|POST|/api/user/profile|Authorization: Bearer {Token}<br>Content-Type: application/json|`{}`|code=200, 所有字段不变||
|TC-USR-006|未登录|P0|无Token|更新个人资料|POST|/api/user/profile|Content-Type: application/json|`{"name":"test"}`|返回401||
|TC-USR-007|正常修改密码|P0|已登录|修改密码|POST|/api/user/change-password|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"oldPassword":"123456","newPassword":"654321"}`|code=200, message="密码修改成功"||
|TC-USR-008|旧密码错误|P0|已登录|修改密码|POST|/api/user/change-password|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"oldPassword":"wrong","newPassword":"654321"}`|返回错误，message="旧密码不正确"||
|TC-USR-009|缺oldPassword|P0|已登录|修改密码|POST|/api/user/change-password|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"newPassword":"654321"}`|返回错误||
|TC-USR-010|缺newPassword|P0|已登录|修改密码|POST|/api/user/change-password|Authorization: Bearer {Token}<br>Content-Type: application/json|`{"oldPassword":"123456"}`|返回错误||
|TC-USR-011|修改后用新密码登录|P0|密码修改成功|修改密码→登录|POST→POST|/api/user/change-password → /api/auth/login|Authorization: Bearer {Token}|用新密码登录|登录成功||
|TC-USR-012|修改后用旧密码登录|P0|密码修改成功|修改密码→登录|POST→POST|/api/user/change-password → /api/auth/login|Authorization: Bearer {Token}|用旧密码登录|登录失败||
|TC-USR-013|未登录修改密码|P0|无Token|修改密码|POST|/api/user/change-password|Content-Type: application/json|`{"oldPassword":"123","newPassword":"456"}`|返回401||

\---

## 五、通知模块

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-NTF-001|获取通知列表（有通知）|P0|已登录，有通知|获取通知列表|GET|/api/notifications|Authorization: Bearer {Token}|无|code=200, data为通知列表，含id/userId/title/content/type/isRead/createdAt||
|TC-NTF-002|获取通知列表（无通知）|P0|无通知|获取通知列表|GET|/api/notifications|Authorization: Bearer {Token}|无|code=200, data为空数组\[], total=0||
|TC-NTF-003|分页获取通知|P1|有>20条通知|获取通知列表|GET|/api/notifications?page=0\&size=20|Authorization: Bearer {Token}|无|返回分页数据，默认size=20||
|TC-NTF-004|只返回自己的通知|P0|学生A和学生B都有通知|获取通知列表|GET|/api/notifications|Authorization: Bearer {学生A Token}|无|只返回userId=学生A的通知||
|TC-NTF-005|未登录|P0|无Token|获取通知列表|GET|/api/notifications|无|无|返回401||
|TC-NTF-006|标记单条已读|P0|有未读通知|标记已读|PUT|/api/notifications/{id}/read|Authorization: Bearer {Token}|无|code=200, message="已读"||
|TC-NTF-007|标记已读通知|P1|通知已读|标记已读|PUT|/api/notifications/{id}/read|Authorization: Bearer {Token}|无|成功（重复标记不报错）||
|TC-NTF-008|标记不存在的通知|P1|无|标记已读|PUT|/api/notifications/9999/read|Authorization: Bearer {Token}|无|返回错误||
|TC-NTF-009|全部标记已读|P0|有未读通知|全部标记已读|PUT|/api/notifications/read-all|Authorization: Bearer {Token}|无|code=200, message="全部已读"||
|TC-NTF-010|无通知时全部标记|P1|无通知|全部标记已读|PUT|/api/notifications/read-all|Authorization: Bearer {Token}|无|成功，不报错||
|TC-NTF-011|全部标记后未读数为0|P0|标记全部已读|全部标记→查未读数|PUT→GET|/api/notifications/read-all → /api/notifications/unread-count|Authorization: Bearer {Token}|无|unread-count=0||
|TC-NTF-012|获取未读数量（有未读）|P0|有3条未读|获取未读数量|GET|/api/notifications/unread-count|Authorization: Bearer {Token}|无|code=200, data=3||
|TC-NTF-013|获取未读数量（无未读）|P0|全部已读|获取未读数量|GET|/api/notifications/unread-count|Authorization: Bearer {Token}|无|code=200, data=0||
|TC-NTF-014|标记后数量变化|P0|有未读|标记一条→查数量→标记全部→查数量|PUT→GET|/api/notifications/{id}/read → /api/notifications/unread-count|Authorization: Bearer {Token}|无|数量逐步减少到0||
|TC-NTF-015|未登录获取未读数|P0|无Token|获取未读数量|GET|/api/notifications/unread-count|无|无|返回401||

\---

## 六、字典管理

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-DCT-001|获取字典类型列表|P0|教师已登录|获取字典类型|GET|/api/teacher/dict/types|Authorization: Bearer {教师Token}|无|code=200, data为类型列表||
|TC-DCT-002|创建字典类型|P0|教师已登录|创建字典类型|POST|/api/teacher/dict/types|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"typeName":"面试结果","typeCode":"interview\\\\\\\_result","description":"结果选项"}`|code=200, message="字典类型创建成功"||
|TC-DCT-003|重复typeCode|P0|typeCode已存在|创建字典类型|POST|/api/teacher/dict/types|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"typeName":"test","typeCode":"question\\\\\\\_category"}`|返回错误（唯一约束）||
|TC-DCT-004|缺typeName|P0|教师已登录|创建字典类型|POST|/api/teacher/dict/types|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"typeCode":"test"}`|返回错误||
|TC-DCT-005|编辑字典类型|P0|教师已登录|编辑字典类型|PUT|/api/teacher/dict/types/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"typeName":"修改名称","typeCode":"test","description":"新描述"}`|code=200, message="字典类型更新成功"||
|TC-DCT-006|删除字典类型|P0|教师已登录|删除字典类型|DELETE|/api/teacher/dict/types/{id}|Authorization: Bearer {教师Token}|无|code=200, message="字典类型删除成功"||
|TC-DCT-007|获取字典数据|P0|教师已登录|获取字典数据|GET|/api/teacher/dict/data/question\_category|Authorization: Bearer {教师Token}|无|code=200, data为数据列表||
|TC-DCT-008|创建字典数据|P0|教师已登录|创建字典数据|POST|/api/teacher/dict/data|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"dictTypeCode":"question\\\\\\\_category","label":"前端开发","value":"FRONTEND","sortOrder":1,"status":"1"}`|code=200, message="字典数据创建成功"||
|TC-DCT-009|缺dictTypeCode|P0|教师已登录|创建字典数据|POST|/api/teacher/dict/data|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"label":"test","value":"test"}`|返回错误||
|TC-DCT-010|缺label|P0|教师已登录|创建字典数据|POST|/api/teacher/dict/data|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"dictTypeCode":"qc","value":"test"}`|返回错误||
|TC-DCT-011|编辑字典数据|P0|教师已登录|编辑字典数据|PUT|/api/teacher/dict/data/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"dictTypeCode":"question\\\\\\\_category","label":"修改标签","value":"MODIFIED"}`|code=200, message="字典数据更新成功"||
|TC-DCT-012|切换启用/禁用|P1|数据存在|编辑字典数据|PUT|/api/teacher/dict/data/{id}|Authorization: Bearer {教师Token}<br>Content-Type: application/json|`{"dictTypeCode":"question\\\\\\\_category","label":"test","value":"test","status":"0"}`|更新成功，下拉列表不再显示||
|TC-DCT-013|删除字典数据|P0|教师已登录|删除字典数据|DELETE|/api/teacher/dict/data/{id}|Authorization: Bearer {教师Token}|无|code=200, message="字典数据删除成功"||
|TC-DCT-014|获取题库分类下拉|P0|教师已登录|获取题库分类|GET|/api/teacher/dict/categories|Authorization: Bearer {教师Token}|无|code=200, 只返回status="1"的分类||
|TC-DCT-015|学生角色访问字典|P0|学生Token|获取字典类型|GET|/api/teacher/dict/types|Authorization: Bearer {学生Token}|无|返回403||

\---

## 七、公共接口

|编号|用例名称|优先级|前置条件|接口名称|请求方法|URL|请求头|请求数据|预期结果|实际结果|
|-|-|-|-|-|-|-|-|-|-|-|
|TC-PUB-001|获取所有公司|P0|有公司数据|获取所有公司|GET|/api/common/companies|无|无|code=200, data为公司列表||
|TC-PUB-002|无公司时获取|P1|无公司|获取所有公司|GET|/api/common/companies|无|无|code=200, data为空数组\[]||
|TC-PUB-003|无需认证|P0|无Token|获取所有公司|GET|/api/common/companies|无|无|正常返回，不需要认证||
|TC-PUB-004|搜索公司|P0|有公司|搜索公司|GET|/api/common/companies/search?keyword=腾讯|无|无|code=200, 返回匹配的公司||
|TC-PUB-005|搜索无结果|P1|有公司|搜索公司|GET|/api/common/companies/search?keyword=不存在|无|无|code=200, data为空数组\[]||
|TC-PUB-006|获取公司详情|P0|公司存在|获取公司详情|GET|/api/common/companies/1|无|无|code=200, data为完整公司信息||
|TC-PUB-007|不存在的公司|P0|无|获取公司详情|GET|/api/common/companies/9999|无|无|返回错误或空||
|TC-PUB-008|获取所有题目|P0|有题目|获取所有题目|GET|/api/common/questions|无|无|code=200, data为全部题目||
|TC-PUB-009|获取题目详情|P0|题目存在|获取题目详情|GET|/api/common/questions/1|无|无|code=200, data为完整题目信息||
|TC-PUB-010|搜索题目|P0|有题目|搜索题目|GET|/api/common/questions/search?keyword=Java|无|无|code=200, 返回匹配结果||
|TC-PUB-011|获取公开记录|P0|有公开记录|获取公开记录|GET|/api/common/records/public|无|无|code=200, data为公开记录，只含isPublic=true且status=APPROVED||
|TC-PUB-012|无公开记录|P1|无公开记录|获取公开记录|GET|/api/common/records/public|无|无|code=200, data为空数组\[]||
|TC-PUB-013|按公司获取公开记录|P0|公司有公开记录|按公司获取公开记录|GET|/api/common/records/company/1|无|无|code=200, data为该公司公开记录||
|TC-PUB-014|获取记录详情|P0|记录存在|获取记录详情|GET|/api/common/records/1|无|无|code=200, data为完整记录||
|TC-PUB-015|不存在的记录|P0|无|获取记录详情|GET|/api/common/records/9999|无|无|返回错误||

\---

## 八、测试用例汇总

### 8.1 按模块统计

|模块|用例范围|用例数|P0|P1|P2|
|-|-|-|-|-|-|
|认证模块|TC-AUTH-001 \~ TC-AUTH-020|20|13|7|0|
|学生端|TC-STU-001 \~ TC-STU-069|69|52|14|3|
|教师端|TC-TCH-001 \~ TC-TCH-107|107|82|22|3|
|个人信息|TC-USR-001 \~ TC-USR-013|13|10|3|0|
|通知模块|TC-NTF-001 \~ TC-NTF-015|15|10|5|0|
|字典管理|TC-DCT-001 \~ TC-DCT-015|15|12|3|0|
|公共接口|TC-PUB-001 \~ TC-PUB-015|15|11|4|0|
|**合计**||**254**|**190**|**58**|**6**|

### 8.2 按测试类型统计

|类型|用例数|说明|
|-|-|-|
|正常场景|95|正常输入、正常流程|
|异常输入|55|空值、无效格式、缺失字段|
|权限验证|62|未登录(401)、角色越权(403)|
|数据完整性|25|字段完整性、数据一致性|
|流程串联|17|多步骤端到端流程|

### 8.3 测试执行建议

1. 先执行 P0 用例，确保核心功能正常
2. 再执行 P1/P2 用例，覆盖边界场景
3. 每个用例的"实际结果"列由测试人员执行后填写
4. 建议使用 Postman Collection Runner 批量执行
5. 权限测试重点关注：401（未登录）、403（越权访问）

\---

> \\\\\\\*\\\\\\\*文档结束\\\\\\\*\\\\\\\* - 共 254 条测试用例，覆盖 85 个接口，请按编号顺序执行测试。

