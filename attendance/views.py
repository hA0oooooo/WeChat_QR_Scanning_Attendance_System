from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import SystemSettings, PermissionSettings, SystemLog, AttendanceEvent, AttendanceRecord, Course, Student, Teacher
from .utils import log_activity

def index(request):
    """首页视图"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        elif request.user.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    return render(request, 'common/index.html')

def login_view(request):
    """登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_activity(user, '用户登录', True)
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误')
    return render(request, 'common/login.html')

def logout_view(request):
    """登出视图"""
    if request.user.is_authenticated:
        log_activity(request.user, '用户登出', True)
        logout(request)
    return redirect('login')

@login_required
def settings_view(request):
    """系统设置页面视图"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以访问系统设置")
    
    context = {
        'settings': SystemSettings.objects.first(),
        'permissions': PermissionSettings.objects.first(),
        'logs': SystemLog.objects.all().order_by('-timestamp')[:100]  # 只显示最近100条日志
    }
    return render(request, 'admin/settings.html', context)

@login_required
@require_http_methods(["POST"])
def update_system_settings(request):
    """更新系统设置"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以修改系统设置")
    
    try:
        settings = SystemSettings.objects.first()
        if not settings:
            settings = SystemSettings.objects.create()
        
        settings.system_name = request.POST.get('system_name')
        settings.attendance_start_time = request.POST.get('attendance_start_time')
        settings.attendance_end_time = request.POST.get('attendance_end_time')
        settings.late_threshold = int(request.POST.get('late_threshold', 15))
        settings.early_leave_threshold = int(request.POST.get('early_leave_threshold', 15))
        settings.max_leave_days = int(request.POST.get('max_leave_days', 30))
        settings.save()
        
        log_activity(request.user, '更新系统设置', True)
        return JsonResponse({'success': True})
    except Exception as e:
        log_activity(request.user, f'更新系统设置失败: {str(e)}', False)
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def update_permission_settings(request):
    """更新权限设置"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以修改权限设置")
    
    try:
        permissions = PermissionSettings.objects.first()
        if not permissions:
            permissions = PermissionSettings.objects.create()
        
        permissions.student_view_attendance = request.POST.get('student_view_attendance') == 'on'
        permissions.student_apply_leave = request.POST.get('student_apply_leave') == 'on'
        permissions.teacher_create_attendance = request.POST.get('teacher_create_attendance') == 'on'
        permissions.teacher_approve_leave = request.POST.get('teacher_approve_leave') == 'on'
        permissions.save()
        
        log_activity(request.user, '更新权限设置', True)
        return JsonResponse({'success': True})
    except Exception as e:
        log_activity(request.user, f'更新权限设置失败: {str(e)}', False)
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["GET"])
def export_logs(request):
    """导出系统日志"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以导出系统日志")
    
    try:
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="system_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['时间', '用户', '操作', 'IP地址', '状态'])
        
        logs = SystemLog.objects.all().order_by('-timestamp')
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.username,
                log.action,
                log.ip_address,
                '成功' if log.status else '失败'
            ])
        
        log_activity(request.user, '导出系统日志', True)
        return response
    except Exception as e:
        log_activity(request.user, f'导出系统日志失败: {str(e)}', False)
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def clear_logs(request):
    """清空系统日志"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以清空系统日志")
    
    try:
        SystemLog.objects.all().delete()
        log_activity(request.user, '清空系统日志', True)
        return JsonResponse({'success': True})
    except Exception as e:
        log_activity(request.user, f'清空系统日志失败: {str(e)}', False)
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def student_dashboard(request):
    """学生仪表板"""
    if not hasattr(request.user, 'student'):
        raise PermissionDenied("只有学生可以访问此页面")
    return render(request, 'student/dashboard.html')

@login_required
def teacher_dashboard(request):
    """教师仪表板"""
    if not hasattr(request.user, 'teacher'):
        raise PermissionDenied("只有教师可以访问此页面")
    return render(request, 'teacher/dashboard.html')

@login_required
def admin_dashboard(request):
    """管理员仪表板"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以访问此页面")
    return render(request, 'admin/dashboard.html')

@login_required
def scan_qr_code(request):
    """扫描二维码"""
    if request.method == 'POST':
        qr_code = request.POST.get('qr_code')
        try:
            event = AttendanceEvent.objects.get(qr_code=qr_code, is_active=True)
            # 处理考勤逻辑
            return JsonResponse({'success': True})
        except AttendanceEvent.DoesNotExist:
            return JsonResponse({'success': False, 'message': '无效的二维码'})
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
def attendance(request):
    """考勤页面"""
    return render(request, 'common/attendance.html')

@login_required
def attendance_records(request):
    """考勤记录"""
    records = AttendanceRecord.objects.all().order_by('-timestamp')
    return render(request, 'common/attendance_records.html', {'records': records})

@login_required
def attendance_stats(request):
    """考勤统计"""
    return render(request, 'common/attendance_stats.html')

@login_required
def student_courses(request):
    """学生课程列表"""
    if not hasattr(request.user, 'student'):
        raise PermissionDenied("只有学生可以访问此页面")
    courses = request.user.student.courses.all()
    return render(request, 'student/courses.html', {'courses': courses})

@login_required
def student_attendance(request):
    """学生考勤记录"""
    if not hasattr(request.user, 'student'):
        raise PermissionDenied("只有学生可以访问此页面")
    records = AttendanceRecord.objects.filter(student=request.user.student).order_by('-timestamp')
    return render(request, 'student/attendance.html', {'records': records})

@login_required
def teacher_courses(request):
    """教师课程列表"""
    if not hasattr(request.user, 'teacher'):
        raise PermissionDenied("只有教师可以访问此页面")
    courses = request.user.teacher.courses.all()
    return render(request, 'teacher/courses.html', {'courses': courses})

@login_required
def create_attendance_event(request):
    """创建考勤事件"""
    if not hasattr(request.user, 'teacher'):
        raise PermissionDenied("只有教师可以访问此页面")
    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, id=course_id, teacher=request.user.teacher)
        event = AttendanceEvent.objects.create(
            course=course,
            teacher=request.user.teacher,
            is_active=True
        )
        return JsonResponse({'success': True, 'qr_code': event.qr_code})
    courses = request.user.teacher.courses.all()
    return render(request, 'teacher/create_attendance.html', {'courses': courses})

@login_required
def view_attendance_results(request, event_id):
    """查看考勤结果"""
    if not hasattr(request.user, 'teacher'):
        raise PermissionDenied("只有教师可以访问此页面")
    event = get_object_or_404(AttendanceEvent, id=event_id, teacher=request.user.teacher)
    records = AttendanceRecord.objects.filter(event=event)
    return render(request, 'teacher/attendance_results.html', {
        'event': event,
        'records': records
    })

@login_required
def manage_students(request):
    """管理学生"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以访问此页面")
    students = Student.objects.all()
    return render(request, 'admin/manage_students.html', {'students': students})

@login_required
def manage_teachers(request):
    """管理教师"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以访问此页面")
    teachers = Teacher.objects.all()
    return render(request, 'admin/manage_teachers.html', {'teachers': teachers})

@login_required
def manage_courses(request):
    """管理课程"""
    if not request.user.is_staff:
        raise PermissionDenied("只有管理员可以访问此页面")
    courses = Course.objects.all()
    return render(request, 'admin/manage_courses.html', {'courses': courses})

@login_required
def check_attendance(request):
    """检查考勤"""
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        student_id = request.POST.get('student_id')
        try:
            event = AttendanceEvent.objects.get(id=event_id, is_active=True)
            student = Student.objects.get(id=student_id)
            record = AttendanceRecord.objects.create(
                event=event,
                student=student,
                status='present'
            )
            return JsonResponse({'success': True})
        except (AttendanceEvent.DoesNotExist, Student.DoesNotExist):
            return JsonResponse({'success': False, 'message': '无效的考勤事件或学生'})
    return JsonResponse({'success': False, 'message': '无效的请求方法'}) 