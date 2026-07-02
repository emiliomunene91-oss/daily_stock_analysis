# WhatsApp 通知集成指南

## 快速开始 (Twilio 沙箱 - 推荐测试)

Twilio 提供免费的 WhatsApp 沙箱环境，无需等待验证，可立即测试。

### 第一步：获取 Twilio 凭证

1. **注册 Twilio 账户**（免费 $15 试用额度）
   - 访问 https://www.twilio.com/try-twilio
   - 使用邮箱注册

2. **获取 WhatsApp 沙箱凭证**
   - 登录 https://console.twilio.com/
   - 左侧菜单 → **Messaging** → **Try it out**
   - 点击 **Send a WhatsApp Message**
   - 页面会显示：
     - **Sandbox Number**: `whatsapp:+14155552671` (示例)
     - 完整的 Account SID 和 Auth Token

3. **复制关键信息**
   ```
   Account SID:     AC... (21 个字符)
   Auth Token:      ... (34 个字符)
   Sandbox Number:  whatsapp:+14155552671
   ```

### 第二步：配置环境变量

编辑 `.env` 文件，添加以下配置：

```dotenv
# WhatsApp 通知配置 (Twilio 沙箱)
WHATSAPP_ENABLED=true
WHATSAPP_PROVIDER=twilio

# Twilio 凭证
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671

# 接收人号码（必填）
WHATSAPP_RECIPIENT_PHONE=+254768148010

# 可选配置
WHATSAPP_MESSAGE_MAX_LENGTH=4096
WHATSAPP_RETRY_MAX=3
WHATSAPP_TIMEOUT_SEC=30
```

### 第三步：加入沙箱

1. **从手机上**，打开 WhatsApp
2. 发送以下消息到沙箱号码（`+1 415-555-0162` 等 - 从 Twilio 控制面板复制）：
   ```
   join garden-fence
   ```
   （将 `garden-fence` 替换为 Twilio 沙箱页面显示的实际代码）

3. **收到确认消息** → 成功加入沙箱！

### 第四步：测试发送

```bash
# 本地测试
python -c "
from src.services.whatsapp_service import send_whatsapp_notification_sync
result = send_whatsapp_notification_sync(
    '📊 测试消息\n\n这是来自股票分析系统的 WhatsApp 测试消息。',
    title='GTC Agent 股票分析'
)
print('发送成功！' if result else '发送失败')
"
```

---

## 生产部署 (Official WhatsApp Business API)

Twilio 沙箱用于测试，生产环境需要使用 Meta 的 Official WhatsApp Business API。

### 第一步：注册 Meta Business Account

1. 访问 https://www.facebook.com/business/tools/meta-business-suite
2. 创建或关联现有的 Meta Business Account
3. 设置支付方式（用于 WhatsApp 消息费用）

### 第二步：创建 WhatsApp Business App

1. 登录 Meta Developers：https://developers.facebook.com/
2. **创建新应用** → 选择 **Business**
3. 配置应用
   - 应用名称：`Stock Analysis WhatsApp Bot`
   - 应用用途：`Business`

### 第三步：设置 WhatsApp Integration

1. 在应用中添加 **WhatsApp** 产品
2. 进入 **Settings** → **WhatsApp Business Account**
3. **链接现有账户** 或 **创建新账户**
4. **获取以下信息**：
   - Phone Number ID
   - Business Account ID  
   - Permanent Access Token

### 第四步：验证接收号码

1. 前往 **WhatsApp Manager**
2. 添加接收人号码（`+254768148010`）到**测试号码列表**
3. 接收人会收到验证代码，需要回复确认

### 第五步：配置环境变量

```dotenv
# WhatsApp 通知配置 (Official API)
WHATSAPP_ENABLED=true
WHATSAPP_PROVIDER=official

# Official WhatsApp Business API 凭证
WHATSAPP_PHONE_NUMBER_ID=123456789123456
WHATSAPP_ACCESS_TOKEN=EAABsabcdefg...
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789123456

# 接收人号码
WHATSAPP_RECIPIENT_PHONE=+254768148010
```

---

## 集成到股票分析流程

### 在通知���道中启用 WhatsApp

编辑 `src/core/notification_manager.py` 或通过 Web 设置页面：

```python
from src.services.whatsapp_service import send_whatsapp_notification_sync

# 在分析完成后发送通知
def notify_analysis_complete(report: str, title: str):
    # 其他通知渠道...
    
    # WhatsApp 通知
    send_whatsapp_notification_sync(report, title)
```

### 自动推送 GTC Agent 决策

```bash
# 启用 Agent 模式和 WhatsApp
AGENT_MODE=true
AGENT_SKILLS=gtc_agent
WHATSAPP_ENABLED=true
WHATSAPP_PROVIDER=twilio  # 或 official
```

每次 GTC Agent 生成买卖建议时，会自动通过 WhatsApp 推送到 `+254768148010`。

---

## 消息格式

### 支持的文本格式

WhatsApp 支持以下 Markdown 风格的格式：

```
*粗体文本*
_斜体文本_
~删除线~
```

### 自动分割

长消息会自动分割成多条，避免单条超过 4096 字符：

```python
# 示例：1 万字的报告会分成 3 条消息自动发送
message = "很长的股票分析报告..." * 1000
send_whatsapp_notification_sync(message)
```

### 报告示例

```
*🎯 GTC Agent 决策报告*

📊 个股代码：600519
💰 最新价格：1250.50 (↑2.5%)
⭐ 综合评分：72/100
🎲 推荐决策：买入
📈 置信度：85%

*三维评分明细*
📊 情绪面：+15/30 (正面新闻)
📈 技术面：+28/30 (多头排列，低乖离)
💎 基本面：+18/20 (业绩高增长)

*核心理由*
均线金叉形成，量能配合良好，基本面支撑强劲。

*风险提示*
⚠️ 融资余额处高位
⚠️ 需防止获利回吐
```

---

## 故障排查

### 消息未发送

**检查清单**：

```bash
# 1. 验证配置
grep WHATSAPP_ .env

# 2. 查看日志
tail -f logs/stock_analysis.log | grep -i whatsapp

# 3. 测试连接
python -c "
from src.services.whatsapp_service import get_whatsapp_service
service = get_whatsapp_service()
print(f'启用: {service.enabled}')
print(f'供应商: {service.provider}')
print(f'接收号: {service.recipient_phone}')
"
```

### Twilio 沙箱错误

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| `Invalid From Number` | Sandbox 号码错误 | 检查 TWILIO_WHATSAPP_NUMBER，确保格式为 `whatsapp:+...` |
| `Unregistered Recipient` | 号码未加入沙箱 | 从手机发送 `join [code]` 到沙箱号码 |
| `Invalid Auth` | Token 过期 | 从 Twilio 控制台重新获取 Auth Token |
| `Rate Limited` | 发送过于频繁 | 等待 60 秒后重试 |

### Official API 错误

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| `WABA-Invalid-Request` | 号码未验证 | 在 WhatsApp Manager 中验证接收号码 |
| `INVALID_PHONE_NUMBER` | 号码格式错误 | 确保包含 + 和国家代码：`+254768148010` |
| `(131031) Unknown user` | 号码不在测试列表中 | 添加到 WhatsApp Manager 的测试号码 |

---

## 成本估算

### Twilio 沙箱（免费）
- 免费试用：$15 额度
- 沙箱消息：完全免费
- 无需付款方式

### Official WhatsApp Business API（按使用付费）
- 国际消息：$0.04 - $0.20 / 条（根据国家而定）
- 中国（+86）：约 $0.04 / 条
- 肯尼亚（+254）：约 $0.01 / 条
- 美国（+1）：约 $0.04 / 条

### 估算示例
- 每天 1 条消息，肯尼亚号码：$0.30 / 月
- 每天 10 条消息，国际：$12 / 月

---

## 与 GTC Agent 的协作

### 场景 1：每日自动推送

```bash
# 配置
SCHEDULE_ENABLED=true
SCHEDULE_TIME=18:00
AGENT_MODE=true
AGENT_SKILLS=gtc_agent
WHATSAPP_ENABLED=true
```

**效果**：每天下午 6 点，系统自动分析 STOCK_LIST 中的股票，使用 GTC Agent 生成决策报告，并通过 WhatsApp 推送。

### 场景 2：实时告警

```python
# 当 GTC Agent 检测到买入信号时立即推送
from src.services.whatsapp_service import send_whatsapp_notification_sync

if gtc_decision == "BUY" and confidence > 0.8:
    send_whatsapp_notification_sync(
        f"🚨 买入信号：{stock_code}\n价格：{price}\n置信度：{confidence}%",
        title="GTC 实时告警"
    )
```

---

## 下一步

✅ **已完成**：
- ✓ GTC Agent 策略创建
- ✓ WhatsApp 服务集成
- ✓ Twilio 沙箱快速开始
- ✓ Official API 生产指南

🚀 **可选扩展**：
- [ ] 创建 WhatsApp 指令机器人（Web 集成）
- [ ] 设置告警规则自动推送
- [ ] 添加语音消息支持
- [ ] 集成多个 WhatsApp 账户

---

## 文档链接

- [Twilio WhatsApp Sandbox 文档](https://www.twilio.com/docs/whatsapp/quickstart/python)
- [Meta WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [GTC Agent 策略文档](../strategies/README.md)
- [通知渠道配置](../../docs/full-guide.md#通知渠道详细配置)
