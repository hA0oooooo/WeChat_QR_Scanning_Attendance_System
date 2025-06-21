"""
测试数据初始化脚本 - 主入口
用于初始化完整的测试数据，包括用户账号、教师、学生、课程、选课等信息
这个文件现在作为主入口，调用tests文件夹中的模块化测试代码
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """主函数 - 初始化测试数据"""
    try:
        # 导入Django设置以获取配置信息
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
        import django
        django.setup()
        from django.conf import settings
        
        # 导入并运行测试数据初始化
        from tests.test_data_initialization import create_test_data
        
        create_test_data()
        
        # 获取配置信息
        wechat_notify_url = getattr(settings, 'WECHAT_NOTIFY_URL', '未配置')
        csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        public_url = csrf_origins[0] if csrf_origins else '未配置'
        
        # 获取学生的openid
        from attendance.models import Student
        try:
            student = Student.objects.get(stu_id='23307130001')
            student_openid = student.openid
        except:
            student_openid = '未找到'
        
        print("系统初始化完成")
        print("\n可用的登录账号:")
        print("   管理员: admin / 1")
        print("   教师:   12345 / 1") 
        print("   学生:   23307130001 / 1 (开心)")
        
        print("\n访问地址:")
        print(f"   本地地址: http://127.0.0.1:8000/")
        if public_url != '未配置':
            print(f"   公网地址: {public_url}")
        
        print("\n微信配置信息:")
        print(f"   用户获取的真实微信openid: {student_openid}")
        print(f"   回调地址: {wechat_notify_url}")
        
        print("\n使用说明:")
        print("   1. 确保内网穿透工具正在运行")
        print("   2. 运行 'python manage.py runserver' 启动服务器")
        print("   3. 在微信测试号平台配置服务器URL和Token")
        if public_url != '未配置':
            print(f"   4. 访问 {public_url} 开始测试")
        else:
            print("   4. 访问本地地址或配置内网穿透后的公网地址")
        
        print("\n演示数据状态:")
        print("   - 6月11日：学生开心出勤")
        print("   - 6月18日：学生开心缺勤（可通过扫码变为出勤）")
        print("   - 6月25日：学生开心未开始（可申请请假）")
        print("   - 当前时间：6月18日10:00（课程进行中）")
        print("   - 待审批请假：空（可演示申请请假）")
        
        print("\n扫码测试流程:")
        print("   1. 教师登录 → 我的课程 → 数据库及实现")
        print("   2. 管理考勤事件 → 选择6月18日考勤")
        print("   3. 生成二维码")
        print("   4. 微信扫码 → 自动签到")
        print("   5. 学生端查看考勤记录更新")
            
    except ImportError as e:
        print(f"Warning: 导入错误: {e}")
        print("请确保所有依赖模块都已正确安装。")
        sys.exit(1)
    except Exception as e:
        print(f"Warning: 初始化失败: {e}")
        print("请检查数据库连接和Django配置。")
        sys.exit(1)


if __name__ == '__main__':
    main() 