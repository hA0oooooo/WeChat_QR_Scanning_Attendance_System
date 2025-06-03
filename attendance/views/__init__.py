from .student_views import (
    student_dashboard,
    student_courses,
    student_attendance,
    submit_leave_request,
    leave_request_history
)

from .teacher_views import (
    teacher_dashboard,
    teacher_courses,
    create_attendance_event,
    view_attendance_results,
    approve_leave_request,
    leave_request_list
)

from .admin_views import (
    admin_dashboard,
    manage_students,
    manage_teachers,
    manage_courses,
    manage_departments,
    manage_majors,
    manage_classes
)

# 基础视图函数
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from ..models import AttendanceRecord

def index(request):
    """首页视图"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # 获取今日考勤记录
    today = timezone.now().date()
    today_attendance = AttendanceRecord.objects.filter(
        user=request.user,
        date=today
    ).first()
    
    context = {
        'today_attendance': today_attendance
    }
    return render(request, 'attendance/index.html', context)

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
    return render(request, 'attendance/login.html')

def logout_view(request):
    """退出登录视图"""
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('login') 