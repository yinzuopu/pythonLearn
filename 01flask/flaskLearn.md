# Flask框架：使用Flask搭建一个简单的接口自动化测试服务
## 0、目标说明
使用flask搭建一个简单的可用于接口自动化的api服务<br/>
包含文件
+ start.py 程序主文件，用于启动程序
+ api_server.py 定义5个接口，分别是查询用户信息列表、查询单个用户信息、增加用户、修改用户信息、删除用户
+ test_api.py 测试api_server.py中自定义的接口
+ user.json 保存用户信息，采用json文件存储
+ Python版本：3.7.4 (v3.7.4:e09359112e, Jul  8 2019, 14:54:52) 
+ Flask版本：Flask 2.1.3

## 1、Flask介绍
Flask 的设计易于使用和扩展。它的初衷是为各种复杂的Web应用程序构建坚实的基础。可以自由地插入任何扩展。也可以自由构建自己的模块。Flask 适合各种项目。它对原型设计特别有用。Flask 依赖于两个外部库：Jinja2 模板引擎和 Werkzeug WSGI 工具包。 Flask 是最精致，功能最丰富的微框架之一。Flask 还很年轻，拥有蓬勃发展的社区，一流的扩展和漂亮的 API。Flask 具有快速模板，强大的 WSGI 功能，在 Web 应用程序和库级别的完整单元可测性，以及大量文档等优点。 选用 Flask 框架也是因为它方便入手，结构简单，零配置，是个学习 Python Web 开发的好工具。

## 2、mock接口介绍
mock / muk 接口，就是模拟接口
+ 暂时代替第三方接口测试，自己模拟一个接口
+ 辅助测试，用来代替没有开发好的接口
+ 查看数据

## 3、安装Flask
```commandline
pip install flask
```

## 4、 标准目录结构，分解各个目录文件
```commandline
01flask
├── bin
│   └── mian.py         # 程序入口文件，将启动服务的命令放在这里
├── conf
│   └── user.json       # 保存用户信息，采用json文件存储
├── lib
│   └── api_server.py   # 定义5个接口，分别是查询用户信息列表、查询单个用户信息、增加用户、修改用户信息、删除用户
└── testcase
    └── test_api.py     # 测试api_server.py中自定义的接口
```
## 5、 接口分析
### 5.1 计划
+ 首先，安装Flask环境，同时要确保python版本大于3.6（因为里面使用了Python f-string格式化字符串的语法）
+ 接着，运行api_server.py文件，此时会在本地监听8888端口。
+ 然后，在test_api.py中运行对应的单元测试用例即可测试对应的接口。

### 5.2 接口内容
```commandline
GET     http://[hostname]/users                 获取用户列表
GET     http://[hostname]/user/[user_id]        获取user_id的用户信息
POST    http://[hostname]/users                 创建新用户
PUT     http://[hostname]/users/[user_id]       更新用户信息
DELETE  http://[hostname]/users/[user_id]       删除user_id的用户信息    
```
### 5.3 用户信息结构
用户主要包含name、age、like这3部分信息，同时还存在1个唯一的id标识，用于区分用户。如下：
```json
{
    "id": 1001,
    "name": "Jim",
    "age": "20",
    "like": "jogging"
}
```
## 6、相关代码
### 6.1 api_server.py
```python
from flask import jsonify, Flask, request
import json

"""
功能：实现一个简单的用户查询、增加、修改和删除的api接口，可用于接口自动化测试的api服务。
响应结果说明：
1. api请求成功，则返回状态码200，同时在响应结果中返回api请求的相关信息,比如：
    {
        "result": "success",
        "users": {xxx}
    }
2. api请求失败，则返回状态码400，同时在响应结果中返回失败的原因，比如：
    {
        "result": "There is no user with user_id:xxx"
    }

依赖环境：
Python 3.9.12
Flask   2.1.2
"""

app = Flask(__name__)
json_path = "../conf/users.json"  # 保存用户json信息的路径


def get_json(json_path):
    """读取json数据"""
    with open(json_path, "r", encoding="utf-8") as f:
        res = json.load(f)
    return res


def write_json(json_path, json_data):
    """向文件写入json数据"""
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


@app.route("/users", methods=["GET"])
def get_users():
    """获取所有用户信息"""
    users = get_json(json_path)["users"]
    res = {
        "result": "success",
        "users": users
    }
    return jsonify(res), 200


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):  # 需要将route中的参数传递进来
    """查询指定user_id的用户信息"""
    users = get_json(json_path)["users"]
    user = list(filter(lambda t: t["id"] == user_id, users))  # 获取users中id为user_id的用户列表。
    if len(user) == 0:
        return jsonify({"result": f"There is no user with user_id:{user_id}"}), 400
    else:
        return jsonify({"result": "success", "user": user[0]}), 200


@app.route("/users", methods=["POST"])
def create_user():
    """要求请求的json数据中name、age是必填项，like选填"""
    required = ["name", "age"]  # 设置必填参数
    users = get_json(json_path)["users"]
    req_json = request.json
    if not req_json:
        return jsonify({"result": "Please use application/json to submit json data"}), 400

    # 获取缺少的必填参数
    params_list = set(required) - set(req_json.keys())
    if len(params_list) > 0:
        return jsonify({"result": f"Missing required parameter:{params_list}"}), 400

    # 为新用户设置一个id：
    # 1. 如果没有传递id参数，且当前users中不存在用户信息，此时就设置id为1001。
    # 2. 如果没有传递id参数，且users中存在用户信息，此时就获取最大的用户id，并在此基础上+1，作为new_id。
    # 3. 如果传递了id参数，且这个id已经存在与已有的id，此时返回错误信息。
    # 4. 如果传递了id参数，但是这个id不存在，此时就赋值为用户传递的id。
    ids = [user["id"] for user in users]
    if "id" not in req_json.keys():
        if len(ids) == 0:
            new_id = 1001
        else:
            new_id = max(ids) + 1
    else:
        if int(req_json["id"]) in ids:  # 如果自定义的id已经存在，则此时需要返回提示信息
            res = {"result": f'user_id: {req_json["id"]} already exists'}
            return jsonify(res), 400
        else:
            new_id = int(req_json["id"])

    # 新的用户数据
    user = {
        "id": new_id,
        "name": req_json["name"],
        "age": req_json["age"],
        "like": req_json["like"] if "like" in req_json.keys() else ""
    }
    users.append(user)
    print(users)
    write_json(json_path, {"users": users})
    return jsonify({"user": user, "result": "success"}), 200


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    users = get_json(json_path)["users"]
    user = list(filter(lambda t: t["id"] == user_id, users))
    if len(user) == 0:  # 表示不存在id为user_id的用户
        return jsonify({"result": f"There is no user with user_id:{user_id}"}), 400
    if not request.json:  # 当没有提交数据或者数据没有提交到json
        return jsonify({"result": "Please use application/json to submit json data"}), 400

    # 这里修改user[0]，实际上会修改users里面的内容，user应该也是users中指定id的引用
    user[0]["name"] = request.json.get("name", user[0]["name"])
    user[0]["age"] = request.json.get("age", user[0]["age"])
    user[0]["like"] = request.json.get("like", user[0]["like"])

    write_json(json_path, {"users": users})
    return jsonify(user), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    users = get_json(json_path)["users"]
    user = list(filter(lambda t: t["id"] == user_id, users))
    if len(user) == 0:  # 表示不存在id为user_id的用户
        return jsonify({"result": f"There is no user with user_id:{user_id}"}), 400

    # 直接通过remove删除即可。
    users.remove(user[0])
    write_json(json_path, {"users": users})
    return jsonify(user), 200
```
### 6.2 test_api.py
```python

import requests
import unittest
import json

class APITest(unittest.TestCase):
    # 请求的路径
    base_url = "http://127.0.0.1:8888"

    def test_get_users(self):
        """测试获取用户列表"""
        path = "/users"
        url = f"{self.base_url}{path}"

        res = requests.get(url, params={"token":"1234555"})
        print(res.json())
        assert res.json()["result"] == "success"

    def test_create_user(self):
        """
        创建用户
        """
        path = "/users"
        url = f"{self.base_url}{path}"
        data = {
            "name": "Jim",
            "age": "20",
            "like": "abc",
        }
        res = requests.post(url, headers={"Content-Type": "application/json"},data=json.dumps(data))
        print(res.json())
        assert res.json()["result"] == "success"

    def test_update_user(self):
        path = "/users/1001"
        url = f"{self.base_url}{path}"
        data = {
            "name": "Jim",
            "age": "23",
            "like": "jogging",
        }
        res = requests.put(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        print(res.json())

    def test_delete_user(self):
        path = "/users/1001"
        url = f"{self.base_url}{path}"
        res = requests.delete(url)
        print(res.json())
```
### 6.3 start.py
```python
# 程序入口文件，将启动服务的命令放在这里
# 增加根目录为环境变量，方便底层牡蛎执行时目录错误
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 取到01flask目录，为根目录
# print(BASE_DIR)
sys.path.insert(0, BASE_DIR)    # 引入自己写的程序路径，加环境变量，否则import导入会异常

from lib.api_server import app    # 在lib文件夹下新建__init__.py文件，在Python工程里，当python检测到一个目录下存在__init__.py文件时，python就会把它当成一个模块(module)。
app.run(
    port=8888,          # 默认端口是5000
    host='127.0.0.1',     # host = '0.0.0.0' 代表局域网内别人都可以通ip访问自己的接口
    debug=True          # 启动服务,加debug自动帮忙重启
)
```

### 6.4 start.py启动日志
```commandline
/Users/yinzuopu/pythonLearn/bin/python /Users/yinzuopu/pythonLearn/01flask/bin/start.py
 * Serving Flask app 'lib.api_server' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:8888 (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 136-091-012
127.0.0.1 - - [02/Aug/2022 15:20:54] "GET / HTTP/1.1" 404 -
127.0.0.1 - - [02/Aug/2022 15:20:58] "GET /users HTTP/1.1" 200 -
127.0.0.1 - - [02/Aug/2022 15:21:08] "GET /users/10086 HTTP/1.1" 400 -
127.0.0.1 - - [02/Aug/2022 15:22:34] "GET /users/1001 HTTP/1.1" 200 -
127.0.0.1 - - [02/Aug/2022 15:23:13] "POST /users HTTP/1.1" 200 -
127.0.0.1 - - [02/Aug/2022 15:23:13] "DELETE /users/1001 HTTP/1.1" 200 -
127.0.0.1 - - [02/Aug/2022 15:23:13] "GET /users?token=1234555 HTTP/1.1" 200 -
[{'id': 1001, 'name': 'Jim', 'age': '20', 'like': 'jogging'}, {'id': 1002, 'name': 'Jim', 'age': '20', 'like': 'abc'}]
127.0.0.1 - - [02/Aug/2022 15:23:13] "PUT /users/1001 HTTP/1.1" 400 -
```

### 6.5 test_api执行日志
```commandline
/Users/yinzuopu/pythonLearn/bin/python /Applications/PyCharm.app/Contents/plugins/python/helpers/pycharm/_jb_unittest_runner.py --path /Users/yinzuopu/pythonLearn/01flask/testcase/test_api.py
Testing started at 3:23 下午 ...
Launching unittests with arguments python -m unittest /Users/yinzuopu/pythonLearn/01flask/testcase/test_api.py in /Users/yinzuopu/pythonLearn/01flask/testcase

{'result': 'success', 'user': {'age': '20', 'id': 1002, 'like': 'abc', 'name': 'Jim'}}
[{'age': '20', 'id': 1001, 'like': 'jogging', 'name': 'Jim'}]
{'result': 'success', 'users': [{'age': '20', 'id': 1002, 'like': 'abc', 'name': 'Jim'}]}
{'result': 'There is no user with user_id:1001'}
```




