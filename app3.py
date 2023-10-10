import os
import sys
import click

from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) #主键
    name = db.Column(db.String(20)) #名字

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) #主键
    title = db.Column(db.String(60)) #movie's title
    year = db.Column(db.String(4)) #movie's year

@app.cli.command() ##注册命令
@click.option('--drop', is_flag=True, help='Create after drop!') ##设置选项
def initdb(drop):
    """Initialize the database!"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialize  database")

@app.cli.command()
def forge():
    """Generate fake data"""
    db.create_all()
    # 全局变量移动至此
    name = 'Zsccc'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done!')

@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.errorhandler(404) # 装饰器：错误处理函数
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404

@app.errorhandler(400) # 装饰器：错误处理函数
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404

@app.errorhandler(505) # 装饰器：错误处理函数
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404

'''' 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用。'''
@app.context_processor #模版上下文装饰器
def inject_user():
    user = User.query.first()
    return dict(user=user) #返回字典，等同于return {'user',user}




