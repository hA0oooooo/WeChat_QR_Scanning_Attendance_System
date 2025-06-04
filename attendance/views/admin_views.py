from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from ..models import Student, Teacher, Course, Department, Major

def is_admin(user):
    """检查用户是否是管理员"""
    return user.is_staff and user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """管理员仪表盘"""
    # 获取统计数据
    student_count = Student.objects.count()
    teacher_count = Teacher.objects.count()
    course_count = Course.objects.count()
    department_count = Department.objects.count()
    
    context = {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'course_count': course_count,
        'department_count': department_count
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_students(request):
    """管理学生信息"""
    students = Student.objects.all().order_by('stu_id')
    context = {
        'students': students
    }
    return render(request, 'admin/manage_students.html', context)

@login_required
@user_passes_test(is_admin)
def manage_teachers(request):
    """管理教师信息"""
    teachers = Teacher.objects.all().order_by('teacher_id')
    context = {
        'teachers': teachers
    }
    return render(request, 'admin/manage_teachers.html', context)

@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    """管理课程信息"""
    courses = Course.objects.all().order_by('course_id')
    context = {
        'courses': courses
    }
    return render(request, 'admin/manage_courses.html', context)

@login_required
@user_passes_test(is_admin)
def manage_departments(request):
    """管理部门信息"""
    departments = Department.objects.all().order_by('dept_name')
    context = {
        'departments': departments
    }
    return render(request, 'admin/manage_departments.html', context)

@login_required
@user_passes_test(is_admin)
def manage_majors(request):
    """管理专业信息"""
    majors = Major.objects.all().order_by('major_name')
    context = {
        'majors': majors
    }
    return render(request, 'admin/manage_majors.html', context) 