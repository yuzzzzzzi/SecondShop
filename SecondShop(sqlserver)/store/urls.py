from django.urls import path,re_path
#from . import views
from . import viewsNativeSQL as views

app_name = 'store'

urlpatterns = [
    path('',views.index,name='index'),
    path('search/',views.search,name='search'),
    re_path(r'mysale/(?P<goods_id>\d+)?',views.mysale,name='mysale'),
    path('add_goods/',views.add_goods,name='add_goods'),
    re_path(r'details/(?P<goods_id>\d+)',views.details,name='details'),
    path('addCheck/',views.addCheck,name='addCheck'),
    re_path(r'shoppingcart/(?P<cart_id>\d+)?',views.shoppingcart,name='shoppingcart'),
    path('orderCheck/',views.orderCheck,name='orderCheck'),
    re_path(r'purchased/(?P<order_id>\d+)?',views.purchased,name='purchased'),
    re_path(r'shop/(?P<type_id>\d+)?',views.shop,name='shop'),
]
