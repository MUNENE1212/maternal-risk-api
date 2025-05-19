from fastapi import Request, HTTPException, Depends
from jose import JWTError, jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from app.auth.auth_utils import SECRET_KEY, ALGORITHM


# If you have your user retrieval logic in another file, import it
# from app.routers.auth_router import get_current_user

def require_role(required_roles: list[str]):
    async def role_checker(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_role = payload.get("role")
            if user_role not in required_roles:
                raise HTTPException(status_code=403, detail="Forbidden: Insufficient role")
        except JWTError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        request.state.user = payload  # optional for downstream use
        return payload

    return role_checker  # ✅ return the function itself, not Depends()

