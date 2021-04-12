from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from apps.goods.models import *
from apps.order.models import OrderGoods
from django_redis import get_redis_connection
from django.core.cache import cache
from django.core.paginator import Paginator
# Create your views here.


class IndexView(View):
    """首页视图"""
    def get(self, request):
        context = cache.get('index_page_data')
        if context is None:
            # 首页商品种类
            goods_types = GoodsType.objects.all()
            # 首页轮播商品信息
            goods_banner = IndexGoodsBanner.objects.all().order_by('index')
            # 首页促销活动信息
            promotion_info = IndexPromotionBanner.objects.all().order_by('index')
    
            # 首页分类展示信息
            for types in goods_types:
                image_banner = IndexTypeGoodsBanner.objects.filter(type=types, display_type=1).order_by('index')
                title_banner = IndexTypeGoodsBanner.objects.filter(type=types, display_type=0).order_by('index')
                # 给每个查询集添加属性
                types.image_banner = image_banner
                types.title_banner = title_banner
            # 组织上下文
            context = {
                'goods_types': goods_types,
                'goods_banner': goods_banner,
                'promotion_info': promotion_info,
            }
            
            # 设置缓存 (key, value, timeout)
            cache.set('index_page_data', context, 3600)
        
        # 获取购物车信息
        cart_info = 0
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            if conn.exists(cart_key):
                cart_info = conn.hlen(cart_key)
            else:
                cart_info = 0
        context.update(cart_info=cart_info)
        
        return render(request, 'index.html', context)
    

# detail/goods_id
class DetailView(View):
    """商品详情页视图"""
    def get(self, request, goods_id):
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_comments = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取同一分类中新品信息
        new_goods = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:3]
        
        # 获取同一SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        
        # 组织上下文
        context = {
            'types': types,
            'sku': sku,
            'sku_comments': sku_comments,
            'new_goods': new_goods,
            'same_spu_skus': same_spu_skus,
        }
        
        # 获取用户购物车中商品的数目
        cart_info = 0
        user = request.user
        if user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            if conn.exists(cart_key):
                cart_info = conn.hlen(cart_key)
            else:
                cart_info = 0
            # 添加浏览记录
            history_key = 'history_%d' % user.id
            # 移除表中原有的该商品记录
            conn.lrem(history_key, 0, goods_id)
            # 移动到最左侧
            conn.lpush(history_key, goods_id)
            # 修剪列表长度，只保留最近的5条记录
            conn.ltrim(history_key, 0, 4)

        context.update(cart_info=cart_info)
        
        # 返回模板
        return render(request, 'detail.html', context)


# list/type_id/page?sort=
class ListView(View):
    """某种商品类型列表视图"""
    def get(self, request, type_id, page):
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取排序的方式 # 获取分类商品的信息
        # sort=default 按照默认id排序
        # sort=price 按照商品价格排序
        # sort=hot 按照商品销量排序
        sort = request.GET.get('sort')

        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus, 5)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)

        # 进行页码的控制，页面上最多显示5个页码
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

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车中商品的数目
        user = request.user
        cart_info = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_info = conn.hlen(cart_key)

        # 组织模板上下文
        context = {'type': type, 'types': types,
                   'skus_page': skus_page,
                   'new_skus': new_skus,
                   'cart_info': cart_info,
                   'pages': pages,
                   'sort': sort}

        # 使用模板
        return render(request, 'list.html', context)