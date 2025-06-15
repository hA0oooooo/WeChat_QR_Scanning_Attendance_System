from .student_views import (
    student_dashboard,
    student_courses,
    student_attendance,
    submit_leave_request,
    leave_request_history,
    student_profile,
    student_leave
)

from .teacher_views import (
    teacher_dashboard,
    teacher_courses,
    create_attendance_event,
    view_attendance_results,
    approve_leave_request,
    leave_request_list,
    teacher_profile,
    course_detail,
    manage_attendance_events,
    toggle_event_status,
    event_qr_code,
    event_detail
)

from .admin_views import (
    admin_dashboard,
    manage_students,
    manage_teachers,
    manage_courses,
    manage_departments,
    manage_majors
)

# 基础视图函数
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from ..models import Attendance, Student, Teacher, AttendanceEvent, Enrollment
from django.http import JsonResponse, HttpResponse
import qrcode
from io import BytesIO

def index(request):
    """首页视图：登录后根据用户类型跳转到对应仪表盘"""
    if not request.user.is_authenticated:
        return redirect('login')
    # 管理员
    if request.user.is_superuser or (hasattr(request.user, 'is_staff') and request.user.is_staff):
        return redirect('admin_dashboard')
    # 教师
    if Teacher.objects.filter(teacher_id=request.user.username).exists():
        return redirect('teacher_dashboard')
    # 学生
    if Student.objects.filter(stu_id=request.user.username).exists():
        return redirect('student_dashboard')
    # 其他用户类型
    return HttpResponse("登录成功，欢迎进入系统！")

def login_view(request):
    """登录视图"""
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误')
    # 传递二维码图片URL
    context = {'qr_code_url': '/login/qr/'}
    return render(request, 'login.html', context)

def logout_view(request):
    """退出登录视图"""
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('login')

def scan_qr_code(request):
    """处理微信扫码签到请求"""
    from django.http import JsonResponse
    from django.utils import timezone
    from datetime import datetime, time
    from ..models import AttendanceEvent, Attendance, Student, Enrollment

    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST请求'}, status=405)

    try:
        # 获取请求参数
        qr_code = request.POST.get('qr_code')
        student_openid = request.POST.get('student_openid')

        if not qr_code or not student_openid:
            return JsonResponse({'error': '缺少必要参数'}, status=400)

        # 获取考勤事件
        try:
            event = AttendanceEvent.objects.get(event_id=qr_code)
        except AttendanceEvent.DoesNotExist:
            return JsonResponse({'error': '无效的二维码'}, status=400)

        # 获取学生信息
        try:
            student = Student.objects.get(openid=student_openid)
        except Student.DoesNotExist:
            return JsonResponse({'error': '未找到学生信息'}, status=400)

        # 检查是否已选课
        try:
            enrollment = Enrollment.objects.get(student=student, course=event.course)
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': '未选修该课程'}, status=400)

        # 检查是否重复扫码
        if Attendance.objects.filter(enrollment=enrollment, event=event).exists():
            return JsonResponse({'error': '已经签到过了'}, status=400)

        # 检查是否在考勤时间范围内
        current_time = timezone.now().time()
        if current_time < event.scan_start_time or current_time > event.scan_end_time:
            return JsonResponse({'error': '不在考勤时间范围内'}, status=400)

        # 创建考勤记录
        attendance = Attendance.objects.create(
            enrollment=enrollment,
            event=event,
            scan_time=timezone.now(),
            status=1  # 1表示出勤
        )

        return JsonResponse({
            'success': True,
            'message': '签到成功',
            'attendance_id': attendance.attend_id
        })

    except Exception as e:
        return JsonResponse({'error': f'系统错误: {str(e)}'}, status=500)

def check_attendance(request):
    from django.http import JsonResponse
    return JsonResponse({'success': True, 'message': '考勤检查API-占位'})

def attendance(request):
    from django.http import HttpResponse
    return HttpResponse("考勤页面-占位")

def attendance_records(request):
    from django.http import HttpResponse
    return HttpResponse("考勤记录页面-占位")

def attendance_stats(request):
    from django.http import HttpResponse
    return HttpResponse("考勤统计页面-占位")

def qr_code_view(request):
    """动态生成二维码图片"""
    qr_content = '欢迎扫码登录考勤系统'  # 你可以换成任何内容或token
    img = qrcode.make(qr_content)
    buf = BytesIO()
    img.save(buf, format='PNG')
    image_stream = buf.getvalue()
    return HttpResponse(image_stream, content_type='image/png')

def scan_qr_page(request):
    """扫码签到接口，GET方式，返回签到结果页面"""
    event_id = request.GET.get('event_id')
    openid = request.GET.get('openid')
    context = {}
    if not event_id or not openid:
        context['result'] = 'fail'
        context['message'] = '缺少参数，无法签到。'
        return render(request, 'student/scan_result.html', context)
    try:
        event = AttendanceEvent.objects.get(event_id=event_id)
    except AttendanceEvent.DoesNotExist:
        context['result'] = 'fail'
        context['message'] = '考勤事件不存在。'
        return render(request, 'student/scan_result.html', context)
    try:
        student = Student.objects.get(openid=openid)
    except Student.DoesNotExist:
        context['result'] = 'fail'
        context['message'] = '未找到学生信息。'
        return render(request, 'student/scan_result.html', context)
    try:
        enrollment = Enrollment.objects.get(student=student, course=event.course)
    except Enrollment.DoesNotExist:
        context['result'] = 'fail'
        context['message'] = '未选修该课程，无法签到。'
        return render(request, 'student/scan_result.html', context)
    # 检查时间
    now = timezone.now().time()
    if now < event.scan_start_time or now > event.scan_end_time:
        return JsonResponse({'error': '不在考勤时间范围内，无法签到。'}, status=400)
    # 检查是否已签到
    if Attendance.objects.filter(enrollment=enrollment, event=event).exists():
        return JsonResponse({'error': '您已签到，无需重复操作。'}, status=400)
    # 记录签到
    Attendance.objects.create(
        enrollment=enrollment,
        event=event,
        scan_time=timezone.now(),
        status=1  # 1表示出勤
    )
    context['result'] = 'success'
    context['message'] = '签到成功！'
    return render(request, 'student/scan_result.html', context) 