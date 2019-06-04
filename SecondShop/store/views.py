from django.shortcuts import render,reverse
from django.http import HttpResponse,HttpResponseRedirect
from .models import Comment,Goods,ShoppingCart,Order,Order_goods
from django.contrib.auth.decorators import login_required
from .forms import CommentForm,GoodsForm,ShoppingCartForm,OrderForm,Order_goodsForm
import json
# Create your views here.

def index(request):
    new_goodss = Goods.objects.order_by("-pubDate")[:3]
    hot_goodss = Goods.objects.order_by("-goodssales")[:3]
    # print(new_goodss)
    # return HttpResponse("Hello , world. You're at the Store index.")
    context = {'new_goodss':new_goodss,'hot_goodss':hot_goodss}
    return render(request,'store/index.html',context)

def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        goods_type = '请输入关键词'
        return render(request, 'store/shop.html', {'goods_type': goods_type})

    goodss = Goods.objects.filter(goodsName__icontains=q)
    goods_type = '搜索结果'
    context = {'goodss':goodss,'goods_type':goods_type}
    return render(request, 'store/shop.html', context)

def shop(request,type_id):
    if type_id:
        goodss = Goods.objects.filter(goodsType=type_id).order_by('pubDate')
        GOODS_TYPE = {
            '1':'书籍',
            '2':'手机',
            '3':'电脑',
            '4':'衣服',
            '5':'其他',
        }
        goods_type = GOODS_TYPE[type_id]
    else:
        goodss = Goods.objects.order_by('pubDate') 
        goods_type = '全部'
    
    print(goodss)
    context = {'goodss':goodss,'goods_type':goods_type}
    return render(request,'store/shop.html',context)
    
@login_required
def add_goods(request):
    if request.method != "POST":
        form = GoodsForm()
    else:
        form = GoodsForm(request.POST,files=request.FILES)
        if form.is_valid():
            new_goods = form.save(commit=False)
            new_goods.owner = request.user
            new_goods.goodssales = 0
            new_goods.save()
            return HttpResponseRedirect(reverse('store:mysale'))

    context = {'form':form}
    return render(request,'store/addgoods.html',context)

@login_required
def mysale(request,goods_id):
    try:
        goods = Goods.objects.get(id=goods_id)
        goods.delete()
    except:
        pass
    goodss = Goods.objects.filter(owner=request.user).order_by('pubDate')
    goods_nones = Goods.objects.filter(owner=request.user,goodsNum=0,goodsSelected=0).order_by('pubDate')
    context = {'goodss':goodss,'goods_nones':goods_nones}
    return render(request,'store/mysale.html', context)

def details(request,goods_id):
    goods = Goods.objects.get(id=goods_id)
    comments =  goods.comment_set.order_by('pubDate')
    if request.method != "POST":
        form1 = CommentForm()
        form2 = ShoppingCartForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.owner = request.user
            new_comment.goods = goods
            new_comment.save()
            return HttpResponseRedirect(reverse('store:details',args=goods_id))
    context = {'goods':goods,'comments':comments,'form1':form1,'form2':form2}
    return render(request,'store/details.html', context)

@login_required
def addCheck(request):
    error_list = {'status':True,'errors':None}
    form = ShoppingCartForm(data=request.POST)
    # print(request.POST['id'])
    goods = Goods.objects.get(id=request.POST['id'])
    number = request.POST['number']
    # print(number)
    # print(goods.goodsNum)
    if form.is_valid():
        new_goods = form.save(commit=False)
        new_goods.owner = request.user
        new_goods.subtotal = float(number) * goods.goodsPrice
        new_goods.goods = goods
        goods.goodsNum -= int(number) 
        goods.goodsSelected += int(number)
        goods.save()
        new_goods.save()
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
        cart = ShoppingCart.objects.get(id=cart_id)
        number = cart.number
        goods = cart.goods
        goods.goodsNum += number
        goods.goodsSelected -= number
        goods.save()
        cart.delete()
    except:
        pass
    form = OrderForm()
    goodss = ShoppingCart.objects.filter(owner=request.user).order_by('id')
    context = {'goodss':goodss,'form':form}
    return render(request,'store/shoppingcart.html', context)

@login_required
def orderCheck(request):
    error_list = {'status':True,'errors':None}
    goodss = request.POST['content']
    # print(goodss)
    content = goodss.split(',')
    content = list(set(content))
    print(content)
    form = OrderForm(request.POST)
    if form.is_valid():
        
        new_order = form.save(commit=False)
        new_order.owner = request.user
        new_order.total = float(request.POST['total'])
        new_order.content = request.POST['content']
        new_order.save()

        for goods_id in content:
            goods = Goods.objects.get(id=int(goods_id))
            carts = goods.shoppingcart_set.filter(owner=request.user)
            for cart in carts:
                form2 = Order_goodsForm()
                order_goods = form2.save(commit=False)
                order_goods.number = cart.number
                order_goods.subtotal = cart.subtotal
                order_goods.order = new_order
                order_goods.goods = cart.goods
                order_goods.save()
                number = cart.number
                cart.delete()
                goods.goodssales += number
                goods.goodsSelected -= number
                # print(goods.goodssales)
                # print(goods.goodsSelected)
                goods.save()

        error_list['status']=True
        return HttpResponse(json.dumps(error_list))
    else:
        error_list['status']=False
        # 将错误信息转换为json格式
        error_list['errors']= form.errors.as_json()
        # 将返回到前台的数据转换为json
        return HttpResponse(json.dumps(error_list))

@login_required
def purchased(request,ogoods_id):
    try:
        ogoods = Order_goods.objects.get(id=ogoods_id)
        dorder = ogoods.order
        dorder.total -= ogoods.subtotal  
        ogoods.delete()
        print(dorder.total)
        if dorder.total == 0.0:
            dorder.delete()
        else:
            dorder.save() 
    except:
        pass
    orders = Order.objects.filter(owner=request.user).order_by('-id')
    # print(orders)
    con_orders = []
    
    for order in orders:
        dic_order = {}
        dic_order["name"] = order.name
        dic_order["telephone"] = order.telephone
        dic_order["address"] = order.address
        dic_order["total"] = order.total
        goodss = []
        order_goodss = order.order_goods_set.filter(order=order)
        for goods in order_goodss:
            goodss.append(goods)
        dic_order["goodss"] = goodss
        # print(dic_order)
        con_orders.append(dic_order)
    # print(con_orders)
    context = {'con_orders':con_orders}
    return render(request,'store/purchased.html', context)