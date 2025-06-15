#!/usr/bin/env python
"""
系统验证测试模块
用于检查系统各个组件的完整性和正确性
"""

import os
import sys
import django
import glob

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.urls import reverse
from django.test import TestCase
from attendance.models import Student, User, Course, Teacher, Department


class SystemValidationTest:
    """系统验证测试器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_url_configuration(self):
        """检查URL配置"""
        print('1. URL配置检查:')
        
        urls_to_check = [
            # 学生端URL
            'student_dashboard',
            'student_courses', 
            'student_course_detail',
            'student_attendance',
            'submit_leave_request',
            'leave_request_history',
            'student_profile',
            'attendance_statistics',
            
            # 教师端URL
            'teacher_dashboard',
            'teacher_courses',
            'course_detail',
            'manage_attendance_events',
            'create_attendance_event',
            'view_attendance_results',
            'leave_request_list',
            'teacher_profile',
            
            # 管理员URL
            'admin_dashboard',
            
            # 基础URL
            'index',
            'login',
        ]
        
        for url_name in urls_to_check:
            try:
                if url_name in ['student_course_detail', 'course_detail']:
                    url = reverse(url_name, args=['CS101'])
                elif url_name in ['view_attendance_results', 'manage_attendance_events', 'create_attendance_event']:
                    url = reverse(url_name, args=['DB2024']) if 'course' in url_name else reverse(url_name, args=[1])
                else:
                    url = reverse(url_name)
                print(f'   ✓ {url_name}: {url}')
            except Exception as e:
                error_msg = f'{url_name}: {e}'
                print(f'   ✗ {error_msg}')
                self.errors.append(f'URL配置错误: {error_msg}')
    
    def check_test_data(self):
        """检查测试数据"""
        print('\n2. 测试数据检查:')
        
        try:
            # 检查学生数据
            student_count = Student.objects.count()
            print(f'   ✓ 学生总数: {student_count}')
            
            if student_count > 0:
                student = Student.objects.first()
                print(f'   ✓ 示例学生: {student.stu_name} ({student.stu_id})')
                
                # 检查用户关联
                if hasattr(student, 'user') and student.user:
                    print(f'   ✓ 用户关联: {student.user.username}')
                else:
                    warning_msg = '部分学生未关联用户账号'
                    print(f'   ⚠ {warning_msg}')
                    self.warnings.append(warning_msg)
            
            # 检查教师数据
            teacher_count = Teacher.objects.count()
            print(f'   ✓ 教师总数: {teacher_count}')
            
            # 检查课程数据
            course_count = Course.objects.count()
            print(f'   ✓ 课程总数: {course_count}')
            
            # 检查院系数据
            dept_count = Department.objects.count()
            print(f'   ✓ 院系总数: {dept_count}')
                
        except Exception as e:
            error_msg = f'测试数据检查失败: {e}'
            print(f'   ✗ {error_msg}')
            self.errors.append(error_msg)
    
    def check_template_files(self):
        """检查模板文件"""
        print('\n3. 模板文件检查:')
        
        # 检查学生端模板
        print('   学生端模板:')
        student_templates = [
            'dashboard.html',
            'courses.html', 
            'course_detail.html',
            'attendance.html',
            'leave_request.html',
            'leave_request_history.html',
            'statistics.html',
            'profile.html'
        ]
        
        template_files = glob.glob('attendance/templates/student/*.html')
        for template in student_templates:
            if any(template in f for f in template_files):
                print(f'     ✓ {template}')
            else:
                error_msg = f'学生端模板文件不存在: {template}'
                print(f'     ✗ {error_msg}')
                self.errors.append(error_msg)
        
        # 检查教师端模板
        print('   教师端模板:')
        teacher_templates = [
            'dashboard.html',
            'courses.html',
            'course_detail.html',
            'attendance_results.html',
            'create_attendance_event.html',
            'leave.html',
            'profile.html'
        ]
        
        teacher_template_files = glob.glob('attendance/templates/teacher/*.html')
        for template in teacher_templates:
            if any(template in f for f in teacher_template_files):
                print(f'     ✓ {template}')
            else:
                warning_msg = f'教师端模板可能缺失: {template}'
                print(f'     ⚠ {warning_msg}')
                self.warnings.append(warning_msg)
    
    def check_view_functions(self):
        """检查视图函数"""
        print('\n4. 视图函数检查:')
        
        try:
            # 检查学生端视图函数
            print('   学生端视图函数:')
            from attendance.views.student_views import (
                student_dashboard, student_courses, course_detail, student_attendance,
                submit_leave_request, leave_request_history, student_profile, attendance_statistics
            )
            
            student_view_functions = [
                'student_dashboard', 'student_courses', 'course_detail', 'student_attendance',
                'submit_leave_request', 'leave_request_history', 'student_profile', 'attendance_statistics'
            ]
            
            for func_name in student_view_functions:
                print(f'     ✓ {func_name}: 已导入')
            
            # 检查教师端视图函数
            print('   教师端视图函数:')
            from attendance.views.teacher_views import (
                teacher_dashboard, teacher_courses, course_detail as teacher_course_detail,
                create_attendance_event, view_attendance_results, leave_request_list, teacher_profile
            )
            
            teacher_view_functions = [
                'teacher_dashboard', 'teacher_courses', 'teacher_course_detail',
                'create_attendance_event', 'view_attendance_results', 'leave_request_list', 'teacher_profile'
            ]
            
            for func_name in teacher_view_functions:
                print(f'     ✓ {func_name}: 已导入')
                
        except ImportError as e:
            error_msg = f'视图函数导入失败: {e}'
            print(f'   ✗ {error_msg}')
            self.errors.append(error_msg)
    
    def check_django_system(self):
        """检查Django系统"""
        print('\n5. Django系统检查:')
        
        try:
            from django.core.management import execute_from_command_line
            import io
            import contextlib
            
            # 捕获系统检查输出
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    try:
                        from django.core.management.commands.check import Command
                        command = Command()
                        command.check()
                        print('   ✓ Django系统检查通过')
                    except Exception as e:
                        error_msg = f'Django系统检查失败: {e}'
                        print(f'   ✗ {error_msg}')
                        self.errors.append(error_msg)
        except Exception as e:
            warning_msg = f'无法执行Django系统检查: {e}'
            print(f'   ⚠ {warning_msg}')
            self.warnings.append(warning_msg)
    
    def check_login_accounts(self):
        """检查登录账号"""
        print('\n6. 登录账号检查:')
        
        try:
            # 检查管理员账号
            admin_users = User.objects.filter(is_superuser=True)
            if admin_users.exists():
                admin = admin_users.first()
                print(f'   ✓ 管理员账号: {admin.username}')
            else:
                error_msg = '未找到管理员账号'
                print(f'   ✗ {error_msg}')
                self.errors.append(error_msg)
            
            # 检查教师账号
            teacher_users = User.objects.filter(teacher__isnull=False)
            if teacher_users.exists():
                teacher_user = teacher_users.first()
                print(f'   ✓ 教师账号: {teacher_user.username}')
            else:
                error_msg = '未找到教师账号'
                print(f'   ✗ {error_msg}')
                self.errors.append(error_msg)
            
            # 检查学生账号
            student_users = User.objects.filter(student__isnull=False)
            if student_users.exists():
                student_user = student_users.first()
                print(f'   ✓ 学生账号: {student_user.username}')
            else:
                error_msg = '未找到学生账号'
                print(f'   ✗ {error_msg}')
                self.errors.append(error_msg)
                
        except Exception as e:
            error_msg = f'登录账号检查失败: {e}'
            print(f'   ✗ {error_msg}')
            self.errors.append(error_msg)
    
    def run_all_checks(self):
        """运行所有检查"""
        print('=== 系统验证测试开始 ===\n')
        
        self.check_url_configuration()
        self.check_test_data()
        self.check_template_files()
        self.check_view_functions()
        self.check_django_system()
        self.check_login_accounts()
        
        print('\n=== 系统验证测试完成 ===')
        
        # 输出总结
        if self.errors:
            print(f'\n❌ 发现 {len(self.errors)} 个错误:')
            for i, error in enumerate(self.errors, 1):
                print(f'   {i}. {error}')
        
        if self.warnings:
            print(f'\n⚠️  发现 {len(self.warnings)} 个警告:')
            for i, warning in enumerate(self.warnings, 1):
                print(f'   {i}. {warning}')
        
        if not self.errors and not self.warnings:
            print('\n✅ 系统验证通过，所有检查项目正常！')
        elif not self.errors:
            print('\n✅ 系统基本正常，仅有少量警告。')
        else:
            print('\n❌ 系统存在错误，需要修复后才能正常使用。')
        
        return len(self.errors) == 0


def main():
    """主函数"""
    validator = SystemValidationTest()
    success = validator.run_all_checks()
    
    if success:
        print('\n🎉 系统准备就绪！')
        print('\n可用的登录账号:')
        print('管理员: admin / 1')
        print('教师: 12345 / 1') 
        print('学生: 23307130001 / 1')
        print('\n服务器地址: http://127.0.0.1:8000/')
    else:
        print('\n⚠️  请先修复上述错误后再使用系统。')
    
    return success


if __name__ == '__main__':
    main() 