from django.urls import path
from apps.cart.views import *
from apps.cart import views

urlpatterns = [
    path('', CartInfoView.as_view(), name='cart'),
    path('add', CartAddView.as_view(), name='add'),
    path('update', CartUpdateView.as_view(), name='update'),
    path('delete', CartDeleteView.as_view(), name='delete'),
]

