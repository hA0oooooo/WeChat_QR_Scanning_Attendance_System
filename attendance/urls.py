from django.urls import path
from . import views

urlpatterns = [
    # 系统设置
    path('admin/settings/', views.admin_dashboard, name='settings'),
    path('api/settings/system/', views.update_system_settings, name='update_system_settings'),
] 