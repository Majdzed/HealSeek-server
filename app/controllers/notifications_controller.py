from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.database.database import db, Notification as nt
from app.routes.websocket_endpoint import manager as connection_manager
from app.models.Notifications import Notification
from typing import List

async def send_notification(notification: Notification):
    notification = notification.dict()
    await connection_manager.send_notification(notification["user_id"], notification)
    try:
        notification_query = nt.insert(**notification)
        db.execute_query(notification_query)
        return JSONResponse(content={"data": notification}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

def get_all_notifications(request: Request, skip: int = 0, limit: int = 50):
    user_id = request.state.user
    try:
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM notifications WHERE user_id = %s"
        db.execute_query(count_query, params=(user_id,))
        total_count = db.fetch_one()[0]

        # Get paginated notifications
        notifications_query = f"{nt.find(user_id=user_id)} ORDER BY created_at DESC LIMIT %s OFFSET %s"
        db.execute_query(notifications_query, params=(user_id, limit, skip))
        notifications = db.fetch_all()
        
        notifications_list = [{
            "notification_id": notification[0],
            "content": notification[1],
            "is_read": notification[2],
            "created_at": notification[3].isoformat(),
            "user_id": notification[4]
        } for notification in notifications]

        return JSONResponse(content={
            "data": notifications_list,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")

def get_notification_by_id(request: Request, notification_id: int):
    user_id = request.state.user
    try:
        notification_query = nt.find(notification_id=notification_id)
        db.execute_query(notification_query, params=(notification_id,))
        notification = db.fetch_one()

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        # Verify ownership
        if notification[4] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this notification")

        return JSONResponse(content={
            "notification_id": notification[0],
            "content": notification[1],
            "is_read": notification[2],
            "created_at": notification[3].isoformat(),
            "user_id": notification[4]
        }, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification: {str(e)}")

def update_notification_status(request: Request, notification_id: int, is_read: bool):
    user_id = request.state.user
    try:
        # Verify notification exists and belongs to user
        notification_query = nt.find(notification_id=notification_id)
        db.execute_query(notification_query, params=(notification_id,))
        notification = db.fetch_one()

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification[4] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to modify this notification")

        # Update status
        update_query = nt.update(is_read=is_read, notification_id=notification_id)
        db.execute_query(update_query, params=(is_read, notification_id))
        
        return JSONResponse(content={
            "message": f"Notification marked as {'read' if is_read else 'unread'}",
            "notification_id": notification_id
        }, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update notification status: {str(e)}")

def delete_notification(request: Request, notification_id: int):
    user_id = request.state.user
    try:
        # Verify notification exists and belongs to user
        notification_query = nt.find(notification_id=notification_id)
        db.execute_query(notification_query, params=(notification_id,))
        notification = db.fetch_one()

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification[4] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this notification")

        delete_query = nt.delete(notification_id=notification_id)
        db.execute_query(delete_query, params=(notification_id,))
        
        return JSONResponse(content={
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        }, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

def delete_multiple_notifications(request: Request, notification_ids: List[int]):
    user_id = request.state.user
    try:
        # Verify all notifications exist and belong to user
        for notification_id in notification_ids:
            notification_query = nt.find(notification_id=notification_id)
            db.execute_query(notification_query, params=(notification_id,))
            notification = db.fetch_one()
            
            if not notification:
                raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found")
            if notification[4] != user_id:
                raise HTTPException(status_code=403, detail=f"Not authorized to delete notification {notification_id}")

        # Delete notifications
        placeholders = ','.join(['%s'] * len(notification_ids))
        delete_query = f"DELETE FROM notifications WHERE notification_id IN ({placeholders}) AND user_id = %s"
        db.execute_query(delete_query, params=(*notification_ids, user_id))

        return JSONResponse(content={
            "message": "Notifications deleted successfully",
            "deleted_ids": notification_ids
        }, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notifications: {str(e)}")