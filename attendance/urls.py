from django.urls import path
from .views import (
    index, login_view, scan_qr_code, check_attendance,
    student_dashboard, student_courses, student_course_detail, student_attendance,
    submit_leave_request, leave_request_history, student_profile, attendance_statistics,
    teacher_dashboard, teacher_courses, course_detail,
    manage_attendance_events, toggle_event_status,
    create_attendance_event, view_attendance_results,
    leave_request_list, approve_leave_request, teacher_profile,
    event_qr_code, event_detail, teacher_statistics,
    teacher_update_profile, teacher_change_password,
    admin_dashboard, student_course_attendance,
    course_all_students_attendance, wechat_views,
    scan_qr_page,
    event_attendance_records_api
)
from .views.admin_views import (
    manage_users, manage_departments_majors, manage_courses, 
    admin_statistics, admin_profile, update_department, delete_department,
    update_major, delete_major, add_department, add_major,
    get_majors, get_departments, get_teachers, get_students, add_student, add_teacher, delete_student, delete_teacher,
    update_student, update_teacher, add_course, update_course, delete_course,
    manage_teaching_assignment, manage_enrollment, add_teaching_assignment,
    update_teaching_assignment, delete_teaching_assignment, add_enrollment, delete_enrollment,
    add_class_schedule, update_class_schedule, delete_class_schedule
)
from .views.student_views import update_profile, change_password
from .views.wechat_notify import wechat_notify
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # 基础页面
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    
    # 管理员相关
    path('manage/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('manage/users/', manage_users, name='manage_users'),
    path('manage/departments-majors/', manage_departments_majors, name='manage_departments_majors'),
    path('manage/courses/', manage_courses, name='manage_courses'),
    path('manage/statistics/', admin_statistics, name='admin_statistics'),
    path('manage/profile/', admin_profile, name='admin_profile'),
    
    # API接口 - 院系专业管理
    path('api/get-departments/', get_departments, name='get_departments'),
    path('api/get-majors/', get_majors, name='get_majors'),
    path('api/get-teachers/', get_teachers, name='get_teachers'),
    path('api/get-students/', get_students, name='get_students'),
    path('api/add-department/', add_department, name='add_department'),
    path('api/update-department/', update_department, name='update_department'),
    path('api/delete-department/', delete_department, name='delete_department'),
    path('api/add-major/', add_major, name='add_major'),
    path('api/update-major/', update_major, name='update_major'),
    path('api/delete-major/', delete_major, name='delete_major'),
    
    # API接口 - 人员管理
    path('api/add-student/', add_student, name='add_student'),
    path('api/update-student/', update_student, name='update_student'),
    path('api/delete-student/', delete_student, name='delete_student'),
    path('api/add-teacher/', add_teacher, name='add_teacher'),
    path('api/update-teacher/', update_teacher, name='update_teacher'),
    path('api/delete-teacher/', delete_teacher, name='delete_teacher'),
    
    # API接口 - 课程管理
    path('api/add-course/', add_course, name='add_course'),
    path('api/update-course/', update_course, name='update_course'),
    path('api/delete-course/', delete_course, name='delete_course'),
    
    # 管理页面 - 课程相关
    path('manage/teaching-assignment/<path:course_id>/', manage_teaching_assignment, name='manage_teaching_assignment'),
    path('manage/enrollment/<path:course_id>/', manage_enrollment, name='manage_enrollment'),
    
    # API接口 - 教学安排管理
    path('api/add-teaching-assignment/', add_teaching_assignment, name='add_teaching_assignment'),
    path('api/update-teaching-assignment/', update_teaching_assignment, name='update_teaching_assignment'),
    path('api/delete-teaching-assignment/', delete_teaching_assignment, name='delete_teaching_assignment'),
    
    # API接口 - 选课管理
    path('api/add-enrollment/', add_enrollment, name='add_enrollment'),
    path('api/delete-enrollment/', delete_enrollment, name='delete_enrollment'),
    
    # API接口 - 课程时间安排管理
    path('api/add-class-schedule/', add_class_schedule, name='add_class_schedule'),
    path('api/update-class-schedule/', update_class_schedule, name='update_class_schedule'),
    path('api/delete-class-schedule/', delete_class_schedule, name='delete_class_schedule'),
    
    # API接口
    path('api/scan-qr-code/', scan_qr_code, name='scan_qr_code'),
    path('api/check-attendance/', check_attendance, name='check_attendance'),
    
    # 学生相关
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/courses/', student_courses, name='student_courses'),
    path('student/course/<path:course_id>/', student_course_detail, name='student_course_detail'),
    path('student/attendance/', student_attendance, name='student_attendance'),
    path('student/statistics/', attendance_statistics, name='attendance_statistics'),
    path('student/leave/submit/', submit_leave_request, name='submit_leave_request'),
    path('student/leave/history/', leave_request_history, name='leave_request_history'),
    path('student/profile/', student_profile, name='student_profile'),
    path('student/profile/update/', update_profile, name='update_profile'),
    path('student/profile/change-password/', change_password, name='change_password'),
    
    # 教师相关
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/courses/', teacher_courses, name='teacher_courses'),
    path('teacher/course/<path:course_id>/', course_detail, name='course_detail'),
    path('teacher/course/<path:course_id>/all-attendance/', course_all_students_attendance, name='course_all_students_attendance'),
    path('teacher/course/<path:course_id>/student/<str:stu_id>/attendance/', student_course_attendance, name='student_course_attendance'),
    path('teacher/course/<path:course_id>/events/', manage_attendance_events, name='manage_attendance_events'),
    path('teacher/event/<int:event_id>/toggle/', toggle_event_status, name='toggle_event_status'),
    path('teacher/course/<path:course_id>/attendance/create/', create_attendance_event, name='create_attendance_event'),
    path('teacher/event/<int:event_id>/qr/', event_qr_code, name='event_qr_code'),
    path('teacher/event/<int:event_id>/results/', view_attendance_results, name='view_attendance_results'),
    path('teacher/event/<int:event_id>/detail/', event_detail, name='event_detail'),
    path('teacher/event/<int:event_id>/records/', event_attendance_records_api, name='event_attendance_records_api'),
    path('teacher/leave-requests/', leave_request_list, name='leave_request_list'),
    path('teacher/leave-request/<int:leave_request_id>/approve/', approve_leave_request, name='approve_leave_request'),
    path('teacher/profile/', teacher_profile, name='teacher_profile'),
    path('teacher/profile/update/', teacher_update_profile, name='teacher_update_profile'),
    path('teacher/profile/change-password/', teacher_change_password, name='teacher_change_password'),
    path('teacher/statistics/', teacher_statistics, name='teacher_statistics'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('wechat/get_openid/', wechat_views.get_openid, name='wechat_get_openid'),
    path('wechat/notify/', wechat_notify, name='wechat_notify'),
    path('scan-qr-page/', scan_qr_page, name='scan_qr_page'),
] 