from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from ..models import Student, Teacher, Course, Department, Major, Attendance, AttendanceEvent, Enrollment, TeachingAssignment, ClassSchedule
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def is_admin(user):
    """检查用户是否是管理员"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """管理员仪表盘"""
    # 获取统计数据
    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    course_count = Course.objects.count()
    department_count = Department.objects.count()
    
    # 获取最近的考勤统计
    recent_events = AttendanceEvent.objects.order_by('-event_date')[:5]
    
    context = {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'course_count': course_count,
        'department_count': department_count,
        'recent_events': recent_events,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """管理人员（学生和教师）"""
    # 搜索功能
    search = request.GET.get('search', '')
    user_type = request.GET.get('type', 'all')  # all, student, teacher
    
    # 获取学生数据
    students = Student.objects.select_related('major__dept', 'user').all()
    if search:
        students = students.filter(
            Q(stu_id__icontains=search) | 
            Q(stu_name__icontains=search) |
            Q(major__major_name__icontains=search)
        )
    
    # 获取教师数据
    teachers = Teacher.objects.select_related('dept', 'user').all()
    if search:
        teachers = teachers.filter(
            Q(teacher_id__icontains=search) | 
            Q(teacher_name__icontains=search) |
            Q(dept__dept_name__icontains=search)
        )
    
    # 根据类型过滤
    if user_type == 'student':
        teachers = Teacher.objects.none()
    elif user_type == 'teacher':
        students = Student.objects.none()
    
    context = {
        'students': students,
        'teachers': teachers,
        'search': search,
        'user_type': user_type,
    }
    return render(request, 'admin/manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def manage_departments_majors(request):
    """管理院系和专业"""
    # 获取院系数据（包含专业和学生统计）
    departments = Department.objects.annotate(
        major_count=Count('major', distinct=True),
        student_count=Count('major__student', distinct=True)
    ).order_by('dept_name')
    
    # 获取专业数据（包含学生统计）
    majors = Major.objects.select_related('dept').annotate(
        student_count=Count('student')
    ).order_by('major_name')
    
    # 获取教师总数和学生总数
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    
    context = {
        'departments': departments,
        'majors': majors,
        'teacher_count': teacher_count,
        'student_count': student_count,
    }
    return render(request, 'admin/manage_departments_majors.html', context)

@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    """管理课程（包括教学安排和选课信息）"""
    # 搜索功能
    search = request.GET.get('search', '')
    
    # 获取课程数据
    courses = Course.objects.select_related('dept').all()
    if search:
        courses = courses.filter(
            Q(course_id__icontains=search) | 
            Q(course_name__icontains=search) |
            Q(dept__dept_name__icontains=search)
        )
    
    # 为每个课程添加统计信息
    course_stats = []
    for course in courses:
        # 获取授课教师
        teaching_assignments = TeachingAssignment.objects.filter(course=course).select_related('teacher')
        # 获取选课学生数量
        enrollment_count = Enrollment.objects.filter(course=course).count()
        # 获取考勤事件数量
        event_count = AttendanceEvent.objects.filter(course=course).count()
        
        course_stats.append({
            'course': course,
            'teaching_assignments': teaching_assignments,
            'enrollment_count': enrollment_count,
            'event_count': event_count,
        })
    
    context = {
        'course_stats': course_stats,
        'search': search,
    }
    return render(request, 'admin/manage_courses.html', context)

@login_required
@user_passes_test(is_admin)
def admin_statistics(request):
    """管理员统计报表"""
    # 获取所有课程的考勤统计
    courses = Course.objects.all()
    course_stats = []
    
    for course in courses:
        # 获取该课程的所有考勤记录
        attendances = Attendance.objects.filter(
            enrollment__course=course
        ).exclude(status=4)  # 排除未开始状态
        
        total_count = attendances.count()
        if total_count > 0:
            present_count = attendances.filter(status=1).count()
            absent_count = attendances.filter(status=2).count()
            leave_count = attendances.filter(status=3).count()
            
            present_rate = round((present_count / total_count) * 100, 1)
            absent_rate = round((absent_count / total_count) * 100, 1)
            leave_rate = round((leave_count / total_count) * 100, 1)
            
            # 获取该课程的考勤事件，按日期分组统计
            events = AttendanceEvent.objects.filter(course=course).order_by('event_date')
            event_stats = []
            
            for event in events:
                event_attendances = attendances.filter(event=event)
                event_total = event_attendances.count()
                if event_total > 0:
                    event_present = event_attendances.filter(status=1).count()
                    event_absent = event_attendances.filter(status=2).count()
                    event_leave = event_attendances.filter(status=3).count()
                    event_present_rate = round((event_present / event_total) * 100, 1)
                    
                    event_stats.append({
                        'event': event,
                        'date': event.event_date,
                        'total_count': event_total,
                        'present_count': event_present,
                        'absent_count': event_absent,
                        'leave_count': event_leave,
                        'present_rate': event_present_rate,
                    })
            
            course_stats.append({
                'course': course,
                'total_count': total_count,
                'present_count': present_count,
                'absent_count': absent_count,
                'leave_count': leave_count,
                'present_rate': present_rate,
                'absent_rate': absent_rate,
                'leave_rate': leave_rate,
                'event_stats': event_stats,  # 单次考勤统计
            })
    
    # 按出勤率排序
    course_stats.sort(key=lambda x: x['present_rate'], reverse=True)
    
    # 整体统计
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()
    total_events = AttendanceEvent.objects.count()
    
    # 为图表准备JSON数据
    courses_with_events_serializable = []
    for stat in course_stats:
        event_stats_serializable = []
        for event_stat in stat['event_stats']:
            event_stats_serializable.append({
                'event': {
                    'event_id': event_stat['event'].event_id,
                },
                'date': event_stat['date'].strftime('%Y-%m-%d'),
                'total_count': event_stat['total_count'],
                'present_count': event_stat['present_count'],
                'absent_count': event_stat['absent_count'],
                'leave_count': event_stat['leave_count'],
                'present_rate': event_stat['present_rate'],
            })
        
        courses_with_events_serializable.append({
            'course': {
                'course_id': stat['course'].course_id,
                'course_name': stat['course'].course_name,
            },
            'event_stats': event_stats_serializable,
        })
    
    chart_data_raw = {
        'present_total': sum(stat['present_count'] for stat in course_stats),
        'absent_total': sum(stat['absent_count'] for stat in course_stats),
        'leave_total': sum(stat['leave_count'] for stat in course_stats),
        'course_names': [stat['course'].course_name[:8] for stat in course_stats[:5]],
        'present_rates': [stat['present_rate'] for stat in course_stats[:5]],
        'courses_with_events': courses_with_events_serializable,  # 序列化后的数据
    }
    chart_data = json.dumps(chart_data_raw)
    
    context = {
        'course_stats': course_stats,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_events': total_events,
        'chart_data': chart_data,
    }
    return render(request, 'admin/statistics.html', context)

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    """管理员个人信息"""
    # 获取系统统计数据
    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    course_count = Course.objects.count()
    event_count = AttendanceEvent.objects.count()
    
    context = {
        'user': request.user,
        'student_count': student_count,
        'teacher_count': teacher_count,
        'course_count': course_count,
        'event_count': event_count,
    }
    return render(request, 'admin/profile.html', context)

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_department(request):
    """更新院系信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dept_id = data.get('dept_id')
            dept_name = data.get('dept_name')
            
            if not dept_id or not dept_name:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            department = get_object_or_404(Department, dept_id=dept_id)
            department.dept_name = dept_name
            department.save()
            
            return JsonResponse({'success': True, 'message': '院系更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_department(request):
    """删除院系"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dept_id = data.get('dept_id')
            
            if not dept_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            department = get_object_or_404(Department, dept_id=dept_id)
            
            # 检查是否有关联的专业
            if department.major_set.exists():
                return JsonResponse({'success': False, 'message': '该院系下还有专业，无法删除'})
            
            # 检查是否有关联的教师
            if department.teacher_set.exists():
                return JsonResponse({'success': False, 'message': '该院系下还有教师，无法删除'})
            
            department.delete()
            return JsonResponse({'success': True, 'message': '院系删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_major(request):
    """更新专业信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            major_id = data.get('major_id')
            major_name = data.get('major_name')
            dept_id = data.get('dept_id')
            
            if not major_id or not major_name or not dept_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            major = get_object_or_404(Major, major_id=major_id)
            department = get_object_or_404(Department, dept_id=dept_id)
            
            major.major_name = major_name
            major.dept = department
            major.save()
            
            return JsonResponse({'success': True, 'message': '专业更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_major(request):
    """删除专业"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            major_id = data.get('major_id')
            
            if not major_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            major = get_object_or_404(Major, major_id=major_id)
            
            # 检查是否有关联的学生
            if major.student_set.exists():
                return JsonResponse({'success': False, 'message': '该专业下还有学生，无法删除'})
            
            major.delete()
            return JsonResponse({'success': True, 'message': '专业删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_department(request):
    """添加院系"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dept_name = data.get('dept_name')
            
            if not dept_name:
                return JsonResponse({'success': False, 'message': '院系名称不能为空'})
            
            # 检查是否已存在相同名称的院系
            if Department.objects.filter(dept_name=dept_name).exists():
                return JsonResponse({'success': False, 'message': '该院系名称已存在'})
            
            # 创建新院系
            department = Department.objects.create(dept_name=dept_name)
            
            return JsonResponse({
                'success': True, 
                'message': '院系添加成功',
                'dept_id': department.dept_id,
                'dept_name': department.dept_name
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_major(request):
    """添加专业"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            major_name = data.get('major_name')
            dept_id = data.get('dept_id')
            
            if not major_name or not dept_id:
                return JsonResponse({'success': False, 'message': '专业名称和所属院系不能为空'})
            
            # 检查院系是否存在
            try:
                department = Department.objects.get(dept_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'message': '所选院系不存在'})
            
            # 检查是否已存在相同名称的专业
            if Major.objects.filter(major_name=major_name).exists():
                return JsonResponse({'success': False, 'message': '该专业名称已存在'})
            
            # 创建新专业
            major = Major.objects.create(
                major_name=major_name,
                dept=department
            )
            
            return JsonResponse({
                'success': True, 
                'message': '专业添加成功',
                'major_id': major.major_id,
                'major_name': major.major_name,
                'dept_name': department.dept_name
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
def get_majors(request):
    """获取所有专业列表"""
    majors = Major.objects.select_related('dept').all()
    majors_data = []
    for major in majors:
        majors_data.append({
            'major_id': major.major_id,
            'major_name': major.major_name,
            'dept_name': major.dept.dept_name,
            'dept_id': major.dept.dept_id
        })
    return JsonResponse({'majors': majors_data})

@login_required
@user_passes_test(is_admin)
def get_departments(request):
    """获取所有院系列表"""
    departments = Department.objects.all()
    departments_data = []
    for dept in departments:
        departments_data.append({
            'dept_id': dept.dept_id,
            'dept_name': dept.dept_name
        })
    return JsonResponse({'departments': departments_data})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_student(request):
    """添加学生"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stu_id = data.get('stu_id')
            stu_name = data.get('stu_name')
            stu_sex = data.get('stu_sex')
            major_id = data.get('major_id')
            
            if not stu_id or not stu_name or not stu_sex:
                return JsonResponse({'success': False, 'message': '请填写必要信息'})
            
            # 检查学号是否已存在
            if Student.objects.filter(stu_id=stu_id).exists():
                return JsonResponse({'success': False, 'message': '该学号已存在'})
            
            # 自动生成微信OpenID（临时方案，实际应该通过微信登录获取）
            openid = f"wx_openid_{stu_id}"
            
            # 获取专业对象（如果指定了专业）
            major = None
            if major_id:
                try:
                    major = Major.objects.get(major_id=major_id)
                except Major.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '所选专业不存在'})
            
            # 创建学生
            student = Student.objects.create(
                stu_id=stu_id,
                stu_name=stu_name,
                stu_sex=int(stu_sex),
                major=major,
                openid=openid
            )
            
            return JsonResponse({
                'success': True,
                'message': '学生添加成功',
                'student_data': {
                    'stu_id': student.stu_id,
                    'stu_name': student.stu_name,
                    'major_name': major.major_name if major else None
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_teacher(request):
    """添加教师"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            teacher_id = data.get('teacher_id')
            teacher_name = data.get('teacher_name')
            dept_id = data.get('dept_id')
            
            if not teacher_id or not teacher_name or not dept_id:
                return JsonResponse({'success': False, 'message': '请填写完整信息'})
            
            # 检查工号是否已存在
            if Teacher.objects.filter(teacher_id=teacher_id).exists():
                return JsonResponse({'success': False, 'message': '该工号已存在'})
            
            # 检查院系是否存在
            try:
                department = Department.objects.get(dept_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'message': '所选院系不存在'})
            
            # 创建教师
            teacher = Teacher.objects.create(
                teacher_id=teacher_id,
                teacher_name=teacher_name,
                dept=department
            )
            
            return JsonResponse({
                'success': True,
                'message': '教师添加成功',
                'teacher_data': {
                    'teacher_id': teacher.teacher_id,
                    'teacher_name': teacher.teacher_name,
                    'dept_name': department.dept_name
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_student(request):
    """删除学生"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            stu_id = data.get('stu_id')
            
            if not stu_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            student = get_object_or_404(Student, stu_id=stu_id)
            
            # 直接删除学生，级联删除选课记录
            student.delete()
            return JsonResponse({'success': True, 'message': '学生删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_teacher(request):
    """删除教师"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            teacher_id = data.get('teacher_id')
            
            if not teacher_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            
            # 直接删除教师，级联删除教学安排
            teacher.delete()
            return JsonResponse({'success': True, 'message': '教师删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_student(request):
    """更新学生信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_stu_id = data.get('original_stu_id')
            stu_id = data.get('stu_id')
            stu_name = data.get('stu_name')
            stu_sex = data.get('stu_sex')
            major_id = data.get('major_id')
            
            if not original_stu_id or not stu_id or not stu_name or not stu_sex:
                return JsonResponse({'success': False, 'message': '请填写必要信息'})
            
            student = get_object_or_404(Student, stu_id=original_stu_id)
            
            # 如果学号有变化，检查新学号是否已存在，并更新openid
            if stu_id != original_stu_id:
                if Student.objects.filter(stu_id=stu_id).exists():
                    return JsonResponse({'success': False, 'message': '新学号已存在'})
                # 如果学号改变，重新生成openid
                openid = f"wx_openid_{stu_id}"
            else:
                # 学号未变，保持原有openid
                openid = student.openid
            
            # 获取专业对象
            major = None
            if major_id:
                try:
                    major = Major.objects.get(major_id=major_id)
                except Major.DoesNotExist:
                    return JsonResponse({'success': False, 'message': '所选专业不存在'})
            
            # 更新学生信息
            student.stu_id = stu_id
            student.stu_name = stu_name
            student.stu_sex = int(stu_sex)
            student.major = major
            student.openid = openid
            student.save()
            
            return JsonResponse({'success': True, 'message': '学生信息更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_teacher(request):
    """更新教师信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_teacher_id = data.get('original_teacher_id')
            teacher_id = data.get('teacher_id')
            teacher_name = data.get('teacher_name')
            dept_id = data.get('dept_id')
            
            if not original_teacher_id or not teacher_id or not teacher_name or not dept_id:
                return JsonResponse({'success': False, 'message': '请填写完整信息'})
            
            teacher = get_object_or_404(Teacher, teacher_id=original_teacher_id)
            
            # 如果工号有变化，检查新工号是否已存在
            if teacher_id != original_teacher_id:
                if Teacher.objects.filter(teacher_id=teacher_id).exists():
                    return JsonResponse({'success': False, 'message': '新工号已存在'})
            
            # 检查院系是否存在
            try:
                department = Department.objects.get(dept_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'message': '所选院系不存在'})
            
            # 更新教师信息
            teacher.teacher_id = teacher_id
            teacher.teacher_name = teacher_name
            teacher.dept = department
            teacher.save()
            
            return JsonResponse({'success': True, 'message': '教师信息更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_course(request):
    """添加课程"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            course_name = data.get('course_name')
            dept_id = data.get('dept_id')
            
            if not course_id or not course_name or not dept_id:
                return JsonResponse({'success': False, 'message': '请填写完整信息'})
            
            # 检查课程ID是否已存在
            if Course.objects.filter(course_id=course_id).exists():
                return JsonResponse({'success': False, 'message': '该课程编号已存在'})
            
            # 检查院系是否存在
            try:
                department = Department.objects.get(dept_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'message': '所选院系不存在'})
            
            # 创建课程
            course = Course.objects.create(
                course_id=course_id,
                course_name=course_name,
                dept=department
            )
            
            return JsonResponse({
                'success': True,
                'message': '课程添加成功',
                'course_data': {
                    'course_id': course.course_id,
                    'course_name': course.course_name,
                    'dept_name': department.dept_name
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_course(request):
    """更新课程信息"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            original_course_id = data.get('original_course_id')
            course_id = data.get('course_id')
            course_name = data.get('course_name')
            dept_id = data.get('dept_id')
            
            if not original_course_id or not course_id or not course_name or not dept_id:
                return JsonResponse({'success': False, 'message': '请填写完整信息'})
            
            course = get_object_or_404(Course, course_id=original_course_id)
            
            # 如果课程ID有变化，检查新ID是否已存在
            if course_id != original_course_id:
                if Course.objects.filter(course_id=course_id).exists():
                    return JsonResponse({'success': False, 'message': '新课程ID已存在'})
            
            # 检查院系是否存在
            try:
                department = Department.objects.get(dept_id=dept_id)
            except Department.DoesNotExist:
                return JsonResponse({'success': False, 'message': '所选院系不存在'})
            
            # 更新课程信息
            course.course_id = course_id
            course.course_name = course_name
            course.dept = department
            course.save()
            
            return JsonResponse({'success': True, 'message': '课程信息更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_course(request):
    """删除课程"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            
            if not course_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            course = get_object_or_404(Course, course_id=course_id)
            
            # 直接删除课程，级联删除相关数据
            course.delete()
            return JsonResponse({'success': True, 'message': '课程删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
def get_teachers(request):
    """获取所有教师列表"""
    teachers = Teacher.objects.select_related('dept').all()
    teachers_data = []
    for teacher in teachers:
        teachers_data.append({
            'teacher_id': teacher.teacher_id,
            'teacher_name': teacher.teacher_name,
            'dept_name': teacher.dept.dept_name,
            'dept_id': teacher.dept.dept_id
        })
    return JsonResponse({'teachers': teachers_data})

@login_required
@user_passes_test(is_admin)
def get_students(request):
    """获取所有学生列表"""
    students = Student.objects.select_related('major', 'major__dept').all()
    students_data = []
    for student in students:
        students_data.append({
            'stu_id': student.stu_id,
            'stu_name': student.stu_name,
            'major_name': student.major.major_name if student.major else None,
            'dept_name': student.major.dept.dept_name if student.major else None,
        })
    return JsonResponse({'students': students_data})

@login_required
@user_passes_test(is_admin)
def manage_teaching_assignment(request, course_id):
    """管理教学安排页面"""
    try:
        course = get_object_or_404(Course, course_id=course_id)
        teaching_assignments = TeachingAssignment.objects.filter(course=course).select_related('teacher__dept')
        
        # 获取该课程的课程时间安排
        class_schedules = ClassSchedule.objects.filter(
            assignment__course=course
        ).select_related('assignment__teacher', 'assignment__teacher__dept').order_by('class_date', 'start_period')
        
        # 获取所有教师用于下拉选择
        teachers = Teacher.objects.all().select_related('dept')
        
        context = {
            'course': course,
            'teaching_assignments': teaching_assignments,
            'class_schedules': class_schedules,
            'teachers': teachers,
        }
        return render(request, 'admin/manage_teaching_assignment.html', context)
    except Exception as e:
        messages.error(request, f'加载教学安排页面失败: {str(e)}')
        return redirect('manage_courses')

@login_required
@user_passes_test(is_admin)
def manage_enrollment(request, course_id):
    """管理选课页面"""
    try:
        course = get_object_or_404(Course, course_id=course_id)
        enrollments = Enrollment.objects.filter(course=course).select_related('student__major__dept')
        
        context = {
            'course': course,
            'enrollments': enrollments,
        }
        return render(request, 'admin/manage_enrollment.html', context)
    except Exception as e:
        messages.error(request, f'加载选课管理页面失败: {str(e)}')
        return redirect('manage_courses')

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_enrollment(request):
    """添加选课记录"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            student_id = data.get('student_id')
            
            if not course_id or not student_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            course = get_object_or_404(Course, course_id=course_id)
            student = get_object_or_404(Student, stu_id=student_id)
            
            # 检查是否已存在相同的选课记录
            if Enrollment.objects.filter(student=student, course=course).exists():
                return JsonResponse({'success': False, 'message': '该学生已经选修此课程'})
            
            # 创建选课记录
            enrollment = Enrollment.objects.create(
                student=student,
                course=course
            )
            
            return JsonResponse({'success': True, 'message': '选课记录添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_enrollment(request):
    """删除选课记录"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            enroll_id = data.get('enroll_id')
            
            if not enroll_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            enrollment = get_object_or_404(Enrollment, enroll_id=enroll_id)
            
            # 检查是否有考勤记录，如果有则不允许删除
            if Attendance.objects.filter(enrollment=enrollment).exists():
                return JsonResponse({'success': False, 'message': '该学生已有考勤记录，无法删除选课记录'})
            
            enrollment.delete()
            
            return JsonResponse({'success': True, 'message': '选课记录删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_teaching_assignment(request):
    """添加教学安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            teacher_id = data.get('teacher_id')
            
            if not course_id or not teacher_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            course = get_object_or_404(Course, course_id=course_id)
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            
            # 检查是否已存在相同的教学安排
            if TeachingAssignment.objects.filter(course=course, teacher=teacher).exists():
                return JsonResponse({'success': False, 'message': '该教师已经被安排到此课程'})
            
            # 创建教学安排
            assignment = TeachingAssignment.objects.create(
                course=course,
                teacher=teacher
            )
            
            return JsonResponse({'success': True, 'message': '教学安排添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_teaching_assignment(request):
    """更新教学安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assignment_id = data.get('assignment_id')
            teacher_id = data.get('teacher_id')
            
            if not assignment_id or not teacher_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            assignment = get_object_or_404(TeachingAssignment, assignment_id=assignment_id)
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            
            # 检查是否已存在相同的教学安排
            if TeachingAssignment.objects.filter(course=assignment.course, teacher=teacher).exclude(assignment_id=assignment_id).exists():
                return JsonResponse({'success': False, 'message': '该教师已经被安排到此课程'})
            
            # 更新教学安排
            assignment.teacher = teacher
            assignment.save()
            
            return JsonResponse({'success': True, 'message': '教学安排更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_teaching_assignment(request):
    """删除教学安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            assignment_id = data.get('assignment_id')
            
            if not assignment_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            assignment = get_object_or_404(TeachingAssignment, assignment_id=assignment_id)
            assignment.delete()
            
            return JsonResponse({'success': True, 'message': '教学安排删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def add_class_schedule(request):
    """添加课程时间安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            teacher_id = data.get('teacher_id')
            class_date = data.get('class_date')
            weekday = data.get('weekday')
            start_period = data.get('start_period')
            end_period = data.get('end_period')
            location = data.get('location')
            
            if not all([course_id, teacher_id, class_date, weekday, start_period, end_period, location]):
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            course = get_object_or_404(Course, course_id=course_id)
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            
            # 获取或创建教学安排
            assignment, created = TeachingAssignment.objects.get_or_create(
                course=course,
                teacher=teacher
            )
            
            # 检查时间冲突（同一日期、同一时间段、同一地点）
            if ClassSchedule.objects.filter(
                class_date=class_date,
                location=location,
                start_period__lte=end_period,
                end_period__gte=start_period
            ).exists():
                return JsonResponse({'success': False, 'message': '该日期、时间段和地点已有其他课程安排'})
            
            # 创建课程时间安排
            schedule = ClassSchedule.objects.create(
                assignment=assignment,
                class_date=class_date,
                weekday=weekday,
                start_period=start_period,
                end_period=end_period,
                location=location
            )
            
            return JsonResponse({'success': True, 'message': '课程时间安排添加成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def update_class_schedule(request):
    """更新课程时间安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('schedule_id')
            teacher_id = data.get('teacher_id')
            class_date = data.get('class_date')
            weekday = data.get('weekday')
            start_period = data.get('start_period')
            end_period = data.get('end_period')
            location = data.get('location')
            
            if not all([schedule_id, teacher_id, class_date, weekday, start_period, end_period, location]):
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            schedule = get_object_or_404(ClassSchedule, schedule_id=schedule_id)
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            
            # 检查时间冲突（排除当前记录，同一日期、同一时间段、同一地点）
            if ClassSchedule.objects.filter(
                class_date=class_date,
                location=location,
                start_period__lte=end_period,
                end_period__gte=start_period
            ).exclude(schedule_id=schedule_id).exists():
                return JsonResponse({'success': False, 'message': '该日期、时间段和地点已有其他课程安排'})
            
            # 如果教师变更，需要更新或创建新的教学安排
            if schedule.assignment.teacher != teacher:
                # 获取或创建新的教学安排
                new_assignment, created = TeachingAssignment.objects.get_or_create(
                    course=schedule.assignment.course,
                    teacher=teacher
                )
                schedule.assignment = new_assignment
            
            # 更新课程时间安排
            schedule.class_date = class_date
            schedule.weekday = weekday
            schedule.start_period = start_period
            schedule.end_period = end_period
            schedule.location = location
            schedule.save()
            
            return JsonResponse({'success': True, 'message': '课程时间安排更新成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

@login_required
@user_passes_test(is_admin)
@csrf_exempt
def delete_class_schedule(request):
    """删除课程时间安排"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('schedule_id')
            
            if not schedule_id:
                return JsonResponse({'success': False, 'message': '参数不完整'})
            
            schedule = get_object_or_404(ClassSchedule, schedule_id=schedule_id)
            assignment = schedule.assignment
            
            # 删除课程时间安排
            schedule.delete()
            
            # 如果该教学安排下没有其他课程安排了，也删除教学安排
            if not ClassSchedule.objects.filter(assignment=assignment).exists():
                assignment.delete()
            
            return JsonResponse({'success': True, 'message': '课程时间安排删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'}) 