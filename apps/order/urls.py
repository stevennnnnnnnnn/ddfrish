from django.urls import path
from apps.order.views import *

urlpatterns = [
    path('place', OrderPlaceView.as_view(), name='place'),  # 提交订单页面显示
    path('buy_now', OrderBuyNowView.as_view(), name='buy_now'),  # 提交订单页面显示
    path('commit', OrderCommitView.as_view(), name='commit'),  # 订单创建
    path('pay', OrderPayView.as_view(), name='pay'),  # 订单支付
    path('check', CheckPayView.as_view(), name='check'),  # 查询支付订单结果
    path('comment/<int:order_id>', CommentView.as_view(), name='comment'),  # 订单评论
]

