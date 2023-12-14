from . import views
from django.urls import path

urlpatterns = [
    path('members/', views.members, name='members'),
    path('edit/<str:firstName>/', views.edit_item, name='edit_item'),
    path('delete/<str:firstName>/', views.delete_item, name='delete_item'),
    path('inventory/', views.inventory, name='inventory'),
    path('dns/', views.dns_table_data, name='dns'),
    path('distribution/', views.DistributionView.as_view(), name='distribution'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cdn_inventory/', views.cdn_inventory, name='cdn_inventory'),
    path('map/<str:domain_name>/', views.show_map, name='map'),
    path('tab/', views.multi_form, name='tab_form'),
    path('enable_distribution/<str:domain_name>/', views.enable_distribution, name='enable_distribution'),
    path('disable_distribution/<str:domain_name>/', views.disable_distribution, name='disable_distribution'),
    path('delete_distribution/<str:domain_name>/', views.delete_distribution, name='delete_distribution'),
    path('add_distribution/', views.add_distribution, name='add_distribution'),
    path('insights_base/', views.insights_base, name='insights_base'),
    path('insights_base/insight_usage.html', views.insight_usage, name='insight_usage'),
    path('insights_base/insight_monitoring.html', views.insight_monitoring, name='insight_monitoring'),
    path('insights_base/insight_cache_statistics.html', views.insight_stats, name='insight_stats'),        
]
