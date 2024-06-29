# 专门用于填下配置的信息
SECRET_KEY = "a@sda3232123ksa"
# 数据库的配置信息
HOSTNAME = '127.0.0.1'  # 等价于 ‘127.0.0.1’
PORT = '3306'
DATABASE = 'test'
USERNAME = 'yonghu'
PASSWORD = 'yonghu1234'
DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
# 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(DATABASE, PASSWORD, HOSTNAME, POST, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

# 邮箱配置信息
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "邮箱"
MAIL_PASSWORD = "邮箱的特定密码"
MAIL_DEFAULT_SENDER = "邮箱"

"""
# MySQL所在的主机名
HOSTNAME = "127.0.0.1"
# MySQL监听的端口号，默认3306
PORT = 3306
# 连接MySQL的用户名，读者用自己设置的
USERNAME = "root"
# 连接MySQL的密码，读者用自己的
PASSWORD = "root"
# MySQL上创建的数据库名称
DATABASE = "database_learn"

app.config['SQLALCHEMY_DATABASE_URI'] = 
f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
"""
