from celery import Celery
import os


# 指定Django默认配置文件、这里我们把Celery相关配置文件放在Django项目的settings.py里面
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ddfrish.settings')

# 创建Celery实例；这里建议指定broker、不指定broker容易出现错误
app = Celery('celery_tasks')

# 指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')

# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks()


