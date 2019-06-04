from django.db import models
from user.models import MyUser
from django.core.files.storage import FileSystemStorage
import os

# Create your models here.
'''
商品名；商品种类；商品简介；商品价格；商品数量；商品销量；商品图片；商品评价；
'''
class ImageStorage(FileSystemStorage):
    from django.conf import settings
    
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        #初始化
        super(ImageStorage, self).__init__(location, base_url)

    #重写 _save方法        
    def _save(self, name, content):
        import os, time, random
        #文件扩展名
        ext = os.path.splitext(name)[1]
        #文件目录
        d = os.path.dirname(name)
        #定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0,100)
        #重写合成文件名
        name = os.path.join(d, fn + ext)
        #调用父类方法
        return super(ImageStorage, self)._save(name, content)

class Goods(models.Model):
    GOODS_TYPE = (
        ('1','书籍'),
        ('2','手机'),
        ('3','电脑'),
        ('4','衣服'),
        ('5','其他'),
    )
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    goodsName = models.CharField(verbose_name='商品名称', max_length = 100)
    pubDate = models.DateTimeField(verbose_name='上架时间', auto_now_add = True)
    goodsType = models.CharField(verbose_name='商品种类', max_length = 1, choices = GOODS_TYPE) 
    productIntroduction = models.TextField(verbose_name='商品简介')
    goodsPrice = models.FloatField(verbose_name='商品价格')
    goodsNum = models.PositiveIntegerField(verbose_name='商品数量',default=0)
    goodsSelected = models.PositiveIntegerField(verbose_name='商品被选中数量',default=0)
    goodssales = models.PositiveIntegerField(verbose_name='商品销售量',default=0)
    goodsPic = models.ImageField(verbose_name='商品图片',upload_to = 'goods/', storage=ImageStorage(), 
        default="goods/default_goods.png", blank=True, null=True)

class Comment(models.Model):
    pubDate = models.DateTimeField(verbose_name='评论日期',auto_now_add = True)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='评论',max_length = 600)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)

class ShoppingCart(models.Model):
    # pubDate = models.DateTimeField(verbose_name='加入日期',auto_now_add = True)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(verbose_name='购买数量')
    subtotal = models.FloatField(verbose_name='小计')
    # saled = models.BooleanField(verbose_name='已被购买',default=False)

class Order(models.Model):
    # pubDate = models.DateTimeField(verbose_name='下单日期',auto_now_add = True)
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='收货人',max_length=20)
    address = models.CharField(verbose_name='地址',max_length=200)
    telephone = models.CharField(verbose_name='电话号码',max_length=11)
    total = models.FloatField(verbose_name='总金额')
    # content = models.CharField(verbose_name='商品',max_length=400)

class Order_goods(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE)
    number = models.PositiveIntegerField(verbose_name='购买数量', blank=True, null=True) 
    subtotal = models.FloatField(verbose_name='小计', blank=True, null=True)