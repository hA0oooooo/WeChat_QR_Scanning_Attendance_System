from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
from ..models import AttendanceEvent, Attendance, Enrollment, STATUS_PRESENT
from django.utils import timezone
from django.shortcuts import render, redirect

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
    """处理微信授权回调"""
    try:
        # 获取微信授权code和state
        code = request.GET.get('code')
        state = request.GET.get('state')
        event_id = request.GET.get('event_id')
        
        if not all([code, state, event_id]):
            return HttpResponse('缺少必要参数')
            
        # 验证state
        if not state.startswith('event_'):
            return HttpResponse('无效的state参数')
            
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
            return HttpResponse(f'获取openid失败: {data["errmsg"]}')
            
        openid = data.get('openid')
        if not openid:
            return HttpResponse('获取openid失败')
            
        # 处理签到逻辑
        try:
            event = AttendanceEvent.objects.get(event_id=event_id)
            # 检查考勤事件是否有效
            if event.event_status != 1:  # EVENT_VALID
                return HttpResponse('考勤事件已结束')
                
            # 检查是否在签到时间内
            now = timezone.now()
            if not (event.scan_start_time <= now.time() <= event.scan_end_time):
                return HttpResponse('不在签到时间内')
                
            # 查找学生信息
            enrollment = Enrollment.objects.filter(
                course=event.course,
                student__openid=openid
            ).first()
            
            if not enrollment:
                return HttpResponse('未找到学生信息')
                
            # 检查是否已签到
            existing_attendance = Attendance.objects.filter(
                event=event,
                enrollment=enrollment
            ).first()
            
            if existing_attendance:
                return HttpResponse('已经签到过了')
                
            # 创建签到记录
            Attendance.objects.create(
                event=event,
                enrollment=enrollment,
                status=STATUS_PRESENT,
                scan_time=now
            )
            
            # 返回签到成功页面
            context = {
                'event': event,
                'student': enrollment.student,
                'status': 'success',
                'message': '签到成功'
            }
            return render(request, 'student/scan_result.html', context)
            
        except AttendanceEvent.DoesNotExist:
            return HttpResponse('考勤事件不存在')
            
    except Exception as e:
        return HttpResponse(f'服务器错误: {str(e)}') 