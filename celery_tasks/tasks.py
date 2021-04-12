from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.goods.models import *
from django.template import loader
import os


@shared_task
def send_email_active_register(to_email, username, token):
    """定义发送邮件celery异步任务函数"""

    subject = '天天生鲜注册激活信息'
    message = ''
    html_message = '<h1>%s, 欢迎注册成为天天生鲜会员<h1>' \
                   '请点击下面链接激活账户<br/>' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]  # 可能是多个收件人
    send_mail(subject, message, sender, receiver, html_message=html_message)


@shared_task
def generate_static_index_html():
    """生成静态首页文件"""
    # 首页商品种类
    goods_types = GoodsType.objects.all()
    # 首页轮播商品信息
    goods_banner = IndexGoodsBanner.objects.all().order_by('index')
    # 首页促销活动信息
    promotion_info = IndexPromotionBanner.objects.all().order_by('index')

    # 首页分类展示信息
    for type in goods_types:
        type.image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        type.title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

    context = {
        'goods_types': goods_types,
        'goods_banner': goods_banner,
        'promotion_info': promotion_info,
    }

    # 加载模板文件
    temp = loader.get_template('static_index.html')
    static_index_html = temp.render(context)
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
