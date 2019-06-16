from django import forms
from .models import Comment,Goods,ShoppingCart,Order
import re

class GoodsForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ('goodsName', 'goodsType', 'productIntroduction',  
            'goodsPrice', 'goodsNum','goodsPic')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class ShoppingCartForm(forms.ModelForm):
    def clean_number(self):
        number = self.cleaned_data.get("number")
        if int(number) == 0:
            raise forms.ValidationError("购买商品数量不能为0！")
        return number
    class Meta:
        model = ShoppingCart
        fields = ('number',)

class OrderForm(forms.ModelForm):
    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone")
        if len(telephone) != 11:
            raise forms.ValidationError("手机号位数不为11，请检查")
        if not re.match(r'[1]\d{10}',telephone):
            raise forms.ValidationError("手机号只能为数字且第一个数字为1")
        return telephone
    class Meta:
        model = Order
        fields = ('name','address','telephone')
