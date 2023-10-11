from flask import render_template

from watchlist import app

@app.errorhandler(404) # 装饰器：错误处理函数
def page_not_found(e):
    #user = User.query.first()
    return render_template('errors/404.html'), 404

@app.errorhandler(400) # 装饰器：错误处理函数
def page_not_found(e):
    #user = User.query.first()
    return render_template('errors/404.html'), 400

@app.errorhandler(505) # 装饰器：错误处理函数
def page_not_found(e):
    #user = User.query.first()
    return render_template('errors/404.html'), 505