from django.urls import path
from apps.goods.views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('detail/<int:goods_id>', DetailView.as_view(), name='detail'),
    path('list/<int:type_id>/<int:page>', ListView.as_view(), name='list'),
]

