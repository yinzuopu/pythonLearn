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
