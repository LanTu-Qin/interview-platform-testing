import requests


BASE_URL="http://127.0.0.1:8080"
teacher_token=''

def test_login_success():
    global teacher_token
    resp=requests.post(f'{BASE_URL}/api/auth/login',json={
    "username": "admin",
    "password": "123456"
})
    # 协议层
    assert resp.status_code==200
    assert 'application/json' in resp.headers['Content-Type']
    assert resp.elapsed.total_seconds()<2,f'耗时超2s基线：{resp.elapsed.total_seconds():.3f}s'
    # 业务层
    body=resp.json()
    assert body['code']==200
    assert body['message']=="登录成功"
    assert body["data"]["token"]!=''
    assert body['data']['name']=='管理员'
    assert body['data']['role']=='TEACHER'
    teacher_token=body['data']['token']
    assert teacher_token!=''

def test_teacher_token_work():
    resp=requests.get(f'{BASE_URL}/api/teacher/records/pending',headers={'Authorization':f'Bearer {teacher_token}'})
    # 协议层
    assert resp.status_code==200
    assert 'application/json' in resp.headers['Content-Type']
    assert resp.elapsed.total_seconds()<2,f'耗时超基线2s，{resp.elapsed.total_seconds():.3f}s'
    #业务层
    body=resp.json()
    assert body['code']==200
    assert body['message']=='操作成功'
    assert isinstance(body['data'], list) and len(body['data']) > 0, f"待审列表为空或结构异常：{body['data']}"
