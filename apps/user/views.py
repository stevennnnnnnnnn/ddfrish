from django.shortcuts import render, redirect, HttpResponse
from apps.user.models import User, Address
from apps.goods.models import GoodsSKU
from apps.order.models import OrderGoods, OrderInfo
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_email_active_register
from django.contrib.auth import authenticate, login, logout
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
import re


# /user/register
class RegisterView(View):
    """用户注册视图"""
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
        send_email_active_register(email, username, token)

        # 返回应答
        return redirect(reverse('goods:index'))


# /user/active/token
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


# /user/login
class LoginView(View):
    """用户登录视图"""
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

            # 获取从其他页面跳转过来的登陆后要跳转的地址
            next_url = request.GET.get('next', reverse('goods:index'))
            response = redirect(next_url)
            remember = request.POST.get('remember')
            if remember == 'on':  # 勾选记住用户名，则设置cookie
                response.set_cookie('username', username, max_age=24*3600)
            else:
                response.delete_cookie(username)
            return response

        else:
            return render(request, 'login.html', {'errmsg': '账号或密码错误！'})


# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""
    def get(self, request):
        # 获取用户信息
        user = request.user
        addr_default = Address.objects.get_default_addr(user)
        # 获取用户的浏览信息
        conn = get_redis_connection('default')
        history_key = 'history_%d' % user.id
        sku_ids = conn.lrange(history_key, 0, 4)
        goods_set = []
        for sku_id in sku_ids:
            goods_set.append(GoodsSKU.objects.get(id=sku_id))

        # 组织上下文
        content = {
            'page': 'info',
            'addr_default': addr_default,
            'goods_set': goods_set,
        }
        return render(request, 'user_center_info.html', content)


# /user/order/page
class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""
    def get(self, request, page):
        """显示"""
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 便利获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 便利order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount = amount
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 5)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        return render(request, 'user_center_order.html', context)


# /user/address
class UserAddrView(LoginRequiredMixin, View):
    """用户中心-地址页"""
    # TODO: 增加修改默认地址的功能
    def get(self, request):
        # 获取用户的默认地址信息
        user = request.user
        addr_default = Address.objects.get_default_addr(user)
        addr_all = Address.objects.get_all_addr(user)
        content = {
            'page': 'address',
            'addr_default': addr_default,
            'addr_all': addr_all,
        }
        return render(request, 'user_center_address.html', content)

    def post(self, request):
        # 接受数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_address.html', {'msg': '请填写完整的信息'})

        if not re.match(r'1[3,4,5,7,8]\d{9}$', phone):
            return render(request, 'user_center_address.html', {'msg': '手机号不合法'})

        # if len(zip_code) != 6:
        #     return render(request, 'user_center_address.html', {'errmsg': '邮件编码错误'})

        # 处理业务
        user = request.user

        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回
        return redirect(reverse('user:address'))


# /user/logout
class LogoutView(LoginRequiredMixin, View):
    """退出登录视图"""
    def get(self, request):
        # 会自动清除session
        logout(request)
        return redirect(reverse('user:login'))



