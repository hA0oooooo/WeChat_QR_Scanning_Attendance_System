from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.contrib.auth import authenticate, update_session_auth_hash
from ..models import (
    Course, AttendanceEvent, Attendance, LeaveRequest, Enrollment,
    Student, ClassSchedule, STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE, STATUS_NOT_STARTED,
    LEAVE_PENDING, LEAVE_APPROVED, LEAVE_REJECTED
)
from datetime import datetime, date
import json

@login_required
def student_dashboard(request):
    """学生仪表板"""
    student = request.user.student
    
    # 模拟当前时间为2025年6月18日11:00（课程进行中）
    now = datetime(2025, 6, 18, 11, 0)
    today = now.date()
    
    # 获取今日考勤事件
    today_events = AttendanceEvent.objects.filter(
        course__enrollment__student=student,
        event_date=today
    ).select_related('course').distinct()
    
    # 为今日事件添加考勤状态
    events_with_attendance = []
    for event in today_events:
        try:
            enrollment = Enrollment.objects.get(student=student, course=event.course)
            attendance = Attendance.objects.get(enrollment=enrollment, event=event)
            event.current_attendance = attendance
        except (Enrollment.DoesNotExist, Attendance.DoesNotExist):
            event.current_attendance = None
        events_with_attendance.append(event)
    
    # 获取最近考勤记录
    recent_attendance = Attendance.objects.filter(
        enrollment__student=student
    ).select_related('event__course').order_by('-event__event_date')[:5]
    
    # 计算统计数据 - 只计算已开始的课程（排除未开始状态）
    all_attendance = Attendance.objects.filter(
        enrollment__student=student
    ).exclude(status=STATUS_NOT_STARTED)  # 排除未开始的课程
    
    total_events = all_attendance.count()
    attended_count = all_attendance.filter(status=STATUS_PRESENT).count()
    leave_count = all_attendance.filter(status=STATUS_LEAVE).count()
    absent_count = all_attendance.filter(status=STATUS_ABSENT).count()
    
    # 计算出勤率
    if total_events > 0:
        attendance_rate = round((attended_count / total_events) * 100, 1)
    else:
        attendance_rate = 0.0
    
    # 获取待审批的请假申请
    pending_leaves = LeaveRequest.objects.filter(
        enrollment__student=student,
        approval_status=LEAVE_PENDING
    ).select_related('event__course').order_by('-submit_time')
    
    context = {
        'student': student,
        'today_events': events_with_attendance,
        'recent_attendance': recent_attendance,
        'pending_leaves': pending_leaves,
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
    
    # 为每个课程添加课表信息
    course_info = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # 获取该课程的时间安排
        schedules = ClassSchedule.objects.filter(
            assignment__course=course
        ).select_related('assignment__teacher').order_by('class_date')
        
        # 组合课程时间信息
        if schedules.exists():
            schedule = schedules.first()  # 取第一个时间安排作为主要显示
            
            # 格式化时间信息
            weekday_map = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
            weekday_name = weekday_map.get(schedule.weekday, str(schedule.weekday))
            
            if schedule.start_period == schedule.end_period:
                period_str = f'第{schedule.start_period}节'
            else:
                period_str = f'第{schedule.start_period}-{schedule.end_period}节'
            
            # 如果有多个时间安排，显示所有日期
            if schedules.count() > 1:
                dates = ', '.join([s.class_date.strftime('%m月%d日') for s in schedules])
                class_time = f'{dates} 星期{weekday_name} {period_str}'
            else:
                class_time = f'{schedule.class_date.strftime("%m月%d日")} 星期{weekday_name} {period_str}'
            
            course_info.append({
                'enrollment': enrollment,
                'course': course,
                'teacher_name': schedule.assignment.teacher.teacher_name,
                'class_time': class_time,
                'location': schedule.location,
            })
        else:
            # 如果没有时间安排，使用默认值
            course_info.append({
                'enrollment': enrollment,
                'course': course,
                'teacher_name': '未安排',
                'class_time': '时间待定',
                'location': '地点待定',
            })
    
    context = {
        'student': student,
        'course_info': course_info,
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
    
    # 按课程分组统计 - 只统计已开始的课程
    course_stats = {}
    for record in attendance_records:
        # 排除未开始的课程
        if record.status == STATUS_NOT_STARTED:
            continue
            
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
            
            # 检查是否已经提交过请假申请
            if LeaveRequest.objects.filter(enrollment=enrollment, event=event).exists():
                messages.error(request, '您已经为该课程提交过请假申请')
                return redirect('submit_leave_request')
            
            # 检查考勤状态，只有未开始的课程才能申请请假
            try:
                attendance = Attendance.objects.get(enrollment=enrollment, event=event)
                if attendance.status != STATUS_NOT_STARTED:
                    messages.error(request, '只能对未开始的课程申请请假')
                    return redirect('submit_leave_request')
            except Attendance.DoesNotExist:
                # 如果没有考勤记录，也可以申请请假
                pass
            
            # 创建请假申请
            leave_request = LeaveRequest.objects.create(
                enrollment=enrollment,
                event=event,
                reason=reason,
                approval_status=LEAVE_PENDING
            )
            
            # 设置固定的演示时间：6月18日10:00
            from django.utils import timezone
            from datetime import datetime
            demo_time = timezone.make_aware(datetime(2025, 6, 18, 10, 0))
            leave_request.submit_time = demo_time
            leave_request.save()
            
            messages.success(request, '请假申请已提交，等待教师审批')
            return redirect('submit_leave_request')
            
        except (AttendanceEvent.DoesNotExist, Enrollment.DoesNotExist):
            messages.error(request, '无效的考勤事件或未选修该课程')
            return redirect('submit_leave_request')
    
    # GET请求：显示可申请请假的考勤事件
    enrollments = Enrollment.objects.filter(student=student)
    
    # 获取所有考勤事件（包括未来和当前的）
    all_events = AttendanceEvent.objects.filter(
        course__in=enrollments.values_list('course', flat=True)
    ).select_related('course').order_by('event_date')
    
    # 过滤出可以申请请假的事件（未开始状态且未申请过请假）
    available_events = []
    for event in all_events:
        enrollment = enrollments.get(course=event.course)
        
        # 检查是否已申请过请假
        has_leave_request = LeaveRequest.objects.filter(enrollment=enrollment, event=event).exists()
        if has_leave_request:
            continue
            
        # 检查考勤状态，只有未开始的才能申请请假
        try:
            attendance = Attendance.objects.get(enrollment=enrollment, event=event)
            if attendance.status == STATUS_NOT_STARTED:
                available_events.append(event)
        except Attendance.DoesNotExist:
            # 没有考勤记录的也可以申请
            available_events.append(event)
    
    # 获取所有请假申请历史
    leave_requests = LeaveRequest.objects.filter(
        enrollment__student=student
    ).select_related('event__course', 'approver').order_by('-submit_time')
    
    context = {
        'student': student,
        'available_events': available_events,
        'leave_requests': leave_requests,
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
    
    context = {
        'student': student,
        'user': request.user,
    }
    return render(request, 'student/profile.html', context)

@login_required
def update_profile(request):
    """更新个人信息"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方法错误'})
    
    try:
        data = json.loads(request.body)
        field_type = data.get('field_type')
        new_value = data.get('new_value', '').strip()
        
        if not field_type or not new_value:
            return JsonResponse({'success': False, 'message': '参数不完整'})
        
        student = request.user.student
        
        if field_type == 'name':
            if len(new_value) > 50:
                return JsonResponse({'success': False, 'message': '姓名长度不能超过50个字符'})
            student.stu_name = new_value
            student.save()
            # 同时更新User表的first_name
            request.user.first_name = new_value
            request.user.save()
            return JsonResponse({'success': True, 'message': '姓名更新成功'})
        else:
            return JsonResponse({'success': False, 'message': '不支持的字段类型'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '数据格式错误'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'更新失败：{str(e)}'})

@login_required
def change_password(request):
    """修改密码"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '请求方法错误'})
    
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return JsonResponse({'success': False, 'message': '参数不完整'})
        
        # 验证旧密码
        if not authenticate(username=request.user.username, password=old_password):
            return JsonResponse({'success': False, 'message': '当前密码错误'})
        
        # 验证新密码长度
        if len(new_password) < 8:
            return JsonResponse({'success': False, 'message': '新密码长度至少8位'})
        
        # 更新密码
        request.user.set_password(new_password)
        request.user.save()
        
        # 更新会话，避免用户被登出
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({'success': True, 'message': '密码修改成功'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '数据格式错误'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'密码修改失败：{str(e)}'})

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