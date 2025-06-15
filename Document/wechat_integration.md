# 微信集成说明

### 配置参数

```python
# attendance_system/settings.py
WECHAT_APPID = 'your_appid_here'                    # 微信公众号AppID
WECHAT_SECRET = 'your_secret_here'                  # 微信公众号AppSecret  
WECHAT_TOKEN = 'your_token_here'                    # 微信公众号Token
WECHAT_ENCODING_AES_KEY = 'your_encoding_aes_key_here'  # 消息加解密密钥
WECHAT_ATTENDANCE_TEMPLATE_ID = 'your_template_id_here'  # 考勤通知模板ID
```

### 核心文件

##### WeChatService 服务类
- 位置: `attendance/services/wechat_service.py`
- 功能: 处理微信API交互和扫码考勤逻辑
- 状态: 已实现基础框架，待完善微信API对接

##### 扫码API接口
- URL: `/api/scan-qr-code/`
- 实现: `attendance/views/__init__.py`
- 状态: 已实现接口框架和基础验证逻辑

### 扫码考勤流程

1. 验证微信签名
2. 检查考勤事件和学生信息
3. 验证选课关系和时间范围
4. 记录考勤并推送通知

### 数据模型

- **AttendanceEvent**: 考勤事件
- **Student**: 学生信息（含openid字段）
- **Enrollment**: 选课记录  
- **Attendance**: 考勤记录

##### 注意事项
- 当前为开发阶段，微信API功能需要真实的微信公众号配置
- 测试数据中学生的openid字段为空，需要与微信用户绑定后使用 