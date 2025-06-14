from .models import SystemLog
import qrcode
import io
import base64
from datetime import datetime, time
from django.conf import settings
from .models import AttendanceEvent, Attendance, Enrollment, STATUS_PRESENT, STATUS_ABSENT

def log_activity(user, action, status=True):
    """
    记录系统操作日志
    
    Args:
        user: 操作用户
        action: 操作描述
        status: 操作状态（True表示成功，False表示失败）
    """
    try:
        SystemLog.objects.create(
            user=user,
            action=action,
            ip_address=user.last_login_ip if hasattr(user, 'last_login_ip') else '0.0.0.0',
            status=status
        )
    except Exception as e:
        print(f"记录日志失败: {str(e)}")

def generate_qr_code(event_id):
    """生成考勤二维码"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(event_id))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{qr_code}"

def verify_qr_code(qr_code, student_openid):
    """验证二维码并记录考勤"""
    try:
        # 获取考勤事件
        event = AttendanceEvent.objects.get(
            event_id=qr_code,
            event_status=1  # 确保二维码有效
        )
        
        # 验证时间是否在有效范围内
        current_time = datetime.now().time()
        if not (event.scan_start_time <= current_time <= event.scan_end_time):
            return False, "不在考勤时间范围内"
        
        # 获取学生选课记录
        enrollment = Enrollment.objects.get(
            student__openid=student_openid,
            course=event.course
        )
        
        # 检查是否已经签到
        if Attendance.objects.filter(enrollment=enrollment, event=event).exists():
            return False, "已经签到过了"
        
        # 记录考勤
        Attendance.objects.create(
            enrollment=enrollment,
            event=event,
            scan_time=datetime.now(),
            status=STATUS_PRESENT
        )
        
        return True, "签到成功"
        
    except AttendanceEvent.DoesNotExist:
        return False, "无效的二维码"
    except Enrollment.DoesNotExist:
        return False, "您未选修该课程"
    except Exception as e:
        return False, f"系统错误: {str(e)}"

def get_attendance_status(event_id):
    """获取考勤状态统计"""
    event = AttendanceEvent.objects.get(event_id=event_id)
    total = Enrollment.objects.filter(course=event.course).count()
    present = Attendance.objects.filter(event=event, status=STATUS_PRESENT).count()
    absent = Attendance.objects.filter(event=event, status=STATUS_ABSENT).count()
    
    return {
        'total': total,
        'present': present,
        'absent': absent,
        'attendance_rate': round(present / total * 100, 2) if total > 0 else 0
    } 