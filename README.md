# 微信扫码考勤系统

洪家权，陈皓阳，盖烈森，马静
2024-2025学年春季学期 数据库及实现

### 文档指引

请查看 `Document/` 目录下的详细文档：

- **[安装部署文档](Document/安装部署文档.pdf)** - 系统安装和部署指南
- **[用户手册](Document/用户手册.pdf)** - 完整的用户操作手册
- **[数据库设计文档](Document/数据库设计文档.pdf)** - 数据库架构设计说明

### 项目目录结构

```
WeChat_QR_Scanning_Attendance_System/
├── attendance/                         # 主应用模块
│   ├── migrations/                     # 数据库迁移文件
│   ├── models.py                       # 数据模型定义
│   ├── services/                       
│   │   └── wechat_service.py           
│   ├── templates/                      ### 网页
│   │   ├── admin/                      # 管理员页面模板
│   │   ├── student/                    # 学生页面模板
│   │   ├── teacher/                    # 教师页面模板
│   │   ├── base.html                   # 基础模板
│   │   ├── index.html                  # 首页模板
│   │   └── login.html                  # 登录页面模板
│   ├── templatetags/                  
│   │   └── attendance_filters.py       # 时间转换过滤器
│   ├── views/                          ### 视图
│   │   ├── admin_views.py              # 管理员视图
│   │   ├── student_views.py            # 学生视图
│   │   ├── teacher_views.py            # 教师视图
│   │   ├── wechat_views.py             # 微信相关
│   │   └── wechat_notify.py            
│   ├── urls.py                         
│   └── utils.py                        
├── attendance_system/                  # Django项目配置
│   ├── settings.py                     # 主配置文件
│   ├── urls.py                         # URL配置
│   ├── asgi.py                         
│   └── wsgi.py                        
├── Document/                           ### 项目文档
│   ├── source/                         
│   ├── 安装部署文档.pdf                
│   ├── 数据库设计文档.pdf              
│   └── 用户手册.pdf                   
├── tests/                              ### 测试与导入数据
│   ├── test_data_initialization.py     # 测试数据初始化
│   └── test_utilities.py               # 测试工具函数
├── static/                             
├── init_test_data.py                   # 测试数据导入脚本
├── setup_wechat_demo.py                # 微信功能配置脚本 
├── manage.py                           # Django管理脚本
├── requirements.txt                    # 项目依赖
└── README.md                           # 项目说明
```

### 快速开始

##### 本地体验
```bash
python init_test_data.py
python manage.py runserver
```

##### 扫码功能体验
```bash
python setup_wechat_demo.py
```

详细说明请参考 [安装部署文档](Document/安装部署文档.pdf)。