from django.urls import path,re_path
from . import views,viewsNativeSQL

app_name = 'store'

urlpatterns = [
    path('',viewsNativeSQL.index,name='index'),
    path('search/',viewsNativeSQL.search,name='search'),
    re_path(r'mysale/(?P<goods_id>\d+)?',viewsNativeSQL.mysale,name='mysale'),
    path('add_goods/',viewsNativeSQL.add_goods,name='add_goods'),
    re_path(r'details/(?P<goods_id>\d+)',viewsNativeSQL.details,name='details'),
    path('addCheck/',viewsNativeSQL.addCheck,name='addCheck'),
    re_path(r'shoppingcart/(?P<cart_id>\d+)?',viewsNativeSQL.shoppingcart,name='shoppingcart'),
    path('orderCheck/',viewsNativeSQL.orderCheck,name='orderCheck'),
    re_path(r'purchased/(?P<order_id>\d+)?',viewsNativeSQL.purchased,name='purchased'),
    re_path(r'shop/(?P<type_id>\d+)?',viewsNativeSQL.shop,name='shop'),
]
