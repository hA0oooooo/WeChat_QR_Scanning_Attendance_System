from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from ..models import (
    Course, AttendanceEvent, Attendance, LeaveRequest, Enrollment,
    Student, STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE,
    LEAVE_PENDING, LEAVE_APPROVED, LEAVE_REJECTED
)
from datetime import datetime, date
import json

@login_required
def student_dashboard(request):
    """学生仪表盘"""
    # 获取学生对象
    student = request.user.student
    
    # 使用演示时间
    now = datetime(2025, 6, 23, 8, 0, 0)
    today = now.date()
    
    # 获取学生的选课信息
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    courses = [enrollment.course for enrollment in enrollments]
    
    # 获取今日考勤事件
    today_events = AttendanceEvent.objects.filter(
        course__in=courses,
        event_date=today
    ).select_related('course')
    
    # 获取最近的考勤记录
    recent_attendance = Attendance.objects.filter(
        enrollment__student=student
    ).select_related('event__course').order_by('-event__event_date', '-event__scan_start_time')[:5]
    
    # 获取待审批的请假申请
    pending_leave_requests = LeaveRequest.objects.filter(
        enrollment__student=student,
        approval_status=LEAVE_PENDING
    ).select_related('event__course').order_by('-submit_time')[:3]
    
    # 统计数据
    total_events = AttendanceEvent.objects.filter(course__in=courses).count()
    attended_count = Attendance.objects.filter(
        enrollment__student=student,
        status=STATUS_PRESENT
    ).count()
    leave_count = Attendance.objects.filter(
        enrollment__student=student,
        status=STATUS_LEAVE
    ).count()
    absent_count = Attendance.objects.filter(
        enrollment__student=student,
        status=STATUS_ABSENT
    ).count()
    
    # 计算出勤率
    attendance_rate = round((attended_count / total_events * 100), 1) if total_events > 0 else 0
    
    context = {
        'student': student,
        'courses': courses,
        'today_events': today_events,
        'recent_attendance': recent_attendance,
        'pending_leave_requests': pending_leave_requests,
        'stats': {
            'total_events': total_events,
            'attended_count': attended_count,
            'leave_count': leave_count,
            'absent_count': absent_count,
            'attendance_rate': attendance_rate,
        },
        'now': now,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def student_courses(request):
    """学生课程列表"""
    student = request.user.student
    
    # 获取学生的选课记录
    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'course__dept')
    
    # 为每个课程添加统计信息
    course_stats = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # 统计该课程的考勤情况
        total_events = AttendanceEvent.objects.filter(course=course).count()
        attended = Attendance.objects.filter(
            enrollment=enrollment,
            status=STATUS_PRESENT
        ).count()
        leave = Attendance.objects.filter(
            enrollment=enrollment,
            status=STATUS_LEAVE
        ).count()
        absent = Attendance.objects.filter(
            enrollment=enrollment,
            status=STATUS_ABSENT
        ).count()
        
        attendance_rate = round((attended / total_events * 100), 1) if total_events > 0 else 0
        
        course_stats.append({
            'enrollment': enrollment,
            'course': course,
            'total_events': total_events,
            'attended': attended,
            'leave': leave,
            'absent': absent,
            'attendance_rate': attendance_rate,
        })
    
    context = {
        'student': student,
        'course_stats': course_stats,
    }
    return render(request, 'student/courses.html', context)

@login_required
def course_detail(request, course_id):
    """课程详情"""
    student = request.user.student
    course = get_object_or_404(Course, course_id=course_id)
    
    # 验证学生是否选修了该课程
    try:
        enrollment = Enrollment.objects.get(student=student, course=course)
    except Enrollment.DoesNotExist:
        messages.error(request, '您未选修该课程')
        return redirect('student_courses')
    
    # 获取该课程的所有考勤事件
    events = AttendanceEvent.objects.filter(course=course).order_by('-event_date', '-scan_start_time')
    
    # 获取学生在该课程的考勤记录
    attendance_records = Attendance.objects.filter(
        enrollment=enrollment
    ).select_related('event')
    
    # 创建考勤记录字典，方便模板查询
    attendance_dict = {record.event.event_id: record for record in attendance_records}
    
    # 为每个事件添加考勤状态
    events_with_status = []
    for event in events:
        attendance_record = attendance_dict.get(event.event_id)
        events_with_status.append({
            'event': event,
            'attendance': attendance_record,
        })
    
    context = {
        'student': student,
        'course': course,
        'enrollment': enrollment,
        'events_with_status': events_with_status,
    }
    return render(request, 'student/course_detail.html', context)

@login_required
def student_attendance(request):
    """学生考勤记录"""
    student = request.user.student
    
    # 获取所有考勤记录
    attendance_records = Attendance.objects.filter(
        enrollment__student=student
    ).select_related('event__course', 'enrollment__course').order_by('-event__event_date', '-event__scan_start_time')
    
    # 按课程分组统计
    course_stats = {}
    for record in attendance_records:
        course_id = record.enrollment.course.course_id
        if course_id not in course_stats:
            course_stats[course_id] = {
                'course': record.enrollment.course,
                'total': 0,
                'present': 0,
                'leave': 0,
                'absent': 0,
            }
        
        course_stats[course_id]['total'] += 1
        if record.status == STATUS_PRESENT:
            course_stats[course_id]['present'] += 1
        elif record.status == STATUS_LEAVE:
            course_stats[course_id]['leave'] += 1
        elif record.status == STATUS_ABSENT:
            course_stats[course_id]['absent'] += 1
    
    # 计算出勤率
    for stats in course_stats.values():
        if stats['total'] > 0:
            stats['attendance_rate'] = round((stats['present'] / stats['total'] * 100), 1)
        else:
            stats['attendance_rate'] = 0
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'course_stats': course_stats.values(),
    }
    return render(request, 'student/attendance.html', context)

@login_required
def submit_leave_request(request):
    """提交请假申请"""
    student = request.user.student
    
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        reason = request.POST.get('reason')
        
        if not event_id or not reason:
            messages.error(request, '请填写完整信息')
            return redirect('submit_leave_request')
        
        try:
            event = AttendanceEvent.objects.get(event_id=event_id)
            enrollment = Enrollment.objects.get(student=student, course=event.course)
            
            # 检查是否已经有考勤记录
            if Attendance.objects.filter(enrollment=enrollment, event=event).exists():
                messages.error(request, '该课程已有考勤记录，无法申请请假')
                return redirect('submit_leave_request')
            
            # 检查是否已经提交过请假申请
            if LeaveRequest.objects.filter(enrollment=enrollment, event=event).exists():
                messages.error(request, '您已经为该课程提交过请假申请')
                return redirect('submit_leave_request')
            
            # 创建请假申请
            LeaveRequest.objects.create(
                enrollment=enrollment,
                event=event,
                reason=reason,
                approval_status=LEAVE_PENDING
            )
            
            messages.success(request, '请假申请已提交，等待教师审批')
            return redirect('leave_request_history')
            
        except (AttendanceEvent.DoesNotExist, Enrollment.DoesNotExist):
            messages.error(request, '无效的考勤事件或未选修该课程')
            return redirect('submit_leave_request')
    
    # GET请求：显示可申请请假的考勤事件
    enrollments = Enrollment.objects.filter(student=student)
    
    # 获取未来的考勤事件（可以申请请假）
    future_events = AttendanceEvent.objects.filter(
        course__in=enrollments.values_list('course', flat=True),
        event_date__gte=date.today()
    ).select_related('course')
    
    # 过滤掉已有考勤记录或已申请请假的事件
    available_events = []
    for event in future_events:
        enrollment = enrollments.get(course=event.course)
        
        # 检查是否已有考勤记录或请假申请
        has_attendance = Attendance.objects.filter(enrollment=enrollment, event=event).exists()
        has_leave_request = LeaveRequest.objects.filter(enrollment=enrollment, event=event).exists()
        
        if not has_attendance and not has_leave_request:
            available_events.append(event)
    
    context = {
        'student': student,
        'available_events': available_events,
    }
    return render(request, 'student/leave_request.html', context)

@login_required
def leave_request_history(request):
    """请假申请历史"""
    student = request.user.student
    
    # 获取所有请假申请
    leave_requests = LeaveRequest.objects.filter(
        enrollment__student=student
    ).select_related('event__course', 'approver').order_by('-submit_time')
    
    context = {
        'student': student,
        'leave_requests': leave_requests,
    }
    return render(request, 'student/leave_request_history.html', context)

@login_required
def student_profile(request):
    """学生个人信息"""
    student = request.user.student
    
    if request.method == 'POST':
        # 处理信息更新（这里可以扩展为信息变更申请）
        messages.info(request, '个人信息变更需要提交申请，请联系管理员')
        return redirect('student_profile')
    
    # 获取学生的选课信息
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'student/profile.html', context)

@login_required
def attendance_statistics(request):
    """出勤统计"""
    student = request.user.student
    
    # 获取学生的所有选课
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    # 统计每门课程的出勤情况
    course_statistics = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # 获取该课程的所有考勤事件
        total_events = AttendanceEvent.objects.filter(course=course).count()
        
        # 统计各种状态的考勤记录
        attendance_stats = Attendance.objects.filter(
            enrollment=enrollment
        ).aggregate(
            present_count=Count('attend_id', filter=Q(status=STATUS_PRESENT)),
            leave_count=Count('attend_id', filter=Q(status=STATUS_LEAVE)),
            absent_count=Count('attend_id', filter=Q(status=STATUS_ABSENT))
        )
        
        present_count = attendance_stats['present_count'] or 0
        leave_count = attendance_stats['leave_count'] or 0
        absent_count = attendance_stats['absent_count'] or 0
        
        # 计算出勤率
        if total_events > 0:
            attendance_rate = round((present_count / total_events * 100), 1)
        else:
            attendance_rate = 0
        
        course_statistics.append({
            'course': course,
            'total_events': total_events,
            'present_count': present_count,
            'leave_count': leave_count,
            'absent_count': absent_count,
            'attendance_rate': attendance_rate,
        })
    
    # 总体统计
    total_stats = {
        'total_events': sum(stat['total_events'] for stat in course_statistics),
        'total_present': sum(stat['present_count'] for stat in course_statistics),
        'total_leave': sum(stat['leave_count'] for stat in course_statistics),
        'total_absent': sum(stat['absent_count'] for stat in course_statistics),
    }
    
    if total_stats['total_events'] > 0:
        total_stats['overall_rate'] = round((total_stats['total_present'] / total_stats['total_events'] * 100), 1)
    else:
        total_stats['overall_rate'] = 0
    
    context = {
        'student': student,
        'course_statistics': course_statistics,
        'total_stats': total_stats,
    }
    return render(request, 'student/statistics.html', context)

# 扫码签到相关视图（保留原有功能）
def student_leave(request):
    """学生请假页面（兼容性保留）"""
    return redirect('submit_leave_request') 