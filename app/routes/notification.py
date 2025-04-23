from fastapi import APIRouter
router = APIRouter(
    prefix="/notification",
    tags=["notification"],
)


@router.get("/")
def get_notification():
    return {"notification": "notifications"}

@router.get("/{notification_id}")
def get_notification(notification_id: int):
    return {"notification_id": notification_id}

@router.post("/")
def create_notification():
    return {"message": "notification created"}

@router.put("/{notification_id}")
def update_notification(notification_id: int):
    return {"message": "notification updated"}

@router.delete("/{notification_id}")
def delete_notification(notification_id: int):
    return {"message": "notification deleted"}