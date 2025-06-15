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
    """主函数 - 初始化测试数据并验证系统"""
    print("=== 微信扫码考勤系统 - 测试数据初始化 ===\n")
    
    try:
        # 导入并运行测试数据初始化
        print("步骤 1: 初始化测试数据...")
        from tests.test_data_initialization import TestDataInitializer
        
        initializer = TestDataInitializer()
        initializer.initialize_all_data()
        
        print("\n" + "="*50)
        
        # 导入并运行系统验证
        print("步骤 2: 验证系统完整性...")
        from tests.test_system_validation import SystemValidationTest
        
        validator = SystemValidationTest()
        success = validator.run_all_checks()
        
        print("\n" + "="*50)
        
        if success:
            print("\n🎉 系统初始化完成！所有检查通过！")
            print("\n📋 可用的登录账号:")
            print("   管理员: admin / 1")
            print("   教师:   12345 / 1") 
            print("   学生:   23307130001 / 1")
            print("\n🌐 服务器地址: http://127.0.0.1:8000/")
            print("\n💡 使用说明:")
            print("   1. 运行 'python manage.py runserver' 启动服务器")
            print("   2. 在浏览器中访问上述地址")
            print("   3. 使用上述账号登录测试不同角色功能")
            print("\n✨ 系统功能:")
            print("   - 学生端: 查看课程、考勤记录、请假申请、统计分析")
            print("   - 教师端: 课程管理、考勤事件、审批请假、查看统计")
            print("   - 管理员: 系统管理、用户管理、数据统计")
        else:
            print("\n⚠️  系统初始化完成，但存在一些问题需要修复。")
            print("请查看上述错误信息并修复后再使用系统。")
            
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