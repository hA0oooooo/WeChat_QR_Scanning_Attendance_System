from .models import SystemLog

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