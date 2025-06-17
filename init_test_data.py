#!/usr/bin/env python
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
    print("=== 微信扫码考勤系统 - 测试数据初始化 ===\n")
    
    try:
        # 导入并运行测试数据初始化
        print("正在初始化测试数据...")
        from tests.test_data_initialization import create_test_data
        
        create_test_data()
        
        print("\n" + "="*50)
        print("\n🎉 系统初始化完成！")
        print("\n📋 可用的登录账号:")
        print("   管理员: admin / 1")
        print("   教师:   12345 / 1") 
        print("   学生:   23307130001 / 1 (开心)")
        print("\n🌐 服务器地址: http://127.0.0.1:8000/")
        print("\n💡 使用说明:")
        print("   1. 运行 'python manage.py runserver' 启动服务器")
        print("   2. 在浏览器中访问上述地址")
        print("   3. 使用上述账号登录测试不同角色功能")
        print("\n✨ 演示数据状态:")
        print("   - 6月11日：学生开心出勤")
        print("   - 6月18日：学生开心缺勤（可通过扫码变为出勤）")
        print("   - 6月25日：学生开心未开始（可申请请假）")
        print("   - 当前时间：6月18日10:00（课程进行中）")
        print("   - 待审批请假：空（可演示申请请假）")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖模块都已正确安装。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("请检查数据库连接和Django配置。")
        sys.exit(1)


if __name__ == '__main__':
    main() 