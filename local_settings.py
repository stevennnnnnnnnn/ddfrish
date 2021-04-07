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