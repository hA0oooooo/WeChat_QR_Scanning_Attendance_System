#!/usr/bin/env python
"""
测试工具模块
包含各种测试和验证功能，用于系统开发和调试
"""

import os
import sys
import django
import json
from datetime import datetime, date

# 设置Django环境
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from attendance.models import (
    Course, Teacher, TeachingAssignment, ClassSchedule, AttendanceEvent, 
    Attendance, Student, Enrollment, STATUS_PRESENT, STATUS_ABSENT
)


def test_time_conversion():
    """测试时间换算功能"""
    print("=== 测试时间换算功能 ===")
    
    # 获取课程和教师
    course = Course.objects.filter(course_id='DATA130026.01').first()
    teacher = Teacher.objects.filter(teacher_id='12345').first()
    
    if not course or not teacher:
        print("❌ 未找到测试用的课程或教师")
        return
        
    print(f"课程: {course.course_name}")
    print(f"教师: {teacher.teacher_name}")
    
    # 测试不同的节次组合
    test_periods = [
        (1, 2),   # 第1-2节
        (3, 5),   # 第3-5节（数据库及实现）
        (6, 8),   # 第6-8节
        (9, 10),  # 第9-10节
        (11, 12), # 第11-12节
    ]
    
    for start_period, end_period in test_periods:
        print(f"\n--- 测试第{start_period}-{end_period}节 ---")
        
        # 创建临时课程时间安排进行测试
        assignment, created = TeachingAssignment.objects.get_or_create(
            course=course,
            teacher=teacher,
            defaults={'semester': '2024-2025-2'}
        )
        
        schedule = ClassSchedule.objects.create(
            assignment=assignment,
            class_date=date(2025, 6, 20),  # 测试日期
            weekday=5,  # 星期五
            start_period=start_period,
            end_period=end_period,
            location='测试教室'
        )
        
        # 获取换算后的时间
        start_time = schedule.get_start_time()
        end_time = schedule.get_end_time()
        start_datetime = schedule.get_start_datetime()
        end_datetime = schedule.get_end_datetime()
        
        print(f"开始时间: {start_time}")
        print(f"结束时间: {end_time}")
        print(f"完整开始时间: {start_datetime}")
        print(f"完整结束时间: {end_datetime}")
        
        # 清理测试数据
        schedule.delete()


def test_api_request():
    """测试API请求功能"""
    print("=== 测试API请求功能 ===")
    
    # 创建测试客户端
    client = Client()
    
    # 获取管理员用户
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ 没有找到管理员用户")
        return
    
    # 登录
    client.force_login(admin_user)
    print(f"已登录用户: {admin_user.username}")
    
    # 获取测试数据
    course = Course.objects.first()
    teacher = Teacher.objects.first()
    
    if not course or not teacher:
        print("❌ 没有找到课程或教师数据")
        return
    
    print(f"使用课程: {course.course_name}")
    print(f"使用教师: {teacher.teacher_name}")
    
    # 准备请求数据
    data = {
        'course_id': course.course_id,
        'teacher_id': teacher.teacher_id,
        'class_date': '2025-06-26',
        'weekday': '4',  # 星期四
        'start_period': 4,
        'end_period': 6,
        'location': '测试教室'
    }
    
    print(f"请求数据: {data}")
    
    # 发送POST请求
    response = client.post('/api/add-class-schedule/', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.content.decode()}")
    
    # 检查数据库
    print(f"\n数据库检查:")
    print(f"课程时间安排总数: {ClassSchedule.objects.count()}")
    print(f"考勤事件总数: {AttendanceEvent.objects.count()}")


def check_attendance_status():
    """检查考勤状态"""
    print("=== 检查考勤状态 ===")
    
    # 查找学生"开心"
    target_date = date(2025, 6, 18)
    student = Student.objects.filter(stu_name='开心').first()
    
    if not student:
        print("❌ 未找到学生开心")
        return
        
    print(f"正在查看 {target_date} 的考勤记录...")
    
    # 查找6月18日的考勤事件
    events = AttendanceEvent.objects.filter(event_date=target_date)
    if not events.exists():
        print(f"❌ 未找到 {target_date} 的考勤事件")
        return
    
    print(f"找到 {events.count()} 个考勤事件")
    print(f"\n📋 {student.stu_name} ({student.stu_id}) 的考勤记录:")
    print("-" * 40)
    
    for event in events:
        try:
            attendance = Attendance.objects.get(
                enrollment__student=student,
                event=event
            )
            
            # 获取状态描述
            status_map = {
                STATUS_PRESENT: '出勤',
                STATUS_ABSENT: '缺勤'
            }
            status_desc = status_map.get(attendance.status, f'未知状态({attendance.status})')
            
            print(f"课程: {event.course.course_name}")
            print(f"状态: {status_desc}")
            print(f"扫码时间: {attendance.scan_time or '无'}")
            print(f"备注: {attendance.notes or '无'}")
            
        except Attendance.DoesNotExist:
            print(f"课程: {event.course.course_name}")
            print(f"状态: 无考勤记录")
        except Exception as e:
            print(f"❌ 查询考勤记录时出错: {e}")
        
        print("-" * 40)


def verify_system_data():
    """验证系统数据完整性"""
    print("=== 验证系统数据完整性 ===")
    
    # 检查基础数据
    from attendance.models import Department, Major
    
    dept_count = Department.objects.count()
    major_count = Major.objects.count()
    course_count = Course.objects.count()
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    
    print(f"部门数量: {dept_count}")
    print(f"专业数量: {major_count}")
    print(f"课程数量: {course_count}")
    print(f"教师数量: {teacher_count}")
    print(f"学生数量: {student_count}")
    
    # 检查考勤数据
    schedule_count = ClassSchedule.objects.count()
    event_count = AttendanceEvent.objects.count()
    attendance_count = Attendance.objects.count()
    enrollment_count = Enrollment.objects.count()
    
    print(f"课程安排数量: {schedule_count}")
    print(f"考勤事件数量: {event_count}")
    print(f"考勤记录数量: {attendance_count}")
    print(f"选课记录数量: {enrollment_count}")
    
    # 检查用户账号
    user_count = User.objects.count()
    admin_count = User.objects.filter(is_staff=True).count()
    student_with_account = Student.objects.filter(user__isnull=False).count()
    teacher_with_account = Teacher.objects.filter(user__isnull=False).count()
    
    print(f"用户账号总数: {user_count}")
    print(f"管理员账号数: {admin_count}")
    print(f"有账号的学生数: {student_with_account}")
    print(f"有账号的教师数: {teacher_with_account}")


def cleanup_test_data():
    """清理测试数据"""
    print("=== 清理测试数据 ===")
    
    # 查找最优化方法课程
    course = Course.objects.filter(course_name='最优化方法').first()
    if not course:
        print("❌ 没有找到最优化方法课程")
        return
    
    print(f"课程: {course.course_name} ({course.course_id})")
    
    # 查找需要清理的测试数据（测试教室）
    test_schedules = ClassSchedule.objects.filter(
        assignment__course=course,
        location='测试教室'
    )
    
    print(f"找到 {test_schedules.count()} 个测试课程时间安排")
    
    if test_schedules.exists():
        for schedule in test_schedules:
            print(f"  删除: ID:{schedule.schedule_id}, 日期:{schedule.class_date}, "
                  f"节次:{schedule.start_period}-{schedule.end_period}, 地点:{schedule.location}")
            
            # 查找对应的考勤事件并删除
            events = AttendanceEvent.objects.filter(
                course=course,
                event_date=schedule.class_date
            )
            
            for event in events:
                # 检查时间是否匹配
                schedule_start_time = schedule.get_start_datetime().time()
                schedule_end_time = schedule.get_end_datetime().time()
                event_start_time = event.scan_start_time.time()
                event_end_time = event.scan_end_time.time()
                
                # 时间差在30分钟内认为是匹配的
                from datetime import datetime, date as date_module
                base_date = date_module(2000, 1, 1)
                start_diff = abs((datetime.combine(base_date, event_start_time) - 
                                datetime.combine(base_date, schedule_start_time)).total_seconds() / 60)
                end_diff = abs((datetime.combine(base_date, event_end_time) - 
                              datetime.combine(base_date, schedule_end_time)).total_seconds() / 60)
                
                if start_diff <= 30 and end_diff <= 30:
                    print(f"    删除对应考勤事件: ID:{event.event_id}")
                    event.delete()
            
            # 删除课程时间安排
            schedule.delete()
        
        print("清理完成！")
    else:
        print("没有找到需要清理的测试数据")


if __name__ == '__main__':
    print("测试工具模块")
    print("可用的测试函数:")
    print("- test_time_conversion(): 测试时间换算功能")
    print("- test_api_request(): 测试API请求功能")
    print("- check_attendance_status(): 检查考勤状态")
    print("- verify_system_data(): 验证系统数据完整性")
    print("- cleanup_test_data(): 清理测试数据") 