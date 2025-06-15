from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from ..models import (
    Course, AttendanceEvent, Attendance, LeaveRequest, TeachingAssignment,
    Enrollment, EVENT_VALID, EVENT_INVALID, STATUS_PRESENT, STATUS_ABSENT,
    STATUS_LEAVE, Teacher, Student
)
import qrcode
from io import BytesIO
from django.conf import settings
from datetime import datetime

@login_required
def teacher_dashboard(request):
    """教师仪表盘"""
    # 获取教师对象 - 使用正确的关联关系
    teacher = request.user.teacher
    # now = timezone.now()  # 注释掉真实时间
    now = datetime(2025, 6, 23, 8, 0, 0)  # 演示用假时间
    today = now.date()
    # 获取今日考勤事件（多门课）
    today_events = AttendanceEvent.objects.filter(
        course__teachingassignment__teacher=teacher,
        event_date=today
    ).select_related('course')
    # 获取最近的待审批请假申请
    recent_leave_requests = LeaveRequest.objects.filter(
        event__course__teachingassignment__teacher=teacher,
        approval_status=1
    ).select_related('enrollment__student', 'event__course').order_by('-submit_time')[:5]
    # 获取教师所授课程列表
    teaching_assignments = TeachingAssignment.objects.filter(teacher=teacher)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    # 获取所有相关考勤事件，按时间排序
    all_events = AttendanceEvent.objects.filter(
        course__teachingassignment__teacher=teacher
    ).select_related('course').order_by('event_date', 'scan_start_time')
    context = {
        'teacher': teacher,
        'today_events': today_events,
        'recent_leave_requests': recent_leave_requests,
        'courses': courses,
        'all_events': all_events,
        'now': now,
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def teacher_courses(request):
    """教师课程列表"""
    # 获取教师的课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher=request.user.teacher)
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
    leave_request = LeaveRequest.objects.get(leave_request_id=leave_request_id)
    
    if request.method == 'POST':
        # 获取审批结果
        approval_status = int(request.POST.get('status', request.POST.get('approval_status', 1)))
        approver_notes = request.POST.get('comment', request.POST.get('approver_notes', ''))
        
        # 更新请假申请状态
        leave_request.approval_status = approval_status
        leave_request.approver_notes = approver_notes
        leave_request.approver = request.user.teacher
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
    """请假申请列表，显示所有请假记录（包括待审批、已通过、已驳回）"""
    teaching_assignments = TeachingAssignment.objects.filter(teacher=request.user.teacher)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    # 显示所有请假申请
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
    teacher = request.user.teacher
    
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
    """生成考勤事件二维码，内容为事件ID"""
    # 只生成事件ID作为二维码内容
    img = qrcode.make(str(event_id))
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
    present_count = sum(1 for s in students if s.stu_id in attendance_map and attendance_map[s.stu_id].status == STATUS_PRESENT)
    leave_count = sum(1 for s in students if s.stu_id in attendance_map and attendance_map[s.stu_id].status == STATUS_LEAVE)
    absent_count = total_count - present_count - leave_count
    # 构造展示数据
    student_status_list = []
    for student in students:
        att = attendance_map.get(student.stu_id)
        status = 'present' if att and att.status == STATUS_PRESENT else \
                'leave' if att and att.status == STATUS_LEAVE else 'absent'
        student_status_list.append({
            'stu_id': student.stu_id,
            'stu_name': student.stu_name,
            'scan_time': att.scan_time if att else None,
            'status': status,
        })
    context = {
        'event': event,
        'students': student_status_list,
        'total_count': total_count,
        'present_count': present_count,
        'leave_count': leave_count,
        'absent_count': absent_count,
    }
    return render(request, 'teacher/event_detail.html', context)

@login_required
def student_course_attendance(request, course_id, stu_id):
    """查看学生在特定课程下的考勤记录"""
    # 获取课程和学生信息
    course = get_object_or_404(Course, course_id=course_id)
    student = get_object_or_404(Student, stu_id=stu_id)
    
    # 获取该课程的所有考勤事件
    events = AttendanceEvent.objects.filter(course=course).order_by('event_date', 'scan_start_time')
    
    # 获取该学生的考勤记录
    enrollment = get_object_or_404(Enrollment, course=course, student=student)
    attendance_records = Attendance.objects.filter(
        enrollment=enrollment,
        event__in=events
    ).select_related('event')
    
    # 创建考勤记录映射
    attendance_map = {record.event.event_id: record for record in attendance_records}
    
    # 统计出勤情况
    total_events = events.count()
    present_count = sum(1 for record in attendance_records if record.status == STATUS_PRESENT)
    attendance_rate = (present_count / total_events * 100) if total_events > 0 else 0
    
    # 构造展示数据
    attendance_list = []
    for event in events:
        record = attendance_map.get(event.event_id)
        status = 'present' if record and record.status == STATUS_PRESENT else \
                'leave' if record and record.status == STATUS_LEAVE else 'absent'
        attendance_list.append({
            'event_date': event.event_date,
            'status': status,
            'scan_time': record.scan_time if record else None
        })
    
    context = {
        'course': course,
        'student': student,
        'attendance_list': attendance_list,
        'total_events': total_events,
        'present_count': present_count,
        'attendance_rate': round(attendance_rate, 1)
    }
    return render(request, 'teacher/student_course_attendance.html', context)

@login_required
def course_all_students_attendance(request, course_id):
    """查看课程中所有学生的考勤情况"""
    # 获取课程信息
    course = get_object_or_404(Course, course_id=course_id)
    
    # 获取所有选课学生
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    
    # 获取该课程的所有考勤事件
    events = AttendanceEvent.objects.filter(course=course).order_by('event_date', 'scan_start_time')
    
    # 获取所有考勤记录
    attendance_records = Attendance.objects.filter(
        enrollment__in=enrollments,
        event__in=events
    ).select_related('event', 'enrollment__student')
    
    # 创建考勤记录映射
    attendance_map = {}
    for record in attendance_records:
        key = (record.enrollment.student.stu_id, record.event.event_id)
        attendance_map[key] = record
    
    # 构造展示数据
    students_attendance = []
    for enrollment in enrollments:
        student = enrollment.student
        student_attendance = []
        present_count = 0
        
        for event in events:
            record = attendance_map.get((student.stu_id, event.event_id))
            status = 'present' if record and record.status == STATUS_PRESENT else \
                    'leave' if record and record.status == STATUS_LEAVE else 'absent'
            if status == 'present':
                present_count += 1
            student_attendance.append({
                'event_date': event.event_date,
                'status': status,
                'scan_time': record.scan_time if record else None
            })
        
        attendance_rate = (present_count / len(events) * 100) if events else 0
        students_attendance.append({
            'student': student,
            'attendance_list': student_attendance,
            'present_count': present_count,
            'attendance_rate': round(attendance_rate, 1)
        })
    
    context = {
        'course': course,
        'events': events,
        'students_attendance': students_attendance
    }
    return render(request, 'teacher/course_all_students_attendance.html', context) 