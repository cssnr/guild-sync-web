from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    path('', views.start_oauth, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('callback/', views.oauth_callback, name='callback'),
]
