from django.urls import path, re_path
from apps.user.views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    re_path('active/(?P<token>.*)$', ActivateView.as_view(), name='activate'),
    path('login', LoginView.as_view(), name='login')
]

