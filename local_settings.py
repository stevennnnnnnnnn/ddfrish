# STATIC_ROOT = '/home/steven/static'

# celery生成静态Index地址
STATIC_INDEX_PATH = '/www/wwwroot/index.html'


# 修改自用的数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dfresh',
        'USER': 'root',
        'PASSWORD': 'aa991215',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}


# Celery相关配置
# 配置redis作为
CELERY_BROKER_URL = 'redis://localhost:6379/3'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'
CELERY_TIMEZONE = 'Asia/Shanghai'
# 更多参数：https://docs.celeryproject.org/en/stable/userguide/configuration.html


# 配置cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# fastdfs设置
FDFS_CLIENT_CONF = './utils/client.conf'
FDFS_STORAGE_URL = 'http://steven.run/'  # 另一台nginx服务器
DEFAULT_FILE_STORAGE = 'utils.fdfs_storage.FdfsStorage'


# 126 email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.126.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'stevennnn@126.com'  # 发送邮件的邮箱
EMAIL_HOST_PASSWORD = 'LYTKLSNPDNONKKLL'  # 邮箱授权码
# EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)
EMAIL_FROM = '天天生鲜<stevennnn@126.com>'  # EMAIL_FROM 和 EMAIL_HOST_USER必须一样



# 支付宝沙箱APP_ID
ALIPAY_APP_ID = '2021000117636668'
# 支付宝网站回调url地址
ALIPAY_APP_NOTIFY_URL = None
# 支付宝同步return_url地址
ALIPAY_APP_RETURN_URL = 'http://localhost:8000/order/check'


