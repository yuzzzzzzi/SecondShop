"""为应用程序users定义URL模式"""

from django.urls import path,re_path
#from . import views
from . import viewsNativeSQL as views


app_name = 'user'

urlpatterns = [
	#登录界面
	path('login/',views.ulogin,name='ulogin'),
	#注销
	path('logout/',views.ulogout,name='ulogout'),
	path('register/',views.register,name='register'),
	re_path(r'person/(?P<user_id>\d+)',views.person,name = 'person'),
]