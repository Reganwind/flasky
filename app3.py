import os
import sys
import click

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)
login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login'

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


@app.cli.command() ##注册命令
@click.option('--drop', is_flag=True, help='Create after drop!') ##设置选项
def initdb(drop):
    """Initialize the database!"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialize  database")

@app.cli.command() ##初始化db
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

@app.cli.command() ##装饰 生成admin用户密码
@click.option('--username', prompt=True, help='The username used to login!')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login!')
def admin(username, password):
    """create user"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo("Creating user...")
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done!')

@login_manager.user_loader
def load_user(user_id): #创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id)) # 用ID 作为User 模型的主键查询对应的用户
    return user #返回用户对象


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated: # 用户未认证
            return redirect(url_for('index')) # 返回主页
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input!')
            return redirect(url_for('index'))#重定向回主页
        movie = Movie(title=title, year=year)
        db.session.add(movie) #新增
        db.session.commit() #提交
        flash('Item created!')
        return redirect(url_for('index'))#重定向回主页
    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input!')
            return redirect(url_for('login'))
        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login Success!')
            return redirect(url_for('index'))
        flash('Invalid username or password!')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required #视图保护
def logout():
    logout_user() # 登出用户
    flash('Goodbye!')
    return redirect(url_for('index')) #重定向首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input!')
            return redirect(url_for('settings'))
        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')

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

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required #登录保护login_manager
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST']) # 限定只接受POST
@login_required #登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted!')
    return redirect(url_for('index'))



