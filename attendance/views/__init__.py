from .student_views import (
    student_dashboard,
    student_courses,
    course_detail as student_course_detail,
    student_attendance,
    submit_leave_request,
    leave_request_history,
    student_profile,
    attendance_statistics,
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
    event_detail,
    student_course_attendance,
    course_all_students_attendance,
    event_attendance_records_api
)

from .admin_views import (
    admin_dashboard,
    manage_students,
    manage_teachers,
    manage_courses,
    manage_departments,
    manage_majors
)

from .wechat_notify import wechat_notify

# 基础视图函数
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from ..models import Attendance, Student, Teacher, AttendanceEvent, Enrollment
from django.http import JsonResponse, HttpResponse
import qrcode
from io import BytesIO
from attendance.services.wechat_service import WeChatService

def index(request):
    """首页视图：登录后根据用户类型跳转到对应仪表盘"""
    if not request.user.is_authenticated:
        return redirect('login')
    # 超级管理员
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    # 教师
    if hasattr(request.user, 'teacher') or request.user.is_staff:
        return redirect('teacher_dashboard')
    # 学生（使用正确的关联关系判断）
    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')
    # 兜底：强制登出并提示
    logout(request)
    messages.error(request, '用户身份异常，请重新登录。')
    return redirect('login')

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
    """处理微信扫码考勤请求"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})

    # 获取请求参数
    qr_code = request.POST.get('qr_code')
    student_id = request.POST.get('student_id')
    openid = request.POST.get('openid')
    signature = request.POST.get('signature')
    timestamp = request.POST.get('timestamp')
    nonce = request.POST.get('nonce')

    # 验证必要参数
    if not all([qr_code, student_id, openid, signature, timestamp, nonce]):
        return JsonResponse({'success': False, 'message': '缺少必要参数'})

    # 初始化微信服务
    wechat_service = WeChatService()

    # 验证签名
    if not wechat_service.verify_signature(signature, timestamp, nonce):
        return JsonResponse({'success': False, 'message': '签名验证失败'})

    # 处理扫码考勤
    result = wechat_service.handle_scan_qr(qr_code, student_id, openid)
    return JsonResponse(result)

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
    """扫码签到接口，支持微信授权code换openid"""
    import requests
    from django.conf import settings
    event_id = request.GET.get('event_id')
    openid = request.GET.get('openid')
    code = request.GET.get('code')
    context = {}
    context['course_code'] = ''
    context['course_name'] = ''
    context['student_name'] = ''
    context['student_id'] = ''
    # 如果没有openid但有code，先换openid
    if not openid and code:
        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET
        url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
        resp = requests.get(url)
        data = resp.json()
        openid = data.get('openid')
        if openid:
            # 换到openid后重定向到自身
            import urllib.parse
            params = {'event_id': event_id, 'openid': openid}
            redirect_url = f"/scan-qr-page/?{urllib.parse.urlencode(params)}"
            from django.shortcuts import redirect
            return redirect(redirect_url)
        else:
            context['result'] = 'fail'
            context['message'] = '微信授权失败，无法获取openid。'
            return render(request, 'student/scan_result.html', context)
    # 原有逻辑
    if not event_id or not openid:
        context['result'] = 'fail'
        context['message'] = '缺少参数，无法签到。'
        return render(request, 'student/scan_result.html', context)
    try:
        event = AttendanceEvent.objects.get(event_id=event_id)
        context['course_code'] = event.course.course_id if hasattr(event.course, 'course_id') else ''
        context['course_name'] = event.course.course_name if hasattr(event.course, 'course_name') else ''
    except AttendanceEvent.DoesNotExist:
        context['result'] = 'fail'
        context['message'] = '考勤事件不存在。'
        return render(request, 'student/scan_result.html', context)
    try:
        student = Student.objects.get(openid=openid)
        context['student_name'] = student.stu_name if hasattr(student, 'stu_name') else ''
        context['student_id'] = student.stu_id if hasattr(student, 'stu_id') else ''
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
    now = timezone.now()
    if now < event.scan_start_time or now > event.scan_end_time:
        context['result'] = 'fail'
        context['message'] = '不在考勤时间范围内，无法签到。'
        return render(request, 'student/scan_result.html', context)
    if Attendance.objects.filter(enrollment=enrollment, event=event).exists():
        context['result'] = 'repeat'
        context['message'] = '您已签到，无需重复操作。'
    else:
        Attendance.objects.create(
            enrollment=enrollment,
            event=event,
            scan_time=now,
            status=1
        )
        context['result'] = 'success'
        context['message'] = '签到成功！'
    return render(request, 'student/scan_result.html', context) 