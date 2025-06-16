"""
微信扫码考勤系统 - 测试数据初始化模块
用于创建完整的演示数据环境

功能说明：
- 创建系统所需的基础数据（部门、专业、课程）
- 创建用户账号（管理员、教师、学生）
- 创建考勤事件和考勤记录
- 设置符合演示需求的数据状态
"""

import os
import sys
import django
from datetime import datetime, date, time

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import (
    Department, Major, Course, Teacher, Student, Enrollment, 
    AttendanceEvent, Attendance, LeaveRequest,
    STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE, STATUS_NOT_STARTED,
    LEAVE_PENDING, LEAVE_APPROVED, LEAVE_REJECTED
)


def create_basic_data():
    """创建基础数据：部门、专业、课程"""
    print("创建基础数据...")
    
    # 创建部门
    dept, _ = Department.objects.get_or_create(
        dept_name='大数据学院'
    )
    
    # 创建专业
    major, _ = Major.objects.get_or_create(
        major_name='数据科学与大数据技术',
        defaults={'dept': dept}
    )
    
    # 创建课程
    course, _ = Course.objects.get_or_create(
        course_id='DATA130039.01',
        defaults={
            'course_name': '数据库及实现',
            'dept': dept,
            'credit': 3
        }
    )
    
    print(f"✓ 部门: {dept.dept_name}")
    print(f"✓ 专业: {major.major_name}")
    print(f"✓ 课程: {course.course_name} ({course.course_id})")
    
    return dept, major, course


def create_users_and_roles(dept, major):
    """创建用户账号和角色"""
    print("\n创建用户账号...")
    
    # 创建管理员
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('1')
        admin_user.save()
    print(f"✓ 管理员: admin/1")
    
    # 创建教师
    teacher_user, created = User.objects.get_or_create(
        username='12345',
        defaults={
            'email': 'teacher@example.com',
            'first_name': '郑',
            'last_name': '老师'
        }
    )
    if created:
        teacher_user.set_password('1')
        teacher_user.save()
    
    teacher, _ = Teacher.objects.get_or_create(
        teacher_id='12345',
        defaults={
            'teacher_name': '郑老师',
            'dept': dept,
            'user': teacher_user
        }
    )
    print(f"✓ 教师: 12345/1 ({teacher.teacher_name})")
    
    # 创建学生
    student_id, name = '23307130001', '开心'
    
    user, created = User.objects.get_or_create(
        username=student_id,
        defaults={
            'email': f'{student_id}@student.edu.cn',
            'first_name': name
        }
    )
    if created:
        user.set_password('1')
        user.save()
    
    student, _ = Student.objects.get_or_create(
        stu_id=student_id,
        defaults={
            'stu_name': name,
            'stu_sex': 1,
            'major': major,
            'openid': f'wx_openid_{student_id}',
            'user': user
        }
    )
    students = [student]
    print(f"✓ 学生: {student_id}/1 ({name})")
    
    return teacher, students


def create_course_data(course, students):
    """创建课程相关数据：选课记录、考勤事件、考勤记录"""
    print("\n创建课程数据...")
    
    # 创建选课记录
    for student in students:
        Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'semester': '202501'}
        )
    print(f"✓ 选课记录: {len(students)}个学生选修{course.course_name}")
    
    # 创建考勤事件
    events_data = [
        (date(2025, 6, 11), '第一次课'),  # 过去 - 出勤
        (date(2025, 6, 18), '第二次课'),  # 今天 - 缺勤(等待扫码)
        (date(2025, 6, 25), '第三次课'),  # 未来 - 未开始(可请假)
    ]
    
    for event_date, description in events_data:
        start_datetime = datetime.combine(event_date, time(9, 55))
        end_datetime = datetime.combine(event_date, time(12, 30))
        
        event, _ = AttendanceEvent.objects.get_or_create(
            course=course,
            event_date=event_date,
            defaults={
                'scan_start_time': start_datetime,
                'scan_end_time': end_datetime
            }
        )
        
        # 创建考勤记录
        for student in students:
            enrollment = Enrollment.objects.get(student=student, course=course)
            
            # 清除旧记录
            Attendance.objects.filter(enrollment=enrollment, event=event).delete()
            
            # 设置考勤状态
            if event_date == date(2025, 6, 11):  # 6月11日 - 出勤
                status = STATUS_PRESENT
                scan_time = datetime.combine(event_date, time(10, 0))
            elif event_date == date(2025, 6, 18):  # 6月18日 - 缺勤
                status = STATUS_ABSENT
                scan_time = None
            else:  # 6月25日 - 未开始
                status = STATUS_NOT_STARTED
                scan_time = None
            
            Attendance.objects.create(
                enrollment=enrollment,
                event=event,
                status=status,
                scan_time=scan_time
            )
        
        print(f"✓ 考勤事件: {event_date} - {description}")


def clear_leave_requests():
    """清空请假申请（用于演示）"""
    LeaveRequest.objects.all().delete()
    print("\n✓ 清空请假申请 - 准备演示环境")


def create_test_data():
    """主函数：创建完整的测试数据"""
    print("=" * 50)
    print("微信扫码考勤系统 - 测试数据初始化")
    print("=" * 50)
    
    try:
        # 1. 创建基础数据
        dept, major, course = create_basic_data()
        
        # 2. 创建用户和角色
        teacher, students = create_users_and_roles(dept, major)
        
        # 3. 创建课程数据
        create_course_data(course, students)
        
        # 4. 清空请假申请
        clear_leave_requests()
        
        print("\n" + "=" * 50)
        print("✅ 测试数据初始化完成!")
        print("\n📊 演示场景:")
        print("  • 6月11日：学生开心出勤")
        print("  • 6月18日：学生开心缺勤（可通过扫码变为出勤）")
        print("  • 6月25日：学生开心未开始（可申请请假）")
        print("  • 当前时间：6月18日11:00（课程进行中）")
        print("  • 待审批请假：空（可演示申请请假）")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        raise


if __name__ == '__main__':
    create_test_data() 