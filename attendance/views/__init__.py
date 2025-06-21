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
    event_attendance_records_api,
    teacher_statistics,
    teacher_update_profile,
    teacher_change_password
)

from .admin_views import (
    admin_dashboard,
    manage_users,
    manage_departments_majors,
    manage_courses,
    admin_statistics,
    admin_profile
)

from .wechat_notify import wechat_notify
from . import wechat_views

# 基础视图函数
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from ..models import Attendance, Student, Teacher, AttendanceEvent, Enrollment
from django.http import JsonResponse, HttpResponse
import qrcode
from io import BytesIO
from attendance.services.wechat_service import WeChatService
from django.views.decorators.csrf import csrf_exempt
import requests

def index(request):
    """首页视图，根据用户身份跳转到对应页面"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'teacher'):
        return redirect('teacher_dashboard')
    elif hasattr(request.user, 'student'):
        return redirect('student_dashboard')
    else:
        logout(request)
        messages.error(request, '用户身份异常，请联系管理员。')
        return redirect('login')

def login_view(request):
    """用户登录"""
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
    
    return render(request, 'login.html')

def logout_view(request):
    """用户登出"""
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
    """考勤检查API"""
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
    """扫码签到页面"""
    event_id = request.GET.get('event_id')
    openid = request.GET.get('openid')
    code = request.GET.get('code')
    
    context = {
        'course_code': '',
        'course_name': '',
        'student_name': '',
        'student_id': ''
    }
    
    # 如果没有openid但有code，先换openid
    if not openid and code:
        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET
        url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
        resp = requests.get(url)
        data = resp.json()
        openid = data.get('openid')
        if openid:
            import urllib.parse
            params = {'event_id': event_id, 'openid': openid}
            redirect_url = f"/scan-qr-page/?{urllib.parse.urlencode(params)}"
            return redirect(redirect_url)
        else:
            context['result'] = 'fail'
            context['message'] = '微信授权失败，无法获取openid。'
            return render(request, 'student/scan_result.html', context)
            
    # 参数验证
    if not event_id or not openid:
        context['result'] = 'fail'
        context['message'] = '缺少参数，无法签到。'
        return render(request, 'student/scan_result.html', context)
        
    # TODO: 处理扫码签到逻辑
    return render(request, 'student/scan_result.html', context) 