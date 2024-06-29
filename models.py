# 用于数据库创建的模块
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


# 基础db.Model，这样就将一个类与一张表相对应起来了
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mailbox = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    appraise = db.Column(JSON)
    cookie = db.Column(db.String(100))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    keyword = db.Column(JSON)