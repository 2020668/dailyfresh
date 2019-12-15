import django
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import time
# import redis
import os

# 在任务处理者一端加
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()

# 使用celery
# 创建Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://118.24.221.133:6379/8')


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    # 发邮件
    subject = '史莱克学院欢迎你'
    message = ''
    html_message = '<h1>{}, 恭喜你正式成为史莱克学院的一员魂师</h1>请点击以下链接激活账号<br/><a href="http://127.0.0.1:8000/user/active/{}">http://127.0.0.1:8000/user/active/{}</a>'.format(
        username, token, token)
    sender = settings.EMAIL_FORM
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)


