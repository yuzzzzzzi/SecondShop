# SecondShop(Django)
二手交易市场，使用Python主流框架Django进行搭建，使用pyvenv进行应用层Python环境隔离，使用时可直接进入隔离环境中进行操作。
该环境中有项目所需要的依赖包，无需担心项目依赖包的问题，二次开发也推荐在隔离环境中进行。


## 数据库配置

如果想使用自己的数据库的话可按照以下进行配置

更改settings.py中的DATABASES内容

### SQLite3 数据库配置

```python
DATABASES = {
	#SQLite3 数据库配置(无需安装，可直接使用)
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}
```


### MYSQL 数据库配置(需要安装MYSQL数据库)
```python
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'second_shop',
		'USER': 'root',
		'PASSWORD': '123456',
		'HOST': '127.0.0.1',
		'PORT': '3306',
	}
}
```
### SQL Server 数据库配置(需要安装SQL Server数据库)
```python
DATABASES = {
	'default': {
		#数据库引擎设置 
		'ENGINE': 'sql_server.pyodbc',
		#要连接的数据库名 
		'NAME': 'second_shop',
		#数据库用户名(使用windows本地账户进行登陆，USER与为空)
		'USER': '',
		#数据库密码 
		'PASSWORD': '',
		#数据库主机地址
		'HOST': '127.0.0.1',
		#数据库端口号，默认可以不写
		'PORT': '1433', 
		'OPTIONS': {
			#选项，这个要先在操作系统上完成ODBC的连接创建，并连接成功，注意10.0这个地方，要和自己的ODBC版本一致
			'driver':'SQL Server Native Client 11.0',
			'MARS_Connection': True,#使用MARS (multiple active result sets)，支持异步
		},
	},
}
```
如果出现错误可参考这篇博客：[Django中使用Microsoft SQL SERVER](https://www.cnblogs.com/pythonkids/p/7943376.html)

配置完数据库之后就可以愉快的进行操作了！！

## 进入Python隔离环境
cd 到 `Scripts` 文件夹中 在命令行中执行`activate`命令就可以进入隔离环境了

标志为在命令行的前面出现`(Second_Shop)`标记。
## 初始执行命令
可不用切换目录直接执行以下命令
```bash
(Second_Shop) E:\Second_Shop_mysql\Scripts>python ..\SecondShop\manage.py makemigrations
(Second_Shop) E:\Second_Shop_mysql\Scripts>python ..\SecondShop\manage.py migrate
(Second_Shop) E:\Second_Shop_mysql\Scripts>python ..\SecondShop\manage.py createsuperuser
(Second_Shop) E:\Second_Shop_mysql\Scripts>python ..\SecondShop\manage.py runserver
```
`makemigrations`根据项目中的model进行创建需要执行的SQL命令

`migrate`执行上一步创建好的SQL命令，完毕后可直接就拥有项目所需的数据库结构了

`createsuperuser`创建超级账户，用于后台管理，管理页面在`127.0.0.1:8000/admin`

`runserver`启动服务，执行后就可以在浏览器中进行查看了

出现以下的内容即代表运行成功
```bash
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
May 27, 2019 - 19:44:43
Django version 2.2.1, using settings 'SecondShop.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
进入`http://127.0.0.1:8000/`即可。