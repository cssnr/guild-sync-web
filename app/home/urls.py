from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('about/', views.about_view, name='about'),
    path('server/<str:serverid>/', views.server_view, name='server'),
    path('callback/', views.callback_view, name='callback'),
    path('client/auth/', views.client_auth, name='auth'),
    path('client/upload/', views.client_upload, name='upload'),
]
