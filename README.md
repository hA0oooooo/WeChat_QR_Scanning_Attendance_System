# 微信扫码考勤系统



### 安装运行
```bash
# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 导入测试数据
python init_test_data.py

# 运行项目
python manage.py runserver
```



## ✨ 主要功能

### 🎨 学生端UI优化
- 现代化响应式界面设计
- 直观的课程和考勤信息展示
- 便捷的请假申请流程
- 清晰的考勤统计可视化

### 🛠️ 管理员端完整功能（并非完整）
**院系专业管理**
- 新增/编辑/删除院系
- 新增/编辑/删除专业
- 院系-专业关联管理


## 📁 项目结构

```
WeChat_QR_Scanning_Attendance_System/
├── 📁 attendance/                           # 主应用目录
│   ├── 📁 views/                           # 视图模块
│   │   ├── __init__.py                     # 主视图和登录逻辑
│   │   ├── student_views.py                # 学生端视图 (8个视图函数)
│   │   ├── teacher_views.py                # 教师端视图 (12个视图函数)
│   │   └── admin_views.py                  # 管理员视图 (25个视图函数)
│   ├── 📁 services/                        # 服务模块
│   │   ├── __init__.py                     # 服务模块初始化
│   │   └── wechat_service.py               # 微信服务接口
│   ├── 📁 templates/                       # 模板文件目录
│   │   ├── 📁 student/                     # 学生端模板 (8个页面)
│   │   │   ├── dashboard.html              # 学生仪表板
│   │   │   ├── courses.html                # 课程列表
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── attendance.html             # 考勤记录
│   │   │   ├── leave.html                  # 请假申请
│   │   │   ├── leave_request_history.html  # 请假历史
│   │   │   ├── statistics.html             # 考勤统计
│   │   │   └── profile.html                # 个人资料
│   │   ├── 📁 teacher/                     # 教师端模板 (7个页面)
│   │   │   ├── dashboard.html              # 教师仪表板
│   │   │   ├── courses.html                # 课程管理
│   │   │   ├── course_detail.html          # 课程详情
│   │   │   ├── attendance_results.html     # 考勤结果
│   │   │   ├── leave.html                  # 请假审批
│   │   │   └── profile.html                # 个人资料
│   │   ├── 📁 admin/                       # 管理员模板 (11个页面)
│   │   │   ├── dashboard.html              # 管理员仪表板
│   │   │   ├── statistics.html             # 数据统计
│   │   │   ├── manage_users.html           # 人员管理(学生/教师)
│   │   │   ├── manage_departments_majors.html # 院系专业管理
│   │   │   ├── manage_courses.html         # 课程管理
│   │   │   ├── manage_teaching_assignment.html # 教学安排管理
│   │   │   ├── manage_enrollment.html      # 选课管理
│   │   │   ├── manage_students.html        # 学生管理
│   │   │   ├── manage_teachers.html        # 教师管理
│   │   │   ├── profile.html                # 个人资料
│   │   │   └── courses.html                # 课程列表
│   │   ├── base.html                       # 基础模板
│   │   ├── index.html                      # 首页模板
│   │   └── login.html                      # 登录模板
│   ├── 📁 migrations/                      # 数据库迁移文件
│   ├── 📄 models.py                        # 数据模型 (12个模型类)
│   ├── 📄 views.py                         # 主视图文件
│   ├── 📄 urls.py                          # URL路由配置 (75个路由)
│   ├── 📄 utils.py                         # 工具函数
│   ├── 📄 admin.py                         # Django管理后台配置
│   └── 📄 __init__.py                      # 应用初始化
├── 📁 attendance_system/                   # Django项目配置
├── 📁 tests/                               # 测试文件目录
├── 📁 static/                              # 静态文件目录
├── 📁 Document/                            # 项目文档目录
├── 📄 init_test_data.py                    # 测试数据初始化脚本
├── 📄 README_TEST_DATA.md                  # 测试数据说明文档
├── 📄 manage.py                            # Django管理脚本
└── 📄 db.sqlite3                           # SQLite数据库文件
```

