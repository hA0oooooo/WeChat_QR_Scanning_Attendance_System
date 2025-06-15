from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    Course, Teacher, Student, Department, Major, TeachingAssignment,
    Enrollment, AttendanceEvent, Attendance, LeaveRequest,
    EVENT_VALID, EVENT_INVALID, STATUS_PRESENT, STATUS_ABSENT, STATUS_LEAVE,
    LEAVE_APPROVED, LEAVE_PENDING
)
from django.utils import timezone
from datetime import date, time, timedelta, datetime

class AttendanceSystemTest(TestCase):
    def setUp(self):
        self.client = Client()
        # 创建院系、专业、课程
        self.dept = Department.objects.create(dept_name="计算机科学与技术学院")
        self.major = Major.objects.create(major_name="软件工程", dept=self.dept)
        self.course = Course.objects.create(course_id="CS101", course_name="软件工程导论", dept=self.dept)
        # 创建教师和学生的User账号
        self.teacher_user = User.objects.create_user(username="teacher1", password="testpass")
        self.student_user = User.objects.create_user(username="student1", password="testpass")
        # 创建教师和学生
        self.teacher = Teacher.objects.create(teacher_id="T001", teacher_name="张老师", dept=self.dept)
        self.student = Student.objects.create(stu_id="20230001", stu_name="小明", stu_sex=1, major=self.major, openid="openid123")
        # 选课
        self.enroll = Enrollment.objects.create(student=self.student, course=self.course, semester="202301")
        # 设置考勤时间为全天覆盖
        self.event = AttendanceEvent.objects.create(
            course=self.course,
            event_date=date.today(),
            scan_start_time=time(0, 0),  # 全天开始
            scan_end_time=time(23, 59),  # 全天结束
            event_status=1
        )

    def test_scan_qr_code(self):
        """测试扫码签到"""
        self.client.force_login(self.student_user)
        # 模拟扫码签到请求
        response = self.client.post('/api/scan-qr/', {
            'qr_code': str(self.event.event_id),
            'student_openid': self.student.openid
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], '签到成功')

    def test_duplicate_scan(self):
        """测试重复扫码"""
        self.client.force_login(self.student_user)
        # 第一次扫码
        self.client.post('/api/scan-qr/', {
            'qr_code': str(self.event.event_id),
            'student_openid': self.student.openid
        })
        # 第二次扫码
        response = self.client.post('/api/scan-qr/', {
            'qr_code': str(self.event.event_id),
            'student_openid': self.student.openid
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], '已经签到过了')

    def test_out_of_time(self):
        """测试超出考勤时间扫码"""
        self.client.force_login(self.student_user)
        # 修改考勤事件为已过期
        self.event.scan_start_time = time(6, 0)
        self.event.scan_end_time = time(7, 0)
        self.event.save()
        response = self.client.post('/api/scan-qr/', {
            'qr_code': str(self.event.event_id),
            'student_openid': self.student.openid
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], '不在考勤时间范围内')

class TeacherViewsTest(TestCase):
    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        self.teacher_user = User.objects.create_user(username='test_teacher', password='test123')
        self.department = Department.objects.create(dept_name='计算机学院')
        self.teacher = Teacher.objects.create(teacher_id='test_teacher', teacher_name='测试教师', dept=self.department)
        self.course = Course.objects.create(course_id='CS101', course_name='测试课程', credit=3, dept=self.department)
        self.teaching_assignment = TeachingAssignment.objects.create(teacher=self.teacher, course=self.course)
        self.attendance_event = AttendanceEvent.objects.create(
            event_id=1,
            course=self.course,
            event_date=date.today(),
            scan_start_time=time(8, 0),
            scan_end_time=time(9, 0),
            event_status=EVENT_VALID
        )
        self.leave_request = LeaveRequest.objects.create(
            leave_request_id=1,
            enrollment=Enrollment.objects.create(
                student=Student.objects.create(
                    stu_id='test_student',
                    stu_name='测试学生',
                    stu_sex=1,
                    openid='test_openid'
                ),
                course=self.course
            ),
            event=self.attendance_event,
            reason='测试请假',
            approval_status=LEAVE_PENDING
        )
    
    def test_teacher_dashboard(self):
        """测试教师仪表盘"""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/teacher/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_teacher_courses(self):
        """测试教师课程列表"""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/teacher/courses/')
        self.assertEqual(response.status_code, 200)
    
    def test_course_detail(self):
        """测试课程详情"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(f'/teacher/course/{self.course.course_id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_manage_attendance_events(self):
        """测试管理考勤事件"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(f'/teacher/course/{self.course.course_id}/attendance/')
        self.assertEqual(response.status_code, 200)
    
    def test_toggle_event_status(self):
        """测试切换考勤事件状态"""
        self.client.force_login(self.teacher_user)
        response = self.client.post(f'/teacher/event/{self.attendance_event.event_id}/toggle/')
        self.assertEqual(response.status_code, 302)
    
    def test_create_attendance_event(self):
        """测试创建考勤事件"""
        self.client.force_login(self.teacher_user)
        response = self.client.post(f'/teacher/course/{self.course.course_id}/attendance/create/', {
            'event_date': date.today(),
            'scan_start_time': '08:00',
            'scan_end_time': '09:00'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_view_attendance_results(self):
        """测试查看考勤结果"""
        self.client.force_login(self.teacher_user)
        response = self.client.get(f'/teacher/event/{self.attendance_event.event_id}/results/')
        self.assertEqual(response.status_code, 200)
    
    def test_leave_request_list(self):
        """测试请假申请列表"""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/teacher/leave/')
        self.assertEqual(response.status_code, 200)
    
    def test_approve_leave_request(self):
        """测试审批请假申请"""
        self.client.force_login(self.teacher_user)
        response = self.client.post(f'/teacher/leave/{self.leave_request.leave_request_id}/approve/', {
            'status': 2,
            'comment': '同意'
        })
        self.assertEqual(response.status_code, 302)
        self.leave_request.refresh_from_db()
        self.assertEqual(self.leave_request.approval_status, LEAVE_APPROVED)
    
    def test_teacher_profile(self):
        """测试教师个人信息"""
        self.client.force_login(self.teacher_user)
        response = self.client.get('/teacher/profile/')
        self.assertEqual(response.status_code, 200)

class StudentViewsTest(TestCase):
    def setUp(self):
        """设置测试环境"""
        self.client = Client()
        # 创建学生用户
        self.student_user = User.objects.create_user(
            username='test_student',
            password='test123'
        )
        # 创建院系
        self.department = Department.objects.create(
            dept_name='计算机学院'
        )
        # 创建专业
        self.major = Major.objects.create(
            major_name='计算机科学',
            dept=self.department
        )
        # 创建学生
        self.student = Student.objects.create(
            stu_id='2024001',
            stu_name='测试学生',
            stu_sex=1,
            major=self.major,
            openid='test_student'
        )
        # 创建课程
        self.course = Course.objects.create(
            course_id='CS001',
            course_name='测试课程',
            dept=self.department
        )
        # 创建选课记录
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            semester='2024-1'
        )
        # 创建考勤事件
        self.event = AttendanceEvent.objects.create(
            course=self.course,
            event_date=date.today(),
            scan_start_time=time(8, 0),
            scan_end_time=time(9, 0)
        )

    def test_submit_leave_request(self):
        """测试提交请假申请"""
        self.client.force_login(self.student_user)
        response = self.client.post('/student/leave/submit/', {
            'event_id': self.event.event_id,
            'reason': '生病请假'
        })
        self.assertEqual(response.status_code, 302)  # 成功后重定向
        self.assertTrue(LeaveRequest.objects.filter(
            enrollment=self.enrollment,
            event=self.event,
            approval_status=LEAVE_PENDING
        ).exists())
