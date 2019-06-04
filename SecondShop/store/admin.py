from django.contrib import admin
from .models import Goods,Comment,ShoppingCart,Order,Order_goods
from .forms import ShoppingCartForm 
# Register your models here.

class GoodsAdmin(admin.ModelAdmin):
    list_display = ('goodsName','goodsPic','goodsType','productIntroduction','goodsPrice','goodsNum','goodsSelected','goodssales','owner','pubDate')
    fieldsets = [
        (None,               {'fields': ['goodsName','goodsPic','goodsType','productIntroduction','goodsPrice']}),
        ('count', {'fields': ['goodsNum','goodsSelected','goodssales','owner']}),
    ]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('goods','content','owner','pubDate')

class ShoppingCartAdmin(admin.ModelAdmin):
    # add_form_template = ShoppingCartForm
    list_display = ('owner','goods','number','subtotal')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('owner','name','address','telephone','total')

class Order_goodsAdmin(admin.ModelAdmin):
    list_display = ('order','goods','number','subtotal')

admin.site.register(Goods, GoodsAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Order_goods, Order_goodsAdmin)