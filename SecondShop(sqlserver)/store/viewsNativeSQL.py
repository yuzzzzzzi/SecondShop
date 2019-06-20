from django.shortcuts import render,reverse
from django.http import HttpResponse,HttpResponseRedirect
from .models import Comment,Goods,ShoppingCart,Order
from django.contrib.auth.decorators import login_required
from .forms import CommentForm,GoodsForm,ShoppingCartForm,OrderForm
from django.core.files.storage import FileSystemStorage
from django.db import connection,transaction
from collections import namedtuple
from django.conf import settings
import time
import json

# 以dict类型存储数据
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# Create your views here.
def index(request):
    with connection.cursor() as cursor: 
        #执行sql语句,查询最新的3个商品
        cursor.execute("SELECT TOP 3 * FROM store_goods ORDER BY pubDate DESC") 
        new_goodss = dictfetchall(cursor)
        #查询销量最高的3个商品
        cursor.execute("SELECT TOP 3 * FROM store_goods ORDER BY goodssales DESC") 
        hot_goodss = dictfetchall(cursor)
    context = {'new_goodss':new_goodss,'hot_goodss':hot_goodss}
    return render(request,'store/index.html',context)

def search(request):
    q = request.GET.get('q')
    if not q:
        goods_type = '请输入关键词'
        return render(request, 'store/shop.html', {'goods_type': goods_type})
    with connection.cursor() as cursor: 
        #执行sql语句,模糊查询
        strq = "%%"+q+"%%" #解决查询时的%问题
        cursor.execute("SELECT * FROM store_goods WHERE goodsName LIKE %s",[strq]) 
        goodss = dictfetchall(cursor)

    #goodss = Goods.objects.filter(goodsName__icontains=q)
    goods_type = '搜索结果'
    context = {'goodss':goodss,'goods_type':goods_type}
    return render(request, 'store/shop.html', context)

def shop(request,type_id):
    if type_id:
        with connection.cursor() as cursor: 
            #执行sql语句,查找种类
            cursor.execute("SELECT * FROM store_goods WHERE goodsType = %s ORDER BY pubDate",[type_id]) 
            goodss = dictfetchall(cursor)
            #goodss = Goods.objects.filter(goodsType=type_id).order_by('pubDate')
        GOODS_TYPE = {
            '1':'书籍',
            '2':'手机',
            '3':'电脑',
            '4':'衣服',
            '5':'其他',
        }
        goods_type = GOODS_TYPE[type_id]
    else:
        with connection.cursor() as cursor: 
            #执行sql语句,查找种类
            cursor.execute("SELECT * FROM store_goods ORDER BY pubDate") 
            goodss = dictfetchall(cursor)
        goods_type = '全部'
    context = {'goodss':goodss,'goods_type':goods_type}
    return render(request,'store/shop.html',context)
    
@login_required
def add_goods(request):
    if request.method != "POST":
        form = GoodsForm()
    else:
        form = GoodsForm(request.POST,files=request.FILES)
        if form.is_valid():
            if request.FILES:
                import os, random
                # 获取上传文件的处理对象
                pic = request.FILES.get('goodsPic') 
                name = str(request.FILES['goodsPic'])
                # 文件扩展名
                ext = os.path.splitext(name)[1]
                # 定义文件名，年月日时分秒随机数
                fn = time.strftime('%Y%m%d%H%M%S')
                fn = fn + '_%d' % random.randint(0,100)
                # 重写合成文件名
                goodsPic = os.path.join(fn + ext)
                # 创建一个文件(用于保存图片)
                save_path = '%s/goods/%s'%(settings.MEDIA_ROOT,goodsPic)  # pic.name 上传文件的源文件名
                with open(save_path, 'wb') as f:
                    # 获取上传文件的内容并写到创建的文件中
                    for content in pic.chunks():   # pic.chunks() 上传文件的内容。
                        f.write(content)
                save_path = 'goods/%s'%(goodsPic)
            else:
                goodsPic = 'default_goods.png'
                save_path = 'goods/%s'%(goodsPic)
            # 需要插入的数据
            params = [int(request.user.id),request.POST['goodsName'],time.strftime("%Y-%m-%d %H:%M", time.localtime()),
                request.POST['goodsType'],"".join(request.POST['productIntroduction'],),float(request.POST['goodsPrice']),
                int(request.POST['goodsNum']),0,0,save_path]
            with connection.cursor() as cursor: 
            # 执行sql语句,插入商品
                cursor.execute("SET NOCOUNT ON INSERT INTO [store_goods] ([owner_id], [goodsName], [pubDate], [goodsType], \
                    [productIntroduction], [goodsPrice], [goodsNum], [goodsSelected], [goodssales],[goodsPic]) VALUES \
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",params) 
            return HttpResponseRedirect(reverse('store:mysale'))

    context = {'form':form}
    return render(request,'store/addgoods.html',context)

@login_required
def mysale(request,goods_id):
    try:
        with connection.cursor() as cursor: 
            #执行sql语句,删除指定id的商品
            cursor.execute("DELETE FROM store_goods WHERE id = %s",[goods_id]) 
    except:
        pass

    with connection.cursor() as cursor: 
        #执行sql语句,商品所有人是当前用户的商品
        cursor.execute("SELECT * FROM store_goods WHERE owner_id = %s and goodsNum >= 0",[request.user.id]) 
        goodss = dictfetchall(cursor)
        #执行sql语句,商品所有人是当前用户的商品，并且商品数量为0，商品被选中的数量为0的商品（已售罄的商品）
        cursor.execute("SELECT * FROM store_goods WHERE owner_id = %s and goodsNum = 0 and goodsSelected = 0",[request.user.id]) 
        goods_nones = dictfetchall(cursor)

    context = {'goodss':goodss,'goods_nones':goods_nones}
    return render(request,'store/mysale.html', context)

def details(request,goods_id):
    with connection.cursor() as cursor: 
        # 执行sql语句,获取指定id的商品及所需的商品所有人的数据
        cursor.execute("SELECT sg.*, um.nickname, um.avatar, um.telephone\
                        FROM store_goods AS sg FULL JOIN user_myuser AS um ON sg.owner_id = um.id \
                        WHERE sg.id = %s",[goods_id]) 
        goods = dictfetchall(cursor)
        # 执行sql语句,获取指定id的商品的所有评论及所需评论所有人的数据
        cursor.execute("SELECT sc.*, um.nickname, um.avatar\
                        FROM store_comment AS sc FULL JOIN user_myuser AS um ON sc.owner_id = um.id \
                        WHERE sc.goods_id = %s ORDER BY pubDate",[goods_id]) 
        comments = dictfetchall(cursor)

    if request.method != "POST":
        form1 = CommentForm()
        form2 = ShoppingCartForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            params = [time.strftime("%Y-%m-%d %H:%M", time.localtime()),goods_id,request.POST['content'],request.user.id]
            with connection.cursor() as cursor: 
            # 执行sql语句,插入评论
                cursor.execute("SET NOCOUNT ON INSERT INTO [store_comment] ([pubDate], [goods_id], [content], [owner_id])\
                                VALUES (%s, %s, %s, %s)",params) 
            return HttpResponseRedirect(reverse('store:details',args=[goods_id]))
    context = {'goods':goods[0],'comments':comments,'form1':form1,'form2':form2}
    return render(request,'store/details.html', context)

@login_required
def addCheck(request):
    error_list = {'status':True,'errors':None}
    form = ShoppingCartForm(data=request.POST)
    number = request.POST['number']
    if form.is_valid():
        with connection.cursor() as cursor: 
            # 执行sql语句,获取指定id的商品
            cursor.execute("SELECT * FROM store_goods WHERE id = %s",[request.POST['id']]) 
            goods = dictfetchall(cursor)[0]
            # 执行sql语句,获取当前用户的所有购物车条目
            cursor.execute("SELECT * FROM store_shoppingcart WHERE owner_id = %s",[request.user.id]) 
            added_goodss = dictfetchall(cursor)
            for added_goods in added_goodss:
                # 如果改商品在购物车已存在，进行叠加商品数量并修改subtotal
                if goods['id'] == added_goods['goods_id']:
                    added_goods['number'] += int(number)
                    added_goods['subtotal'] += float(number) * goods['goodsPrice']
                    goods['goodsNum'] -= int(number)
                    goods['goodsSelected'] += int(number)
                    # 执行sql语句,更新指定购物车条目
                    cursor.execute("UPDATE store_shoppingcart \
                                    SET number = %s ,subtotal = %s\
                                    WHERE id = %s",[added_goods['number'],added_goods['subtotal'],added_goods['id']]) 
                    # 执行sql语句,更新指定商品条目的数量
                    cursor.execute("UPDATE store_goods \
                                    SET goodsNum = %s ,goodsSelected = %s\
                                    WHERE id = %s",[goods['goodsNum'],goods['goodsSelected'],goods['id']]) 
                    error_list['status'] = True
                    return HttpResponse(json.dumps(error_list))
            # 商品不在购物车中不存在,执行一下操作,为用户添加新的购物车条目
            params = [request.user.id,request.POST['id'],number,float(number) * goods['goodsPrice']]  
            goods['goodsNum'] -= int(number) 
            goods['goodsSelected'] += int(number)   
            # 执行sql语句,插入新的购物车条目
            cursor.execute("SET NOCOUNT ON INSERT INTO [store_shoppingcart] ([owner_id], [goods_id], [number], [subtotal]) \
                            VALUES (%s, %s, %s, %s)",params) 
            # 执行sql语句,更新商品条目的数量
            cursor.execute("UPDATE store_goods \
                            SET goodsNum = %s ,goodsSelected = %s\
                            WHERE id = %s",[goods['goodsNum'],goods['goodsSelected'],goods['id']]) 
            
            error_list['status']=True
            return HttpResponse(json.dumps(error_list))
    else:
        error_list['status']=False
        # 将错误信息转换为json格式
        error_list['errors']= form.errors.as_json()
        # 将返回到前台的数据转换为json
        return HttpResponse(json.dumps(error_list))

@login_required
def shoppingcart(request,cart_id):
    try:
        with connection.cursor() as cursor: 
            # 执行sql语句,获取指定id的购物车条目
            cursor.execute("SELECT * FROM store_shoppingcart WHERE id = %s",[cart_id]) 
            cart = dictfetchall(cursor)[0]
            # 执行sql语句,获取指定id的购物车条目
            cursor.execute("SELECT * FROM store_goods WHERE id = %s",[cart['goods_id']]) 
            goods = dictfetchall(cursor)[0]
            # 执行sql语句,更新商品数据并删除指定购物车条目
            cursor.execute("UPDATE store_goods \
                            SET goodsNum = %s ,goodsSelected = %s\
                            WHERE id = %s;\
                            DELETE FROM store_shoppingcart \
                            WHERE id = %s",
                            [goods['goodsNum']+ cart['number'],goods['goodsSelected']- cart['number'],goods['id'],cart_id]) 
    except:
        pass
    form = OrderForm()
    with connection.cursor() as cursor: 
        #执行sql语句,查找当前用户的购物车
        cursor.execute("SELECT ss.*, sg.goodsName, sg.goodsPrice, sg.goodsPic\
                        FROM store_shoppingcart AS ss FULL JOIN store_goods AS sg ON ss.goods_id = sg.id \
                        WHERE ss.owner_id = %s ORDER BY pubDate",[request.user.id]) 
        goodss = dictfetchall(cursor)
    context = {'goodss':goodss,'form':form}
    return render(request,'store/shoppingcart.html', context)

@login_required
def orderCheck(request):
    error_list = {'status':True,'errors':None}
    goodss = request.POST['content']
    # print(goodss)
    content = goodss.split(',')
    content = list(set(content))
    ids = []
    for entry in content:
        tlist = entry.split("*")
        ids.append(tlist[0])
    form = OrderForm(request.POST)
    if form.is_valid():
        with connection.cursor() as cursor: 
            # 执行sql语句,插入新的订单
            params = [request.user.id,request.POST['name'],request.POST['address'],request.POST['telephone'],
                    float(request.POST['total']),request.POST['content']]
            cursor.execute("SET NOCOUNT ON INSERT INTO [store_order] ([owner_id], [name], [address], [telephone], [total], [content]) \
                            VALUES (%s, %s, %s, %s, %s, %s)",params) 
            for goods_id in ids:
                cursor.execute("SELECT * FROM store_goods WHERE id = %s",[goods_id]) 
                goods = dictfetchall(cursor)[0]
                # 执行sql语句,查找结算的指定id的商品的数量,并将其在购物车条目中删除
                cursor.execute("SELECT number FROM store_shoppingcart WHERE goods_id = %s and owner_id = %s \
                                DELETE FROM store_shoppingcart WHERE goods_id = %s and owner_id = %s ",
                                [goods_id, request.user.id, goods_id, request.user.id]) 
                number = int(dictfetchall(cursor)[0]['number'])
                # 执行sql语句,更新商品数据
                cursor.execute("UPDATE store_goods \
                                SET goodssales = %s ,goodsSelected = %s\
                                WHERE id = %s",
                                [goods['goodssales'] + number, goods['goodsSelected'] - number, goods_id]) 

        error_list['status']=True
        return HttpResponse(json.dumps(error_list))
    else:
        error_list['status']=False
        # 将错误信息转换为json格式
        error_list['errors']= form.errors.as_json()
        # 将返回到前台的数据转换为json
        return HttpResponse(json.dumps(error_list))

@login_required
def purchased(request,order_id):
    if request.method == "POST":
        with connection.cursor() as cursor: 
            # 执行sql语句,获取指定id的订单条目
            cursor.execute("SELECT * FROM store_order WHERE id = %s",[order_id]) 
            tar_order = dictfetchall(cursor)[0]
            tar_content = tar_order['content']
            # 执行sql语句,获取指定id的商品条目
            cursor.execute("SELECT * FROM store_goods WHERE id = %s",[request.POST["gid"]]) 
            tar_goods = dictfetchall(cursor)[0]

            tconlist = tar_content.split(",")
            for i in range(len(tconlist)):
                tconitemlist = tconlist[i].split("*")
                if tconitemlist[0] == request.POST["gid"]:
                    tconlist.pop(i)
                    tar_num = int(tconitemlist[1])
                    break
            editcontent =  ",".join(tconlist)
            tar_order['total'] -= tar_goods['goodsPrice'] * tar_num 
            tar_order['content'] = editcontent
            if tar_order['total'] == 0.0:
                cursor.execute("DELETE FROM store_order WHERE id = %s",[order_id]) 
            else:
                # 执行sql,更新订单数据
                cursor.execute("UPDATE store_order \
                                SET total = %s ,content = %s\
                                WHERE id = %s",
                                [tar_order['total'], tar_order['content'], order_id]) 
            return HttpResponseRedirect(reverse('store:purchased'))
    else:
        with connection.cursor() as cursor: 
            # 执行sql语句,获取指定id的订单条目
            cursor.execute("SELECT * FROM store_order WHERE owner_id = %s ORDER BY id DESC",[request.user.id]) 
            orders = dictfetchall(cursor)
            con_orders = []
            for order in orders:
                dic_order = {}
                dic_order["name"] = order['name']
                dic_order["telephone"] = order['telephone']
                dic_order["address"] = order['address']
                dic_order["total"] = order['total']
                dic_order["id"] = order['id']
                goodss = []
                order_content = order['content']
                order_content_list = order_content.split(",")
                for entry in order_content_list:
                    tlist = entry.split("*")
                    goods_content = {}
                    # 执行sql语句,获取指定id的商品条目
                    cursor.execute("SELECT * FROM store_goods WHERE id = %s",[int(tlist[0])]) 
                    goods = dictfetchall(cursor)[0]
                    goods_content["goods"] = goods
                    goods_content["num"] = int(tlist[1])
                    subtotal = goods['goodsPrice'] * int(tlist[1])
                    goods_content["subtotal"] = subtotal
                    goodss.append(goods_content)
                dic_order["goodss"] = goodss
                # print(dic_order)
                con_orders.append(dic_order)
        # print(con_orders)
        context = {'con_orders':con_orders}
        return render(request,'store/purchased.html', context)