from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.contrib.auth import logout,login,authenticate
from .forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from .models import MyUser

from django.core import serializers
import json

# Create your views here.

def ulogin(request):
    if request.method == 'POST':
		#处理填写好的表单
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        print(request.POST)
        user = authenticate(request, username=username, password=password)
        print(request.POST)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('store:index'))
        else:
            message = "登陆失败！请检查用户名和密码"
            return HttpResponse(message)
    print(request.POST)
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
		print(request.POST)
		print(request.FILES)
		form = UserCreationForm(data=request.POST,files=request.FILES)
		if form.is_valid():
			new_user = form.save()
			#让用户自动登录，在重定向到主页
			authenticated_user = authenticate(username = new_user.username,
				password = request.POST['password1'])
			login(request,authenticated_user)
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
		# form1 = UserChangeForm(instance=user)
		# form2 = PasswordChangeForm(request.user)
		if 'nickname' in request.POST:	
			# print(request.POST)
			# print(request.FILES.get("avatar"))
			form1 = UserChangeForm(data=request.POST,files=request.FILES,instance=user)
			if form1.is_valid():
				form1.save()
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
				form2.save()
				#让用户自动登录，在重定向到主页
				# authenticated_user = authenticate(username = request.user.username,
				# 	password = request.POST['new_password1'])
				# login(request,authenticated_user)
				error_list['status']=True
				return HttpResponse(json.dumps(error_list))
			else:
				error_list['status']=False
				# 将错误信息转换为json格式
				error_list['errors']= form2.errors.as_json()
				# 将返回到前台的数据转换为json
				return HttpResponse(json.dumps(error_list))
	return render(request,'user/person.html', context)