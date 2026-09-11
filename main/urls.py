from django.urls import path, register_converter

from . import views

app_name = 'main'
urlpatterns = [


    path('about/', views.AboutView.as_view(), name='about'),
    path('app/<int:app_id>/', views.AppDetailView.as_view(), name='app_detail'),
    path('new/', views.NewAppView.as_view(), name='new'),


    path('', views.index, name='index'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('top/',views.top,name='top'),
    path('free/',views.free,name='free'),
    path('no_category/',views.no_category,name='no_category'),
    path('cheap/',views.cheap,name='cheap'),
    path('free/<int:category_id>/', views.free_in_category, name='free_in_category'),
    path('developer/<str:developer_name>/', views.developer, name='developer'),
    path('app/secure/<uuid:unique_key>/', views.secure_app, name='secure_app'),
    path('free-apps/', views.apps_list, {'is_free': True}, name='free_apps'),
    path('paid-apps/', views.apps_list, {'is_free': False}, name='paid_apps'),
    path('api/app/<int:app_id>/', views.api_app_detail, name='api_app_detail'),
]