from django.urls import path, re_path
from apps.user.views import *


urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    re_path('active/(?P<token>.*)$', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', UserInfoView.as_view(), name='info'),
    path('order/<int:page>', UserOrderView.as_view(), name='order'),
    path('address', UserAddrView.as_view(), name='address'),

]

