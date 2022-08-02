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