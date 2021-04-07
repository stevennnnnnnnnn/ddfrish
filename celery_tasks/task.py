from celery import Celery
from django.core.mail import send_mail
from django.conf import settings

#####################################
# worker 设置项----来源于ddfirsh/wsgi.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ddfrish.settings')
django.setup()
#####################################

app = Celery('celery_tasks.task', broker='redis://127.0.0.1:6379/8')


@app.task
def send_emial_active_register(to_email, username, token):
    """定义发送邮件celery异步任务函数"""

    subject = '天天生鲜注册激活信息'
    message = ''
    html_message = '<h1>%s, 欢迎注册成为天天生鲜会员<h1>' \
                   '请点击下面链接激活账户<br/>' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)