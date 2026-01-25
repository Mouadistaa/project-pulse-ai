from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from app.db.session import get_db
from app.modules.users.schemas import User, UserCreate, Token, UserUpdate, Workspace, WorkspaceCreate
from app.modules.users.service import UserService
from app.core.security import create_access_token
from app.core.errors import AuthError, EntityNotFound
from app.core.config import settings
from jose import jwt, JWTError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
user_service = UserService()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.post("/auth/register", response_model=User)
async def register(user_in: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await user_service.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(db, user_in)

@router.post("/auth/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    user = await user_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise AuthError("Incorrect email or password")
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@router.get("/workspaces", response_model=List[Workspace])
async def read_workspaces(current_user: Annotated[User, Depends(get_current_active_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    # Determine what workspaces user can see. For now, just their own.
    # If user has workspace_id, return that workspace.
    if current_user.workspace:
        return [current_user.workspace]
    return []

# Example Create Workspace endpoint if needed
@router.post("/workspaces", response_model=Workspace)
async def create_workspace_endpoint(workspace_in: WorkspaceCreate, current_user: Annotated[User, Depends(get_current_active_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    # Only allow if user has no workspace? Or allow multiple?
    # Simple implementation:
    # ...
    pass
