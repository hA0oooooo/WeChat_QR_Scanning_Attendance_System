# 微信扫码考勤系统 - 安装部署文档

### 1. 环境要求

* Python 3.8+
* Django 4.2
* SQLite（默认数据库）
* 微信公众号测试号（关联扫码功能）
* 内网穿透工具（花生壳）

### 2. 依赖包安装

##### 2.1 安装Python依赖

```bash
pip install -r requirements.txt
```

主要依赖包：
* Django==4.2.20
* qrcode==7.4.2
* Pillow==10.0.0
* requests==2.31.0

### 3. 本地体验模式

如果您只想查看系统界面和基本功能，无需微信配置：

##### 3.1 初始化数据库

```bash
python init_test_data.py
```

##### 3.2 启动服务

```bash
python manage.py runserver
```

##### 3.3 访问系统

打开浏览器访问：http://127.0.0.1:8000

默认账号：
* 管理员：admin / 123456
* 教师：teacher1 / 123456
* 学生：23307130001 / 123456

### 4. 扫码功能部署

如果您想体验完整的微信扫码功能，需要以下步骤：

##### 4.1 安装花生壳内网穿透

1. 安装花生壳客户端（已经在项目根目录准备了安装文件）
2. 注册并登录花生壳客户端（新用户可以有两个小时的免费体验时间）

![花生壳](花生壳.png)

##### 4.2 配置内网穿透

1. 在花生壳客户端中添加内网穿透映射
2. 点击自定义映射右边的 + 号，配置内网主机：127.0.0.1 ；内网端口：8000
3. 获取公网访问地址（如：https://1ka10063yf404.vicp.fun/）

##### 4.3 申请微信公众号测试号

1. 访问微信公众平台测试号：https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login
2. 扫码登录微信
3. 填写接口配置信息，URL 在公网访问地址后添加 /wechat/notify/ (如：https://1ka10063yf404.vicp.fun/wechat/notify/)，Token 输入 mytesttoken

![测试号管理](测试号管理.png)

4. 记录信息：appID，appsecret，以及您的微信openid（扫描左侧二维码关注微信测试公众号后在用户列表中获取）

![微信openid](微信openid.png)


##### 4.4 配置微信回调

1. 在接口配置信息中填写（上一步 4.3 中已经完成）：
   * URL：https://您的域名/wechat/notify/
   * Token：mytesttoken

2. 滑动到下方，体验接口权限表->网页服务->网页账号->点击修改，在网页授权获取用户基本信息中填写：您内网穿透后的域名（不含https://）

![回调](回调.png)

![回调网址](回调网址.png)


##### 4.5 一键配置系统

运行配置脚本：

```bash
python setup_wechat_demo.py
```

按提示输入：
* 微信 AppID
* 微信 AppSecret  
* 内网穿透地址
* 您的微信 OpenID

脚本将自动：
* 更新系统配置文件 setting.py 
* 初始化测试数据（包括用户真实微信 openid ）


##### 4.6 启动系统

```bash
python manage.py runserver
```


### 5. 注意事项

* 确保内网穿透工具正常运行
* 微信公众平台配置必须与系统设置一致
* 系统使用模拟时间：2025-06-18 10:00:00
* 扫码功能直接在手机端微信扫描二维码

