from django.shortcuts import render, redirect, HttpResponse
import re
from apps.user.models import User
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.task import send_emial_active_register
from django.contrib.auth import authenticate, login, logout


class RegisterView(View):
    """"""
    def get(self, request):
        """显示注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """处理注册请求"""
        # 接收数据
        username = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        pwd2 = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, pwd, pwd2, email]):
            # 信息完整性校验
            return render(request, 'register.html', {'errmsg': '请输入完整信息！'})

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            User.username = None
        except Exception as ret:
            return HttpResponse('发生未知错误...', ret)

        if User.username:
            # 用户名是否已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在！'})

        if pwd != pwd2:
            # 两次密码是否相同
            return render(request, 'register.html', {'errmsg': '两次输入的密码不相同！'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 邮箱是否合法
            return render(request, 'register.html', {'errmsg': '邮箱格式错误！'})

        if allow != 'on':
            # 勾选注册协议
            return render(request, 'register.html', {'errmsg': '请勾选注册协议！'})

        # 进行用户注册，使用django自带的user模型类
        user = User.objects.create_user(username=username, email=email, password=pwd)
        user.is_active = 0
        user.save()

        # 生成激活链接： /user/active/加密token
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 过期时间：3600s
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode('utf8')

        # celery异步发送激活邮件
        send_emial_active_register(email, username, token)

        # 返回应答
        return redirect(reverse('goods:index'))


class ActivateView(View):
    """用户激活视图"""
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转登录
            return render(request, 'activate_confirm.html', {'confirm': "激活成功!"})
        except SignatureExpired as e:
            return render(request, 'activate_confirm.html', {'confirm': "激活链接已过期，请重新激活！"})
        except Exception as ret:
            print(ret)
            return render(request, 'activate_confirm.html', {'confirm': "激活链接不存在！"})


class LoginView(View):
    """登录视图"""
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')

        if not all([username, pwd]):  # 检查要素完整性
            return render(request, 'login.html', {'errmsg': '请输入完整的账号密码！'})

        try:  # 检查账号是否存在
            User.objects.get(username=username)
        except:
            return render(request, 'login.html', {'errmsg': '账号不存在！'})

        # 检查账号密码是否正确
        user = authenticate(username=username, password=pwd)
        if user is not None:
            login(request, user)  # 账户验证正确，记录用户登录状态

            response = redirect(reverse('goods:index'))
            remember = request.POST.get('remember')
            if remember == 'on':  # 勾选记住用户名，则设置cookie
                response.set_cookie('username', username, max_age=24*3600)
            else:
                response.delete_cookie(username)
            return response

        else:
            return render(request, 'login.html', {'errmsg': '账号或密码错误！'})



