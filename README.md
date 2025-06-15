# 微信扫码考勤系统 - 项目结构

### 📁 项目结构

```
WeChat_QR_Scanning_Attendance_System/
├── 📁 attendance/                           # 主应用目录
│   ├── 📁 views/                           # 视图模块
│   │   ├── __init__.py                     # 主视图和登录逻辑
│   │   ├── student_views.py                # 学生端视图 (8个视图函数)
│   │   ├── teacher_views.py                # 教师端视图 (7个视图函数)
│   │   └── admin_views.py                  # 管理员视图 (1个视图函数)
│   ├── 📁 services/                        # 服务模块
│   │   ├── __init__.py                     # 服务模块初始化
│   │   └── wechat_service.py               # 微信服务接口
│   ├── 📁 templates/                       # 模板文件目录
│   │   ├── 📁 student/                     # 学生端模板
│   │   │   ├── dashboard.html              # 学生仪表板
│   │   │   ├── courses.html                # 课程列表
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── attendance.html             # 考勤记录
│   │   │   ├── leave_request.html          # 请假申请
│   │   │   ├── leave_request_history.html  # 请假历史
│   │   │   ├── statistics.html             # 考勤统计
│   │   │   └── profile.html                # 个人资料
│   │   ├── 📁 teacher/                     # 教师端模板
│   │   │   ├── dashboard.html              # 教师仪表板
│   │   │   ├── courses.html                # 课程管理
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── attendance_results.html     # 考勤结果
│   │   │   ├── leave.html                  # 请假审批
│   │   │   └── profile.html                # 个人资料
│   │   ├── 📁 admin/                       # 管理员模板
│   │   │   └── dashboard.html              # 管理员仪表板
│   │   ├── base.html                       # 基础模板
│   │   ├── index.html                      # 首页模板
│   │   └── login.html                      # 登录模板
│   ├── 📁 migrations/                      # 数据库迁移文件
│   │   ├── 0001_initial.py                 # 初始数据库结构
│   │   ├── 0002_alter_department_dept_id.py
│   │   ├── 0003_alter_major_major_id.py
│   │   ├── 0004_alter_teachingassignment_assignment_id.py
│   │   ├── 0005_course_credit_alter_course_course_id_and_more.py
│   │   ├── 0006_student_user_teacher_user.py  # 用户关联
│   │   ├── 0007_alter_classschedule_schedule_id.py
│   │   └── __init__.py
│   ├── 📄 models.py                        # 数据模型 (12个模型类)
│   ├── 📄 views.py                         # 主视图文件
│   ├── 📄 urls.py                          # URL路由配置 (20个路由)
│   ├── 📄 utils.py                         # 工具函数
│   ├── 📄 admin.py                         # Django管理后台配置
│   └── 📄 __init__.py                      # 应用初始化
├── 📁 attendance_system/                   # Django项目配置
│   ├── 📄 settings.py                      # 项目设置
│   ├── 📄 urls.py                          # 主URL配置
│   ├── 📄 wsgi.py                          # WSGI配置
│   ├── 📄 asgi.py                          # ASGI配置
│   └── 📄 __init__.py                      # 项目初始化
├── 📁 tests/                               # 测试文件目录
│   ├── 📄 test_data_initialization.py      # 测试数据初始化测试
│   ├── 📄 test_system_validation.py        # 系统验证测试
│   └── 📄 __init__.py                      # 测试模块初始化
├── 📁 static/                              # 静态文件目录
│   ├── 📁 css/                             # CSS样式文件
│   ├── 📁 js/                              # JavaScript文件
│   └── 📁 images/                          # 图片资源
├── 📁 Document/                            # 项目文档目录
├── 📄 init_test_data.py                    # 测试数据初始化脚本
├── 📄 README_TEST_DATA.md                  # 测试数据说明文档
├── 📄 manage.py                            # Django管理脚本
├── 📄 db.sqlite3                           # SQLite数据库文件
├── 📄 .gitignore                           # Git忽略文件配置
└── 📄 README.md                            # 项目说明文档 (本文件)
```
