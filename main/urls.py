from django.urls import path, register_converter

from . import views

app_name = 'main'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('app/<int:app_id>/', views.app_detail, name='app_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('new/', views.new, name='new'),
    path('top/',views.top,name='top'),
    path('free/',views.free,name='free'),
    path('no_category/',views.no_category,name='no_category'),
    path('cheap/',views.cheap,name='cheap'),
    path('free/<int:category_id>/', views.free_in_category, name='free_in_category'),

    path('developer/<str:developer_name>/', views.developer, name='developer'),

    path('app/secure/<uuid:unique_key>/', views.secure_app, name='secure_app'),
]