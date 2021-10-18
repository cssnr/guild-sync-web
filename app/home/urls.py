from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('news/', views.news_view, name='news'),
    path('server/<str:serverid>/', views.server_view, name='server'),
    path('callback/', views.callback_view, name='callback'),
]
