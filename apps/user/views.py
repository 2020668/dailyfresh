from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
import re
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired

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

        # 发邮件


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
