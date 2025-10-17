from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('article/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('category/<str:category_name>/', views.category_view, name='category'),
    path('search/', views.search_view, name='search'),
]