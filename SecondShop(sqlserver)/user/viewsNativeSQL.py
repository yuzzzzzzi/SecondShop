from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.contrib.auth import logout,login,authenticate
from .forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from .models import MyUser
from django.db import connection,transaction
from collections import namedtuple
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.conf import settings
import json
import time

# 以dict类型存储数据
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
# Create your views here.

def ulogin(request):
    if request.method == 'POST':
		#处理填写好的表单
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('store:index'))
        else:
            message = "登陆失败！请检查用户名和密码"
            return HttpResponse(message)
    return render(request,'user/login.html')

def ulogout(request):
	"""注销用户"""
	logout(request)
	return HttpResponseRedirect(reverse('store:index'))

def register(request):
    """注册新用户"""
    if request.method != 'POST':
        #显示空的注册表单
        form = UserCreationForm()
    else:
		#处理填写好的表单
        form = UserCreationForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            print(request.POST)
            with connection.cursor() as cursor: 
                if request.FILES:
                    import os, random
                    # 获取上传文件的处理对象
                    pic = request.FILES.get('avatar') 
                    name = str(request.FILES['avatar'])
                    # 文件扩展名
                    ext = os.path.splitext(name)[1]
                    # 定义文件名，年月日时分秒随机数
                    fn = time.strftime('%Y%m%d%H%M%S')
                    fn = fn + '_%d' % random.randint(0,100)
                    # 重写合成文件名
                    goodsPic = os.path.join(fn + ext)
                    # 创建一个文件(用于保存图片)
                    save_path = '%s/avatar/%s'%(settings.MEDIA_ROOT,goodsPic)  # pic.name 上传文件的源文件名
                    with open(save_path, 'wb') as f:
                        # 获取上传文件的内容并写到创建的文件中
                        for content in pic.chunks():   # pic.chunks() 上传文件的内容。
                            f.write(content)
                    save_path = 'avatar/%s'%(goodsPic)
                else:
                    goodsPic = 'default_avatar.png'
                    save_path = 'avatar/%s'%(goodsPic)
                params = [request.POST['username'],request.POST['nickname'],request.POST['telephone'],save_path,make_password(request.POST['password2']),False,True]
                # 执行sql语句,插入新用户
                cursor.execute("SET NOCOUNT ON INSERT INTO [user_myuser] ([username], [nickname], [telephone], [avatar], [password],[is_admin],[is_active])\
                                VALUES (%s, %s, %s, %s, %s, %s, %s)",params) 
            # new_user = form.save()
            # 让用户自动登录，在重定向到主页
            authenticated_user = authenticate(username = request.POST['username'],
                password = request.POST['password1'])
            login(request,authenticated_user)
            for item in connection.queries:
                print(item)
            return HttpResponseRedirect(reverse('store:index'))

    context = {'form':form}
    return render(request,'user/register.html',context)

def person(request,user_id):
    """用户信息与修改"""
    user = MyUser.objects.get(id=user_id)
    #显示空的注册表单
    form1 = UserChangeForm(instance=user)
    form2 = PasswordChangeForm(user)
    context = {'form1':form1 , 'form2':form2 , 'uuser':user}
		
    if request.method == 'POST':
        error_list = {'status':True,'errors':None}
        if 'nickname' in request.POST:	
            form1 = UserChangeForm(data=request.POST,files=request.FILES,instance=user)
            if form1.is_valid():
                with connection.cursor() as cursor: 
                    print(request.POST)
                    if request.FILES:
                        import os, random
                        # 获取上传文件的处理对象
                        pic = request.FILES.get('avatar') 
                        name = str(request.FILES['avatar'])
                        # 文件扩展名
                        ext = os.path.splitext(name)[1]
                        # 定义文件名，年月日时分秒随机数
                        fn = time.strftime('%Y%m%d%H%M%S')
                        fn = fn + '_%d' % random.randint(0,100)
                        # 重写合成文件名
                        goodsPic = os.path.join(fn + ext)
                        # 创建一个文件(用于保存图片)
                        save_path = '%s/avatar/%s'%(settings.MEDIA_ROOT,goodsPic)  # pic.name 上传文件的源文件名
                        with open(save_path, 'wb') as f:
                            # 获取上传文件的内容并写到创建的文件中
                            for content in pic.chunks():   # pic.chunks() 上传文件的内容。
                                f.write(content)
                        save_path = 'avatar/%s'%(goodsPic)
                    else:
                        cursor.execute("SELECT avatar FROM user_myuser WHERE id = %s",[user_id]) 
                        save_path = dictfetchall(cursor)[0]['avatar']
                        print(save_path)
                    # 需要插入的数据
                    params = [request.POST['nickname'],request.POST['telephone'],save_path,request.POST['address'],request.POST['major'],user_id]
                    # 执行sql语句,更新用户信息
                    cursor.execute("UPDATE user_myuser\
                                    SET nickname = %s, telephone = %s, avatar = %s, address = %s,major = %s\
                                    WHERE id = %s;"
                                    ,params) 
                error_list['status']=True
                return HttpResponse(json.dumps(error_list))
            else:
                error_list['status']=False
                # 将错误信息转换为json格式
                error_list['errors']= form1.errors.as_json()
                # 将返回到前台的数据转换为json
                return HttpResponse(json.dumps(error_list))
        elif 'old_password' in request.POST:
            form2 = PasswordChangeForm(request.user,request.POST)
            if form2.is_valid():
                print(request.POST)
                with connection.cursor() as cursor:
                    # 执行sql语句,更新指定购物车条目
                    cursor.execute("UPDATE user_myuser \
                                    SET password = %s \
                                    WHERE id = %s",[make_password(request.POST['new_password2']),user_id]) 
                error_list['status']=True
                return HttpResponse(json.dumps(error_list))
            else:
                error_list['status']=False
                # 将错误信息转换为json格式
                error_list['errors']= form2.errors.as_json()
                # 将返回到前台的数据转换为json
                return HttpResponse(json.dumps(error_list))
    return render(request,'user/person.html', context)