# 权限测试矩阵

| token 状态        | 访问受保护接口                   | 结果                                                         | 预期                                                   | 用例                                               |
| ----------------- | -------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------ | -------------------------------------------------- |
| 没带              | 学生接口：/api/student/questions | ![](assets/image-20261112234340034-1794498227514-1.png)      | code=401，message=“未登录，请登录”，data=null          | TC-SEC-001_无 token 访问受保护接口                 |
| 乱写              | 学生接口：/api/student/questions | ![image-20261112234442189](assets/image-20261112234442189-1794498284273-3.png) | code=401，message=“token无效，请重新登录”，data=null   | TC-SEC-002_错误token访问受保护接口                 |
| 过期              | 学生接口：/api/student/questions | ![image-20261112234535590](assets/image-20261112234535590-1794498338251-5.png) | code=401，message=“token已过期，请重新登录”，data=null | TC-SEC-003_使用过期token访问受保护接口             |
| 伪造 role=TEACHER | 教师接口：/api/teacher/users     | ![image-20261112234850914](assets/image-20261112234850914-1794498534091-7.png) | code=401，message=“token无效，请重新登录”，data=null   | TC-SEC-004_改成教师身份的学生token访问教师专属接口 |
| 真学生            | 教师接口：/api/teacher/users     | ![image-20261112234940379](assets/image-20261112234940379-1794498582904-9.png) | code=403，message=“权限不足，仅教师可查看”，data=null  | TC-SEC-005_学生token访问教师的用户中心             |
| 真老师            | 学生接口：/api/student/questions | ![image-20261114000505216](assets/image-20261114000505216-1794585910430-1.png) | code=403，message=“权限不足，仅学生可查看”，data=null  | TC-SEC-006_教师访问学生受保护接口                  |
| 伪造 role=STUDENT | 学生接口：/api/student/questions | ![image-20261114000623435](assets/image-20261114000623435-1794585985521-3.png) | code=401，message=“token无效，请重新登录”，data=null   | TC-SEC-007_教师伪造学生token访问学生受保护接口     |

> 伪造 token 那行，“预期结果”和“实际结果”为什么不一致？（它就是缺陷的定义）
>
> 因为预期的话，使用伪造的token应该被拦截，而不是成功访问并返回数据

>这个矩阵还缺什么行？（提示：教师 token 访问学生接口算不算越权？vertical 方向还没测）
>
>还缺真教师token访问学生接口和伪造role=STUDENT