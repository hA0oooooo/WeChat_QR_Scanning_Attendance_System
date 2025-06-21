from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
from ..models import AttendanceEvent, Attendance, Enrollment, STATUS_PRESENT
from django.utils import timezone
from django.shortcuts import render, redirect
from attendance.services.wechat_service import WeChatService
from attendance.models import Student
import urllib.parse

@csrf_exempt
def get_openid(request):
    """获取微信用户的openid并处理签到"""
    # 支持GET和POST请求
    if request.method not in ['GET', 'POST']:
        return HttpResponse('不支持的请求方法', status=405)
    
    try:
        # 从GET或POST中获取参数
        code = request.GET.get('code') or request.POST.get('code')
        state = request.GET.get('state') or request.POST.get('state')
        event_id = request.GET.get('event_id') or request.POST.get('event_id')
        
        if not all([code, state, event_id]):
            return HttpResponse('缺少必要参数', status=400)
            
        # 验证state
        if not state.startswith('event_'):
            return HttpResponse('无效的state参数', status=400)
            
        # 获取openid
        url = f'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            'appid': settings.WECHAT_APPID,
            'secret': settings.WECHAT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'errcode' in data:
            return HttpResponse(f'获取openid失败: {data["errmsg"]}', status=400)
            
        openid = data.get('openid')
        if not openid:
            return HttpResponse('获取openid失败', status=400)
            
        # 处理签到逻辑
        try:
            event = AttendanceEvent.objects.get(event_id=event_id)
            # 检查考勤事件是否有效
            if event.event_status != 1:  # EVENT_VALID
                return HttpResponse('考勤事件已结束', status=400)
                
            # 检查是否在签到时间内
            now = timezone.now()
            if not (event.scan_start_time <= now.time() <= event.scan_end_time):
                return HttpResponse('不在签到时间内', status=400)
                
            # 查找学生信息
            enrollment = Enrollment.objects.filter(
                course=event.course,
                student__openid=openid
            ).first()
            
            if not enrollment:
                return HttpResponse('未找到学生信息', status=400)
                
            # 检查是否已签到
            existing_attendance = Attendance.objects.filter(
                event=event,
                enrollment=enrollment
            ).first()
            
            if existing_attendance:
                return HttpResponse('已经签到过了', status=400)
                
            # 创建签到记录
            Attendance.objects.create(
                event=event,
                enrollment=enrollment,
                status=STATUS_PRESENT,
                scan_time=now
            )
            
            return HttpResponse('签到成功')
            
        except AttendanceEvent.DoesNotExist:
            return HttpResponse('考勤事件不存在', status=404)
            
    except Exception as e:
        return HttpResponse(f'服务器错误: {str(e)}', status=500)

@csrf_exempt
def scan_qr_page(request):
    """扫码签到接口，支持微信授权code换openid"""
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
            params = {'event_id': event_id, 'openid': openid}
            redirect_url = f"/scan-qr-page/?{urllib.parse.urlencode(params)}"
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
    # 检查考勤记录
    existing_attendance = Attendance.objects.filter(enrollment=enrollment, event=event).first()
    if existing_attendance:
        if existing_attendance.status == 3:
            # 已请假
            context['result'] = 'leave'
            context['message'] = '您已请假无需签到'
            context['scan_time'] = None
        elif existing_attendance.status == 1:
            # 已出勤
            context['result'] = 'success'
            context['message'] = '您已签到无需重复扫码'
            context['scan_time'] = existing_attendance.scan_time
        elif existing_attendance.status == 2:
            # 缺勤，扫码后改为出勤
            existing_attendance.status = 1
            existing_attendance.scan_time = now
            existing_attendance.save()
            context['result'] = 'success'
            context['message'] = '签到成功'
            context['scan_time'] = existing_attendance.scan_time
        else:
            context['result'] = 'fail'
            context['message'] = '考勤状态异常'
    else:
        # 无考勤记录，创建缺勤记录
        attendance = Attendance.objects.create(
            enrollment=enrollment,
            event=event,
            scan_time=now,
            status=2  # 缺勤
        )
        context['result'] = 'success'
        context['message'] = '签到成功'
        context['scan_time'] = attendance.scan_time
    return render(request, 'student/scan_result.html', context)

@csrf_exempt
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