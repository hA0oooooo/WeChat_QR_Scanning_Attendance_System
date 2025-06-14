from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # 管理后台
    path("admin/", admin.site.urls),
    
    # 包含应用的URL配置
    path("", include('attendance.urls')),
    
    # 基础页面
    path("", views.index, name='index'),
    path("login/", views.login_view, name='login'),
    path("logout/", views.logout_view, name='logout'),
    
    # 学生相关
    path("student/dashboard/", views.student_dashboard, name='student_dashboard'),
    path("student/courses/", views.student_courses, name='student_courses'),
    path("student/attendance/", views.student_attendance, name='student_attendance'),
    path("student/leave/request/", views.submit_leave_request, name='submit_leave_request'),
    path("student/leave/history/", views.leave_request_history, name='leave_request_history'),
    path("student/profile/", views.student_profile, name='student_profile'),
    path("student/leave/", views.student_leave, name='student_leave'),
    
    # 教师相关
    path("teacher/dashboard/", views.teacher_dashboard, name='teacher_dashboard'),
    path("teacher/courses/", views.teacher_courses, name='teacher_courses'),
    path("teacher/course/<str:course_id>/", views.course_detail, name='course_detail'),
    path("teacher/attendance/create/", views.create_attendance_event, name='create_attendance_event'),
    path("teacher/attendance/results/<int:event_id>/", views.view_attendance_results, name='view_attendance_results'),
    path("teacher/profile/", views.teacher_profile, name='teacher_profile'),
    path("teacher/leave/approve/<int:request_id>/", views.approve_leave_request, name='approve_leave_request'),
    path("teacher/leave/list/", views.leave_request_list, name='leave_request_list'),
    
    # 管理员相关
    path("admin/dashboard/", views.admin_dashboard, name='admin_dashboard'),
    path("admin/students/", views.manage_students, name='manage_students'),
    path("admin/teachers/", views.manage_teachers, name='manage_teachers'),
    path("admin/courses/", views.manage_courses, name='manage_courses'),
    path("admin/departments/", views.manage_departments, name='manage_departments'),
    path("admin/majors/", views.manage_majors, name='manage_majors'),
    
    # 考勤相关
    path("attendance/", views.attendance, name='attendance'),
    path("attendance/records/", views.attendance_records, name='attendance_records'),
    path("attendance/stats/", views.attendance_stats, name='attendance_stats'),
    
    # API接口
    path("api/scan-qr/", views.scan_qr_code, name='scan_qr_code'),
    path("api/attendance/check/", views.check_attendance, name='check_attendance'),
]

# 添加静态文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) 