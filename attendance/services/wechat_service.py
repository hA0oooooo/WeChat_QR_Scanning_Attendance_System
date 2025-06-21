import requests
import json
import time
import hashlib
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from attendance.models import AttendanceEvent, Student, Attendance, Enrollment

class WeChatService:
    """微信服务类"""
    
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.secret = settings.WECHAT_SECRET
        self.token = getattr(settings, 'WECHAT_TOKEN', '')
        self.encoding_aes_key = settings.WECHAT_ENCODING_AES_KEY
        self.template_id = settings.WECHAT_ATTENDANCE_TEMPLATE_ID
    
    def get_access_token(self):
        """获取微信访问令牌，使用缓存避免频繁请求"""
        cache_key = 'wechat_access_token'
        access_token = cache.get(cache_key)
        
        if not access_token:
            url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.secret}'
            response = requests.get(url)
            result = response.json()
            
            if 'access_token' in result:
                access_token = result['access_token']
                expires_in = result.get('expires_in', 7200)
                cache.set(cache_key, access_token, expires_in - 300)  # 提前5分钟过期
            else:
                raise Exception(f"获取access_token失败: {result}")
        
        return access_token
    
    def verify_signature(self, signature, timestamp, nonce):
        """验证微信请求签名"""
        if not all([signature, timestamp, nonce]):
            return False
            
        temp_list = [self.token, timestamp, nonce]
        temp_list.sort()
        temp_str = ''.join(temp_list)
        hash_obj = hashlib.sha1(temp_str.encode('utf-8'))
        return hash_obj.hexdigest() == signature
    
    def get_user_info(self, openid):
        """获取微信用户信息"""
        access_token = self.get_access_token()
        url = f'https://api.weixin.qq.com/cgi-bin/user/info?access_token={access_token}&openid={openid}&lang=zh_CN'
        response = requests.get(url)
        return response.json()
    
    def send_template_message(self, openid, data):
        """
        发送微信模板消息
        :param openid: 用户openid
        :param data: 模板消息内容（dict）
        :return: 微信API响应
        """
        access_token = self.get_access_token()
        url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        payload = {
            'touser': openid,
            'template_id': settings.WECHAT_ATTENDANCE_TEMPLATE_ID,
            'data': data
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def handle_scan_qr(self, qr_code, student_id, openid):
        """
        处理扫码考勤请求
        基础校验：事件和学生是否存在，以及是否选修该课程，是否已签到，是否在签到时间范围内
        """
        try:
            # 获取考勤事件
            event = AttendanceEvent.objects.get(event_id=qr_code)
            
            # 获取学生信息
            student = Student.objects.get(stu_id=student_id, openid=openid)
            
            # 检查是否选修该课程
            try:
                enrollment = Enrollment.objects.get(student=student, course=event.course)
            except Enrollment.DoesNotExist:
                return {'success': False, 'message': '您未选修该课程', 'status': 'fail'}
            
            # 检查是否在签到时间范围内
            now = timezone.now()
            if now < event.scan_start_time or now > event.scan_end_time:
                return {'success': False, 'message': '不在签到时间范围内', 'status': 'fail'}
            
            # 检查考勤记录
            attendance = Attendance.objects.filter(enrollment=enrollment, event=event).first()
            if attendance:
                return {'success': False, 'message': '您已经签到过了', 'status': 'fail'}
            
            # 创建考勤记录
            attendance = Attendance.objects.create(
                enrollment=enrollment,
                event=event,
                status='present',
                scan_time=now
            )
            
            return {
                'success': True,
                'message': '签到成功',
                'status': 'success',
                'data': {
                    'course_name': event.course.name,
                    'student_name': student.name,
                    'scan_time': now.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except AttendanceEvent.DoesNotExist:
            return {'success': False, 'message': '无效的考勤码', 'status': 'fail'}
        except Student.DoesNotExist:
            return {'success': False, 'message': '学生信息不存在或openid不匹配', 'status': 'fail'}
        except Exception as e:
            return {'success': False, 'message': f'系统错误: {str(e)}', 'status': 'fail'} 