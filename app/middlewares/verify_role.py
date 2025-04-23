from fastapi import HTTPException, Request, Response
from app.enums.roles import Roles


from app.models.enums.roles_enums import RolesEnum
def verify_role(user, allowed_roles):
    # Convert allowed_roles to a list if it's not already
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    elif isinstance(allowed_roles, Roles):  # Assuming Roles is your custom class
        allowed_roles = [allowed_roles.value]

    # Check if the user's role matches any of the allowed roles
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")

    return user
