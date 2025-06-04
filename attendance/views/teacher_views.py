from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from ..models import Course, AttendanceEvent, Attendance, LeaveRequest, TeachingAssignment

@login_required
def teacher_dashboard(request):
    """教师仪表盘"""
    # 获取教师的课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    
    # 获取今日考勤事件
    today = timezone.now().date()
    today_events = AttendanceEvent.objects.filter(
        course__in=courses,
        event_date=today
    )
    
    # 获取待处理的请假申请
    pending_leave_requests = LeaveRequest.objects.filter(
        event__course__in=courses,
        approval_status='pending'
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
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    context = {
        'courses': courses
    }
    return render(request, 'teacher/courses.html', context)

@login_required
def create_attendance_event(request):
    """创建考勤事件"""
    if request.method == 'POST':
        course_id = request.POST.get('course')
        event_date = request.POST.get('event_date')
        scan_start_time = request.POST.get('scan_start_time')
        scan_end_time = request.POST.get('scan_end_time')
        
        course = get_object_or_404(Course, course_id=course_id, teachingassignment__teacher__teacher_id=request.user.username)
        
        event = AttendanceEvent.objects.create(
            course=course,
            event_date=event_date,
            scan_start_time=scan_start_time,
            scan_end_time=scan_end_time
        )
        
        messages.success(request, '考勤事件创建成功')
        return redirect('view_attendance_results', event_id=event.event_id)
    
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    context = {
        'courses': courses
    }
    return render(request, 'teacher/create_attendance.html', context)

@login_required
def view_attendance_results(request, event_id):
    """查看考勤结果"""
    event = get_object_or_404(AttendanceEvent, event_id=event_id, course__teachingassignment__teacher__teacher_id=request.user.username)
    records = Attendance.objects.filter(event=event)
    
    context = {
        'event': event,
        'records': records
    }
    return render(request, 'teacher/attendance_results.html', context)

@login_required
def approve_leave_request(request, request_id):
    """审批请假申请"""
    leave_request = get_object_or_404(LeaveRequest, leave_request_id=request_id, event__course__teachingassignment__teacher__teacher_id=request.user.username)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        leave_request.approval_status = status
        leave_request.approver_notes = remarks
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
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    leave_requests = LeaveRequest.objects.filter(
        event__course__in=courses
    ).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'teacher/leave_list.html', context) 