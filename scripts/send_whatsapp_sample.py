#!/usr/bin/env python3
"""
Send WhatsApp test message using Twilio
"""
import sys

try:
    from twilio.rest import Client
    
    # Initialize Twilio client with your credentials
    account_sid = "ACc1b8720784"
    auth_token = "33d9bcf21107075a85488f4704882597"
    client = Client(account_sid, auth_token)
    
    # Sample GTC Agent message
    sample_message = """🎯 *GTC Agent 综合决策报告*

📊 个股代码：600519 (茅台)
💰 最新价格：1,850.50 ↑2.5%
⭐ 综合评分：78/100
🎲 推荐决策：*BUY (买入)*
📈 置信度：82%

━━━━━━━━━━━━━━━━━━━━━
*三维评分明细*

📊 情绪面：+18/30 分
   • 新闻情绪：积极
   • 市场热度：高
   • 机构关注：增加中

📈 技术面：+30/30 分 ⭐
   • 均线排列：MA5>MA10>MA20 多头
   • 乖离率：-2% (合理区间)
   • 量能表现：温和 ✓
   • 支撑位：1,820

💎 基本面：+20/20 分 ⭐
   • 业绩增速：+28% YoY
   • PE 估值：32倍（历史中位）
   • 资金态度：净流入

━━━━━━━━━━━━━━━━━━━━━
*核心理由*
均线金叉形成，技术面完美，基本面支撑强劲，情绪面积极。

*建议操作*
✓ 在 1,820-1,840 分批布局
✓ 目标位：1,950
✓ 止损位：1,760

*风险提示*
⚠️ 融资余额处历史高位
⚠️ 需防止获利回吐
⚠️ 关注行业政策变化

━━━━━━━━━━━━━━━━━━━━━
📱 GTC Agent v1.0 | 时间：2026-07-02"""

    print("📤 正在发送 WhatsApp 测试消息...")
    print(f"📱 目标号码：+254768148010")
    print(f"🔵 Twilio 沙箱号码：+18316033262")
    print("-" * 60)
    
    # Send message via Twilio
    message = client.messages.create(
        from_="whatsapp:+18316033262",
        body=sample_message,
        to="+254768148010"
    )
    
    print(f"✅ 消息发送成功！")
    print(f"📌 消息 ID：{message.sid}")
    print(f"📊 状态：{message.status}")
    print("\n" + "="*60)
    print("✨ 检查你的 WhatsApp - 你应该会收到一条消息！")
    print("="*60)
    print("\n📝 发送的内容预览：")
    print(sample_message)
    
except ImportError:
    print("❌ Twilio SDK 未安装")
    print("请运行: pip install twilio")
    sys.exit(1)
except Exception as e:
    print(f"❌ 发送失败：{e}")
    print(f"\n调试信息：")
    print(f"  Account SID：ACc1b8720784")
    print(f"  Twilio 号码：+18316033262")
    print(f"  接收号码：+254768148010")
    sys.exit(1)
