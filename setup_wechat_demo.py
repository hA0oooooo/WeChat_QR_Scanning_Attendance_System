#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信扫码考勤系统一键配置脚本
自动配置微信参数和内网穿透地址，并初始化测试数据
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("    微信扫码考勤系统 - 一键配置脚本")
    print("=" * 60)
    print("本脚本将帮助您配置微信公众号参数和内网穿透地址")
    print("配置完成后将自动初始化测试数据")
    print("-" * 60)

def get_user_input():
    """获取用户输入的配置信息"""
    print("\n请输入以下配置信息：")
    print("(提示：可以从微信公众平台测试号管理页面获取)")
    print()
    
    # 获取微信配置
    appid = input("请输入微信 AppID: ").strip()
    if not appid:
        print("错误：AppID 不能为空")
        sys.exit(1)
    
    secret = input("请输入微信 AppSecret: ").strip()
    if not secret:
        print("错误：AppSecret 不能为空")
        sys.exit(1)
    
    # 获取内网穿透地址
    print("\n请输入内网穿透地址（如：https://abc123.vicp.fun）：")
    tunnel_url = input("内网穿透地址: ").strip()
    if not tunnel_url:
        print("错误：内网穿透地址不能为空")
        sys.exit(1)
    
    # 确保URL格式正确
    if not tunnel_url.startswith(('http://', 'https://')):
        tunnel_url = 'https://' + tunnel_url
    
    # 移除末尾的斜杠
    tunnel_url = tunnel_url.rstrip('/')
    
    # 获取用户的微信openid
    print("\n请输入您的微信 OpenID：")
    print("(提示：可以通过微信公众平台测试号的用户列表获取)")
    openid = input("您的微信 OpenID: ").strip()
    if not openid:
        print("错误：OpenID 不能为空")
        sys.exit(1)
    
    return {
        'appid': appid,
        'secret': secret,
        'tunnel_url': tunnel_url,
        'openid': openid
    }

def update_settings_file(config):
    """更新Django设置文件"""
    settings_file = Path('attendance_system/settings.py')
    
    if not settings_file.exists():
        print(f"错误：找不到设置文件 {settings_file}")
        sys.exit(1)
    
    print(f"\n正在更新 {settings_file}...")
    
    # 读取文件内容
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新微信配置
    content = re.sub(
        r"WECHAT_APPID = '[^']*'",
        f"WECHAT_APPID = '{config['appid']}'",
        content
    )
    
    content = re.sub(
        r"WECHAT_SECRET = '[^']*'",
        f"WECHAT_SECRET = '{config['secret']}'",
        content
    )
    
    # 更新回调地址
    notify_url = f"{config['tunnel_url']}/wechat/notify/"
    content = re.sub(
        r"WECHAT_NOTIFY_URL = '[^']*'",
        f"WECHAT_NOTIFY_URL = '{notify_url}'",
        content
    )
    
    # 更新CSRF信任域名
    domain = config['tunnel_url']
    content = re.sub(
        r'CSRF_TRUSTED_ORIGINS = \[[^\]]*\]',
        f'CSRF_TRUSTED_ORIGINS = [\n    "{domain}",\n]',
        content,
        flags=re.MULTILINE
    )
    
    # 写回文件
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Django设置文件更新完成")
    print("  - 微信配置已更新")
    print("  - 回调地址已更新") 
    print("  - CSRF信任域名已更新")
    print("  - 二维码生成将自动使用新域名")

def update_init_test_data(config):
    """更新测试数据初始化文件"""
    init_file = Path('tests/test_data_initialization.py')
    
    if not init_file.exists():
        print(f"错误：找不到测试数据文件 {init_file}")
        sys.exit(1)
    
    print(f"\n正在更新 {init_file}...")
    
    # 读取文件内容
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新用户openid配置
    content = re.sub(
        r'YOUR_WECHAT_OPENID = ".*?"',
        f'YOUR_WECHAT_OPENID = "{config["openid"]}"',
        content
    )
    
    # 写回文件
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 测试数据文件更新完成")

def run_init_test_data():
    """运行测试数据初始化"""
    print("\n正在初始化测试数据...")
    print("-" * 40)
    
    try:
        # 运行初始化脚本
        result = subprocess.run([sys.executable, 'init_test_data.py'], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("-" * 40)
            print("✓ 测试数据初始化完成")
        else:
            print("✗ 测试数据初始化失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ 运行初始化脚本时出错: {e}")
        sys.exit(1)


def main():
    """主函数"""
    print_banner()
    
    # 检查是否在正确的目录
    if not Path('manage.py').exists():
        print("错误：请在Django项目根目录下运行此脚本")
        sys.exit(1)
    
    try:
        # 获取用户输入
        config = get_user_input()
        
        # 确认配置
        print("\n" + "-" * 40)
        print("请确认以下配置信息：")
        print(f"  微信 AppID: {config['appid']}")
        print(f"  微信 AppSecret: {config['secret']}")
        print(f"  内网穿透地址: {config['tunnel_url']}")
        print(f"  您的 OpenID: {config['openid']}")
        print("-" * 40)
        
        confirm = input("确认配置并继续？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("配置已取消")
            sys.exit(0)
        
        # 更新配置文件
        update_settings_file(config)
        update_init_test_data(config)
        
        # 运行测试数据初始化
        run_init_test_data()
        
        
    except KeyboardInterrupt:
        print("\n\n配置已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n配置过程中出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 