"""为应用程序users定义URL模式"""

from django.urls import path,re_path
from . import views,viewsNativeSQL

app_name = 'user'

urlpatterns = [
	#登录界面
	path('login/',viewsNativeSQL.ulogin,name='ulogin'),
	#注销
	path('logout/',viewsNativeSQL.ulogout,name='ulogout'),
	path('register/',viewsNativeSQL.register,name='register'),
	re_path(r'person/(?P<user_id>\d+)',viewsNativeSQL.person,name = 'person'),
]