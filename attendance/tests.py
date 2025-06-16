from django.test import TestCase, Client
from django.utils import timezone
from .models import Student, Course, Teacher, AttendanceEvent, Enrollment, Attendance, Major, Department

class ScanQrPageTest(TestCase):
    def setUp(self):
        # 创建院系和专业
        self.dept = Department.objects.create(dept_name='数学学院')
        self.major = Major.objects.create(major_name='数学与应用数学', dept=self.dept)
        # 创建教师、课程、学生、考勤事件、选课关系
        self.teacher = Teacher.objects.create(teacher_name='张老师', teacher_id='T001', dept=self.dept)
        self.course = Course.objects.create(course_id='C001', course_name='高等数学', dept=self.dept)
        self.student = Student.objects.create(stu_name='小明', stu_id='S001', stu_sex=1, major=self.major, openid='openid123')
        self.event = AttendanceEvent.objects.create(
            course=self.course,
            event_date=timezone.now().date(),
            scan_start_time=timezone.now() - timezone.timedelta(minutes=10),
            scan_end_time=timezone.now() + timezone.timedelta(minutes=10),
            status=1
        )
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course, semester='202401')
        self.client = Client()

    def test_attendance_success(self):
        url = f'/scan-qr-page/?event_id={self.event.event_id}&openid={self.student.openid}'
        response = self.client.get(url)
        self.assertContains(response, '签到成功')
        self.assertContains(response, self.course.course_id)
        self.assertContains(response, self.course.course_name)
        self.assertContains(response, self.student.stu_name)
        self.assertContains(response, self.student.stu_id)

    def test_attendance_repeat(self):
        # 先签到一次
        Attendance.objects.create(enrollment=self.enrollment, event=self.event, scan_time=timezone.now(), status=1)
        url = f'/scan-qr-page/?event_id={self.event.event_id}&openid={self.student.openid}'
        response = self.client.get(url)
        self.assertContains(response, '您已签到，无需重复操作')
        self.assertContains(response, self.course.course_id)
        self.assertContains(response, self.student.stu_name)

    def test_attendance_fail_event_not_exist(self):
        url = f'/scan-qr-page/?event_id=99999&openid={self.student.openid}'
        response = self.client.get(url)
        self.assertContains(response, '考勤事件不存在')

    def test_attendance_fail_student_not_exist(self):
        url = f'/scan-qr-page/?event_id={self.event.event_id}&openid=notexistopenid'
        response = self.client.get(url)
        self.assertContains(response, '未找到学生信息')

    def test_attendance_fail_not_enrolled(self):
        other_student = Student.objects.create(stu_name='小红', stu_id='S002', stu_sex=2, major=self.major, openid='openid456')
        url = f'/scan-qr-page/?event_id={self.event.event_id}&openid={other_student.openid}'
        response = self.client.get(url)
        self.assertContains(response, '未选修该课程')

    def test_attendance_fail_time_invalid(self):
        # 创建一个已过期的考勤事件
        event = AttendanceEvent.objects.create(
            course=self.course,
            event_date=timezone.now().date(),
            scan_start_time=timezone.now() - timezone.timedelta(hours=2),
            scan_end_time=timezone.now() - timezone.timedelta(hours=1),
            status=1
        )
        url = f'/scan-qr-page/?event_id={event.event_id}&openid={self.student.openid}'
        response = self.client.get(url)
        self.assertContains(response, '不在考勤时间范围内') 