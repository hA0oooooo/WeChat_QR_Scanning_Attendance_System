from django.test import TestCase
from django.utils import timezone
from ..models import Department, Major, Teacher, Course, Student, Enrollment, AttendanceEvent
from attendance.services.wechat_service import WeChatService
import time
from unittest.mock import patch, MagicMock
import hashlib

class TestWeChatService(TestCase):
    def setUp(self):
        """设置测试数据"""
        # 创建测试数据
        self.department = Department.objects.create(name='计算机系')
        self.major = Major.objects.create(name='软件工程', department=self.department)
        self.teacher = Teacher.objects.create(
            teacher_id='T001',
            name='张老师',
            department=self.department
        )
        self.course = Course.objects.create(
            course_id='C001',
            name='Python编程',
            teacher=self.teacher,
            major=self.major
        )
        self.student = Student.objects.create(
            student_id='S001',
            name='李同学',
            major=self.major
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.event = AttendanceEvent.objects.create(
            course=self.course,
            qr_code='test_qr_code',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )
        self.wechat_service = WeChatService()

    def test_verify_signature(self):
        """测试微信签名验证"""
        token = self.wechat_service.token
        timestamp = '1234567890'
        nonce = 'testnonce'
        temp_list = [token, timestamp, nonce]
        temp_list.sort()
        temp_str = ''.join(temp_list)
        signature = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
        self.assertTrue(self.wechat_service.verify_signature(signature, timestamp, nonce))
        self.assertFalse(self.wechat_service.verify_signature('wrongsignature', timestamp, nonce))

    def test_handle_scan_qr_success(self):
        """测试成功扫码考勤"""
        result = self.wechat_service.handle_scan_qr(
            self.event.qr_code,
            self.student.student_id,
            'test_openid'
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], '签到成功')

    def test_handle_scan_qr_invalid_event(self):
        """测试无效的考勤码"""
        result = self.wechat_service.handle_scan_qr(
            'invalid_qr_code',
            self.student.student_id,
            'test_openid'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '无效的考勤码')

    def test_handle_scan_qr_duplicate(self):
        """测试重复签到"""
        # 第一次签到
        self.wechat_service.handle_scan_qr(
            self.event.qr_code,
            self.student.student_id,
            'test_openid'
        )
        # 第二次签到
        result = self.wechat_service.handle_scan_qr(
            self.event.qr_code,
            self.student.student_id,
            'test_openid'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '您已经签到过了')

    def test_handle_scan_qr_out_of_time(self):
        """测试超出签到时间范围"""
        # 创建已结束的考勤事件
        expired_event = AttendanceEvent.objects.create(
            course=self.course,
            qr_code='expired_qr_code',
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            is_active=True
        )
        result = self.wechat_service.handle_scan_qr(
            expired_event.qr_code,
            self.student.student_id,
            'test_openid'
        )
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '不在签到时间范围内')

    @patch('requests.get')
    def test_get_access_token_success(self, mock_get):
        """测试成功获取access_token"""
        # 模拟微信API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 7200
        }
        mock_get.return_value = mock_response

        # 测试获取access_token
        access_token = self.wechat_service.get_access_token()
        self.assertEqual(access_token, 'test_access_token')

    @patch('requests.get')
    def test_get_access_token_failure(self, mock_get):
        """测试获取access_token失败的情况"""
        # 模拟微信API错误响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'errcode': 40001,
            'errmsg': 'invalid credential'
        }
        mock_get.return_value = mock_response

        # 测试异常情况
        with self.assertRaises(Exception) as context:
            self.wechat_service.get_access_token()
        self.assertIn('获取access_token失败', str(context.exception))

    def test_handle_scan_qr_event_not_exist(self):
        result = self.wechat_service.handle_scan_qr('not_exist_qr', self.student.student_id, 'openid')
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '无效的考勤码')

    def test_handle_scan_qr_student_not_exist(self):
        result = self.wechat_service.handle_scan_qr(self.event.qr_code, 'not_exist_id', 'openid')
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '学生信息不存在')

    def test_handle_scan_qr_not_enrolled(self):
        # 删除选修关系
        Enrollment.objects.filter(course=self.course, student=self.student).delete()
        result = self.wechat_service.handle_scan_qr(self.event.qr_code, self.student.student_id, 'openid')
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], '您未选修该课程')

    def test_handle_scan_qr_success(self):
        result = self.wechat_service.handle_scan_qr(self.event.qr_code, self.student.student_id, 'openid')
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], '校验通过')

    @patch('attendance.services.wechat_service.requests.post')
    def test_send_template_message(self, mock_post):
        """测试模板消息推送接口参数和调用"""
        mock_post.return_value.json.return_value = {'errcode': 0, 'errmsg': 'ok'}
        openid = 'test_openid'
        data = {
            'first': {'value': '签到成功！'},
            'keyword1': {'value': '测试课程'},
            'keyword2': {'value': '2024-01-01'},
            'keyword3': {'value': '2024-01-01 08:00:00'},
            'remark': {'value': '如有疑问请联系老师'}
        }
        result = self.wechat_service.send_template_message(openid, data)
        self.assertEqual(result['errcode'], 0)
        self.assertEqual(result['errmsg'], 'ok')
        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        self.assertIn('access_token', called_args[0])
        self.assertEqual(called_kwargs['json']['touser'], openid)
        self.assertEqual(called_kwargs['json']['data'], data) 