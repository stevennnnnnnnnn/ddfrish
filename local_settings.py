LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

# mysql
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ddfrish',
#         'USER': 'root',
#         'PASSWORD': 'mysql',
#         'HOST': 'localhost',
#         'PORT': 3306,
#     }
# }

# redis session
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 2
SESSION_REDIS_PASSWORD = ''
SESSION_REDIS_PREFIX = 'session'