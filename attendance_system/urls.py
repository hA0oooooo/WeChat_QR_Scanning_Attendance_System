from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),  # Django后台
    path('', include('attendance.urls')),  # 业务路由
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]

# 添加静态文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) 