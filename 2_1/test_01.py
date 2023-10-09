from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello Word</h1>'

app.add_url_rule('/', 'index', index)

@app.route('/user/<name>')
def user(name):
    return '<h1>hello,{}!</h1>'.format(name)

