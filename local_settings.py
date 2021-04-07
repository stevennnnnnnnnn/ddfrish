LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

# mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ddfrish',
        'USER': 'root',
        'PASSWORD': 'mysql',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

# redis session
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 2
SESSION_REDIS_PASSWORD = ''
SESSION_REDIS_PREFIX = 'session'

# 系统默认的用户验证类为：’auth.User’
# 修改用户验证类为自定义：‘user.User’
AUTH_USER_MODEL = 'user.User'

# tinymce富文本编辑器参数
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400
}

# 126 email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.126.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'stevennnn@126.com'  # 发送邮件的邮箱
EMAIL_HOST_PASSWORD = 'LYTKLSNPDNONKKLL'  # qq邮箱授权码
# EMAIL_USE_TLS = True  # 与SMTP服务器通信时，是否启动TLS链接(安全链接)
EMAIL_FROM = '天天生鲜<stevennnn@126.com>'  # EMAIL_FROM 和 EMAIL_HOST_USER必须一样