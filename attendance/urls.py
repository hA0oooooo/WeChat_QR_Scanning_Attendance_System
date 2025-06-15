from django.urls import path
from .views import (
    index, login_view, scan_qr_code, check_attendance,
    student_dashboard, student_courses, student_attendance,
    submit_leave_request, leave_request_history, student_profile,
    teacher_dashboard, teacher_courses, course_detail,
    manage_attendance_events, toggle_event_status,
    create_attendance_event, view_attendance_results,
    leave_request_list, approve_leave_request, teacher_profile,
    event_qr_code, event_detail,
    admin_dashboard, student_course_attendance,
    course_all_students_attendance
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # 基础页面
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    # 管理员仪表盘
    path('manage/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # API接口
    path('api/scan-qr-code/', scan_qr_code, name='scan_qr_code'),
    path('api/check-attendance/', check_attendance, name='check_attendance'),
    
    # 学生相关
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/courses/', student_courses, name='student_courses'),
    path('student/attendance/', student_attendance, name='student_attendance'),
    path('student/leave/submit/', submit_leave_request, name='submit_leave_request'),
    path('student/leave/history/', leave_request_history, name='leave_request_history'),
    path('student/profile/', student_profile, name='student_profile'),
    
    # 教师相关
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', teacher_courses, name='teacher_courses'),
    path('teacher/course/<str:course_id>/', course_detail, name='course_detail'),
    path('teacher/course/<str:course_id>/all-attendance/', course_all_students_attendance, name='course_all_students_attendance'),
    path('teacher/course/<str:course_id>/student/<str:stu_id>/attendance/', student_course_attendance, name='student_course_attendance'),
    path('teacher/course/<str:course_id>/events/', manage_attendance_events, name='manage_attendance_events'),
    path('teacher/event/<int:event_id>/toggle/', toggle_event_status, name='toggle_event_status'),
    path('teacher/course/<str:course_id>/attendance/create/', create_attendance_event, name='create_attendance_event'),
    path('teacher/event/<int:event_id>/qr/', event_qr_code, name='event_qr_code'),
    path('teacher/event/<int:event_id>/results/', view_attendance_results, name='view_attendance_results'),
    path('teacher/event/<int:event_id>/detail/', event_detail, name='event_detail'),
    path('teacher/leave-requests/', leave_request_list, name='leave_request_list'),
    path('teacher/leave-request/<int:leave_request_id>/approve/', approve_leave_request, name='approve_leave_request'),
    path('teacher/profile/', teacher_profile, name='teacher_profile'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
] 