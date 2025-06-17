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
from django.utils import timezone
import pytz

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import (
    Department, Major, Course, Teacher, Student, Enrollment, 
    AttendanceEvent, Attendance, LeaveRequest, TeachingAssignment, ClassSchedule,
    STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE, STATUS_NOT_STARTED,
    LEAVE_PENDING, LEAVE_APPROVED, LEAVE_REJECTED
)


def create_basic_data():
    """创建基础数据：部门、专业、课程"""
    print("创建基础数据...")
    
    # 创建部门
    dept_bigdata, _ = Department.objects.get_or_create(
        dept_name='大数据学院'
    )
    
    dept_math, _ = Department.objects.get_or_create(
        dept_name='数学科学学院'
    )
    
    # 创建专业
    major_bigdata, _ = Major.objects.get_or_create(
        major_name='数据科学与大数据技术',
        defaults={'dept': dept_bigdata}
    )
    
    major_math, _ = Major.objects.get_or_create(
        major_name='应用数学',
        defaults={'dept': dept_math}
    )
    
    # 创建课程
    course_database, _ = Course.objects.get_or_create(
        course_id='DATA130039.01',
        defaults={
            'course_name': '数据库及实现',
            'dept': dept_bigdata
        }
    )
    
    # 添加最优化方法课程（凑数用）
    course_optimization, _ = Course.objects.get_or_create(
        course_id='DATA130026.01',
        defaults={
            'course_name': '最优化方法',
            'dept': dept_math
        }
    )
    
    print(f"✓ 部门: {dept_bigdata.dept_name}, {dept_math.dept_name}")
    print(f"✓ 专业: {major_bigdata.major_name}, {major_math.major_name}")
    print(f"✓ 课程: {course_database.course_name} ({course_database.course_id})")
    print(f"✓ 课程: {course_optimization.course_name} ({course_optimization.course_id})")
    
    return dept_bigdata, dept_math, major_bigdata, major_math, course_database, course_optimization


def create_users_and_roles(dept_bigdata, major_bigdata):
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
            'dept': dept_bigdata,
            'user': teacher_user
        }
    )
    print(f"✓ 教师: 12345/1 ({teacher.teacher_name})")
    
    # 创建10个学生数据，但只有23307130001有用户账号
    students_data = [
        ('23307130001', '开心', True),    # 有账号
        ('23307130002', '勇敢', False),   # 只有数据，无账号
        ('23307130003', '自信', False),
        ('23307130004', '坚强', False),
        ('23307130005', '美丽', False),
        ('23307130006', '智慧', False),
        ('23307130007', '努力', False),
        ('23307130008', '温暖', False),
        ('23307130009', '光明', False),
        ('23307130010', '希望', False),
    ]
    
    students = []
    for student_id, name, create_user in students_data:
        user = None
        if create_user:
            # 只为23307130001创建用户账号
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
                'stu_sex': 1 if student_id[-1] in '13579' else 0,  # 奇数学号为男，偶数为女
                'major': major_bigdata,
                'openid': f'wx_openid_{student_id}',  # 所有学生都需要openid，但只有开心的是真实的
                'user': user  # 只有23307130001有用户关联
            }
        )
        students.append(student)
    
    print(f"✓ 学生: 创建了{len(students)}个学生数据（仅23307130001有登录账号）")
    
    return teacher, students


def create_teaching_assignments(course, teacher):
    """创建教学安排和课程时间安排"""
    print("\n创建教学安排...")
    
    # 数据库及实现课程的教学安排
    assignment, _ = TeachingAssignment.objects.get_or_create(
        course=course,
        teacher=teacher
    )
    
    # 清除旧的课程时间安排
    ClassSchedule.objects.filter(assignment=assignment).delete()
    
    # 创建数据库及实现的时间安排（星期三第3-5节）
    schedule_data = [
        (date(2025, 6, 11), 3, 3, 5, 'HGX508'),
        (date(2025, 6, 18), 3, 3, 5, 'HGX508'),
        (date(2025, 6, 25), 3, 3, 5, 'HGX508'),
    ]
    
    for class_date, weekday, start_period, end_period, location in schedule_data:
        ClassSchedule.objects.create(
            assignment=assignment,
            class_date=class_date,
            weekday=weekday,
            start_period=start_period,
            end_period=end_period,
            location=location
        )
    
    print(f"✓ {course.course_name}: 3次课程安排 (HGX508)")


def create_teaching_assignments_optimization(course, teacher):
    """创建最优化方法的教学安排和课程时间安排"""
    print(f"\n创建{course.course_name}教学安排...")
    
    # 最优化方法课程的教学安排
    assignment, _ = TeachingAssignment.objects.get_or_create(
        course=course,
        teacher=teacher
    )
    
    # 清除旧的课程时间安排
    ClassSchedule.objects.filter(assignment=assignment).delete()
    
    # 创建最优化方法的时间安排（星期四第6-8节）
    schedule_data = [
        (date(2025, 6, 12), 4, 6, 8, 'H3209'),
        (date(2025, 6, 19), 4, 6, 8, 'H3209'),
        (date(2025, 6, 26), 4, 6, 8, 'H3209'),
    ]
    
    for class_date, weekday, start_period, end_period, location in schedule_data:
        ClassSchedule.objects.create(
            assignment=assignment,
            class_date=class_date,
            weekday=weekday,
            start_period=start_period,
            end_period=end_period,
            location=location
        )
    
    print(f"✓ {course.course_name}: 3次课程安排 (H3209)")


def create_course_data(course, students):
    """创建课程相关数据：选课记录、考勤事件、考勤记录"""
    print("\n创建课程数据...")
    
    # 为课程创建选课记录
    for student in students:
        Enrollment.objects.get_or_create(
            student=student,
            course=course
        )
    print(f"✓ 选课记录: {len(students)}个学生选修{course.course_name}")
    
    # 数据库及实现课程的考勤事件
    events_data = [
        (date(2025, 6, 11), '第一次课'),  # 过去 - 按README要求，开心出勤
        (date(2025, 6, 18), '第二次课'),  # 今天 - 按README要求，开心缺勤(等待扫码)
        (date(2025, 6, 25), '第三次课'),  # 未来 - 未开始(可请假)
    ]
    
    for event_date, description in events_data:
        start_datetime = timezone.make_aware(datetime.combine(event_date, time(9, 55)))
        end_datetime = timezone.make_aware(datetime.combine(event_date, time(12, 30)))
        
        event, _ = AttendanceEvent.objects.get_or_create(
            course=course,
            event_date=event_date,
            defaults={
                'scan_start_time': start_datetime,
                'scan_end_time': end_datetime
            }
        )
        
        # 创建考勤记录
        for i, student in enumerate(students):
            enrollment = Enrollment.objects.get(student=student, course=course)
            
            # 清除旧记录
            Attendance.objects.filter(enrollment=enrollment, event=event).delete()
            
            # 设置考勤状态 - 为了演示效果，创建丰富的数据
            if event_date == date(2025, 6, 11):  # 6月11日 - 8个出勤，2个缺勤
                if i < 8:  # 前8个学生出勤（包括开心）
                    status = STATUS_PRESENT
                    scan_time = timezone.make_aware(datetime.combine(event_date, time(10, 0 + i)))
                else:  # 后2个学生缺勤
                    status = STATUS_ABSENT
                    scan_time = None
            elif event_date == date(2025, 6, 18):  # 6月18日 - 开心缺勤，其他学生有出勤有缺勤
                if i == 0:  # 开心（第一个学生）缺勤，符合README要求
                    status = STATUS_ABSENT
                    scan_time = None
                elif i < 5:  # 其他4个学生出勤
                    status = STATUS_PRESENT
                    scan_time = timezone.make_aware(datetime.combine(event_date, time(9, 55 + i)))
                elif i < 8:  # 3个学生缺勤
                    status = STATUS_ABSENT
                    scan_time = None
                else:  # 2个学生请假
                    status = STATUS_LEAVE
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
        
        print(f"✓ 考勤事件: {course.course_name} {event_date} - {description}")


def create_course_data_optimization(course, all_students):
    """创建最优化方法课程数据：选课记录、考勤事件、考勤记录"""
    print(f"\n创建{course.course_name}课程数据...")
    
    # 选择5个学生（不包括开心，即学号23307130001）
    # 选择学号为23307130002-23307130006的5个学生
    selected_students = [student for student in all_students if student.stu_id in [
        '23307130002', '23307130003', '23307130004', '23307130005', '23307130006'
    ]]
    
    # 为最优化方法课程创建选课记录
    for student in selected_students:
        Enrollment.objects.get_or_create(
            student=student,
            course=course
        )
    print(f"✓ 选课记录: {len(selected_students)}个学生选修{course.course_name}")
    
    # 最优化方法课程的考勤事件（周四课程）
    events_data = [
        (date(2025, 6, 12), '第一次课'),  # 过去 - 高出勤率
        (date(2025, 6, 19), '第二次课'),  # 未来 - 中等出勤率  
        (date(2025, 6, 26), '第三次课'),  # 未来 - 未开始
    ]
    
    for event_date, description in events_data:
        start_datetime = timezone.make_aware(datetime.combine(event_date, time(13, 30)))
        end_datetime = timezone.make_aware(datetime.combine(event_date, time(16, 10)))
        
        event, _ = AttendanceEvent.objects.get_or_create(
            course=course,
            event_date=event_date,
            defaults={
                'scan_start_time': start_datetime,
                'scan_end_time': end_datetime
            }
        )
        
        # 创建考勤记录
        for i, student in enumerate(selected_students):
            enrollment = Enrollment.objects.get(student=student, course=course)
            
            # 清除旧记录
            Attendance.objects.filter(enrollment=enrollment, event=event).delete()
            
            # 设置考勤状态 - 为了统计报表展示效果，创建不同的出勤模式
            if event_date == date(2025, 6, 12):  # 6月12日 - 高出勤率：4人出勤，1人缺勤
                if i < 4:  # 前4个学生出勤
                    status = STATUS_PRESENT
                    scan_time = timezone.make_aware(datetime.combine(event_date, time(13, 20 + i)))
                else:  # 1个学生缺勤
                    status = STATUS_ABSENT
                    scan_time = None
            elif event_date == date(2025, 6, 19):  # 6月19日 - 中等出勤率：3人出勤，1人缺勤，1人请假
                if i < 3:  # 前3个学生出勤
                    status = STATUS_PRESENT
                    scan_time = timezone.make_aware(datetime.combine(event_date, time(13, 21 + i)))
                elif i == 3:  # 1个学生缺勤
                    status = STATUS_ABSENT
                    scan_time = None
                else:  # 1个学生请假
                    status = STATUS_LEAVE
                    scan_time = None
            else:  # 6月26日 - 未开始
                status = STATUS_NOT_STARTED
                scan_time = None
            
            Attendance.objects.create(
                enrollment=enrollment,
                event=event,
                status=status,
                scan_time=scan_time
            )
        
        print(f"✓ 考勤事件: {course.course_name} {event_date} - {description}")


def clear_leave_requests():
    """清空请假申请（用于演示）"""
    LeaveRequest.objects.all().delete()
    print("\n✓ 清空请假申请 - 准备演示环境")


def reset_database():
    """重置数据库 - 清理所有测试数据"""
    print("正在重置数据库...")
    
    # 按照外键依赖顺序删除数据
    Attendance.objects.all().delete()
    LeaveRequest.objects.all().delete()
    AttendanceEvent.objects.all().delete()
    ClassSchedule.objects.all().delete()
    TeachingAssignment.objects.all().delete()
    Enrollment.objects.all().delete()
    Student.objects.all().delete()
    Teacher.objects.all().delete()
    Course.objects.all().delete()
    Major.objects.all().delete()
    Department.objects.all().delete()
    
    # 删除用户账号（保留超级用户）
    User.objects.filter(is_superuser=False).delete()
    
    print("✓ 数据库重置完成")


def create_test_data():
    """主函数：创建完整的测试数据"""
    print("=" * 50)
    print("微信扫码考勤系统 - 测试数据初始化")
    print("=" * 50)
    
    try:
        # 0. 重置数据库
        reset_database()
        # 1. 创建基础数据
        dept_bigdata, dept_math, major_bigdata, major_math, course_database, course_optimization = create_basic_data()
        
        # 2. 创建用户和角色
        teacher, students = create_users_and_roles(dept_bigdata, major_bigdata)
        
        # 3. 创建教学安排
        create_teaching_assignments(course_database, teacher)
        create_teaching_assignments_optimization(course_optimization, teacher)
        
        # 4. 创建课程数据
        create_course_data(course_database, students)
        create_course_data_optimization(course_optimization, students)
        
        # 5. 清空请假申请
        clear_leave_requests()
        
        print("\n" + "=" * 50)
        print("✅ 测试数据初始化完成!")
        print("\n📝 登录账号（密码统一为1）:")
        print("  👤 管理员: admin")
        print("  👨‍🏫 教师: 12345 (郑老师)")
        print("  👨‍🎓 学生: 23307130001 (开心)")
        print("\n📊 演示场景:")
        print("  👥 数据库中有15个选课记录（开心仅选修数据库课程）")
        print("  📚 数据库及实现课程 (HGX508) - 10个学生:")
        print("    • 6月11日：8人出勤，2人缺勤（开心出勤）")
        print("    • 6月18日：4人出勤，4人缺勤，2人请假（开心缺勤，等待扫码）")
        print("    • 6月25日：未开始（可申请请假）")
        print("  📐 最优化方法课程 (H3209) - 5个学生（不含开心）:")
        print("    • 6月12日：4人出勤，1人缺勤（出勤率80%）")
        print("    • 6月19日：3人出勤，1人缺勤，1人请假（出勤率60%）")
        print("    • 6月26日：未开始（可申请请假）")
        print("  🕐 当前模拟时间：6月18日10:00（课程进行中）")
        print("  📝 待审批请假：空（可演示申请请假）")
        print("\n🎯 统计报表展示:")
        print("  • 可查看两门课程的出勤统计对比")
        print("  • 数据库课程：总考勤人次20，总考勤次数2，出勤率60%")
        print("  • 最优化方法：总考勤人次10，总考勤次数2，出勤率70%")
        print("  • 点击深蓝色'查看单次考勤'按钮查看每次课的详细统计")
        print("  • 每次课的出勤情况都有独立的甜甜圈图表")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        raise


if __name__ == '__main__':
    create_test_data() 