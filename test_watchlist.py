import  unittest

from app3 import app, db, Movie, User

class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        #更新配置
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URL='sqlite:///:memory:'
        )
        # 创建数据库和表
        db.create_all()
        #创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title', year='2023')
        #使用add_all()方法，一次添加多条
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client() #创建测试客户端
        self.runner = app.test_cli_runner() #创建测试命令运行器

    def tearDown(self):
        db.session.remove() #清除数据会话
        db.drop_all() #删除数据库表

    #测试实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    #测试程序是否处于测试状态
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404) #判断响应码

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    #辅助方法，用于登入用户
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    def test_creat_item(self):
        self.login()
        #测试创建条目
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created', data)
        self.assertIn('New Movie', data)

        #创建测试条目，但是电影名为空
        response =self.client.post('/',data=dict(
            title='',
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created', data)
        self.assertIn('Invalid input', data)

        # 创建测试条目，但是年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created', data)
        self.assertIn('Invalid input', data)

    #更新测试条目
    def test_update_item(self):
        self.login()

        #测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Watchlist', data)
        self.assertIn('2023', data)

        #测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated', data)
        self.assertIn('Invalid input', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input', data)

    #测试删除电影条目
    def test_delete_item(self):
        self.login()
        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted', data)
        self.assertIn('Test\'s Watchlist', data)

    #测试认证相关功能
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Layout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    #测试登录
    def test_login(self):
        response = self.client.post('/login', data=dict(
            username = 'test',
            password = '123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login Success', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        #测试使用错误密码登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password!', data)

        #测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input!', data)

        # 测试使用密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input!', data)

    #测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye!', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    # 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name='Grey Li',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated', data)
        self.assertIn('Grey Li', data)

        # 测试更新设置，名称为空
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated', data)
        self.assertIn('Invalid input!', data)

if __name__ == '__main__':
    unittest.main()