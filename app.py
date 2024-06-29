from flask import Flask, render_template, jsonify, request, session, g, url_for, redirect
from pydantic import BaseModel
from random import shuffle, choices
import config
from flask_mail import Mail, Message
from sqlalchemy.exc import IntegrityError
import string
from getfile import AddNews
from models import User, db, Article
import json
import os
import base64
from datetime import datetime


# 配置flask
app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
mail = Mail()
mail.init_app(app)

# 用来装今日新闻的变量
today_news = []

# 用于邮箱验证码临时保存数据
user_appraise = []

# 用于邮箱验证码临时保存数据
temporary_user = {}

# 用于保存api
apiUrl = ""


# 设置反馈格式
class Res(BaseModel):
    status: str = None
    message: str = None
    data: dict = None


# 初始化 today_news 和保存到数据库中（要更新的话需要手动删除data1）
def processingData():
    global today_news
    # 如果文件不存在 则调用一次
    if not os.path.exists('data2.json'):
        AddNews()
    with open('data2.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data = data["news"]

    # 利用K来只检测一次，减少反应时间
    K = True
    for i, da in enumerate(data):

        # 保存数据
        if K:
            try:
                ua = Article(url=da["url"], keyword=da["keyword"])
                db.session.add(ua)
                db.session.commit()
            except IntegrityError as e:
                # 这里错误不用处理
                K = False
                db.session.rollback()

        # 保存到全局数据
        today_news.append({"id": i + 1, "title": da["title"], "url": da["url"],
                           "content": da["content"], "keyword": da["keyword"]})


@app.before_request
def check_user_authenticated():
    # 利用钩子函数使一些界面没登入就无法访问
    if request.endpoint not in ['login_view', 'register_view', 'static', 'email_view', 'share_view'] \
            and 'user_id' not in session:
        return Res(status="fail", message="no login").json()


@app.route('/vote', methods=['POST'])
def vote():
    # 读取前端发送的数据和准备数据库的数据
    action = request.form.get('action')
    user = User.query.filter_by(cookie=session.get('user_id', None)).first()
    article = Article.query.filter_by(url=request.form.get('url')).first()

    if not user or not article:
        # 处理用户不存在的情况
        return Res(status="error", message="User not found").json()

    dicts = user.appraise

    if dicts is None:
        dicts = {}
    else:
        # 必须通过copy保存一次 否则好像出现了浅拷贝的问题
        dicts = user.appraise.copy()

    # 不管dicts[str(article.id)]原来存在否，直接覆盖
    if action == 'upvote':
        # 如果不用str(article.id)而直接用article.id，结果好像会随机出现结果
        dicts[str(article.id)] = 1  # if article.id not in dicts or dicts[article.id] != -1 else dicts[article.id]
    elif action == 'downvote':
        dicts[str(article.id)] = -1  # if article.id not in dicts or dicts[article.id] != 1 else dicts[article.id]
    else:
        # 处理无效的操作
        return Res(status="error", message="Invalid action").json()

    # 保存到数据库中
    user.appraise = dicts.copy()
    db.session.commit()
    return Res(status="success").json()


# 登入界面
@app.route('/', methods=['GET', 'POST'], endpoint='login_view')
def index():
    # 设计上出现个大问题，需要通过全局apiUrl（不过好像通过其他方法解决，不确定不敢删了）
    global apiUrl

    if request.method == 'POST':

        # 读取前端的数据
        user_name = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=user_name).first()

        # 判断用户是否存在
        if not user:
            # 如果不存在
            return Res(status="fail", message="账号或密码错误").json()
        else:
            # 如果存在
            if user.password == password:
                # 设置cookie
                co = list(str(user.username) + "user@SD1ame")
                shuffle(co)
                session['user_id'] = ''.join(co)
                # 必须要保存下cookie，不然其他视图不方便确定身份
                user.cookie = session['user_id']
                db.session.commit()

                return Res(status="success").json()
                # return render_template('index.html', news_data=today_news, isLoggedIn=True, apiUrl=apiUrl)
            else:

                return Res(status="fail", message="账号或密码错误").json()
    else:
        # 如果通过if判断减少processingData()调用的次数
        if not len(today_news):
            processingData()

        # 利用这个可以实现主要用户浏览器有cookie就可以免登入
        isLoggedIn = False
        apiUrl = "还没登入"
        # 查找用户，用来给数据赋值
        try:
            user = User.query.filter_by(cookie=session.get('user_id', None)).first()
        except:
            user = None

        if user:
            isLoggedIn = True
            # 生成api，并利用base64简单加密数据
            apiUrl = request.url_root[:-1] + url_for('share_view') + \
                     base64.b64encode(("jia" + user.mailbox + "mi").encode()).decode()

        return render_template('index.html', news_data=today_news, isLoggedIn=isLoggedIn, apiUrl=apiUrl)


@app.route('/register', methods=['POST', 'GET'], endpoint='register_view')
def register():

    if request.method == 'POST':
        # 读取前端的数据
        try:
            # user = Users(
            #     mailbox=request.form.get('mailbox'),
            #     user_name=request.form.get('user_name'),
            #     password=request.form.get('password'),
            # )
            mailbox = request.form.get('mailbox')
            user_name = request.form.get('user_name')
            password = request.form.get('password')
            verification_code = request.form.get('verification_code')
            password_confirm = request.form.get('password_confirm')

            # 对前端数据进行判断
            if password != password_confirm:
                return Res(status="fail", message="密码不相同").json()
            if mailbox not in temporary_user:
                return Res(status="fail", message="验证码不存在").json()
            elif verification_code != temporary_user.get(mailbox, None):
                return Res(status="fail", message="验证码不正确").json()
            elif User.query.filter_by(mailbox=mailbox).first() is not None:
                return Res(status="fail", message="重复建立").json()

        except ValueError as e:
            print(e)
            return Res(status="fail", message="参数错误！").json()  # Res(status="fail", message="输入参数错误").json()

        user = User(mailbox=mailbox, username=user_name, password=password)
        db.session.add(user)
        db.session.commit()

        return Res(status="success").json()
    else:
        return render_template('root.html')


# 发送邮箱验证码
@app.route('/mailsend', methods=['POST'], endpoint='email_view')
def mailTest():
    global temporary_user
    email_id = request.form.get("email")
    print(email_id)
    if not email_id:
        return Res(status="fail", message="空地址发送失败").json()
    try:
        # validate_email(email_id)
        characters = string.ascii_uppercase + string.digits
        code = ''.join(choices(characters, k=6))
        message = Message(subject="网易新闻推荐验证码", recipients=[email_id], body="这您的验证码：" + code)
        mail.send(message)
        temporary_user[email_id] = code
        return Res(status="success").json()
    except Exception as e:
        print(2)
        return Res(status="fail", message=str(e)).json()


# 退出时使用的
@app.route('/logout', methods=['GET'])
def logout():
    user = User.query.filter_by(cookie=session.get('user_id', None)).first()
    if user is not None:
        user.cookie = ""
        db.session.commit()
    session.clear()
    return redirect(url_for('login_view'))


# 计算文章关键字与情感关键词的关系
def calculateWeightedSimilarity(keywords, emotional_words):
    total_score = 0.0

    for keyword, freq in keywords.items():
        if keyword in emotional_words:
            # 使用词频和评分来计算加权相似度
            weighted_score = freq * emotional_words.get(keyword, 0)
            total_score += weighted_score

    return total_score


@app.route('/share/<key>', methods=['GET'], endpoint='share_view')
@app.route('/share/', methods=['GET'], endpoint='share_view')
def share(key=None):
    # 获取日期
    now = datetime.now()

    # 设置消息格式
    news = {
        "code": 200,
        "message": "获取成功",
        "total": 0,
        "updateTime": now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "data": {
        }
    }

    # 身份认证
    key = base64.b64decode(key.encode()).decode()
    print(key)
    if key[:3] != 'jia' or key[-2:] != 'mi':
        news["code"] = 400
        news["message"] = "获取失败"
        return jsonify(news)
    print(news)
    # 从数据库导入文章和用户数据
    user = User.query.filter_by(username="gxf").first()
    # user = User.query.filter_by(username=key[3:-3]).first()1948667127@qq.com
    dicts = user.appraise
    if dicts is None:
        dicts = {}
    else:
        dicts = user.appraise.copy()
    print(news)
    # 生成用户情感词典
    emotional_words = {}
    for Id, boo in dicts.items():
        article = Article.query.filter_by(id=Id).first()
        if article:
            keyword = article.keyword
            if keyword is None:
                keyword = {}

            # 算法是根据词频和正负评价加权求和
            for words, score in keyword.items():
                if not emotional_words.get(str(words), None):
                    emotional_words[str(words)] = score * boo
                else:
                    emotional_words[str(words)] += score * boo
    # 保留分数最高的10个
    emotional_words = sorted(emotional_words.items(), key=lambda x: x[1], reverse=True)[:10]
    emotional_words = {key: value for key, value in emotional_words}
    # print(emotional_words)
    print(news)
    # 获取今日新闻关键词
    if not len(today_news):
        processingData()
    article_score = {}
    print(news)
    # 利用成用户情感词典和获取今日新闻关键词求推荐分数
    for newss in today_news:
        article_score[newss["id"]] = calculateWeightedSimilarity(newss["keyword"], emotional_words)
    print(newss)
    article_score = sorted(article_score.items(), key=lambda x: x[1], reverse=True)
    news["data"] = [
        {"id": idx, "title": today_news[i - 1]["title"], "url": today_news[i - 1]["url"],
         "content": today_news[i - 1]["content"]}
        for idx, (i, value) in enumerate(article_score, start=1)
    ]
    news["total"] = len(news["data"])
    return jsonify(news)


with app.app_context():
    # 将db的表全部导入到数据库里面
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
