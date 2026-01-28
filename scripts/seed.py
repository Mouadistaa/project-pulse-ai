from app.db.session import AsyncSessionLocal
from app.modules.users.service import UserService
from app.modules.users.schemas import UserCreate
from app.modules.integrations.models import Integration, IntegrationType, IntegrationStatus
from app.modules.ingestion.jobs import sync_workspace
import asyncio
import os

async def seed():
    async with AsyncSessionLocal() as session:
        # 1. Create Admin User
        user_service = UserService()
        email = "admin@pulse.ai"
        
        # Check if exists
        existing = await user_service.get_user_by_email(session, email)
        if existing:
            print("User already exists.")
            return

        print("Creating User...")
        user = await user_service.create_user(session, UserCreate(
            email=email,
            password="password",
            full_name="Admin User",
            workspace_slug="demo-workspace"
        ))
        
        # 2. Add GitHub Integration
        print("Adding GitHub Integration...")
        github_integration = Integration(
            workspace_id=user.workspace_id,
            type=IntegrationType.GITHUB,
            status=IntegrationStatus.ACTIVE,
            name="Demo GitHub",
            config={"repo": "demo/repo"}
        )
        session.add(github_integration)
        
        # 3. Add Trello Integration
        print("Adding Trello Integration...")
        trello_integration = Integration(
            workspace_id=user.workspace_id,
            type=IntegrationType.TRELLO,
            status=IntegrationStatus.ACTIVE,
            name="Demo Trello",
            config={"boards": ["demo-board"]}
        )
        session.add(trello_integration)
        await session.commit()
        
        # 4. Trigger Sync
        print("Triggering Data Sync...")
        # Set Env var strictly for this call (though typically set in docker env)
        os.environ["MOCK_MODE"] = "true"
        await sync_workspace(user.workspace_id)
        
        print("Seeding Complete. Login with admin@pulse.ai / password")

if __name__ == "__main__":
    asyncio.run(seed())
