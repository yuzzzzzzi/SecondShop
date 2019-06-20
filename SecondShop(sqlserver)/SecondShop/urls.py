"""SecondShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.views.static import serve
from SecondShop.settings import MEDIA_ROOT # 导入项目文件夹中setting中的MEDIA_ROOT绝对路径
from django.views.generic.base import RedirectView
from django.conf.urls.static import static

urlpatterns = [
    re_path('media/(?P<path>.*)',  serve, {"document_root": MEDIA_ROOT}),
    path(r'favicon.ico',RedirectView.as_view(url=r'static/favicon.ico')),
    path('',include('store.urls')),
    path('user/',include('user.urls')),
    path('admin/', admin.site.urls),
]
