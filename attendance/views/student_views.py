from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import Attendance, LeaveRequest, Enrollment

@login_required
def student_dashboard(request):
    """学生仪表盘"""
    # 获取今日考勤记录
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(
        enrollment__student__openid=request.user.username,
        event__event_date=today
    ).first()
    
    # 获取最近的请假记录
    recent_leave_requests = LeaveRequest.objects.filter(
        enrollment__student__openid=request.user.username
    ).order_by('-created_at')[:5]
    
    context = {
        'today_attendance': today_attendance,
        'recent_leave_requests': recent_leave_requests
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def student_courses(request):
    """学生课程列表"""
    # 获取学生的课程列表
    enrollments = Enrollment.objects.filter(
        student__openid=request.user.username
    )
    context = {
        'enrollments': enrollments
    }
    return render(request, 'student/courses.html', context)

@login_required
def student_attendance(request):
    """学生考勤记录"""
    # 获取学生的考勤记录
    records = Attendance.objects.filter(
        enrollment__student__openid=request.user.username
    ).order_by('-event__event_date')
    
    context = {
        'records': records
    }
    return render(request, 'student/attendance.html', context)

@login_required
def submit_leave_request(request):
    """提交请假申请"""
    if request.method == 'POST':
        # 处理请假申请逻辑
        pass
    return render(request, 'student/leave_request.html')

@login_required
def leave_request_history(request):
    """请假记录历史"""
    # 获取学生的请假记录
    leave_requests = LeaveRequest.objects.filter(
        enrollment__student__openid=request.user.username
    ).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'student/leave_history.html', context) 