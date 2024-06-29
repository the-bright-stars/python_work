1. 通过requirements.txt配置好环境
2. 将getfile.py中的dashscope.api_key赋予自己key(通义千文模型)并设置model
3. 使用deletefile.py删除旧的数据，并获取新的数据
4. 在config.py设置好自己数据库连接的信息和邮箱连接信息
4. 运行app.py
5. 程序更新数据需要依靠deletefile.py，但目前只是手中执行的，所以要更新数据要自己手动启动