# 微信扫码考勤系统


### 数据库初始化
```bash
python manage.py makemigrations
python manage.py migrate
```

### 导入测试数据
```bash
python init_test_data.py
```

### 启动开发服务器
```bash
python manage.py runserver
```

### 访问系统
- 系统地址：http://127.0.0.1:8000/
- 演示时间：2025年6月18日 10:00


### 📁 项目文件目录结构

```
WeChat_QR_Scanning_Attendance_System/
├── 📁 attendance/                           # 主应用目录
│   ├── 📁 views/                           # 视图模块
│   │   ├── __init__.py                     # 视图模块初始化
│   │   ├── student_views.py                # 学生端视图
│   │   ├── teacher_views.py                # 教师端视图
│   │   ├── admin_views.py                  # 管理员视图
│   │   ├── wechat_views.py                 # 微信接口视图
│   │   └── wechat_notify.py                # 微信通知视图
│   ├── 📁 services/                        # 服务模块
│   │   ├── __init__.py                     # 服务模块初始化
│   │   └── wechat_service.py               # 微信服务接口
│   ├── 📁 templates/                       # 模板文件目录
│   │   ├── 📁 student/                     # 学生端模板
│   │   │   ├── dashboard.html              # 学生仪表板
│   │   │   ├── courses.html                # 课程列表
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── attendance.html             # 考勤记录
│   │   │   ├── leave.html                  # 请假申请
│   │   │   ├── leave_request.html          # 请假申请表单
│   │   │   ├── leave_request_history.html  # 请假历史
│   │   │   ├── statistics.html             # 考勤统计
│   │   │   ├── profile.html                # 个人资料
│   │   │   └── scan_result.html            # 扫码结果
│   │   ├── 📁 teacher/                     # 教师端模板
│   │   │   ├── dashboard.html              # 教师仪表板
│   │   │   ├── courses.html                # 课程管理
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── create_attendance.html      # 创建考勤
│   │   │   ├── manage_attendance_events.html # 管理考勤事件
│   │   │   ├── event_detail.html           # 事件详情
│   │   │   ├── attendance_results.html     # 考勤结果
│   │   │   ├── course_all_students_attendance.html # 课程全体学生考勤
│   │   │   ├── student_course_attendance.html # 学生课程考勤
│   │   │   ├── approve_leave_request.html  # 请假审批
│   │   │   ├── leave.html                  # 请假管理
│   │   │   ├── statistics.html             # 统计报表
│   │   │   └── profile.html                # 个人资料
│   │   ├── 📁 admin/                       # 管理员模板
│   │   │   ├── dashboard.html              # 管理员仪表板
│   │   │   ├── statistics.html             # 数据统计
│   │   │   ├── users.html                  # 用户列表
│   │   │   ├── manage_users.html           # 用户管理
│   │   │   ├── manage_students.html        # 学生管理
│   │   │   ├── manage_teachers.html        # 教师管理
│   │   │   ├── manage_departments_majors.html # 院系专业管理
│   │   │   ├── manage_courses.html         # 课程管理
│   │   │   ├── manage_teaching_assignment.html # 教学安排管理
│   │   │   ├── manage_enrollment.html      # 选课管理
│   │   │   ├── courses.html                # 课程列表
│   │   │   └── profile.html                # 个人资料
│   │   ├── base.html                       # 基础模板
│   │   ├── index.html                      # 首页模板
│   │   └── login.html                      # 登录模板
│   ├── 📁 migrations/                      # 数据库迁移文件
│   │   ├── __init__.py                     # 迁移模块初始化
│   │   ├── 0001_consolidated_initial.py    # 合并后的初始迁移
│   │   └── 0002_add_class_date_to_schedule.py # 添加课表日期字段
│   ├── 📄 models.py                        # 数据模型
│   ├── 📄 views.py                         # 主视图文件
│   ├── 📄 urls.py                          # URL路由配置
│   ├── 📄 utils.py                         # 工具函数
│   ├── 📄 admin.py                         # Django管理后台配置
│   ├── 📄 settings.py                      # 应用设置
│   ├── 📄 tests.py                         # 测试文件
│   └── 📄 __init__.py                      # 应用初始化
├── 📁 attendance_system/                   # Django项目配置
│   ├── 📄 __init__.py                      # 项目初始化
│   ├── 📄 settings.py                      # 项目设置
│   ├── 📄 urls.py                          # 主URL配置
│   ├── 📄 wsgi.py                          # WSGI配置
│   └── 📄 asgi.py                          # ASGI配置
├── 📁 tests/                               # 测试文件目录
│   ├── 📄 __init__.py                      # 测试模块初始化
│   └── 📄 test_data_initialization.py      # 测试数据初始化测试
├── 📁 static/                              # 静态文件目录
├── 📁 Document/                            # 项目文档目录
│   ├── 📄 Database_Design.md               # 数据库设计文档
│   └── 📄 wechat_integration.md            # 微信集成文档
├── 📄 init_test_data.py                    # 测试数据初始化脚本
├── 📄 README_TEST_DATA.md                  # 测试数据说明文档
├── 📄 manage.py                            # Django管理脚本
├── 📄 README.md                            # 项目说明文档
└── 📄 db.sqlite3                           # SQLite数据库文件
```


