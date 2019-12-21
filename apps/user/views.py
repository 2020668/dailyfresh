from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.utils.six import BytesIO
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import random
from PIL import Image, ImageDraw, ImageFont
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection

from celery_tasks.tasks import send_register_active_email
from user.models import User, Address
from goods.models import GoodsSKU


# Create your views here.


# user/register  显示注册页面
# def register(request):
#     if request.method == 'GET':
#         # 显示注册页面
#         return render(request, 'register.html')
#     else:
#         # 执行注册处理


# 注册
class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 执行注册处理
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        cp_password = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        if password != cp_password:
            return render(request, 'register.html', {'errmsg': '两次密码不一致'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选用户协议'})

        # 数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整,请重新提交'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 获取用户输入的验证码
        # vcode1 = request.POST.get('vcode')
        # # 获取session中的验证码
        # vcode2 = request.session.get('verifycode')
        # if vcode1:
        #     if vcode1 != vcode2:
        #         return render(request, 'register.html', {'errmsg': '验证码错误,请重新输入'})
        # else:
        #     return render(request, 'register.html', {'errmsg': '请输入验证码'})

        # 进行业务处理
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  # 默认激活　去掉
        user.save()

        # 发送激活邮件　包含激活链接　　http://127.0.0.1:8000/user/active/id
        # 激活链接中需要包含用户身份信息 加密

        # 加密用户的身份信息　生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发邮件
        # send_register_active_email.delay(email, username, token)

        subject = '史莱克学院欢迎你'
        message = ''
        html_message = '<h1>{}, 恭喜你正式成为史莱克学院的一员魂师</h1>请点击以下链接激活账号<br/><a href="http://127.0.0.1:8000/user/active/{}">http://127.0.0.1:8000/user/active/{}</a>'.format(
            username, token, token)
        sender = settings.EMAIL_FORM
        receiver = [email]
        send_mail(subject, message, sender, receiver, html_message=html_message)

        # 返回应答 跳转到首页
        return redirect(reverse('goods:index'))


# 用户激活
class ActiveView(View):

    def get(self, request, token):
        # 进行解密　获取用户激活信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            #  获取待激活用户的id
            user_id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转登录页
            return redirect(reverse('user:login'))

        except SignatureExpired:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# /user/login
class LoginView(View):

    def get(self, request):
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    # 执行登录
    def post(self, request):
        username = request.POST['username']
        password = request.POST['pwd']
        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '请输入用户名和密码'})
        # 登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活　记录用户的登录状态
                login(request, user)

                # 获取登录后要跳转的地址 否则跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                response = redirect(next_url)

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == "on":
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                return response

            else:
                # 用户未激活
                print('账户未激活')
                return render(request, 'login.html', {'errmsg': '账户未激活，请前往邮箱激活'})
        else:
            # 用户名或密码错误
            print('用户名或密码错误')
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


# /user/logout
class LogoutView(View):

    def get(self, request):
        # 清除用户的session信息
        logout(request)
        return redirect(reverse('user:login'))


def verify_code(request):
    # 定义变量，用于画面的背景色、宽、高
    back_ground_color = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 120
    height = 35
    # 创建画面对象
    im = Image.new('RGB', (width, height), back_ground_color)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 200):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取４个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象 ubuntu的字体路径是/usr/share/fonts/truetype/freefont
    font = ImageFont.truetype('FreeMono.ttf', 23)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制４个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session 用于进一步验证
    request.session['verifycode'] = rand_str
    # 内存文件操作
    buf = BytesIO()
    # 将图片保持在内存中　格式为png
    im.save(buf, 'png')
    # 将内存中的图片返回给客户端　MIME类型为图片png
    print('图片生成')
    return HttpResponse(buf.getvalue(), 'image/png')


# 用户中心　信息页 /user
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # page='user'
        # 除了你个模板文件传递的模板变量外，django框架会把request.user也传递给模板文件
        # 如果未登录　AnonymousUser类的一个实例　登录则是User类的实例

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # sr = StrictRedis(host='118.24.221.133', port=6379, db=9, password='zuo1988')
        con = get_redis_connection('default')   # setting.py中的配置
        history_key = 'history_{}'.format(user.id)
        # 获取用户最新浏览的5条商品id
        sku_ids = con.lrange(history_key, 0, 4)
        # 从数据库中查询用户浏览的商品信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li
                   }

        return render(request, 'user_center_info.html', context)


# 用户中心　订单页 /user/order
class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        # page='order'
        return render(request, 'user_center_order.html', {'page': 'order'})


# 用户中心　地址页  /user/address
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # page='address'
        # 获取用户的默认收货地址
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    # 添加地址
    def post(self, request):
        # 接收数据
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        # 校验数据
        if not all([receiver, address, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号格式非法'})

        # 业务处理　地址添加
        # 如果已有收货地址　则添加的地址不作为默认地址　否则是默认地址
        # 获取登录用户对应的user对象
        user = request.user
        # try:
        #     address_current = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address_current = None
        address_current = Address.objects.get_default_address(user)
        if address_current:
            is_default = False
        else:
            is_default = True
        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               address=address,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default
                               )

        # 返回应答 刷新地址页面
        return redirect(reverse('user:address'))
