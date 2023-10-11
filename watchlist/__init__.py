import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
db = SQLAlchemy(app)
login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id): #创建用户加载回调函数，接受用户ID作为参数
    from watchlist.models import User
    user = User.query.get(int(user_id)) # 用ID 作为User 模型的主键查询对应的用户
    return user #返回用户对象

'''' 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用。'''
@app.context_processor #模版上下文装饰器
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user) #返回字典，等同于return {'user',user}

from watchlist import views, errors, commands
