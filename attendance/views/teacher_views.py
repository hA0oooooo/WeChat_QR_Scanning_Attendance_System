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
from datetime import datetime, date
import urllib.parse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied

@login_required
def teacher_dashboard(request):
    """教师仪表盘"""
    teacher = request.user.teacher
    now = timezone.now()
    today = now.date()
    
    # 获取今日考勤事件
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
    
    # 获取所有相关考勤事件
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
    """教师考勤事件列表"""
    # 获取筛选参数
    course_filter = request.GET.get('course', '')
    date_filter = request.GET.get('date_filter', '')
    
    # 获取教师所教授课程的所有考勤事件
    events = AttendanceEvent.objects.filter(
        course__teachingassignment__teacher=request.user.teacher
    ).select_related('course').order_by('event_date', 'scan_start_time')
    
    # 应用筛选条件
    if course_filter:
        events = events.filter(course__course_id=course_filter)
    
    if date_filter:
        events = events.filter(event_date=date_filter)
    
    # 获取教师所教授的所有课程
    courses = Course.objects.filter(
        teachingassignment__teacher=request.user.teacher
    ).distinct().order_by('course_name')
    
    # 获取所有可用的日期
    available_dates = AttendanceEvent.objects.filter(
        course__teachingassignment__teacher=request.user.teacher
    ).values_list('event_date', flat=True).distinct().order_by('event_date')
    
    now = timezone.now()
    
    context = {
        'events': events,
        'now': now,
        'courses': courses,
        'available_dates': available_dates,
        'selected_course': course_filter,
        'selected_date': date_filter,
    }
    return render(request, 'teacher/courses.html', context)

@login_required
def create_attendance_event(request, course_id):
    """创建考勤事件"""
    course = Course.objects.get(course_id=course_id)
    
    if request.method == 'POST':
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
    
    context = {'course': course}
    return render(request, 'teacher/create_attendance_event.html', context)

@login_required
def view_attendance_results(request, event_id):
    """查看考勤结果"""
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
        'leave_count': leave_count,
        'now': timezone.now()
    }
    return render(request, 'teacher/attendance_results.html', context)

@login_required
def approve_leave_request(request, leave_request_id):
    """审批请假申请"""
    leave_request = LeaveRequest.objects.get(leave_request_id=leave_request_id)
    
    if request.method == 'POST':
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
            attendance, created = Attendance.objects.get_or_create(
                enrollment=leave_request.enrollment,
                event=leave_request.event,
                defaults={
                    'status': 3,  # STATUS_LEAVE
                    'notes': approver_notes
                }
            )
            if not created:
                attendance.status = 3
                attendance.notes = approver_notes
                attendance.save()
        
        messages.success(request, '请假申请已审批')
        return redirect('leave_request_list')
    
    context = {'leave_request': leave_request}
    return render(request, 'teacher/approve_leave_request.html', context)

@login_required
def leave_request_list(request):
    """请假申请列表"""
    teaching_assignments = TeachingAssignment.objects.filter(teacher=request.user.teacher)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    
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
    course = get_object_or_404(Course, course_id=course_id)
    
    # 验证教师是否教授该课程
    if not course.teachingassignment_set.filter(teacher=request.user.teacher).exists():
        raise PermissionDenied("您不是该课程的教师")
    
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
    """生成考勤事件二维码，内容为微信授权链接"""
    try:
        # 获取考勤事件
        event = get_object_or_404(AttendanceEvent, event_id=event_id)
        
        # 微信授权链接参数
        appid = settings.WECHAT_APPID
        # 注意：redirect_uri必须与微信后台配置的域名完全一致
        # 从settings获取域名，确保配置一致性
        # 回调到scan-qr-page，并带上event_id参数
        base_url = settings.WECHAT_NOTIFY_URL.replace('/wechat/notify/', '')
        redirect_uri = f'{base_url}/scan-qr-page/?event_id={event_id}'
        # 确保redirect_uri被正确编码
        redirect_uri_enc = urllib.parse.quote(redirect_uri, safe='')
        state = f'event_{event_id}'
        
        # 构建授权URL
        auth_url = (
            f'https://open.weixin.qq.com/connect/oauth2/authorize'
            f'?appid={appid}'
            f'&redirect_uri={redirect_uri_enc}'
            f'&response_type=code'
            f'&scope=snsapi_base'
            f'&state={state}'
            f'#wechat_redirect'
        )
        
        # 打印详细的调试信息
        print("=== 二维码生成调试信息 ===")
        print(f"原始redirect_uri: {redirect_uri}")
        print(f"编码后redirect_uri: {redirect_uri_enc}")
        print(f"完整授权URL: {auth_url}")
        print("=======================")
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(auth_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        return HttpResponse(buf.getvalue(), content_type='image/png')
        
    except Exception as e:
        print(f"生成二维码时出错: {str(e)}")  # 错误日志
        return HttpResponse(f"生成二维码失败: {str(e)}", status=500)

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
        # 只有出勤状态才显示扫码时间
        scan_time = att.scan_time if att and att.status == STATUS_PRESENT else None
        student_status_list.append({
            'stu_id': student.stu_id,
            'stu_name': student.stu_name,
            'scan_time': scan_time,
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
    """查看指定学生在指定课程中的考勤情况"""
    try:
        # 获取课程和学生信息
        course = Course.objects.get(course_id=course_id)
        student = Student.objects.get(stu_id=stu_id)
        
        # 验证教师是否教授该课程
        if not course.teachingassignment_set.filter(teacher=request.user.teacher).exists():
            raise PermissionDenied("您不是该课程的教师")
        
        # 获取学生的选课记录
        enrollment = Enrollment.objects.get(course=course, student=student)
        
        # 获取该课程的所有考勤事件（只显示6月18日之前的）
        cutoff_date = date(2025, 6, 18)
        events = AttendanceEvent.objects.filter(
            course=course,
            event_date__lt=cutoff_date
        ).order_by('event_date')
        
        # 获取学生的考勤记录
        attendance_records = Attendance.objects.filter(
            enrollment=enrollment,
            event__in=events
        ).select_related('event')
        
        # 创建考勤记录映射
        attendance_map = {record.event.event_id: record for record in attendance_records}
        
        # 构造考勤记录列表
        attendance_list = []
        total_events = events.count()
        present_count = 0
        
        for event in events:
            record = attendance_map.get(event.event_id)
            if record:
                if record.status == STATUS_PRESENT:
                    status = 'present'
                    present_count += 1
                elif record.status == STATUS_LEAVE:
                    status = 'leave'
                else:
                    status = 'absent'
            else:
                status = 'absent'
            
            attendance_list.append({
                'event_date': event.event_date,
                'status': status,
                'scan_time': record.scan_time if record and record.status == STATUS_PRESENT else None
            })
        
        # 计算出勤率
        attendance_rate = (present_count / total_events * 100) if total_events > 0 else 0
        
        context = {
            'course': course,
            'student': student,
            'attendance_list': attendance_list,
            'total_events': total_events,
            'present_count': present_count,
            'attendance_rate': round(attendance_rate, 1)
        }
        return render(request, 'teacher/student_course_attendance.html', context)
        
    except Course.DoesNotExist:
        messages.error(request, '课程不存在')
        return redirect('teacher_courses')
    except Student.DoesNotExist:
        messages.error(request, '学生不存在')
        return redirect('course_detail', course_id=course_id)
    except Enrollment.DoesNotExist:
        messages.error(request, '该学生未选修此课程')
        return redirect('course_detail', course_id=course_id)

@login_required
def course_all_students_attendance(request, course_id):
    """查看课程中所有学生的考勤情况"""
    # 获取课程信息
    course = get_object_or_404(Course, course_id=course_id)
    
    # 验证教师是否教授该课程
    if not course.teachingassignment_set.filter(teacher=request.user.teacher).exists():
        raise PermissionDenied("您不是该课程的教师")
    
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
        valid_events = [event for event in events if event.event_date < date(2025,6,18)]
        total_valid_events = len(valid_events)
        
        for event in events:
            record = attendance_map.get((student.stu_id, event.event_id))
            status = 'present' if record and record.status == STATUS_PRESENT else \
                    'leave' if record and record.status == STATUS_LEAVE else \
                    'absent' if record and record.status == STATUS_ABSENT else 'absent'
            if record and record.status == STATUS_PRESENT and event.event_date < date(2025,6,18):
                present_count += 1
            
            student_attendance.append({
                'event_date': event.event_date,
                'status': status,
                'scan_time': record.scan_time if record and record.status == STATUS_PRESENT else None
            })
        
        # 计算出勤率（只计算6月18日之前的记录）
        attendance_rate = (present_count / total_valid_events * 100) if total_valid_events > 0 else 0
        
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

def event_attendance_records_api(request, event_id):
    """返回指定考勤事件的扫码记录（JSON）"""
    try:
        event = AttendanceEvent.objects.get(event_id=event_id)
    except AttendanceEvent.DoesNotExist:
        return JsonResponse({'success': False, 'message': '考勤事件不存在'}, status=404)
    records = Attendance.objects.filter(event=event).select_related('enrollment__student').order_by('-scan_time')
    data = []
    for record in records:
        student = record.enrollment.student
        data.append({
            'scan_time': record.scan_time.strftime('%Y-%m-%d %H:%M:%S') if record.scan_time else '',
            'student_name': student.stu_name,
            'student_id': student.stu_id,
            'status': record.status,  # 1-出勤 2-缺勤 3-请假
        })
    return JsonResponse({'success': True, 'records': data})

@login_required
def teacher_statistics(request):
    """教师统计报表 - 只显示该教师所授课程的统计"""
    teacher = request.user.teacher
    
    # 获取该教师授课的课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher=teacher)
    courses = Course.objects.filter(teachingassignment__in=teaching_assignments)
    
    course_stats = []
    from django.utils import timezone
    today = timezone.now().date()
    
    for course in courses:
        # 获取该课程的所有考勤事件
        events = AttendanceEvent.objects.filter(course=course)
        # 只统计已经发生的考勤事件（不包括未来的事件）
        past_events = events.filter(event_date__lt=today)
        
        # 获取所有考勤记录（只统计已发生的事件）
        enrollments = Enrollment.objects.filter(course=course)
        all_attendance = Attendance.objects.filter(
            enrollment__in=enrollments,
            event__in=past_events
        ).select_related('event', 'enrollment__student')
        
        # 统计总体数据
        total_count = all_attendance.count()
        present_count = all_attendance.filter(status=STATUS_PRESENT).count()
        absent_count = all_attendance.filter(status=STATUS_ABSENT).count()
        leave_count = all_attendance.filter(status=STATUS_LEAVE).count()
        
        # 计算百分比
        present_rate = round((present_count / total_count * 100), 1) if total_count > 0 else 0
        absent_rate = round((absent_count / total_count * 100), 1) if total_count > 0 else 0
        leave_rate = round((leave_count / total_count * 100), 1) if total_count > 0 else 0
        
        # 统计单次考勤事件数据（包括所有事件，包括未来的事件）
        event_stats = []
        for event in events:
            # 对于已发生的事件，获取实际的考勤记录
            if event.event_date < today:
                event_attendance = all_attendance.filter(event=event)
                event_total = event_attendance.count()
                event_present = event_attendance.filter(status=STATUS_PRESENT).count()
                event_absent = event_attendance.filter(status=STATUS_ABSENT).count()
                event_leave = event_attendance.filter(status=STATUS_LEAVE).count()
                event_present_rate = round((event_present / event_total * 100), 1) if event_total > 0 else 0
            else:
                # 对于未来事件，显示为未开始状态
                event_total = 0
                event_present = 0
                event_absent = 0
                event_leave = 0
                event_present_rate = 0
            
            event_stats.append({
                'event': event,
                'date': event.event_date,
                'total_count': event_total,
                'present_count': event_present,
                'absent_count': event_absent,
                'leave_count': event_leave,
                'present_rate': event_present_rate,
                'is_future': event.event_date >= today,
            })
        # 按date升序排序
        event_stats = sorted(event_stats, key=lambda x: x['date'])
        
        course_stats.append({
            'course': course,
            'total_count': total_count,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'present_rate': present_rate,
            'absent_rate': absent_rate,
            'leave_rate': leave_rate,
            'event_stats': event_stats,
        })
    
    # 计算总计用于图表
    total_present = sum(stat['present_count'] for stat in course_stats)
    total_absent = sum(stat['absent_count'] for stat in course_stats)
    total_leave = sum(stat['leave_count'] for stat in course_stats)
    
    context = {
        'course_stats': course_stats,
        'teacher': teacher,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_leave': total_leave,
    }
    return render(request, 'teacher/statistics.html', context)

@login_required
@csrf_exempt
def teacher_update_profile(request):
    """教师个人信息修改"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            field_type = data.get('field_type')
            new_value = data.get('new_value')
            
            teacher = request.user.teacher
            
            if field_type == 'name':
                teacher.teacher_name = new_value
                teacher.save()
                return JsonResponse({'success': True, 'message': '姓名修改成功'})
            
            return JsonResponse({'success': False, 'message': '不支持的字段类型'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方法错误'})

@login_required
@csrf_exempt
def teacher_change_password(request):
    """教师修改密码"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            user = request.user
            
            # 验证旧密码
            if not user.check_password(old_password):
                return JsonResponse({'success': False, 'message': '当前密码错误'})
            
            # 设置新密码
            user.set_password(new_password)
            user.save()
            
            # 更新session，防止用户被登出
            update_session_auth_hash(request, user)
            
            return JsonResponse({'success': True, 'message': '密码修改成功'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '请求方法错误'}) 

@login_required
def teacher_student_list(request):
    """教师查看所有课程的学生名单"""
    teacher = request.user.teacher
    
    # 获取该教师授课的所有课程
    teaching_assignments = TeachingAssignment.objects.filter(teacher=teacher).select_related('course')
    
    courses_data = []
    for assignment in teaching_assignments:
        course = assignment.course
        # 获取该课程的所有学生
        enrollments = Enrollment.objects.filter(course=course).select_related('student')
        students = [enrollment.student for enrollment in enrollments]
        
        courses_data.append({
            'course': course,
            'students': students
        })
    
    context = {
        'courses_data': courses_data,
        'teacher': teacher
    }
    return render(request, 'teacher/student_list.html', context) 
