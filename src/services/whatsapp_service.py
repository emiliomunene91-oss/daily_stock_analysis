"""
WhatsApp 通知服务集成

支持多种 WhatsApp 发送方式：
1. Official WhatsApp Business API（生产环境推荐）
2. Twilio WhatsApp Sandbox（快速测试）
3. Vonage WhatsApp API（替代方案）
"""

import os
import logging
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum
import httpx
import json

logger = logging.getLogger(__name__)


class WhatsAppProvider(Enum):
    """WhatsApp 服务商枚举"""
    OFFICIAL = "official"
    TWILIO = "twilio"
    VONAGE = "vonage"


class WhatsAppNotificationService:
    """WhatsApp 通知服务"""

    def __init__(self):
        self.enabled = os.getenv("WHATSAPP_ENABLED", "true").lower() == "true"
        self.provider = WhatsAppProvider(os.getenv("WHATSAPP_PROVIDER", "official"))
        self.recipient_phone = os.getenv("WHATSAPP_RECIPIENT_PHONE", "+254768148010")
        self.max_length = int(os.getenv("WHATSAPP_MESSAGE_MAX_LENGTH", "4096"))
        self.retry_max = int(os.getenv("WHATSAPP_RETRY_MAX", "3"))
        self.timeout = int(os.getenv("WHATSAPP_TIMEOUT_SEC", "30"))

        if not self.enabled:
            logger.info("WhatsApp 通知已禁用")
            return

        self._validate_config()

    def _validate_config(self):
        """验证配置完整性"""
        if self.provider == WhatsAppProvider.OFFICIAL:
            required = [
                "WHATSAPP_PHONE_NUMBER_ID",
                "WHATSAPP_ACCESS_TOKEN",
                "WHATSAPP_RECIPIENT_PHONE",
            ]
            missing = [k for k in required if not os.getenv(k)]
            if missing:
                logger.warning(
                    f"Official WhatsApp API 配置不完整，缺少: {', '.join(missing)}"
                )
                self.enabled = False

        elif self.provider == WhatsAppProvider.TWILIO:
            required = [
                "TWILIO_ACCOUNT_SID",
                "TWILIO_AUTH_TOKEN",
                "TWILIO_WHATSAPP_NUMBER",
            ]
            missing = [k for k in required if not os.getenv(k)]
            if missing:
                logger.warning(f"Twilio WhatsApp 配置不完整，缺少: {', '.join(missing)}")
                self.enabled = False

        elif self.provider == WhatsAppProvider.VONAGE:
            required = ["VONAGE_API_KEY", "VONAGE_API_SECRET", "VONAGE_WHATSAPP_NUMBER"]
            missing = [k for k in required if not os.getenv(k)]
            if missing:
                logger.warning(f"Vonage WhatsApp 配置不完整，缺少: {', '.join(missing)}")
                self.enabled = False

    async def send(
        self, message: str, title: Optional[str] = None, retry: int = 0
    ) -> bool:
        """
        发送 WhatsApp 消息

        Args:
            message: 消息内容
            title: 消息标题（可选）
            retry: 当前重试次数

        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.debug("WhatsApp 通知未启用，跳过发送")
            return False

        try:
            # 格式化消息
            formatted_message = self._format_message(message, title)

            # 分割长消息
            messages = self._split_message(formatted_message)

            # 发送每条消息
            success = True
            for msg in messages:
                if self.provider == WhatsAppProvider.OFFICIAL:
                    sent = await self._send_official(msg)
                elif self.provider == WhatsAppProvider.TWILIO:
                    sent = await self._send_twilio(msg)
                elif self.provider == WhatsAppProvider.VONAGE:
                    sent = await self._send_vonage(msg)
                else:
                    sent = False

                if not sent:
                    success = False

            return success

        except Exception as e:
            logger.error(f"WhatsApp 发送失败: {e}")
            if retry < self.retry_max:
                await asyncio.sleep(2 ** retry)  # 指数退避
                return await self.send(message, title, retry + 1)
            return False

    async def _send_official(self, message: str) -> bool:
        """使用 Official WhatsApp Business API 发送"""
        try:
            phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")

            url = f"https://graph.instagram.com/v18.0/{phone_number_id}/messages"

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.recipient_phone.replace("+", ""),
                "type": "text",
                "text": {"preview_url": False, "body": message},
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    logger.info("✓ WhatsApp 消息发送成功 (Official API)")
                    return True
                else:
                    logger.error(
                        f"Official API 发送失败 ({response.status_code}): {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Official WhatsApp API 错误: {e}")
            return False

    async def _send_twilio(self, message: str) -> bool:
        """使用 Twilio WhatsApp Sandbox 发送"""
        try:
            from twilio.rest import Client

            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

            client = Client(account_sid, auth_token)

            msg = client.messages.create(
                from_=twilio_number, body=message, to=self.recipient_phone
            )

            logger.info(f"✓ WhatsApp 消息发送成功 (Twilio, SID: {msg.sid})")
            return True

        except ImportError:
            logger.warning("Twilio SDK 未安装，请运行: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Twilio WhatsApp 错误: {e}")
            return False

    async def _send_vonage(self, message: str) -> bool:
        """使用 Vonage WhatsApp API 发送"""
        try:
            api_key = os.getenv("VONAGE_API_KEY")
            api_secret = os.getenv("VONAGE_API_SECRET")
            vonage_number = os.getenv("VONAGE_WHATSAPP_NUMBER")

            url = "https://messages-sandbox.nexmo.com/v1/messages"

            payload = {
                "messaging_product": "whatsapp",
                "to": self.recipient_phone.replace("+", ""),
                "type": "text",
                "text": {"body": message},
                "from": vonage_number,
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}:{api_secret}",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 202:
                    logger.info("✓ WhatsApp 消息发送成功 (Vonage)")
                    return True
                else:
                    logger.error(
                        f"Vonage 发送失败 ({response.status_code}): {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Vonage WhatsApp 错误: {e}")
            return False

    def _format_message(self, message: str, title: Optional[str] = None) -> str:
        """格式化消息为 WhatsApp 风格"""
        if title:
            # 使用 **粗体** 作为标题（WhatsApp 支持 *粗体* 或 **粗体**）
            formatted = f"*{title}*\n\n{message}"
        else:
            formatted = message

        # 移除多余的空行，WhatsApp 对空行敏感
        lines = formatted.split("\n")
        lines = [line.rstrip() for line in lines]
        formatted = "\n".join(lines)

        return formatted

    def _split_message(self, message: str, max_length: Optional[int] = None) -> List[str]:
        """
        分割长消息

        WhatsApp 限制：
        - 单条消息最多 4096 字符
        - 但建议保守估计为 1000 字符防止显示问题
        """
        if max_length is None:
            max_length = min(self.max_length, 1000)

        if len(message) <= max_length:
            return [message]

        messages = []
        current_pos = 0

        while current_pos < len(message):
            # 查找最后一个换行符
            end_pos = min(current_pos + max_length, len(message))

            if end_pos < len(message):
                # 向后查找最后的换行符
                last_newline = message.rfind("\n", current_pos, end_pos)
                if last_newline > current_pos:
                    end_pos = last_newline

            messages.append(message[current_pos : end_pos].strip())
            current_pos = end_pos

        return messages

    def sync_send(self, message: str, title: Optional[str] = None) -> bool:
        """同步发送（用于非异步上下文）"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果已有运行中的 loop，创建新的协程任务
                task = asyncio.ensure_future(self.send(message, title))
                return True  # 异步发送，返回 True 表示已提交
            else:
                return loop.run_until_complete(self.send(message, title))
        except RuntimeError:
            # 没有 loop，创建新的
            return asyncio.run(self.send(message, title))


# 全局实例
whatsapp_service: Optional[WhatsAppNotificationService] = None


def get_whatsapp_service() -> WhatsAppNotificationService:
    """获取 WhatsApp 服务单例"""
    global whatsapp_service
    if whatsapp_service is None:
        whatsapp_service = WhatsAppNotificationService()
    return whatsapp_service


async def send_whatsapp_notification(
    message: str, title: Optional[str] = None
) -> bool:
    """发送 WhatsApp 通知（异步）"""
    service = get_whatsapp_service()
    return await service.send(message, title)


def send_whatsapp_notification_sync(
    message: str, title: Optional[str] = None
) -> bool:
    """发送 WhatsApp 通知（同步）"""
    service = get_whatsapp_service()
    return service.sync_send(message, title)
