
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
