import pytest
import requests


BASE_URL = "http://127.0.0.1:8080"

# 抽出的登录工具函数(不该管断言，辅助函数的职责是只做动作、返回原始对象)
def login(username, password):
    resp=requests.post(f'{BASE_URL}/api/auth/login',json={
        "username":username,
        "password":password
    })
    return resp
# 抽出的协议层基础断言
def assert_basics(resp):
    assert resp.status_code==200
    assert 'application/json' in resp.headers['Content-Type']
    assert resp.elapsed.total_seconds()<2,f"响应时间大于基线2s,{resp.elapsed.total_seconds():.3f}s"

def test_login_success():
    resp=login("admin","123456")
    # 协议层
    assert_basics(resp)
    # 业务层
    body=resp.json()
    assert body['code']==200
    assert body['message']=="登录成功"
    assert body["data"]["token"]!=''
    assert body['data']['name']=='管理员'
    assert body['data']['role']=='TEACHER'

# 把函数名作为参数使用
@pytest.fixture
def teacher_token():
    resp=login("admin","123456")
    assert resp.status_code==200,f"fixture登录失败，确认mock已启动{resp.status_code}"
    return resp.json()['data']['token']

def test_teacher_token_work(teacher_token):
    resp=requests.get(f'{BASE_URL}/api/teacher/records/pending',headers={'Authorization':f'Bearer {teacher_token}'})
    # 协议层
    assert_basics(resp)
    # 业务层
    body=resp.json()
    assert body['code']==200
    assert body['message']=='操作成功'
    assert isinstance(body['data'], list) and len(body['data']) > 0, f"待审列表为空或结构异常：{body['data']}"

# 把数据进行批量测试
@pytest.mark.parametrize('username,password,expect_name,expect_role',[
    ("admin","123456","管理员","TEACHER"),
    ("student_a","123456","张三","STUDENT"),
    ("student_b","123456","李四","STUDENT"),
])
def test_login_param(username,password,expect_name,expect_role):
    resp=login(username,password)
    # 协议层
    assert_basics(resp)
    # 业务层
    body=resp.json()
    assert body['data']['name']==expect_name
    assert body['data']['role']==expect_role

@pytest.mark.parametrize("username,password",[
                             ("admin","wrong"),
                             ("nobody","123456")
                         ])
def test_login_wrong_credentials(username, password):
    """契约依据：接口文档 §2.1 错误响应体 code=500（注意：HTTP 状态仍为 200，
_fail 默认 http_status=200；500 是业务码）。
观察记录：凭证错误用业务码 500 命名不当（按语义应为 4xx 客户端错），文档=实现一致，按契约断言。"""
    resp=login(username,password)
    # 协议层
    assert_basics(resp)
    # 业务层
    body=resp.json()
    assert body['code']==500
    assert body['message']=="用户名或密码错误"