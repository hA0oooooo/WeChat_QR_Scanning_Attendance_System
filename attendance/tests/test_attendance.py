from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from attendance.models import User, Teacher, Student, Course, Enrollment, AttendanceEvent, Attendance
from attendance.utils import generate_qr_code

class AttendanceTestCase(TestCase):
    def setUp(self):
        # 创建测试用户
        self.teacher = User.objects.create_user(
            username='test_teacher',
            password='test123',
            email='teacher@test.com'
        )
        self.student = User.objects.create_user(
            username='test_student',
            password='test123',
            email='student@test.com'
        )
        
        # 创建教师和学生信息
        self.teacher_info = Teacher.objects.create(
            teacher_id='T001',
            teacher_name='测试教师',
            user=self.teacher
        )
        self.student_info = Student.objects.create(
            stu_id='2023001',
            stu_name='测试学生',
            user=self.student
        )
        
        # 创建课程
        self.course = Course.objects.create(
            course_id='C001',
            course_name='测试课程',
            teacher=self.teacher_info
        )
        
        # 创建选课记录
        self.enrollment = Enrollment.objects.create(
            course=self.course,
            student=self.student_info
        )
        
        # 创建考勤事件
        self.event = AttendanceEvent.objects.create(
            event_id='E001',
            course=self.course,
            event_name='测试考勤',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

    def test_scan_qr_code(self):
        """测试扫描二维码签到"""
        # 生成二维码
        qr_code = generate_qr_code(self.event.event_id)
        
        # 模拟扫描请求
        url = reverse('scan_qr_code')
        data = {
            'qr_code': qr_code,
            'stu_id': self.student_info.stu_id
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        
        # 验证考勤记录
        attendance = Attendance.objects.get(
            event=self.event,
            enrollment=self.enrollment
        )
        self.assertEqual(attendance.status, STATUS_PRESENT)

    def test_leave_request(self):
        """测试请假申请"""
        # 创建请假申请
        url = reverse('leave_request')
        data = {
            'event_id': self.event.event_id,
            'stu_id': self.student_info.stu_id,
            'reason': '生病请假'
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 0)
        
        # 验证考勤记录
        attendance = Attendance.objects.get(
            event=self.event,
            enrollment=self.enrollment
        )
        self.assertEqual(attendance.status, STATUS_LEAVE)
        self.assertEqual(attendance.leave_reason, '生病请假')

    def test_duplicate_attendance(self):
        """测试重复签到"""
        # 先生成一条考勤记录
        Attendance.objects.create(
            event=self.event,
            enrollment=self.enrollment,
            status=STATUS_PRESENT
        )
        
        # 再次扫描二维码
        qr_code = generate_qr_code(self.event.event_id)
        url = reverse('scan_qr_code')
        data = {
            'qr_code': qr_code,
            'stu_id': self.student_info.stu_id
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 1)  # 应该返回错误码
        
        # 验证考勤记录数量
        self.assertEqual(Attendance.objects.count(), 1)

    def test_leave_after_attendance(self):
        """测试已签到后申请请假"""
        # 先生成一条出勤记录
        Attendance.objects.create(
            event=self.event,
            enrollment=self.enrollment,
            status=STATUS_PRESENT
        )
        
        # 尝试申请请假
        url = reverse('leave_request')
        data = {
            'event_id': self.event.event_id,
            'stu_id': self.student_info.stu_id,
            'reason': '生病请假'
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 1)  # 应该返回错误码
        
        # 验证考勤记录状态未改变
        attendance = Attendance.objects.get(
            event=self.event,
            enrollment=self.enrollment
        )
        self.assertEqual(attendance.status, STATUS_PRESENT)

    def test_attendance_after_leave(self):
        """测试请假后尝试签到"""
        # 先生成一条请假记录
        Attendance.objects.create(
            event=self.event,
            enrollment=self.enrollment,
            status=STATUS_LEAVE,
            leave_reason='生病请假'
        )
        
        # 尝试扫描二维码签到
        qr_code = generate_qr_code(self.event.event_id)
        url = reverse('scan_qr_code')
        data = {
            'qr_code': qr_code,
            'stu_id': self.student_info.stu_id
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 1)  # 应该返回错误码
        
        # 验证考勤记录状态未改变
        attendance = Attendance.objects.get(
            event=self.event,
            enrollment=self.enrollment
        )
        self.assertEqual(attendance.status, STATUS_LEAVE)

    def test_invalid_qr_code(self):
        """测试无效的二维码"""
        url = reverse('scan_qr_code')
        data = {
            'qr_code': 'invalid_qr_code',
            'stu_id': self.student_info.stu_id
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 1)  # 应该返回错误码
        
        # 验证没有创建考勤记录
        self.assertEqual(Attendance.objects.count(), 0)

    def test_expired_event(self):
        """测试过期事件的签到"""
        # 创建一个已过期的事件
        expired_event = AttendanceEvent.objects.create(
            event_id='E002',
            course=self.course,
            event_name='过期考勤',
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1)
        )
        
        # 尝试扫描二维码
        qr_code = generate_qr_code(expired_event.event_id)
        url = reverse('scan_qr_code')
        data = {
            'qr_code': qr_code,
            'stu_id': self.student_info.stu_id
        }
        response = self.client.post(url, data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['code'], 1)  # 应该返回错误码
        
        # 验证没有创建考勤记录
        self.assertEqual(Attendance.objects.count(), 0) 