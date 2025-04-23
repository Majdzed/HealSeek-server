from fastapi import APIRouter, HTTPException, Request, Depends, Path, Query, Body
from typing import List, Optional
from app.controllers.notifications_controller import (
    send_notification,
    get_all_notifications,
    get_notification_by_id,
    update_notification_status,
    delete_notification,
    delete_multiple_notifications
)
from app.routes.user_routes import resolve_user_temp
from app.models.Notifications import Notification, NotificationResponse

router = APIRouter()

@router.get(
    "/",
    response_model=List[NotificationResponse],
    description="Get all notifications for the authenticated user",
    responses={
        200: {"description": "Successfully retrieved notifications"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))]
)
async def get_notifications(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return")
):
    return await get_all_notifications(request, skip, limit)

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    description="Get a specific notification by ID",
    responses={
        200: {"description": "Successfully retrieved notification"},
        404: {"description": "Notification not found"},
        403: {"description": "Not authorized to access this notification"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))]
)
async def get_notification(
    request: Request,
    notification_id: int = Path(..., gt=0)
):
    return await get_notification_by_id(request, notification_id)

@router.put(
    "/{notification_id}/read",
    description="Mark a notification as read/unread",
    responses={
        200: {"description": "Successfully updated notification status"},
        404: {"description": "Notification not found"},
        403: {"description": "Not authorized to modify this notification"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))]
)
async def update_read_status(
    request: Request,
    notification_id: int = Path(..., gt=0),
    is_read: bool = Query(..., description="New read status")
):
    return await update_notification_status(request, notification_id, is_read)

@router.delete(
    "/{notification_id}",
    description="Delete a specific notification",
    responses={
        200: {"description": "Successfully deleted notification"},
        404: {"description": "Notification not found"},
        403: {"description": "Not authorized to delete this notification"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))]
)
async def delete_single_notification(
    request: Request,
    notification_id: int = Path(..., gt=0)
):
    return await delete_notification(request, notification_id)

@router.delete(
    "/batch",
    description="Delete multiple notifications",
    responses={
        200: {"description": "Successfully deleted notifications"},
        404: {"description": "One or more notifications not found"},
        403: {"description": "Not authorized to delete one or more notifications"}
    },
    dependencies=[Depends(resolve_user_temp(allowed_roles=["admin", "patient", "doctor"]))]
)
async def delete_batch_notifications(
    request: Request,
    notification_ids: List[int] = Body(..., embed=True)
):
    return await delete_multiple_notifications(request, notification_ids)