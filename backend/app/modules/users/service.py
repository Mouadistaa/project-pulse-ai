from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.users.models import AppUser, Workspace
from app.modules.users.schemas import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.errors import EntityNotFound, AuthError
import uuid

class UserService:
    async def get_user_by_email(self, db: AsyncSession, email: str) -> AppUser | None:
        result = await db.execute(select(AppUser).where(AppUser.email == email))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> AppUser:
        # Check if workspace exists or create default if needed
        # For simplicity, if workspace_slug is provided, try to find it.
        # If not provided, user might be created without workspace or specific logic
        
        workspace_id = None
        if user_in.workspace_slug:
             result = await db.execute(select(Workspace).where(Workspace.slug == user_in.workspace_slug))
             workspace = result.scalars().first()
             if workspace:
                 workspace_id = workspace.id
             else:
                 # Auto create workspace for demo? Or fail. Let's auto create for MVP seeding
                 workspace = Workspace(name=user_in.workspace_slug, slug=user_in.workspace_slug)
                 db.add(workspace)
                 await db.flush()
                 workspace_id = workspace.id
        
        db_user = AppUser(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            workspace_id=workspace_id,
            role="ADMIN" if workspace_id else "READER" # First user of workspace is ADMIN? Simplified logic.
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> AppUser | None:
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
