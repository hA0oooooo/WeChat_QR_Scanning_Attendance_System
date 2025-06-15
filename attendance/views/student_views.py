from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import Attendance, LeaveRequest, Enrollment, AttendanceEvent, Student
from django.http import HttpResponse

@login_required
def student_dashboard(request):
    """学生仪表盘"""
    # 获取学生对象
    student = Student.objects.get(openid=request.user.username)
    today = timezone.now().date()
    # 获取今日所有考勤记录（多门课）
    today_attendance = Attendance.objects.filter(
        enrollment__student=student,
        event__event_date=today
    ).select_related('event__course')
    # 获取最近的请假记录
    recent_leave_requests = LeaveRequest.objects.filter(
        enrollment__student=student
    ).select_related('event__course').order_by('-submit_time')[:5]
    context = {
        'student': student,
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
    """学生查看考勤记录"""
    # 获取学生的考勤记录
    attendance_records = Attendance.objects.filter(
        enrollment__student__openid=request.user.username
    ).order_by('-event__event_date', '-event__scan_start_time')
    
    context = {
        'attendance_records': attendance_records
    }
    return render(request, 'student/attendance.html', context)

@login_required
def submit_leave_request(request):
    """提交请假申请"""
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        reason = request.POST.get('reason')
        if not event_id or not reason:
            messages.error(request, '请填写完整信息')
            return redirect('submit_leave_request')
        try:
            event = AttendanceEvent.objects.get(event_id=event_id)
            # 禁止为过去的考勤事件申请请假
            if event.event_date < timezone.now().date():
                messages.error(request, '不能为已过去的课程申请请假')
                return redirect('submit_leave_request')
            enrollment = Enrollment.objects.get(student__openid=request.user.username, course=event.course)
            LeaveRequest.objects.create(
                enrollment=enrollment,
                event=event,
                reason=reason,
                approval_status=1
            )
            messages.success(request, '请假申请已提交')
            return redirect('leave_request_history')
        except (AttendanceEvent.DoesNotExist, Enrollment.DoesNotExist):
            messages.error(request, '无效的考勤事件或未选修该课程')
            return redirect('submit_leave_request')
    # 获取学生可用的考勤事件
    enrollments = Enrollment.objects.filter(student__openid=request.user.username)
    events = AttendanceEvent.objects.filter(course__in=enrollments.values_list('course', flat=True), event_date__gte=timezone.now().date())
    context = {
        'events': events
    }
    return render(request, 'student/leave_request.html', context)

@login_required
def leave_request_history(request):
    """学生请假历史记录"""
    # 获取学生的请假历史记录
    leave_requests = LeaveRequest.objects.filter(
        enrollment__student__openid=request.user.username
    ).order_by('-submit_time')
    
    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'student/leave_request_history.html', context)

@login_required
def student_profile(request):
    """学生个人信息"""
    # 获取学生信息
    student = Student.objects.get(openid=request.user.username)
    
    context = {
        'student': student
    }
    return render(request, 'student/profile.html', context)

def student_leave(request):
    return HttpResponse("学生请假页-占位") 