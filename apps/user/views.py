from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
import re
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import random
from PIL import Image, ImageDraw, ImageFont
from django.utils.six import BytesIO

from celery_tasks.tasks import send_register_active_email
from user.models import User


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
        vcode1 = request.POST.get('vcode')
        # 获取session中的验证码
        vcode2 = request.session.get('verifycode')
        if vcode1 != vcode2:
            return redirect('user/login')

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
        return render(request, 'login.html')


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
    return HttpResponse(buf.getvalue(), 'image/png')
