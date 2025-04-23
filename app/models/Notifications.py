from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    content: str = Field(..., description="The content of the notification")
    is_read: bool = Field(default=False, description="Whether the notification has been read")
    user_id: int = Field(..., description="The ID of the user this notification is for")

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    created_at: datetime = Field(default_factory=datetime.now, description="When the notification was created")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NotificationResponse(NotificationBase):
    notification_id: int = Field(..., description="The unique identifier of the notification")
    created_at: datetime = Field(..., description="When the notification was created")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        orm_mode = True

class NotificationUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Updated content of the notification")
    is_read: Optional[bool] = Field(None, description="Updated read status")

class NotificationDelete(BaseModel):
    notification_ids: list[int] = Field(..., description="List of notification IDs to delete")