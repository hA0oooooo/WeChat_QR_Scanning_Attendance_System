# 微信集成文档

## 配置说明

在 `settings.py` 中配置以下微信相关参数：

```python
# 微信配置
WECHAT_APPID = 'your_appid_here'  # 微信公众号的AppID
WECHAT_SECRET = 'your_secret_here'  # 微信公众号的AppSecret
WECHAT_TOKEN = 'your_token_here'  # 微信公众号的Token
WECHAT_ENCODING_AES_KEY = 'your_encoding_aes_key_here'  # 消息加解密密钥
WECHAT_ATTENDANCE_TEMPLATE_ID = 'your_template_id_here'  # 考勤通知模板ID
```

## API接口

### 扫码考勤接口

- **URL**: `/api/scan_qr_code/`
- **方法**: POST
- **参数**:
  - `qr_code`: 考勤二维码
  - `student_id`: 学生ID
  - `openid`: 微信用户openid
  - `signature`: 微信请求签名
  - `timestamp`: 时间戳
  - `nonce`: 随机数
- **返回**:
  ```json
  {
    "success": true/false,
    "message": "操作结果说明"
  }
  ```

## 开发说明

### WeChatService类

`WeChatService` 类提供了以下主要功能：

1. `get_access_token()`: 获取微信访问令牌，使用缓存避免频繁请求
2. `verify_signature()`: 验证微信请求签名
3. `get_user_info()`: 获取微信用户信息
4. `send_template_message()`: 发送模板消息
5. `handle_scan_qr()`: 处理扫码考勤

### 缓存机制

使用Django的缓存框架存储access_token，避免频繁请求微信服务器：

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### 安全机制

1. 所有微信请求都需要验证签名
2. 考勤码具有时效性
3. 防止重复签到
4. 验证学生选课信息

## 测试说明

测试文件位于 `attendance/tests/test_wechat_service.py`，包含以下测试用例：

1. 签名验证测试
2. 成功扫码考勤测试
3. 无效考勤码测试
4. 重复签到测试
5. 超出签到时间范围测试

运行测试：
```bash
python manage.py test attendance.tests.test_wechat_service
```

## 注意事项

1. 请妥善保管微信配置参数，不要泄露
2. 定期更新access_token缓存
3. 注意处理微信API的调用频率限制
4. 建议在生产环境使用Redis等缓存后端
5. 需要配置正确的微信模板消息 