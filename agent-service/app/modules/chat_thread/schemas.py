from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator
from app.common.schemas import BaseSchema


class ChatThreadCreate(BaseSchema):
    """创建会话请求"""

    title: str = Field(default="新会话", min_length=1, max_length=200)

    # 前置处理
    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        # 如果标题是 "     ", 是不合理的
        # 去空格，"     " -> ""，则通过不了 min_length=1
        return value.strip()

class ChatThreadResponse(BaseSchema):
    """会话响应"""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

from typing import Literal


class ChatMessageResponse(BaseSchema):
    """历史消息"""

    role: Literal["user", "assistant"]
    content: str


class ChatHistoryResponse(BaseSchema):
    """对话历史列表"""

    thread_id: UUID
    messages: list[ChatMessageResponse]