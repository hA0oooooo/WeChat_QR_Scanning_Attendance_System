#!/usr/bin/env python
"""
测试数据初始化模块
用于初始化完整的测试数据，包括用户账号、教师、学生、课程、选课等信息
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
import random

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import (
    Department, Major, Course, Teacher, Student, 
    TeachingAssignment, Enrollment, AttendanceEvent, 
    Attendance, LeaveRequest, ClassSchedule, EVENT_VALID, STATUS_PRESENT
)
from django.utils import timezone


class TestDataInitializer:
    """测试数据初始化器"""
    
    def __init__(self):
        self.dept = None
        self.major = None
        self.admin_user = None
        self.teacher_user = None
        self.student_user = None
        self.teacher = None
        self.students = []
        self.course = None
        self.enrollments = []
        self.events = []
    
    def clear_all_data(self):
        """清除所有测试数据"""
        print("正在清除现有测试数据...")
        
        # 按依赖关系顺序删除所有数据
        print("  - 清除请假申请...")
        LeaveRequest.objects.all().delete()
        
        print("  - 清除考勤记录...")
        Attendance.objects.all().delete()
        
        print("  - 清除考勤事件...")
        AttendanceEvent.objects.all().delete()
        
        print("  - 清除课程时间安排...")
        ClassSchedule.objects.all().delete()
        
        print("  - 清除选课记录...")
        Enrollment.objects.all().delete()
        
        print("  - 清除教学安排...")
        TeachingAssignment.objects.all().delete()
        
        print("  - 清除教师信息...")
        Teacher.objects.all().delete()
        
        print("  - 清除学生信息...")
        Student.objects.all().delete()
        
        print("  - 清除课程信息...")
        Course.objects.all().delete()
        
        print("  - 清除专业信息...")
        Major.objects.all().delete()
        
        print("  - 清除院系信息...")
        Department.objects.all().delete()
        
        print("  - 清除所有用户...")
        User.objects.all().delete()
        
        print("  - 清除系统设置和日志...")
        try:
            from attendance.models import SystemSettings, PermissionSettings, SystemLog
            SystemLog.objects.all().delete()
            SystemSettings.objects.all().delete()
            PermissionSettings.objects.all().delete()
        except ImportError:
            pass
        except Exception as e:
            print(f"    清除系统设置时出现警告: {e}")
        
        print("测试数据清除完成")
    
    def create_departments_and_majors(self):
        """创建院系和专业"""
        print("创建院系和专业...")
        
        self.dept, created = Department.objects.get_or_create(
            dept_name='大数据学院'
        )
        if created:
            print(f"  - 院系: {self.dept.dept_name}")
        
        self.major, created = Major.objects.get_or_create(
            major_name='数据科学与大数据技术',
            defaults={'dept': self.dept}
        )
        if created:
            print(f"  - 专业: {self.major.major_name}")
    
    def create_users(self):
        """创建测试用户"""
        print("正在创建测试用户...")
        
        # 创建管理员用户
        print("  - 创建管理员用户...")
        self.admin_user = User.objects.create_user(
            username='admin',
            password='1',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        # 创建教师用户
        print("  - 创建教师用户...")
        self.teacher_user = User.objects.create_user(
            username='12345',
            password='1',
            email='teacher@example.com',
            first_name='郑',
            last_name='老师',
            is_active=True
        )
        
        # 创建学生用户
        print("  - 创建学生用户...")
        self.student_user = User.objects.create_user(
            username='23307130001',
            password='1',
            email='student1@example.com',
            first_name='张',
            last_name='三',
            is_active=True
        )
        
        print("测试用户创建完成")
    
    def create_teacher(self):
        """创建教师"""
        print("创建教师...")
        
        self.teacher, created = Teacher.objects.get_or_create(
            teacher_id='12345',
            defaults={
                'user': self.teacher_user,
                'teacher_name': '郑老师',
                'dept': self.dept
            }
        )
        
        if created:
            print(f"  - 教师: {self.teacher.teacher_name} (工号: {self.teacher.teacher_id}) 已创建")
        else:
            self.teacher.user = self.teacher_user
            self.teacher.save()
            print(f"  - 教师: {self.teacher.teacher_name} (工号: {self.teacher.teacher_id}) 已存在，用户关联已更新")
    
    def create_students(self):
        """创建学生"""
        print("创建学生...")
        
        # 显式设计学生信息和扫码时间
        students_data = [
            {'stu_id': '23307130001', 'stu_name': '开心', 'stu_sex': 1, 'user': self.student_user, 'scan_time': None, 'note': '有请假申请'},
            {'stu_id': '23307130002', 'stu_name': '青春', 'stu_sex': 2, 'user': None, 'scan_time': None, 'note': '有请假申请'},
            {'stu_id': '23307130003', 'stu_name': '阳光', 'stu_sex': 1, 'user': None, 'scan_time': time(10, 0), 'note': '正常出勤'},
            {'stu_id': '23307130004', 'stu_name': '梦想', 'stu_sex': 2, 'user': None, 'scan_time': time(9, 55), 'note': '准时出勤'},
            {'stu_id': '23307130005', 'stu_name': '希望', 'stu_sex': 1, 'user': None, 'scan_time': time(11, 30), 'note': '课程中间扫码'},
            {'stu_id': '23307130006', 'stu_name': '未来', 'stu_sex': 2, 'user': None, 'scan_time': time(12, 25), 'note': '快下课时扫码'},
            {'stu_id': '23307130007', 'stu_name': '快乐', 'stu_sex': 1, 'user': None, 'scan_time': time(9, 30), 'note': '早到但无效扫码'},
            {'stu_id': '23307130008', 'stu_name': '自由', 'stu_sex': 2, 'user': None, 'scan_time': time(13, 0), 'note': '迟到无效扫码'},
            {'stu_id': '23307130009', 'stu_name': '勇敢', 'stu_sex': 1, 'user': None, 'scan_time': None, 'note': '未扫码缺勤'},
            {'stu_id': '23307130010', 'stu_name': '智慧', 'stu_sex': 2, 'user': None, 'scan_time': time(10, 45), 'note': '正常出勤'},
        ]
        
        # 保存学生扫码时间信息，供后续使用
        self.students_scan_data = {data['stu_id']: data for data in students_data}
        
        self.students = []
        for data in students_data:
            student = Student.objects.create(
                stu_id=data['stu_id'],
                stu_name=data['stu_name'],
                stu_sex=data['stu_sex'],
                major=self.major,
                user=data['user'],
                openid=f"wx_openid_{data['stu_id']}"
            )
            self.students.append(student)
            print(f"  - 学生: {student.stu_name} (学号: {student.stu_id})")
    
    def create_course_and_schedule(self):
        """创建课程和课程安排"""
        print("创建课程和课程安排...")
        
        self.course, created = Course.objects.get_or_create(
            course_id='DB2024',
            defaults={
                'course_name': '数据库及实现',
                'dept': self.dept,
                'credit': 3
            }
        )
        
        if created:
            print(f"  - 课程: {self.course.course_name} (课程号: {self.course.course_id})")
        
        # 创建教学安排
        teaching_assignment, created = TeachingAssignment.objects.get_or_create(
            teacher=self.teacher,
            course=self.course
        )
        
        if created:
            print(f"  - 教学安排: {self.teacher.teacher_name} 教授 {self.course.course_name}")
        
        # 创建课程时间安排
        schedule, created = ClassSchedule.objects.get_or_create(
            assignment=teaching_assignment,
            weekday=3,  # 星期三
            defaults={
                'start_period': 3,
                'end_period': 5,
                'location': 'HGX508'
            }
        )
        
        if created:
            print(f"  - 课程安排: 星期三 第3-5节 {schedule.location} (9:55-12:30)")
    
    def create_enrollments(self):
        """创建选课记录"""
        print("创建选课记录...")
        
        self.enrollments = []
        for student in self.students:
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=self.course,
                semester='202401'
            )
            self.enrollments.append(enrollment)
            if created:
                print(f"  - {student.stu_name} 选修 {self.course.course_name}")
    
    def create_attendance_events(self):
        """创建考勤事件"""
        print("创建考勤事件...")
        
        # 创建2个考勤事件（1个过去，1个未来）
        # 基于星期三的课程安排创建事件
        base_date = date(2025, 6, 18)  # 2025年6月18日是星期三
        
        event_dates = [
            base_date - timedelta(days=7),   # 一周前的星期三（已完成）
            base_date + timedelta(days=7),   # 下周星期三（未来事件）
        ]
        
        self.events = []
        for i, event_date in enumerate(event_dates):
            event = AttendanceEvent.objects.create(
                course=self.course,
                event_date=event_date,
                scan_start_time=time(9, 55),   # 课程开始时间
                scan_end_time=time(12, 30),    # 课程结束时间
                event_status=EVENT_VALID
            )
            self.events.append(event)
            print(f"  - 考勤事件: {event_date} 9:55-12:30")
    
    def create_attendance_records(self):
        """创建考勤记录"""
        print("创建考勤记录...")
        
        # 为过去的事件创建考勤记录
        today = date(2025, 6, 18)  # 当前日期设为2025年6月18日
        past_events = [event for event in self.events if event.event_date <= today]
        
        for event in past_events:
            for enrollment in self.enrollments:
                student_id = enrollment.student.stu_id
                student_data = self.students_scan_data[student_id]
                
                # 获取显式设计的扫码时间
                designed_scan_time = student_data['scan_time']
                scan_time = None
                status = 2  # 默认缺勤
                
                if designed_scan_time:
                    # 学生有扫码时间
                    scan_time = datetime.combine(event.event_date, designed_scan_time)
                    
                    # 判断扫码时间是否在有效区间内（9:55-12:30）
                    valid_start = time(9, 55)
                    valid_end = time(12, 30)
                    
                    if valid_start <= designed_scan_time <= valid_end:
                        status = STATUS_PRESENT  # 出勤
                    else:
                        status = 2  # 缺勤（扫码时间不在有效区间内）
                else:
                    # 学生没有扫码时间
                    status = 2  # 缺勤
                
                # 检查是否有已批准的请假申请
                leave_request = LeaveRequest.objects.filter(
                    enrollment=enrollment,
                    event=event,
                    approval_status=2  # 已批准
                ).first()
                
                if leave_request:
                    status = 3  # 请假
                    scan_time = None  # 请假的学生没有扫码时间
                
                attendance = Attendance.objects.create(
                    enrollment=enrollment,
                    event=event,
                    scan_time=scan_time,
                    status=status
                )
                
                if status == STATUS_PRESENT:
                    status_text = f"出勤 (扫码时间: {designed_scan_time})"
                elif status == 3:
                    status_text = "请假"
                elif designed_scan_time:
                    status_text = f"缺勤 (扫码时间: {designed_scan_time}, 不在有效区间内)"
                else:
                    status_text = "缺勤 (未扫码)"
                
                print(f"    - {enrollment.student.stu_name}: {event.event_date} - {status_text}")
    
    def create_leave_requests(self):
        """创建请假申请"""
        print("创建请假申请...")
        
        # 为过去和未来的事件都创建一些请假申请
        for event in self.events:
            # 让前2个学生提交请假申请
            for i in range(2):
                enrollment = self.enrollments[i]
                
                # 根据事件日期设置不同的审批状态
                if event.event_date <= date(2025, 6, 18):  # 过去的事件
                    approval_status = 2  # 已批准
                else:  # 未来的事件
                    approval_status = 1  # 待审批
                
                leave_request = LeaveRequest.objects.create(
                    enrollment=enrollment,
                    event=event,
                    reason=f"因个人事务需要请假，无法参加{event.event_date}的《数据库及实现》课程（星期三9:55-12:30）",
                    approval_status=approval_status
                )
                
                status_text = "已批准" if approval_status == 2 else "待审批"
                print(f"    - {enrollment.student.stu_name} 申请 {event.event_date} 请假 ({status_text})")
    
    def initialize_all_data(self):
        """初始化所有测试数据"""
        print("=== 开始初始化测试数据 ===")
        
        self.clear_all_data()
        self.create_departments_and_majors()
        self.create_users()
        self.create_teacher()
        self.create_students()
        self.create_course_and_schedule()
        self.create_enrollments()
        self.create_attendance_events()
        self.create_leave_requests()  # 先创建请假申请
        self.create_attendance_records()  # 再创建考勤记录
        
        print("\n=== 测试数据初始化完成 ===")
        print("\n可用的登录账号:")
        print("管理员: admin / 1")
        print("教师: 12345 / 1")
        print("学生: 23307130001 / 1")
        print("\n服务器地址: http://127.0.0.1:8000/")


def main():
    """主函数"""
    initializer = TestDataInitializer()
    initializer.initialize_all_data()


if __name__ == '__main__':
    main() 