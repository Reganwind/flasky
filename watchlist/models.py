from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #主键
    name = db.Column(db.String(20)) #名字
    username = db.Column(db.String(20)) #用户名
    password_hash = db.Column(db.String(128)) # 密码散列值

    def set_password(self, password): #设置密码
        self.password_hash = generate_password_hash(password) # 将生成的密码保存到对应字段

    def validate_password(self, password): #判断密码
        return check_password_hash(self.password_hash, password) #返回布尔值


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) #主键
    title = db.Column(db.String(60)) #movie's title
    year = db.Column(db.String(4)) #movie's year