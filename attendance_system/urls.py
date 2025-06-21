from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),  # Django后台
    path('', include('attendance.urls')),  # 业务路由
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]
