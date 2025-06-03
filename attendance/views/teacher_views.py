from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from ..models import Course, AttendanceEvent, AttendanceRecord, LeaveRequest

@login_required
def teacher_dashboard(request):
    """教师仪表盘"""
    # 获取教师的课程
    courses = Course.objects.filter(teacher=request.user)
    
    # 获取今日考勤事件
    today = timezone.now().date()
    today_events = AttendanceEvent.objects.filter(
        course__in=courses,
        date=today
    )
    
    # 获取待处理的请假申请
    pending_leave_requests = LeaveRequest.objects.filter(
        course__in=courses,
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'courses': courses,
        'today_events': today_events,
        'pending_leave_requests': pending_leave_requests
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def teacher_courses(request):
    """教师课程列表"""
    courses = Course.objects.filter(teacher=request.user)
    context = {
        'courses': courses
    }
    return render(request, 'teacher/courses.html', context)

@login_required
def create_attendance_event(request):
    """创建考勤事件"""
    if request.method == 'POST':
        course_id = request.POST.get('course')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        course = get_object_or_404(Course, id=course_id, teacher=request.user)
        
        event = AttendanceEvent.objects.create(
            course=course,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        
        messages.success(request, '考勤事件创建成功')
        return redirect('view_attendance_results', event_id=event.id)
    
    courses = Course.objects.filter(teacher=request.user)
    context = {
        'courses': courses
    }
    return render(request, 'teacher/create_attendance.html', context)

@login_required
def view_attendance_results(request, event_id):
    """查看考勤结果"""
    event = get_object_or_404(AttendanceEvent, id=event_id, course__teacher=request.user)
    records = AttendanceRecord.objects.filter(event=event)
    
    context = {
        'event': event,
        'records': records
    }
    return render(request, 'teacher/attendance_results.html', context)

@login_required
def approve_leave_request(request, request_id):
    """审批请假申请"""
    leave_request = get_object_or_404(LeaveRequest, id=request_id, course__teacher=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        leave_request.status = status
        leave_request.teacher_remarks = remarks
        leave_request.save()
        
        messages.success(request, '请假申请已处理')
        return redirect('leave_request_list')
    
    context = {
        'leave_request': leave_request
    }
    return render(request, 'teacher/approve_leave.html', context)

@login_required
def leave_request_list(request):
    """请假申请列表"""
    courses = Course.objects.filter(teacher=request.user)
    leave_requests = LeaveRequest.objects.filter(
        course__in=courses
    ).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'teacher/leave_list.html', context) 