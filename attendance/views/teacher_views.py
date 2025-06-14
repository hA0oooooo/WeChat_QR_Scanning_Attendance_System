from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from ..models import (
    Course, AttendanceEvent, Attendance, LeaveRequest, TeachingAssignment,
    Enrollment, EVENT_VALID, EVENT_INVALID, STATUS_PRESENT, STATUS_ABSENT,
    STATUS_LEAVE, Teacher
)
import qrcode
from io import BytesIO
from django.conf import settings

@login_required
def teacher_dashboard(request):
    """教师仪表盘"""
    # 获取教师信息
    teacher = Teacher.objects.get(teacher_id=request.user.username)
    
    # 获取今日考勤事件
    today = timezone.now().date()
    today_events = AttendanceEvent.objects.filter(
        course__teachingassignment__teacher=teacher,
        event_date=today
    )
    
    # 获取最近的请假申请
    recent_leave_requests = LeaveRequest.objects.filter(
        event__course__teachingassignment__teacher=teacher
    ).order_by('-submit_time')[:5]
    
    context = {
        'teacher': teacher,
        'today_events': today_events,
        'recent_leave_requests': recent_leave_requests
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def teacher_courses(request):
    """教师课程列表"""
    # 获取教师的课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    
    context = {
        'courses': courses
    }
    return render(request, 'teacher/courses.html', context)

@login_required
def create_attendance_event(request, course_id):
    """创建考勤事件"""
    # 获取课程信息
    course = Course.objects.get(course_id=course_id)
    
    if request.method == 'POST':
        # 创建新的考勤事件
        event_date = request.POST.get('event_date')
        scan_start_time = request.POST.get('scan_start_time')
        scan_end_time = request.POST.get('scan_end_time')
        
        AttendanceEvent.objects.create(
            course=course,
            event_date=event_date,
            scan_start_time=scan_start_time,
            scan_end_time=scan_end_time
        )
        messages.success(request, '考勤事件创建成功')
        return redirect('manage_attendance_events', course_id=course_id)
    
    context = {
        'course': course
    }
    return render(request, 'teacher/create_attendance_event.html', context)

@login_required
def view_attendance_results(request, event_id):
    """查看考勤结果"""
    # 获取考勤事件
    event = AttendanceEvent.objects.get(event_id=event_id)
    
    # 获取考勤记录
    attendance_records = Attendance.objects.filter(event=event)
    
    # 统计考勤情况
    total_students = attendance_records.count()
    present_count = attendance_records.filter(status=STATUS_PRESENT).count()
    absent_count = attendance_records.filter(status=STATUS_ABSENT).count()
    leave_count = attendance_records.filter(status=STATUS_LEAVE).count()
    
    context = {
        'event': event,
        'attendance_records': attendance_records,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count
    }
    return render(request, 'teacher/attendance_results.html', context)

@login_required
def approve_leave_request(request, leave_request_id):
    """审批请假申请"""
    # 获取请假申请
    leave_request = LeaveRequest.objects.get(leave_request_id=leave_request_id)
    
    if request.method == 'POST':
        # 获取审批结果
        approval_status = int(request.POST.get('status', request.POST.get('approval_status', 1)))
        approver_notes = request.POST.get('comment', request.POST.get('approver_notes', ''))
        
        # 更新请假申请状态
        leave_request.approval_status = approval_status
        leave_request.approver_notes = approver_notes
        leave_request.approver = Teacher.objects.get(teacher_id=request.user.username)
        leave_request.approval_timestamp = timezone.now()
        leave_request.save()
        
        # 如果批准请假，更新考勤记录
        if approval_status == 2:  # LEAVE_APPROVED
            Attendance.objects.create(
                enrollment=leave_request.enrollment,
                event=leave_request.event,
                status=3,  # STATUS_LEAVE
                notes=approver_notes
            )
        
        messages.success(request, '请假申请已审批')
        return redirect('leave_request_list')
    
    context = {
        'leave_request': leave_request
    }
    return render(request, 'teacher/approve_leave_request.html', context)

@login_required
def leave_request_list(request):
    """请假申请列表"""
    # 获取教师的课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher__teacher_id=request.user.username)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    
    # 获取请假申请列表
    leave_requests = LeaveRequest.objects.filter(
        event__course__in=courses
    ).order_by('-submit_time')
    
    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'teacher/leave.html', context)

@login_required
def teacher_profile(request):
    """教师个人信息"""
    # 获取教师信息
    teacher = Teacher.objects.get(teacher_id=request.user.username)
    
    context = {
        'teacher': teacher
    }
    return render(request, 'teacher/profile.html', context)

@login_required
def course_detail(request, course_id):
    """课程详情"""
    # 获取课程信息
    course = Course.objects.get(course_id=course_id)
    
    # 获取考勤事件列表
    events = AttendanceEvent.objects.filter(course=course).order_by('-event_date', '-scan_start_time')
    
    # 获取选课学生列表
    enrollments = Enrollment.objects.filter(course=course)
    
    context = {
        'course': course,
        'events': events,
        'enrollments': enrollments
    }
    return render(request, 'teacher/course_detail.html', context)

@login_required
def manage_attendance_events(request, course_id):
    """管理考勤事件"""
    # 获取课程信息
    course = Course.objects.get(course_id=course_id)
    
    # 获取考勤事件列表
    events = AttendanceEvent.objects.filter(course=course).order_by('-event_date', '-scan_start_time')
    
    if request.method == 'POST':
        # 创建新的考勤事件
        event_date = request.POST.get('event_date')
        scan_start_time = request.POST.get('scan_start_time')
        scan_end_time = request.POST.get('scan_end_time')
        
        AttendanceEvent.objects.create(
            course=course,
            event_date=event_date,
            scan_start_time=scan_start_time,
            scan_end_time=scan_end_time
        )
        messages.success(request, '考勤事件创建成功')
        return redirect('manage_attendance_events', course_id=course_id)
    
    context = {
        'course': course,
        'events': events
    }
    return render(request, 'teacher/manage_attendance_events.html', context)

@login_required
def toggle_event_status(request, event_id):
    """切换考勤事件状态"""
    # 获取考勤事件
    event = AttendanceEvent.objects.get(event_id=event_id)
    
    # 切换状态
    event.event_status = EVENT_INVALID if event.event_status == EVENT_VALID else EVENT_VALID
    event.save()
    
    messages.success(request, '考勤事件状态已更新')
    return redirect('manage_attendance_events', course_id=event.course.course_id)

@login_required
def event_qr_code(request, event_id):
    """生成考勤事件二维码，内容为签到URL"""
    # 构造签到URL
    base_url = getattr(settings, 'QR_BASE_URL', None) or request.build_absolute_uri('/')[:-1]
    qr_url = f"{base_url}api/scan-qr/?event_id={event_id}"
    img = qrcode.make(qr_url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    image_stream = buf.getvalue()
    return HttpResponse(image_stream, content_type='image/png')

@login_required
def event_detail(request, event_id):
    """考勤事件详情，展示所有学生签到状态和统计"""
    event = AttendanceEvent.objects.get(event_id=event_id)
    # 获取所有选课学生
    enrollments = Enrollment.objects.filter(course=event.course)
    students = [enrollment.student for enrollment in enrollments]
    # 获取所有签到记录
    attendance_records = Attendance.objects.filter(event=event)
    attendance_map = {att.enrollment.student.stu_id: att for att in attendance_records}
    # 统计
    total_count = len(students)
    present_count = sum(1 for s in students if s.stu_id in attendance_map)
    absent_count = total_count - present_count
    # 构造展示数据
    student_status_list = []
    for student in students:
        att = attendance_map.get(student.stu_id)
        student_status_list.append({
            'stu_id': student.stu_id,
            'stu_name': student.stu_name,
            'scan_time': att.scan_time if att else None,
            'status': 'present' if att else 'absent',
        })
    context = {
        'event': event,
        'students': student_status_list,
        'total_count': total_count,
        'present_count': present_count,
        'absent_count': absent_count,
    }
    return render(request, 'teacher/event_detail.html', context) 