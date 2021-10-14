from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('news/', views.news_view, name='news'),
    path('roster/', views.roster_view, name='roster'),
    path('apply/', views.apply_view, name='apply'),
    path('profile/', views.profile_view, name='profile'),
]
